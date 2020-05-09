#!/usr/bin/env python
'''
This script generates input data for testing.
Then will try ellipse estimation.
ELLIPSE: [Axis.x, Axis.y, Rotation, x.Translation, y.Translation, Sigma, Total amount]
NOISE: [x.Range, y.Range, Total amount]
'''

###### INPUT DATA ##########
ELLIPSE = [[200, 200, 0, 350, 350, 3, 300],
           [350, 120, 45, 350, 350, 6, 250],
           [80, 50, 60, 430, 390, 9, 200]]

NOISE = [700, 700, 350]

trial = 5000
test = 3
maxDisplayStructure = 3
########################

import ctypes
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from random import shuffle
import convertEllipse

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))] 
    
def input_Gen():
    input_data = []
    
    #Generate random noise
    range_x, range_y, amount = NOISE
    for i in range(amount):
        x = int(np.random.rand() * range_x)
        y = int(np.random.rand() * range_y)
        input_data.append([x, y])
        
    #Generate inlier structures    
    for a, b, rot, tx, ty, sigma, amount in ELLIPSE:
        rand_val = np.random.normal(0, sigma, 2 * amount)
        cos_rot = np.cos(rot / 180. * 3.14)
        sin_rot = np.sin(rot / 180. * 3.14)  
        for i in range(amount):
            t = np.random.rand() * 2 * 3.14
            x = int(a*np.cos(t)*cos_rot - b*np.sin(t)*sin_rot + tx + rand_val[i])
            y = int(a*np.cos(t)*sin_rot + b*np.sin(t)*cos_rot + ty + rand_val[amount + i])
            input_data.append([x, y])
        
    #Shuffle input data
    shuffle(input_data)        
    return input_data

def run(iteration):
    input_data = input_Gen()
    rng = max(NOISE[:2])
    
    #Plot input data for testing
    plt.axes().set_aspect('equal')
    plt.xlim(0, rng)
    plt.ylim(0, rng)    
    plt.plot(*zip(*input_data), marker='o', color='k', ls='', ms = 2, lw = 0)       
    plt.show()    
    
   #Ctypes
    dll = ctypes.CDLL("ellipse.dll")
    EllipseCtypes = dll.EllipseCtypes
    EllipseCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    EllipseCtypes.restype = ctypes.POINTER(Structure)    

    #Collect inputs
    x = []; y = []
    for (mx, my) in input_data:
        x.append(mx)
        y.append(my)
    inputNum = len(input_data)
    x = (ctypes.c_double * inputNum)(*x)
    y = (ctypes.c_double * inputNum)(*y) 

    #Run Estimator
    result = EllipseCtypes(x, y, inputNum, trial)
        
    #Display result      
    plt.axes().set_aspect('equal')
    plt.xlim(0, rng)
    plt.ylim(0, rng)    
    ax = plt.subplot()       

    structure_count = 0
    max_count = maxDisplayStructure
    dict_color = {0:'r', 1:'g', 2:'b', 3:'c', 4:'y', 5:'m'}
    
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize
        plt.plot(*zip(*[input_data[idx] for idx in
                        result[structure_count].StructureIndex[: structure_size]]),
                 marker='o', color= dict_color[structure_count % len(dict_color)], ls='', ms = 5, lw = 0)       

        # draw TLS ellipse
        TLSestimate = []            
        for item in result[structure_count].StructureTLS[: 6]:
            TLSestimate.append(item)
        try:
            x, y, w, h, rot = convertEllipse.ellipse_general_to_standard(*TLSestimate)            
            ell = Ellipse(xy=(x, y), width=2 *w, height= 2* h, angle=rot / 3.14 * 180,
                          color = dict_color[structure_count % len(dict_color)])
            ell.set_facecolor("None")
            ell.set_linewidth(2)
            ax.add_artist(ell)
        except:
            pass
    
        print "Strength: ", result[structure_count].StructureStrength, \
              "Size: ", structure_size,\
              "Scale: ", result[structure_count].StructureScale
        structure_count += 1
        
    plt.show()

    #Free memory
    dll.FreeMemory(result)
        
if __name__=="__main__":
    for iteration in range(test):        
        print '\nIteration:', iteration
        run(iteration)
