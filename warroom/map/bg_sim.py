# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from warroom.map.models import Map
from main_menu.models import Profile
from BGJobQueue.jobs import Job, DeleteJob

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
    start = timezone.now()

    # get current map
    map = Map.objects.filter(name=mapid).get()

    # find last time a subscribed user was active for this map
    subscriber_query = Profile.objects.filter(subsctibed_to_map=map.pk)
    last_time = max(subscriber_query.values_list('last_active', flat=True))
    # logger.debug(f"Last active time for {mapid:.10}: {last_time}")

    if(last_time+timedelta(seconds=settings.MAX_INACTIVE_TIME) < start):
        # no active users for a while
        logger.debug(f"Deactivating map {mapid:.10} after {start-last_time} s of inactivity.")
        map.active = False
        map.save(update_fields=['active'])

        # unscehedule this simulation job
        dj = DeleteJob(uuid=kwargs['uuid'])
        kwargs['broker_queue'].put(dj)

    else:
        # do the simulation for this map
        logger.debug(f"Simulating map {mapid:.10}.")
        pass;

    # unsubscribe inactive profiles from this map
    subscriber_query.filter(last_active__lt=start-timedelta(seconds=settings.MAX_INACTIVE_TIME)).update(subsctibed_to_map=None)

    # Report run time
    end = timezone.now()
    logger.debug(f"Done with map {mapid:.10} in {(end-start).total_seconds()*1.e3:.3} ms.")