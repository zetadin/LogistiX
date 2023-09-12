import sys, os
import numpy as np
from enum import Enum
import time

from warroom.map.models import Map, Hex, Terrain, Improvement, MapType
MODULE_PATH = os.path.dirname(os.path.realpath(__name__))
sys.path.append(os.path.join(MODULE_PATH, 'deps/terrain_gen/build'))
import terraingen as tg

class MapShape(Enum):
    Square = 0
    Circle = 1
    # Hex = 2
    


def mapgen(mt, map_shape, size=5):
    # minimal size is 1
    if(size<1):
        size=1
    # if(map_shape == MapShape.Hex):
    #     if(size%2==1):
    #         size+=1 # Hex needs even size

    # size is the width of a hex, so 2*a (where a is the lattice constant)
    h = 0.5*np.sqrt(3)        # half of hex height in a
    n_x = size                # num hexes in x
    n_y = np.floor(size/h)    # num hexes in y

    # map hex ids for a square map
    m_x = np.arange(0,n_x).astype(np.int32)
    m_y = np.arange(0,n_y).astype(np.int32)
    
    # real space coords
    r_temp_x = np.linspace(0,size,size, endpoint=False).astype(np.float32)
    r_temp_y = np.linspace(0,size,size, endpoint=False).astype(np.float32)
    r_x, r_y = np.meshgrid(r_temp_x, r_temp_y)
    r_y[:,1::2] += h   # y of every other column is shifted by h
    
    #ensure 1D arrays
    r_x=r_x.flatten()
    r_y=r_y.flatten()

    # this should give us a square map
    # if whe what other shapes, we cut them out of the square with masks
    mask = np.full(r_x.shape, True, dtype=bool)
    if(map_shape == MapShape.Circle):
        # 
        dx = r_x-0.5*size
        dy = r_y-0.5*size
        mask = np.argwhere(dx*dx+dy*dy < 0.25*size*size)
        
    # TODO: add support for other map shapes
    # elif(mt == MapShape.Hex):

    # apply mask
    r_x = r_x[mask]
    r_y = r_y[mask]
    m_x = m_x[mask]
    m_y = m_y[mask]
        
    # generate a terrain data for the above points
    if(mt == MapType.Tutorial):
        v = mapgen_Island()

    else:
        raise ValueError("Non-inplemented MapType requested")

def mapgen_Island(x, y):
    gen=tg.Generator()
    gen.setSeed(time.time_ns())

    return(gen.getTerrain(x,y))
    
    
    
