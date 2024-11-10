# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.
import logging
import datetime
from warroom.map.models import Map
from BGJobQueue.jobs import Job

logger = logging.getLogger(__name__)

class MapSimJob(Job):
    # Prevent simulating the same map more than once
    def isDuplicateInQueue(self, queue):
        """
        Check if this job has already been put into the queue.
        Overrides function in Job.
        """
        mapSims=[j for j in queue if (isinstance(j, MapSimJob) and 'mapid' in j.kwargs.keys())]
        if(self.kwargs['mapid'] in [j.kwargs['mapid'] for j in mapSims]):
            return True
        else:
            return False

def runsim(mapid="bla", *args, **kwargs):
    start = datetime.datetime.now()
    logger.debug(f"Simulatiing map {mapid:.10} at {start}")

    # at the end, deactivate the map
    Map.objects.filter(name=mapid).update(active=False)
    end = datetime.datetime.now()
    logger.debug(f"Done with map {mapid:.10} in {(end-start).total_seconds()*1.e3:.3} ms.")