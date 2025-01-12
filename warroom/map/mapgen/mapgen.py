# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

import sys, os
import numpy as np
from enum import Enum
import time
import json


from django.conf import settings
from warroom.map.models import MapType, Chunk
from warroom.map.facilities import Facility
from warroom.units.models import Company
from warroom.map.mapgen.gen_water import gen_lakes_and_rivers
from warroom.map.mapgen.gen_controls import gen_controls
from warroom.map.mapgen.gen_cities import gen_cities
from warroom.map.mapgen.gen_facilities import gen_spaceports, gen_industrial_regions, gen_fabs, fill_warehouses
from warroom.map.mapgen.gen_units import mapgen_units


MODULE_PATH = os.path.dirname(os.path.realpath(__name__))
sys.path.append(os.path.join(MODULE_PATH, 'deps/terrain_gen/build'))
import terraingen as tg

# class MapShape(Enum):
#     Square = 0
#     Circle = 1
#     # Hex = 2
    


# def mapgen_ter(map_obj, mt, map_shape, size=5):
def mapgen_ter(map_obj, mt, size=5):
    '''Generates map. Starts with Terrain type generation and then calls Structure generation.

    Keyword arguments:
    map_obj -- instance of the Map model
    mt -- map type according to the MapType enum

    Optional arguments:
    size -- desired width of the map in hex widths (default 5).
            Height will be calculated to give the same real space size.
    '''
    if(not mt in MapType):
        raise ValueError("Non-inplemented MapType requested")

    # minimal size is 1
    if(size<1):
        size=1
    # if(map_shape == MapShape.Hex):
    #     if(size%2==1):
    #         size+=1 # Hex needs even size

    # size is number of horizontal a hexes
    a = 1/np.sqrt(3)                    # a is half of hex width, or 3/2 of step between hexes; scale so that real space distance between two neighbours (2*h) is 1
    h = 0.5*np.sqrt(3)*a                # half of hex height in a
    n_x = int(np.floor(size))           # num hexes in x; horizontal step to next hex is 1.5*a
    n_y = int(np.floor(size*0.75*a/h))  # num hexes in y


    start_time = time.time()

    # map hex ids for a square map
    m_x = np.arange(0,n_x).astype(np.int32)
    m_y = np.arange(0,n_y).astype(np.int32)
    m_x, m_y = np.meshgrid(m_x, m_y)
    m_x=m_x.flatten()
    m_y=m_y.flatten()
    
    # real space coords
    r_temp_x = np.linspace(0,size*1.5*a,n_x, endpoint=False).astype(np.float32)
    r_temp_y = np.linspace(0,n_y*2*h,n_y, endpoint=False).astype(np.float32)
    r_x, r_y = np.meshgrid(r_temp_x, r_temp_y)
    r_y[:,1::2] += h   # y of every other column is shifted by h
    
    #ensure 1D arrays
    r_x=r_x.flatten()
    r_y=r_y.flatten()

    # -------- Stick to rectangular maps so neighbour searching is easier --------
    # # this should give us a square map
    # # if we want other shapes, we cut them out of the square with masks
    # mask = np.full(r_x.shape, True, dtype=bool)
    # if(map_shape == MapShape.Circle):
    #     # 
    #     dx = r_x-0.5*size
    #     dy = r_y-0.5*size
    #     mask = np.argwhere(dx*dx+dy*dy < 0.25*size*size)
        
    # # TODO: add support for other map shapes
    # # elif(mt == MapShape.Hex):

    # # apply mask
    # r_x = r_x[mask]
    # r_y = r_y[mask]
    # m_x = m_x[mask]
    # m_y = m_y[mask]
        
    # generate a terrain data for the above points
    gen=tg.Generator()
    gen.setSeed(int(map_obj.seed))
    gen.setFreq(0.003*512/(size*1.5*a))
    v = gen.getTerrain(r_x, r_y, map_type=mt.value, size=size*1.5*a)

    
    ter_names=["None","Sea","Swamp","Plain","Forest","Hills","Mountains", "Lake"]
    ter_names=np.array(ter_names, dtype=object)
    ters_names_by_i = ter_names[v]

    end_time = time.time()
    terrain_dt = end_time - start_time
    start_time = end_time

    # generate map structures
    np.random.seed(map_obj.seed + 331) # make np.choice consistent with map seed
    structures = mapgen_structures(m_x,m_y,v, r_x,r_y, ters_names_by_i)
        
    # decode output
    river_direction = structures[0]
    control_maps = structures[1]
    facilities = structures[2]

    end_time = time.time()
    structure_dt = end_time - start_time
    start_time = end_time


    # generate units
    units = mapgen_units(m_x, m_y, v, r_x, r_y, ters_names_by_i, control_maps)

    end_time = time.time()
    units_dt = end_time - start_time
    start_time = end_time


    # parse the hexes into chunks
    chunks = {}
    for i in range(len(v)):
        # find chunk coords
        chunk_x = int(m_x[i]/settings.CHUNK_SIZE)
        chunk_y = int(m_y[i]/settings.CHUNK_SIZE)
        chunk_id = f"{chunk_x}_{chunk_y}"

        if(chunk_id in chunks.keys()):
            cur_chunk = chunks[chunk_id]
        else:
            cur_chunk = {"chunk_x": chunk_x, "chunk_y": chunk_y, "hexes": []}

        # create hex
        hex = {
                "x": int(m_x[i]), "y": int(m_y[i]),
                "terrain": ters_names_by_i[i],
                "control": control_maps[i].tolist(),
               }

        # encode improvements
        improvements={}
        if(river_direction[i]>=0):
            improvements["river_dir"] = str(river_direction[i])
        hex["improvements"] = improvements

        # add hex to chunk
        cur_chunk["hexes"].append(hex)

        # update chunk in dict
        chunks[chunk_id] = cur_chunk

    # create chunk DB rows
    ready_chunks = []
    for chunk_id in chunks.keys():
        cur_chunk = chunks[chunk_id]
        ready_chunks.append(Chunk(x=cur_chunk["chunk_x"], y=cur_chunk["chunk_y"], map=map_obj,
                                  data=json.dumps(cur_chunk["hexes"])))
        
    Chunk.objects.bulk_create(ready_chunks)

    # assign facilities to chunks and create facility DB rows
    for fac in facilities:
        chunk_x = int(fac.x/settings.CHUNK_SIZE)
        chunk_y = int(fac.y/settings.CHUNK_SIZE)
        fac.chunk = Chunk.objects.get(x=chunk_x, y=chunk_y, map=map_obj)
    Facility.objects.bulk_create(facilities)
    # read facilities from DB with their new pks
    facilities = Facility.objects.filter(chunk__map=map_obj)

    end_time = time.time()
    database_dt = end_time - start_time
    start_time = end_time

    # ------ Populate the industrial regions with Fabs -------
    # this needs to run after facilities have been saved to DB and we have their pks
    fabs = gen_fabs(facilities)

    end_time = time.time()
    structure_dt += start_time - end_time
    start_time = end_time

    # assign fabs to chunks and create their facility DB rows
    for fab in fabs:
        chunk_x = int(fab.x/settings.CHUNK_SIZE)
        chunk_y = int(fab.y/settings.CHUNK_SIZE)
        fab.chunk = Chunk.objects.get(x=chunk_x, y=chunk_y, map=map_obj)
    Facility.objects.bulk_create(fabs)


    # Populate units into the DB
    Company.objects.bulk_create(units)

    end_time = time.time()
    database_dt += end_time - start_time
    
    
    tot_dt = terrain_dt + structure_dt + units_dt + database_dt
    print("############# MAP GEN TIME REPORT #############")
    print(f"Terrain time                       :{terrain_dt*1000:6.1f} ms")
    print(f"Improvements & Facilities time     :{structure_dt*1000:6.1f} ms")
    print(f"Units time                         :{units_dt*1000:6.1f} ms")
    print(f"Database time                      :{database_dt*1000:6.1f} ms")
    print(f"Total generation time              :{tot_dt*1000:6.1f} ms")
    print()





# creates map structures
def mapgen_structures(x, y, v, r_x, r_y, ter_names, width=None, height=None):
    '''Generates structures/improvements on a map: Lakes, Rivers, Towns, Roads, Spaceports, etc.

        Keyword arguments:
        x -- array of map x coord for each hex
        y -- array of map y coord for each hex
        v -- array of terrrain type ids according to the c++ generator
        r_x -- array of real space x coord for each hex
        r_y -- array of real space y coord for each hex
        ter_names -- array of terrain type names for each hex
        
        Optional Rguments:
        width -- map width (default max(x)+1)
        height -- map height (default max(y)+1)
        '''
    if(width==None):
        width = np.max(x)+1
    if(height==None):
        height = np.max(y)+1

    facilities = []
    

    # Build an array of neighbour indices
    per_hex_x_neighs = np.array([0,1,1,0,-1,-1], dtype=int) # go clockwize from top
    per_hex_y_neighs = np.array([-1,-1,0,1,0,-1], dtype=int) # assuming x is even
    x_neighs = x[:,None] + per_hex_x_neighs[None,:]
    y_neighs = y[:,None] + per_hex_y_neighs[None,:]

    # for odd x, move y coord of side neighbours
    temp = y_neighs[x%2==1,:]
    temp[:, [1,2,4,5]] +=1
    y_neighs[x%2==1, :] = temp 
    
    # assume we are dealing with rectangular maps
    x_neighs[np.logical_or(x_neighs<0, x_neighs>=width)] = -10*width*height - 1   # mark neigbours outside the map as negative
    y_neighs[np.logical_or(y_neighs<0, y_neighs>=height)] = -10*width*height -1
    neighbour_ids = y_neighs*width + x_neighs

    del per_hex_x_neighs, per_hex_y_neighs, x_neighs, y_neighs, temp # free memory

    # ------ Rivers -------
    river_direction = gen_lakes_and_rivers(x, y, v, r_x, r_y, ter_names, neighbour_ids,
                                           width=width, height=height)

    # ------ Control Maps -------
    control_levels = gen_controls(x,y,v, r_x,r_y, ter_names, neighbour_ids,
                                     width=width, height=height)
    
    # ------ Cities -------
    gen_cities(x, y, v, ter_names, neighbour_ids, river_direction, control_levels, facilities)

    # ------ Spaceports -------
    gen_spaceports(x, y, ter_names, control_levels, facilities)

    # ------  Industrial Region nodes -------
    gen_industrial_regions(x, y, r_x, r_y, ter_names, river_direction, control_levels, facilities)
        
    return(river_direction, control_levels, facilities)




