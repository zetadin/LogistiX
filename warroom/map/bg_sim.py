# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.
import logging
import datetime
from warroom.map.models import Map

logger = logging.getLogger(__name__)

def runsim(mapid="bla", *args, **kwargs):
    start = datetime.datetime.now()
    logger.debug(f"Simulatiing map {mapid:.10} at {start}")

    # at the end, deactivate the map
    Map.objects.filter(name=mapid).update(active=False)
    end = datetime.datetime.now()
    logger.debug(f"Done with map {mapid:.10} in {(end-start).total_seconds()*1.e3:.3} ms.")