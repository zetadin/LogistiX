# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX..

import numpy as np
import uuid
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



def gen_industry_slots(x, y, v, ter_names, neighbour_ids, control_levels, facilities):
    '''Generates industry slots on a map'''
    pass;


def gen_fabs(x, y, v, ter_names, neighbour_ids, control_levels, facilities):
    '''Generates initial factories on a map'''
    pass;

def gen_warehouses(x, y, v, ter_names, neighbour_ids, control_levels, facilities):
    '''Generates initial warehouses on a map'''
    pass;