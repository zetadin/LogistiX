# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX..

import numpy as np
import scipy as sp
from scipy.spatial.distance import cdist
import uuid
import copy
from django.conf import settings
from warroom.map.facilities import Facility

# ------ Spaceports -------
def gen_spaceports(x, y, ter_names, control_levels, facilities):
    '''Generates spaceports on a map'''
    downtowns = [f for f in facilities if f.type == "Downtown"]
    is_land = np.logical_and(ter_names!="Sea", ter_names!="Lake")
    is_urban = ter_names=="Urban"
    n_side_ports = max(1, int(np.floor(len(downtowns)/settings.N_SIDES * 0.25)))
    search_radius = 3

    for side in range(settings.N_SIDES):
        near_dts = np.empty(0, dtype=int)
        side_dts = [f for f in downtowns if f.side == side]
        for f in side_dts:
            near_dts = np.append(near_dts, np.argwhere( np.logical_and(np.abs(x-f.x)<=search_radius,  np.abs(y-f.y)<=search_radius) ).flatten())

        dt_hexes = np.argwhere(np.logical_and(ter_names=="Urban", control_levels[:,side]>=1.0)).flatten()

        near_dts = np.unique(near_dts)
        conditions = np.logical_and.reduce((is_land[near_dts],
                                            control_levels[near_dts,side]>=1.0,
                                            np.logical_not(is_urban[near_dts])
                                            ))
        candidates = near_dts[conditions]

        side_spaceports = np.random.choice(candidates, size=n_side_ports, replace=False)
        for h in side_spaceports:
            spaceport = Facility(name="Spaceport "+uuid.uuid4().hex[:4],
                                 chunk=None,
                                 x=x[h], y=y[h],
                                 side=side,
                                 type="Spaceport")
            facilities.append(spaceport)



# Each Industrial region has a public warehouse for satisfying nearby pull requests.
# It can also have any number of private factories, including AI controlled ones.
# Private factories can do their own push logistics from their private warehouses.
# A player will only see their own factories in a node and the total output of all the other factories there.

# Industial region represent a manufacturing hub of multiple hexes, but is denoted by a filled circle at its center.
# So if a portion of that region is not controlled by the node's faction, then the output gets scaled down.
# This region should be shown as a circular overlay when the node is sellected.
# Player facilities and total node output can be shown here.

def gen_industrial_regions(x, y, r_x, r_y, ter_names, river_direction, control_levels, facilities):
    '''Generates industrial region nodes on a map'''

    # Can be in any land hex that is not a spaceport or a Downtown (recruiting facility)
    # Urban hexes are more likely to be centers of industrial regions, so are river hexes.

    all_hexes = np.arange(x.shape[0])
    is_land = np.logical_and(ter_names!="Sea", ter_names!="Lake")
    is_urban = ter_names=="Urban"
    is_river = river_direction>0
    num_industrial_regions = np.count_nonzero(is_land) / (np.pi*settings.INDUSTRIAL_REGION_RADIUS**2)
    num_industrial_regions = max(settings.N_SIDES, int(np.floor(num_industrial_regions)))

    weights = np.zeros(is_land.shape)
    weights[is_land] = 1
    weights[is_urban] *= 5
    weights[is_river] *= 2
    
    # don't place industrial regions on existing downtowns or spaceports
    for fac in facilities:
        if(fac.type == "Downtown" or fac.type == "Spaceport"):
            weights[np.logical_and(x==fac.x, y==fac.y)] = 0

    # select guaranteed one region for each side
    guaranteed_region_hexes = []
    for side in range(settings.N_SIDES):
        side_candidates = np.logical_and(is_land, control_levels[:,side]>=1.0)
        side_candidate_weights = weights * side_candidates
        guaranteed_region_hexes.append( np.random.choice(all_hexes, size=1, replace=False,
                                                         p=side_candidate_weights/np.sum(side_candidate_weights))[0] )

    good_region_hexes = copy.deepcopy(guaranteed_region_hexes)

    if(settings.N_SIDES < num_industrial_regions):
        weights[guaranteed_region_hexes] = 0 # prevent duplicate selection

        for l in range(10):
            # select more candidates if needed
            new_region_hexes = np.random.choice(all_hexes, size=num_industrial_regions-settings.N_SIDES,
                                                replace=False, p=weights/np.sum(weights))
            all_region_hexes = np.append(good_region_hexes, new_region_hexes)
            
            # filter out regions too close together
            # print(f"{all_region_hexes.shape=}")
            coord_arr = np.array([r_x[all_region_hexes], r_y[all_region_hexes]]).transpose()
            dist_mat = cdist(coord_arr, coord_arr, metric='euclidean')
            too_close_mat = dist_mat < settings.INDUSTRIAL_REGION_SPACING

            n_good_hexes = len(good_region_hexes)
            
            for i in reversed(range(n_good_hexes, len(all_region_hexes))):
                # count from the end
                if(not np.any(too_close_mat[i,:i-1])):
                    # not too close to another region before it in the list
                    good_region_hexes.append(all_region_hexes[i])
                    weights[all_region_hexes[i]] = 0 # prevent duplicate selection

            if(len(good_region_hexes)>= num_industrial_regions):
                # we found enough regions, stop itterating
                break
    
    # we can have too few regions becasue after 10 attempts still couldn't place enough, but that's okay

    # add the regions to facilities list
    region_names = []
    for h in good_region_hexes:
        name = "Industrial Region "+uuid.uuid4().hex
        while name in region_names:
            name = "Industrial Region "+uuid.uuid4().hex

        region = Facility(name=name,
                          chunk=None,
                          x=x[h], y=y[h],
                          side=np.argmax(control_levels[h,:]),
                          type="Industrial Region")
        facilities.append(region)

        # print(facilities)


def gen_fabs(facilities):
    '''Generates initial factories on a map'''
    possibilities = {
                "Mine": 1,
                "Nano Fab": 1,
                "None": 2
                }
    chances = np.array(list(possibilities.values()), dtype=float)
    chances/=np.sum(chances) # normalize

    fab_names = []
    fabs = []

    for ind_region in facilities:
        if ind_region.type == "Industrial Region":

            # how many fabs to try generating in this region
            num = np.random.randint(0,4)
            for i in range(num):
                selected = np.random.choice(list(possibilities.keys()), p=chances)
                if selected != "None":
                    # make unique name
                    name = "AI "+selected+" "+uuid.uuid4().hex
                    while name in fab_names:
                        name = "AI "+selected+" "+uuid.uuid4().hex
                    fab_names.append(name)

                    # create and register the facility
                    fab = Facility(name=name,
                                chunk=None,
                                x=ind_region.x,
                                y=ind_region.y,
                                side=ind_region.side,
                                parent=ind_region,
                                type=selected)
                    fabs.append(fab)
    return fabs


def fill_warehouses(x, y, v, ter_names, neighbour_ids, control_levels, facilities):
    '''Generates initial warehouses on a map'''
    pass;