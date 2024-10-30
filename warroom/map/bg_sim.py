# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.
import time
from warroom.map.models import Map

def runsim(mapid="bla"):
    start = time.time()
    print(f"\t\tStarting Simulation of map {mapid:.10} at {start} s")
    tot_time = 0.5*60 # seconds
    max_steps = int(tot_time/5) # with 5 second interval
    target_interval = tot_time / max_steps # seconds
    interval = tot_time / max_steps # seconds
    for step in range(max_steps):
        print(f"\t\tSimulating map {mapid:.10}: sleeping for {interval} s")
        time.sleep(interval)

        # how nuch to sleep next
        end = time.time()
        interval = 2*target_interval - (end - start)
        start = end

    # at the end, deactivate the map
    Map.objects.filter(name=mapid).update(active=False)
    print(f"\t\t Done with map {mapid:.10}")