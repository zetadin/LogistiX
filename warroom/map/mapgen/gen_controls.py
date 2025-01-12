# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

import numpy as np
from django.conf import settings

# computes maps of control for the different sides
def gen_controls(x, y, v, r_x, r_y, ter_names, neighbour_ids, width=None, height=None):
    '''Generates control maps for the different sides

        Keyword arguments:
        x -- array of map x coord for each hex
        y -- array of map y coord for each hex
        v -- array of terrrain type ids according to the c++ generator
        r_x -- array of real space x coord for each hex
        r_y -- array of real space y coord for each hex
        ter_names -- array of terrain type names for each hex
        neighbour_ids -- array of neighbouring hex ids for each hex
        
        Optional Rguments:
        width -- map width (default max(x)+1)
        height -- map height (default max(y)+1)
        '''
    if(width==None):
        width = np.max(x)+1
    if(height==None):
        height = np.max(y)+1

    control_map = np.zeros((len(v), settings.N_SIDES))

    # find the center of mass for the land hexes
    land_hexes = np.argwhere(np.logical_and(ter_names!="Sea", ter_names!="Lake")).flatten()
    land_r = np.array([r_x[land_hexes], r_y[land_hexes]])
    land_com = np.mean(land_r, axis=1)

    # pick angle offsets for each side's center lines
    center_angles = np.arange(0, settings.N_SIDES)*2.*np.pi/settings.N_SIDES
    center_angles += np.random.uniform(0., 2.*np.pi)
    center_angles = np.sort(np.fmod(center_angles, 2.*np.pi)) - np.pi
    
    # compute angle to each centerline for each point
    rel_r = np.array([r_x, r_y]).transpose() - land_com
    angles = np.arctan2(rel_r[:,1], rel_r[:,0])
    sector_width = 2*np.pi/settings.N_SIDES

    # hexes belong to the side whose center line is closest (by angle)
    for side in range(settings.N_SIDES):
        dif_angle = angles - center_angles[side] # [-2pi, 2pi]
        dif_angle = np.fmod(dif_angle + 2*np.pi, 2*np.pi) - np.pi # [-pi, pi]
        dif_angle = np.abs(dif_angle) # [0, pi]; 0 is center line

        zone = np.where(dif_angle<0.5*sector_width)[0]
        control_map[zone, side] = 1.0



    controlling_side = np.argmax(control_map, axis=1)
        
    # check any hexes with neighbours of different sides
    change_map = np.zeros((len(v), settings.N_SIDES))
    for side in range(settings.N_SIDES):
        hex_ids = np.argwhere(control_map[:,side]>0).flatten()
        neighs = neighbour_ids[hex_ids].flatten()
        # filter hexes by valid neighbour_ids (neighbours exist in this map)
        hex_ids = np.repeat(hex_ids, 6)[neighs>=0]
        neighs = neighs[neighs>=0]
        # print(f"{side=}, {neighs.shape=}")
        # print(f"{side=}, {hex_ids.shape=}")
        contested_indeces = np.argwhere(controlling_side[neighs]!=side).flatten()
        contested_hexes = np.unique(hex_ids[contested_indeces])
        # print(f"{side=}, {contested_hexes.shape=}")
        change_map[contested_hexes, side] = 0.2 + 0.2*np.random.rand(contested_hexes.size)
        contesting_neighs = np.unique(neighs[contested_indeces])
        # print(f"{side=}, {contesting_neighs.shape=}")
        change_map[contesting_neighs, side] = -0.2 - 0.2*np.random.rand(contesting_neighs.size)

    # apply the changes from contesting sides
    control_map -= change_map

    # normalize control map
    control_map /= np.sum(control_map, axis=1)[:, np.newaxis]

    return(control_map)