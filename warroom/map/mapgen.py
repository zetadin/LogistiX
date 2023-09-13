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
    structures = mapgen_structures(m_x,m_y,v, ters_names_by_i)
    # wb_id, traversed_n = mapgen_structures(m_x,m_y,v, ters_names_by_i)

    start_db = time.time()

    hexes = []
    for i in range(len(v)):   
        hexes.append(Hex(x=m_x[i], y=m_y[i], map = map_obj, terrain=ters_by_v[v[i]],
                        #   improvements={"water_body_id":str(wb_id[i]),
                        #                 "traversed_n":str(traversed_n[i]),
                        #                 "x":str(m_x[i]), "y":str(m_y[i])
                        #                }
                          ))
    Hex.objects.bulk_create(hexes)
    
    end = time.time()
    print("Terrain time       :", start_structs-start, "s")
    print("Structure time     :", start_db-start_structs, "s")
    print("Database time      :", end-start_db, "s")



# modifies the v argument to transform small inland Seas into Lakes
def mapgen_structures(x, y, v,  ter_names, width=None, height=None):
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
            lake_ids = np.argwhere(wb_ids==l)
            v[lake_ids] = 7 # Lake
            ter_names[lake_ids] = "Lake"

    # # debug for lake assignment
    # return((wb_ids, traversal_order))

    # -------- Rivers --------
    # how many large rivers do we need?

    # any Sea hex (not Lake) can be a sink for large rivers

    # any Hill/Mountain/Lake hex can be a source for large rivers


    pass
