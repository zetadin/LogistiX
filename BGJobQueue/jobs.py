import multiprocessing as mp
import datetime
import signal
import logging
import uuid

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, func,
                 when = datetime.datetime.now(),
                 repeat_time = 30.0, # seconds
                 *args, **kwargs):
        """Sets up a job to be run at the given time.
        Set repeat_time <= 0 if you want it to run only once."""
        self.func = func
        self.when = when
        self.repeat_time = repeat_time
        self.args = args
        self.kwargs = kwargs
        # give the function a uuid for the job so it turn off it's own repeat
        self.uuid = uuid.uuid4()
        self.kwargs['uuid'] = self.uuid
        if(not 'broker_queue' in self.kwargs.keys()):
            self.kwargs['broker_queue'] = None


    def __str__(self):
        return(f"{str(self.uuid):.6}__{self.func.__name__}")


    def run(self, lg=None):
        """Runs the job. Call this from workers."""
        if(lg is not None):
            lg.debug(f"{datetime.datetime.now()}: "+
                        f"running {self.func.__name__} scheduled for {self.when}")
        self.func(*self.args, **self.kwargs)


class DeleteJob:
    """Message from a job to the Broker to stop repeating that job."""
    def __init__(self, uuid):
        self.uuid = uuid




class Broker(mp.Process):
    def __init__(self, queue_timeout=0.05, n_workers=1):
        super().__init__()
        self.queue_timeout = queue_timeout
        self.in_queue = mp.Queue()
        self.out_queue = mp.Queue()
        self.jobList = []
        self.joblist_clean = True
        self.workers = []
        self.n_workers = n_workers
        
        self.daemon = False
        self.keep_running = False


    def stop_gracefully(self, signum=None, frame=None):
        if(self.keep_running):
            self.keep_running = False
            for w in self.workers:
                w.terminate()
            logger.info(f"Broker terminating from signal {signum}.")
            exit(0)

    def run(self):
        """Body of the Broker process."""

        self.keep_running = True

        # register graceful shutdown handler
        signal.signal(signal.SIGINT, self.stop_gracefully)
        signal.signal(signal.SIGTERM, self.stop_gracefully)

        # start the workers
        self.workers = [Worker(i, self.out_queue) for i in range(self.n_workers)]
        for w in self.workers:
            w.start()

        # main loop
        while self.keep_running:
            try:
                msg = self.in_queue.get(block=True,
                                        timeout=self.queue_timeout) # 50 ms default

                if isinstance(msg, Job):
                    logger.debug(f"Got new Job: {msg}")
                    self.jobList.append(msg)
                    self.joblist_clean = False

                elif isinstance(msg, DeleteJob):
                    logger.debug(f"Removing job by request: {msg.uuid}")
                    self.jobList = [j for j in self.jobList if j.uuid != msg.uuid]

            except mp.queues.Empty:
                pass # keep looping if queue is empty

            # sort jobs by soonest
            if not self.joblist_clean:
                self.jobList.sort(key=lambda x: x.when, reverse=False) # ascending order
                self.joblist_clean = True
                logger.debug(f"JobList: {self.jobList}")

            now = datetime.datetime.now()
            for job in self.jobList:
                if job.when <= now:
                    self.out_queue.put(job)
                    if job.repeat_time > 0:
                        # next run should be repeat time after last scheduled time
                        job.when += datetime.timedelta(seconds=job.repeat_time)
                    else:
                        # no repeats
                        self.jobList.remove(job)
                        logger.debug(f"JobList: {self.jobList}")
                else: # only jobs at start of sorted list can be ready
                    break
                        

            

class Worker(mp.Process):
    def __init__(self, workerID,
                 job_queue=None,
                 broker_queue=None):
        super().__init__()
        self.daemon = False
        self.in_queue = job_queue
        self.broker_queue = broker_queue
        self.id = workerID
        
    def stop_gracefully(self, signum=None, frame=None):
        if(self.keep_running):
            self.keep_running = False
            logger.info(f"Worker {self.id} terminating from signal {signum}.")
            exit(0)

    def run(self):
        """Body of the Worker process."""
        self.keep_running = True
        
        # register graceful shutdown handler
        signal.signal(signal.SIGINT, self.stop_gracefully)
        signal.signal(signal.SIGTERM, self.stop_gracefully)

        self.logger = logging.getLogger("Worker"+str(self.id))
        self.logger.debug(f"Starting worker {self.id}.")

        while self.keep_running:
            try:
                # no timeout needed here.
                job = self.in_queue.get(block=True)
                self.logger.debug(f"Trying to run Job.")
                job.kwargs['broker_queue'] = self.broker_queue
                job.run(self.logger)

            except mp.queues.Empty:
                # keep looping if queue is empty
                pass
                
                