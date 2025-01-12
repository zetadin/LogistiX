# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

import numpy as np



# modifies the v argument to transform small inland Seas into Lakes
def gen_lakes_and_rivers(x, y, v, r_x, r_y, ter_names, neighbour_ids, width, height):
    '''Generates structures/improvements on a map: Lakes, Rivers, Towns, Roads, Spaceports, etc.

        Keyword arguments:
        x -- array of map x coord for each hex
        y -- array of map y coord for each hex
        v -- array of terrrain type ids according to the c++ generator
        r_x -- array of real space x coord for each hex
        r_y -- array of real space y coord for each hex
        ter_names -- array of terrain type names for each hex
        neighbour_ids -- array of neighbouring hex ids for each hex
        width -- map width
        height -- map height
        '''
    

    # other prep work
    land_mask = ter_names!="Sea"
    lands = np.argwhere(land_mask).flatten()

    # -------- Lakes --------
    # find all contiguous Sea regions
    wb_ids = np.full(x.shape, -1, dtype=int)
    wb_size = [0]
    wb_n = 0
    wb_processing_queue = []
    wb_queued = np.full(x.shape, False, dtype=bool)


    t_n = 0
    traversal_order = np.full(x.shape, -1, dtype=int) # debug array tracking which hexes were traversed when

    def traverse_connected_sea_breadth_first(starting_hex_id):
        nonlocal t_n, wb_n
        # if the starting hex has not been queued and checked previously, queue it now
        if(not wb_queued[starting_hex_id]):
            wb_processing_queue.append(starting_hex_id)
            wb_queued[starting_hex_id] = True

        # process the queue
        while(len(wb_processing_queue)>0):
            i = wb_processing_queue.pop(0)
            if(ter_names[i]=="Sea" and wb_ids[i]<0): # if you are an unassigned sea
                # assign to a water body
                wb_ids[i] = wb_n
                wb_size[wb_n]+=1

                # mark this hex as traversed
                traversal_order[i]=t_n
                t_n+=1

                # look through your neighbours
                neighs = neighbour_ids[i]
                neighs = neighs[neighs>=0] # neighbour_ids are valid and the neighbours exist in this map
                neighs = neighs[np.logical_not(wb_queued[neighs])] # only use neighbours that have not been queued yet
                # queue them
                if(len(neighs)>0):
                    wb_processing_queue.extend(neighs.tolist())
                    wb_queued[neighs] = True

    seas = np.argwhere(ter_names=="Sea").flatten()
    for i in seas:
        if(wb_ids[i]<0):
            # traverse_connected_sea_deapth_first(i)
            traverse_connected_sea_breadth_first(i)
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
    n_large_rivers = int(np.floor(np.sqrt(len(lands))/10))
    n_small_rivers = int(np.floor(np.sqrt(len(lands))/8))

    # LARGE RIVERS
    # any coastal Sea hex (not Lake) or land at map edge can be a sink for large rivers
    seas = np.argwhere(ter_names=="Sea").flatten() # recalculate without lakes
    coastal_seas = []
    for i in seas:
        neighs = neighbour_ids[i]
        neighs = neighs[neighs>=0] # neighbour_ids are valid and the neighbours exist in this map
        if(np.any(ter_names[neighs]!="Sea")):
            coastal_seas.append(i)
    coastal_seas=np.array(coastal_seas, dtype=int)

    coastal_lands = []
    for i in np.argwhere(land_mask).flatten():
        neighs = neighbour_ids[i]
        neighs = neighs[neighs>=0] # neighbour_ids are valid and the neighbours exist in this map
        if(np.any(ter_names[neighs]=="Sea")):
            coastal_lands.append(i)

    map_edge_lands = np.argwhere(np.logical_and(
                        np.any(np.vstack([x==0, x==width-1, y==0, y==height-1]), axis=0),   # map_edge
                        land_mask                                                           # lands
                        )).flatten()
    
    large_sinks_candidates = np.hstack([coastal_seas, map_edge_lands])
    
    # any Hill/Mountain/Swamp/Lake/land at map edge (Forest as backup) hex can be a source for large rivers
    large_sources = np.unique(np.hstack([map_edge_lands,
                              np.argwhere(np.any(np.vstack([
                                              ter_names=="Hills",
                                              ter_names=="Mountains",
                                              ter_names=="Swamp",
                                              ter_names=="Lake",
                                              ]), axis=0)).flatten()]
                            ))
    large_sources = large_sources[np.logical_not(np.isin(large_sources, coastal_lands))] # remove coastal tiles

    if(len(large_sources)<n_large_rivers): # if not enough, add Forests
        large_sources = np.unique(np.hstack([large_sources, np.argwhere(ter_names=="Forest").flatten()]))
        large_sources = large_sources[np.logical_not(np.isin(large_sources, coastal_lands))] # remove coastal tiles

    n_large_rivers = np.min([n_large_rivers, large_sources.size, large_sinks_candidates.size])
    # print(f"{len(lands)}/{len(x)} is land, will try making {n_large_rivers} large and {n_small_rivers} small rivers")

    large_sinks=np.random.choice(large_sinks_candidates, size=n_large_rivers, replace=False, p=None)
    large_sources=np.random.choice(large_sources, size=n_large_rivers, replace=False, p=None)


    # SMALL RIVERS
    # preliminary sinks for small rivers, will add large rivers to here after they are generated
    small_sinks_candidates = np.hstack([ coastal_seas, np.argwhere(ter_names=="Lake").flatten() ])


    river_direction = np.full(x.shape, -1) # -1 is no river, other numbers are downtream neighbor directions
    river_id = np.full(x.shape, -1) # -1 is no river, other numbers are ids of existing rivers

    cur_river_old_neighbours = []

    def trace_river(cur_id, sink_r, i, large_river=True, river_length=0):
        '''Recurcive function for tracing river flow.

        Keyword arguments:
        cur_id -- id of currect hex (int)
        sink_r -- real space coords of the sink hex (where to flow to)
        i -- number of the current river bein traced
        river_length -- how many hexes haev we already flown (default 0)? For debuging.

        Optional arguments:
        large_river -- boolean flag for large rivers. Chooses which sinks to use in stop condition.
        '''
        nonlocal cur_river_old_neighbours;

        # mark this hex as a river
        river_id[cur_id] = i


        river_r = np.array([ r_x[cur_id], r_y[cur_id] ])
        optimal_vector = sink_r-river_r

        # get neighbours of current hex
        neighs = neighbour_ids[cur_id]
        potential_flow_directions = np.argwhere(neighs>=0).flatten() # filter for non-existent neighbours
        neighs = neighs[potential_flow_directions]
        neigh_rs = np.array([ r_x[neighs], r_y[neighs] ]) - river_r[:,None] # all neibours should be at equal distance from current hex

        # calculate flow direction probability
        p = np.sum(optimal_vector[:,None]*neigh_rs, axis=0) # now p goes from -|a||b| to |a||b|
        p/= np.max(p)   # normalize so neighbour closest to sink has p=1, then opposite will be p=-1
        p = (p+1.0)*0.5 # from 0 to 1
        p = p*p         # square to make turning back less likely

        # print(f"river {i}, hex {x[cur_id]}_{y[cur_id]}:\n\t neighbour vectors=", neigh_rs, " cur r-space pos=", river_r, " prefered flow dir=", optimal_vector)

        # penalize flowing towards Hills and Mountains
        p[ter_names[neighs] == "Hills"] *= 0.5
        p[ter_names[neighs] == "Mountains"] *= 0.1
        # boost flowing towards Swamps, Lakes, Seas, and other rivers
        p[ter_names[neighs] == "Swamp"] *= 1.5
        p[ter_names[neighs] == "Lake"] *= 2.0
        p[ter_names[neighs] == "Sea"] *= 4.0
        p[river_id[neighs]>=0] *= 1.5
        
        # np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        # print(f"\thex {x[cur_id]}_{y[cur_id]}: p=", p)

        # prevent river looping back on itself
        p[river_id[neighs]==i] = 0.0
        p[np.isin(neighs, cur_river_old_neighbours)] = 0.0 # prevent looping back to previous neighbours of same river


        # add current neighbours to previous ones
        cur_river_old_neighbours.extend(neighs.tolist())

        # normalize
        # print(f"\thex {x[cur_id]}_{y[cur_id]}: p=", p)
        p /= np.sum(p)
        

        # flow to
        flow_to_dir = np.random.choice(potential_flow_directions, p=p)
        flow_to_id = neighbour_ids[cur_id][flow_to_dir]
        # print(f"\thex {x[cur_id]}_{y[cur_id]}: p=", p, "will flow:", flow_to_dir)

        # mark this hex as flowing in direction flow_to_dir
        river_direction[cur_id] = flow_to_dir
        # river_id[cur_id] = i

        # check stop conditions
        if( river_id[flow_to_id] >= 0 ): # existing river
            cur_river_old_neighbours=[] # changing river, so reset old neighbours
            return(); # stop here
        elif( large_river and (flow_to_id in large_sinks_candidates) ): # sink candidate for large rivers
            cur_river_old_neighbours=[] # changing river, so reset old neighbours
            return(); # stop here
        elif( not large_river and (flow_to_id in small_sinks_candidates) ): # sink candidate for small rivers
            cur_river_old_neighbours=[] # changing river, so reset old neighbours
            return(); # stop here
        # elif(river_length>5): # debug
        #     return(); # stop here
        else:
            # process downriver hex
            trace_river(flow_to_id, sink_r, i, large_river, river_length+1)
            pass

        

    # trace LARGE RIVERS
    for i in range(n_large_rivers):
        sink_r = np.array([ r_x[large_sinks[i]], r_y[large_sinks[i]] ])
        cur_id = large_sources[i]
        if(river_id[cur_id]<0): # don't start on hexes that already have a river
            trace_river(cur_id, sink_r, i, large_river=True)


    # finish setup for SMALL RIVERS
    small_sources = np.argwhere(ter_names!="Sea").flatten() # any land or lake
    small_sources = small_sources[np.logical_not(np.isin(small_sources, coastal_lands))] # remove coastal tiles
    small_sinks_candidates = np.hstack([ small_sinks_candidates, np.argwhere(river_id >=0 ).flatten() ]) # Coastal seas, lakes, or large rivers
    if(small_sinks_candidates.size<=0):
        # no possible small river sinks found, so don't make small  rivers
        return()

    n_small_rivers = np.min([n_small_rivers, small_sources.size, small_sinks_candidates.size])
    # reduce chance to flow directly into the sea to 25%
    if(small_sinks_candidates.size - coastal_seas.size > 0 and coastal_seas.size>0):
        sr_s_sea_prob = 0.25
        small_sink_probabilities = np.full(small_sinks_candidates.shape, (1-sr_s_sea_prob)/(small_sinks_candidates.size - coastal_seas.size))
        small_sink_probabilities[:coastal_seas.size] = sr_s_sea_prob/coastal_seas.size
    else:
        small_sink_probabilities = np.full(small_sinks_candidates.shape, 1.0/small_sinks_candidates.size)

    # chose small river sources and sinks
    small_sinks=np.random.choice(small_sinks_candidates, size=n_small_rivers, replace=False, p=small_sink_probabilities)
    small_sources=np.random.choice(small_sources, size=n_small_rivers, replace=False, p=None)

    # trace SMALL RIVERS
    for i in range(n_small_rivers):
        sink_r = np.array([ r_x[small_sinks[i]], r_y[small_sinks[i]] ])
        cur_id = small_sources[i]
        if(river_id[cur_id]<0): # don't start on hexes that already have a river
            trace_river(cur_id, sink_r, i+n_large_rivers, large_river=False)

    return(river_direction)