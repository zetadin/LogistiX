# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX..

import numpy as np
from django.conf import settings
from warroom.map.facilities import Facility


def gen_city_name():
    '''Generates a random city name'''
    prefixes=["Berry", "Aspen", "Birch", "Mill", "High", "Bright", "Fork", "Lime", "Sap"]
    endings=["ton", "ford", "town", "ville", "creak", "stead", "port", "ham", "field"]
    return(np.random.choice(prefixes)+np.random.choice(endings))



def gen_cities(x, y, v, ter_names, neighbour_ids, river_direction, control_levels, facilities):
    '''Generates control maps for the different sides

    Keyword arguments:
    x -- array of map x coord for each hex
    y -- array of map y coord for each hex
    v -- array of terrrain type ids according to the c++ generator
    ter_names -- array of terrain type names for each hex
    neighbour_ids -- array of neighbouring hex ids for each hex
    control_levels -- array of control levels for each hex
    facilities -- array of facilities for each hex
    '''

    city_names = []

    is_land = np.logical_and(ter_names!="Sea", ter_names!="Lake")
    city_candidate_hexes = np.argwhere(is_land).flatten()
    city_density = 0.05
    downtown_prob = 0.2
    n_cities_per_side = np.floor(city_candidate_hexes.size*city_density/settings.N_SIDES)
    n_cities_per_side = int(max(n_cities_per_side, 1))
    n_downtowns_per_side =  max(1,int(np.floor(n_cities_per_side*downtown_prob)))
    for side in range(settings.N_SIDES):
        side_is_candidate = np.logical_and(is_land, control_levels[:,side]>=1.0)
        side_candidate_hexes = np.argwhere(side_is_candidate).flatten()
        print(f"{side=},\t{n_cities_per_side=},\t{side_candidate_hexes.shape=}")

        # bias city placement away from the front & not on mountains, towards rivers and lake/sea
        p = np.zeros(v.shape) # probability for particular hex
        p[side_candidate_hexes] = 1.0
        neighs = neighbour_ids[side_candidate_hexes].flatten()
        hex_ids = np.repeat(side_candidate_hexes, 6)[neighs>=0]
        neighs = neighs[neighs>=0]
        # print(f"{side=},\t{hex_ids.shape=},\t{neighs.shape=},\t{p.shape=}")
        
        # not near front
        # print(f"{side=},\t{(control_levels[neighs,side]<1.0).shape=}")
        near_front = np.unique(hex_ids[np.argwhere(control_levels[neighs,side]<1.0).flatten()])
        p[near_front] = 0.0

        # not on mountains, penalize hills
        p[side_candidate_hexes[ter_names[side_candidate_hexes]=="Mountains"]] = 0.0
        p[side_candidate_hexes[ter_names[side_candidate_hexes]=="Hills"]] *= 0.3

        # ideally on rivers
        on_river = side_candidate_hexes[river_direction[side_candidate_hexes]>0]
        p[on_river] *= 5.0

        # near sea and lakes
        near_water = np.unique(hex_ids[np.argwhere(np.logical_not(is_land[neighs])).flatten()])
        p[near_water] *= 3.0

        # normalize
        p/=np.sum(p)

        # place cities
        side_city_hexes = np.random.choice(np.arange(len(v)), size=n_cities_per_side, replace=False, p=p)
        ter_names[side_city_hexes] = "Urban"

        print(f"{side=},\t{side_city_hexes=}")

        # place downtowns
        # TODO: make sure downtowns are not in the same continuous urban zone
        side_downtown_hexes = np.random.choice(side_city_hexes, size=n_downtowns_per_side, replace=False)
        print(f"{side=},\t{side_downtown_hexes=}")
        for dtown_hex in side_downtown_hexes:
            name = gen_city_name()
            for retry in range(10):
                if(name in city_names):
                    name = gen_city_name()
                else:
                    break
            if(retry>=10):
                while name in city_names:
                    prepend = ["New", "Lower", "Upper"]
                    name = np.random.choice(prepend)+" "+name
            downtown = Facility(name=name, chunk=None,
                                x=x[dtown_hex], y=y[dtown_hex],
                                type="Downtown")
            facilities.append(downtown)
            city_names.append(name)