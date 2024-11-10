# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.
from django.apps import AppConfig
import signal
import logging
import sys, os
from django.conf import settings
from BGJobQueue.jobs import Job, Broker, DeleteJob

logger = logging.getLogger(__name__)


# def test_job(*args, **kwargs):
#     print("Hello World!")

# def test_job2(*args, **kwargs):
#     print("22222222222! Done!")


class BgjobqueueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BGJobQueue'

    def ready(self):
        print("\nReadying BGJobQueue.")
        self.name = "BGJobQueue"
        self.verbose_name = "Background Job Queue"

        self.broker = Broker(
            getattr(settings, "BGJOBQUEUE_TIMEOUT", 0.05),
            getattr(settings, "BGJOBQUEUE_N_WORKERS", 1)
        )

        if ('runserver' in sys.argv or os.environ.get('SERVER_GATEWAY_INTERFACE') == 'WSGI'):
            # only lauch broker if we are running the server, not during migrations, etc.
            self.start_broker_and_workers()


    def kill_broker(self, signum, frame):
        """Kills the broker. It will kill workers in turn."""
        self.broker.terminate()
        logger.info(f"Server terminating from signal {signum}.")
        exit(1)

    def submit_job(self, job):
        """
        Submits a job to the broker.
        Call this from other apps instead of using the broker directly.
        """
        self.broker.in_queue.put(job)


    def start_broker_and_workers(self):
        logger.info(f"Starting workers and broker.")

        # configure a signal handler to forward SIGKILL, SIGINT, and SiGTERM to the broker
        signal.signal(signal.SIGTERM, self.kill_broker)
        signal.signal(signal.SIGINT, self.kill_broker)

        # start the broker
        self.broker.start()


        # #DEBUG: submit a repeating job
        # t = datetime.datetime.now()
        # t+= datetime.timedelta(seconds=5)
        # j = Job(test_job, when=t, repeat_time=0)
        # self.broker.in_queue.put(j)
        # logger.debug(f"Submitted DEBUG job.")

        # t-= datetime.timedelta(seconds=3)
        # j = Job(test_job2, when=t, repeat_time=1.0)
        # self.broker.in_queue.put(j)
        # logger.debug(f"Submitted repearing DEBUG job.")
        