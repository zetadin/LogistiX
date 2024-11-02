from django.apps import AppConfig
import signal
import logging
import datetime
from BGJobQueue.jobs import Job, Broker, Worker

logger = logging.getLogger(__name__)


class BgjobqueueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BGJobQueue'

    def ready(self):
        print("\nReadying BGJobQueue.")
        self.name = "BGJobQueue"
        self.verbose_name = "Background Job Queue"

        self.broker = Broker()
        self.start_broker_and_workers()


    def kill_broker(self, signum, frame):
        """Kills the broker. It will kill workers in turn."""
        logger.info(f"Stopping server.")
        self.broker.terminate()
        logger.info(f"Server terminating from signal {signum}.")
        exit(1)


    def start_broker_and_workers(self):
        logger.info(f"Starting workers and broker.")

        # configure a signal handler to forward SIGKILL, SIGINT, and SiGTERM to the broker
        signal.signal(signal.SIGTERM, self.kill_broker)
        signal.signal(signal.SIGINT, self.kill_broker)

        # start the broker
        self.broker.start()


        #DEBUG: submit a repeating job
        j = Job(lambda: print("Hello World!"), when=datetime.datetime.now(), repeat_time=5.0)
        logger.debug(f"Submitted DEBUG job.")