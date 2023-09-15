import sys, os
import numpy as np
from enum import Enum
import time


from warroom.map.models import Map, Hex, Terrain, Improvement, MapType
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
    size -- desired width of the map in hexes (default 5).
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

    # size is the width of a hex, so 2*a (where a is the lattice constant)
    h = 0.5*np.sqrt(3)              # half of hex height in a
    n_x = size                      # num hexes in x
    n_y = int(np.floor(size/h))     # num hexes in y


    start = time.time()

    # map hex ids for a square map
    m_x = np.arange(0,n_x).astype(np.int32)
    m_y = np.arange(0,n_y).astype(np.int32)
    m_x, m_y = np.meshgrid(m_x, m_y)
    m_x=m_x.flatten()
    m_y=m_y.flatten()
    
    # real space coords
    r_temp_x = np.linspace(0,size,n_x, endpoint=False).astype(np.float32)
    r_temp_y = np.linspace(0,size,n_y, endpoint=False).astype(np.float32)
    r_x, r_y = np.meshgrid(r_temp_x, r_temp_y)
    r_y[:,1::2] += h   # y of every other column is shifted by h
    
    #ensure 1D arrays
    r_x=r_x.flatten()
    r_y=r_y.flatten()

    # -------- Stick to rectangular maps so neighbour searching is easier --------
    # # this should give us a square map
    # # if whe what other shapes, we cut them out of the square with masks
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
    gen.setFreq(0.003*512/size)
    v = gen.getTerrain(r_x, r_y, map_type=mt.value, size=size)

    
    ter_names=["None","Sea","Swamp","Plain","Forest","Hills","Mountains", "Lake"]
    ters = Terrain.objects.in_bulk(ter_names, field_name="name")
    ter_names=np.array(ter_names, dtype=object)
    ters_by_v=[ters[tn] for tn in ter_names]

    start_structs = time.time()

    # generate map structures
    ters_names_by_i = ter_names[v]
    structures = mapgen_structures(m_x,m_y,v, r_x,r_y, ters_names_by_i)
    
    # decode output
    river_direction = structures

    start_db = time.time()

    hexes = []
    for i in range(len(v)):

        # encode improvements
        improvements={}
        if(river_direction[i]>=0):
            improvements["river_dir"] = str(river_direction[i])

        #   improvements={"water_body_id":str(wb_id[i]),
        #                 "traversed_n":str(traversed_n[i]),
        #                 "x":str(m_x[i]), "y":str(m_y[i])
        #                }

        hexes.append(Hex(x=m_x[i], y=m_y[i], map = map_obj,
                         terrain=ters_by_v[v[i]],
                         improvements=improvements))
    Hex.objects.bulk_create(hexes)
    
    end = time.time()
    print("Terrain time       :", start_structs-start, "s")
    print("Structure time     :", start_db-start_structs, "s")
    print("Database time      :", end-start_db, "s")







# modifies the v argument to transform small inland Seas into Lakes
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

    # Build an array of neighbour indices
    per_hex_x_neighs = np.array([0,1,1,0,-1,-1], dtype=int) # go clockwize from top
    per_hex_y_neighs = np.array([-1,-1,0,1,0,-1], dtype=int) # assuming x is even
    x_neighs = x[:,None] + per_hex_x_neighs[None,:]
    y_neighs = y[:,None] + per_hex_y_neighs[None,:]
    y_neighs[x%2==1][:,[1,2,4,5]]+=1 # for odd x, move y coord of side neighbours

    # assume we are dealing with rectangular maps
    x_neighs[np.logical_or(x_neighs<0, x_neighs>=width)] = -10*width*height - 1   # mark neigbours outside the map as negative
    y_neighs[np.logical_or(y_neighs<0, y_neighs>=height)] = -10*width*height -1
    neighbour_ids = y_neighs*width + x_neighs

    del per_hex_x_neighs, per_hex_y_neighs, x_neighs, y_neighs # free memory

    # other prep work
    land_mask = ter_names!="Sea"
    lands = np.argwhere(land_mask).flatten()

    # -------- Lakes --------
    # find all contiguous Sea regions
    wb_ids = np.full(x.shape, -1, dtype=int)
    wb_size = [0]
    wb_n = 0
    t_n = 0
    traversal_order = np.full(x.shape, -1, dtype=int)
    
    # DANGER: this is a depth first search and may run into max recursion deapth
    def traverse_connected_sea(i):
        nonlocal t_n
        if(ter_names[i]=="Sea" and wb_ids[i]<0): # if you are an unassigned sea
            wb_ids[i] = wb_n
            wb_size[wb_n]+=1
            # look through your neighbours
            neighs = neighbour_ids[i]
            neighs = neighs[neighs>=0] # neighbour_ids are valid and the neighbours exist in this map

            traversal_order[i]=t_n
            t_n+=1
            for j in neighs:
                traverse_connected_sea(j)

    seas = np.argwhere(ter_names=="Sea").flatten()
    for i in seas:
        if(wb_ids[i]<0):
            traverse_connected_sea(i)
            wb_n+=1
            wb_size.append(0)

    # the ones with area of < 5% of the map are Lakes
    lake_area = v.size*0.05
    for l in range(wb_n):
        if( wb_size[l]<=lake_area):
            lake_ids = np.argwhere(wb_ids==l).flatten()
            v[lake_ids] = 7 # Lake
            ter_names[lake_ids] = "Lake"

    # # debug for lake assignment
    # return((wb_ids, traversal_order))

    # -------- Rivers --------
    # how many large rivers do we need?
    n_large_rivers = int(np.floor(len(lands)/50))
    n_small_rivers = int(np.floor(len(lands)/20))   

    # any coastal Sea hex (not Lake) or land at map edge can be a sink for large rivers
    seas = np.argwhere(ter_names=="Sea").flatten() # recalculate without lakes
    coastal_seas = []
    for i in seas:
        neighs = neighbour_ids[i]
        neighs = neighs[neighs>=0] # neighbour_ids are valid and the neighbours exist in this map
        if(np.any(ter_names[neighs]!="Sea")):
            coastal_seas.append(i)
    coastal_seas=np.array(coastal_seas, dtype=int)

    map_edge_lands = np.argwhere(np.logical_and(
                        np.any(np.vstack([x==0, x==width-1, y==0, y==height-1]), axis=0),   # map_edge
                        land_mask                                                           # lands
                        )).flatten()
    
    large_sinks = np.hstack([coastal_seas, map_edge_lands])
    
    # any Hill/Mountain/Swamp/Lake/land at map edge (Forest as backup) hex can be a source for large rivers
    large_sources = np.unique(np.hstack([map_edge_lands,
                              np.argwhere(np.any(np.vstack([
                                              ter_names=="Hills",
                                              ter_names=="Mountains",
                                              ter_names=="Swamp",
                                              ter_names=="Lake",
                                              ]), axis=0)).flatten()]
                            ))
    if(len(large_sources)<n_large_rivers): # if not enough, add Forests
        large_sources = np.unique(np.hstack([large_sources, np.argwhere(ter_names=="Forest").flatten()]))

    n_large_rivers = np.min([n_large_rivers, large_sources.size, large_sinks.size])
    # print(f"{len(lands)}/{len(x)} is land, will try making {n_large_rivers} large and {n_small_rivers} small rivers")

    large_sinks=np.random.choice(large_sinks, size=n_large_rivers, replace=False, p=None)
    large_sources=np.random.choice(large_sources, size=n_large_rivers, replace=False, p=None)

    river_direction = np.full(x.shape, -1) # -1 is no river, other numbers are downtream neighbor directions
    river_id = np.full(x.shape, -1) # -1 is no river, other numbers are ids of existing rivers

    def trace_river(cur_id, sink_id):
        '''Recurcive function for tracing river flow.

        Keyword arguments:
        cur_id -- id of currect hex (int)
        sink_id -- id of sink hex (where to flow to) (int)
        '''

    for i in range(n_large_rivers):
        sink_r = np.array([ r_x[large_sinks[i]], r_y[large_sinks[i]] ])

        cur_id = large_sources[i]
        river_r = np.array([ r_x[cur_id], r_y[cur_id] ])
        optimal_vector = sink_r-river_r # constant lenth vector

        neighs = neighbour_ids[cur_id]
        potential_flow_directions = np.argwhere(neighs>=0).flatten() # filter for non-existent neighbours
        neighs = neighs[potential_flow_directions]
        neigh_rs = np.array([ r_x[neighs], r_y[neighs] ]) - river_r[:,None] # all neibours should be at equal distance from current hex

        # calculate flow direction probability
        p = np.sum(optimal_vector[:,None]*neigh_rs, axis=0) # now p goes from -|a||b| to |a||b|
        p/= np.max(p)   # normalize so neighbour closest to sink has p=1, then opposite will be p=-1
        p = (p+1.0)*0.5 # from 0 to 1
        p = p*p         # square to make turning back less likely

        print(neigh_rs, river_r, optimal_vector)

        # penalize flowing towards Hills and Mountains
        p[ter_names[neighs] == "Hills"] *= 0.7
        p[ter_names[neighs] == "Mountains"] *= 0.25
        # boost flowing towards Swamps, Lakes, Seas, and other rivers
        p[ter_names[neighs] == "Swamp"] *= 1.2
        p[ter_names[neighs] == "Lake"] *= 1.5
        p[ter_names[neighs] == "Sea"] *= 2.0
        p[river_id[neighs]>=0] *= 1.5

        # prevent river looping back on itself
        p[river_id[neighs]==i] = 0.0

        # normalize
        p /= np.sum(p)
        print("p=", p)

        # flow to
        flow_to_dir = np.random.choice(potential_flow_directions, p=p)
        flow_to_id = neighbour_ids[cur_id][flow_to_dir]

        # mark this hex as a river flowing in direction flow_to_dir
        river_direction[cur_id] = flow_to_dir
        river_id[cur_id] = i

        # process downriver hex
        pass
        
    return(river_direction)

    pass
