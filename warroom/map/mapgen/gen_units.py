# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

import numpy as np
import scipy as sp
from scipy.spatial.distance import cdist
import uuid
from django.conf import settings
from warroom.units.models import Company
from LogistiX_backend.user_utils import fast_hash_mod, th


def mapgen_units(x, y, r_x, r_y, ter_names, control_maps, neighbour_ids, facilities):
    """
    Generates all the starting units on the map.
    """
    unit_names=[]

    units = gen_frontline_units(x, y, r_x, r_y, ter_names, control_maps, neighbour_ids, unit_names)
    units.extend(gen_reserve_units(x, y, ter_names, control_maps, facilities, unit_names))

    return units




def gen_frontline_units(x, y, r_x, r_y, ter_names, control_maps, neighbour_ids, unit_names):
    """
    Places initial units near the front line.
    """
    units = []

    # frontline unit types
    # TODO: this needs to be generated from RuleSet units without the Reserve tag
    unit_possibilities={
        "Foot Infantry": 2,
        "Scouts": 0.5,
        "Mobile Infantry": 1,
    }
    unit_chances = np.array(list(unit_possibilities.values()), dtype=float)
    unit_chances/=np.sum(unit_chances) # normalize
    unit_types = list(unit_possibilities.keys())

    # how many units to place
    is_land = np.logical_and(ter_names!="Sea", ter_names!="Lake")
    print(f"{ter_names=}")
    print(f"{is_land=}")
    max_control = np.max(control_maps, axis=1)
    is_contested = np.logical_and(max_control>0, max_control<1)
    is_gray_zone = np.logical_and(max_control>0.25, max_control<0.75)
    has_contested_neighbor = np.full_like(is_contested, False)
    hexes_w_contested_neighbors = neighbour_ids[is_contested].flatten()
    hexes_w_contested_neighbors = hexes_w_contested_neighbors[hexes_w_contested_neighbors>=0] # remove missing neighburs
    has_contested_neighbor[hexes_w_contested_neighbors] = True
    is_threatened = np.logical_or(is_contested, has_contested_neighbor)
    print(f"{is_threatened.shape=}")
    print(f"{is_gray_zone.shape=}")
    print(f"{is_land.shape=}")
    is_front_line = np.logical_and.reduce((is_threatened, np.logical_not(is_gray_zone), is_land))

    front_line_hexids = np.argwhere(is_front_line).flatten()
    N_front_line_hexes = front_line_hexids.size
    N_frontline_units_per_side = max(1,
                int(N_front_line_hexes*settings.FRONT_LINE_UNIT_DENSITY/settings.N_SIDES))
    print(f"{N_frontline_units_per_side=}")

    # place the units
    for side in range(settings.N_SIDES):
        side_front_line_hexids = front_line_hexids[control_maps[front_line_hexids,side]>=0.75]
        print(f"{side=}: {side_front_line_hexids.size=}")
        place_units_at = np.random.choice(side_front_line_hexids,
                                size=min(N_frontline_units_per_side, len(side_front_line_hexids)),
                                replace=False)
        
        for h in place_units_at:
            # pick unit type
            selected = np.random.choice(unit_types, p=unit_chances)
                
            # make unique name
            battalion_num = np.random.randint(101,100000)
            battalion_desig = settings.SIDE_BATTALION_DESIGNATIONS[side][fast_hash_mod(battalion_num, len(settings.SIDE_BATTALION_DESIGNATIONS[side]))]
            battallion_name = f"{battalion_num}{th(battalion_num)} {battalion_desig} Battalion"
            company_number = np.random.randint(0,4)
            name = f"{selected}, {settings.SIDE_COMPANY_DESIGNATIONS[side][company_number]} Company, {battallion_name}"
            while name in unit_names:
                battalion_num = np.random.randint(101,100000)
                battalion_desig = settings.SIDE_BATTALION_DESIGNATIONS[side][fast_hash_mod(battalion_num, len(settings.SIDE_BATTALION_DESIGNATIONS[side]))]
                battallion_name = f"{battalion_num}{th(battalion_num)} {battalion_desig}"
                company_number = np.random.randint(0,4)
                name = f"{selected}, {settings.SIDE_COMPANY_DESIGNATIONS[side][company_number]} Company, {battallion_name}"
            unit_names.append(name)

            # create the unit
            unit = Company(name=name,
                           x=x[h], y=y[h],
                           faction=side,
                           type=selected,
                           visible_to=[1]*settings.N_SIDES
                           )
            
            # provide starting equipment
            # TODO: this needs to be generated based on unit definition in the RuleSet
            unit.all_equipment = {"Infantry Kit":1}
            unit.active_equipment = {"Infantry Kit":1}

            # done with unit
            units.append(unit)

    return units

def gen_reserve_units(x, y, ter_names, control_maps, facilities, unit_names):
    """
    Places initial units to guard important infrastructure: Industrial Regions,
    Spaceports, and Downtowns.
    """
    units = []

    return units

def em_frontline_units():
    """
    Redistribute frontline units so they evenly cover the front line.
    Uses energy minimization with springs between unit pairs and units and front line.
    """
    pass;