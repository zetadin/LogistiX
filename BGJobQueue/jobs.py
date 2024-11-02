import multiprocessing as mp
import datetime
import signal
import logging
from django.conf import settings
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


    def run(self, workerID, lg=None):
        """Runs the job. Call this from workers."""
        if(lg is not None):
            lg.debug(f"{datetime.datetime.now()}: "+
                        f"running {self.func.__name__} scheduled for {self.when}")
        self.func(*self.args, **self.kwargs)



class Broker(mp.Process):
    def __init__(self, queue_timeout=0.05):
        super().__init__()
        self.queue_timeout = queue_timeout
        self.in_queue = mp.Queue()
        self.out_queue = mp.Queue()
        self.jobList = []
        self.workers = []

        self.n_workers = getattr(settings, "BGJOBQUEUE_N_WORKERS", 1)
        
        self.daemon = False
        self.keep_running = False


    def stop_gracefully(self, signum=None, frame=None):
        self.keep_running = False
        for w in self.workers:
            w.terminate()
        logger.info(f"Broker terminating from signal {signum}.")

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
                    self.jobList.append(msg)

            except mp.queues.Empty:
                # keep looping if queue is empty
                pass

            # sort jobs by soonest
            self.jobList.sort(key=lambda x: x.when, reverse=False) # ascending order
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
                        

            

class Worker(mp.Process):
    def __init__(self, workerID,
                 job_queue=None, queue_timeout=0.05):
        super().__init__()
        self.queue_timeout = queue_timeout
        self.daemon = True # multiprocessing with auto-terminate this if parent dies
        self.in_queue = job_queue
        self.id = workerID
        

    def run(self):
        """Body of the Worker process."""
        self.keep_running = True

        self.logger = logging.getLogger("Worker"+str(self.id))
        self.logger.debug(f"Starting worker {self.id}.")

        while self.keep_running:
            self.logger.debug(f"Looping.")
            try:
                # self.logger.debug(f"Polling.")
                job = self.in_queue.get(block=True,
                                        timeout=self.queue_timeout) # 50 ms default
                # self.logger.debug(f"Trying to run Job.")
                job.run(self.logger)

            except mp.queues.Empty:
                # keep looping if queue is empty
                pass
                
                