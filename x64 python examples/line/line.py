#!/usr/bin/env python
'''
This script generates input data for testing.
Then will try line estimation.
LINE: [x.Start, y.Start, x.End, y.End, Sigma, Total amount]
NOISE: [x.Range, y.Range, Total amount]
'''

###### INPUT DATA ##########
LINE = [[30, 90, 510, 650, 3, 300],
            [510, 650, 490, 100, 6, 250],
            [490, 100, 30, 580, 9, 200],
            [30, 580, 650, 350, 12, 150],
            [650, 350, 30, 90, 15, 100]]

NOISE = [700, 700, 350]

trial = 1000
test = 3
maxDisplayStructure = 5
#########################

import ctypes
import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
import platform


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
        input_data.append((x, y))
        
    #Generate inlier structures
    for x1, y1, x2, y2, sigma, amount in LINE:
        rand_val = np.random.normal(0, sigma, 2 * amount)
        vec_x, vec_y = x2 - x1, y2 - y1        
        for i in range(amount):
            t = np.random.rand()
            x = int(x1 + t * vec_x + rand_val[i])
            y = int(y1 + t * vec_y + rand_val[amount + i])
            input_data.append((x, y))
            
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
    if platform.system() == 'Windows':
        dll = ctypes.CDLL("line.dll")
    else:
        dll = ctypes.CDLL("line.so")
    LineCtypes = dll.LineCtypes
    LineCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    LineCtypes.restype = ctypes.POINTER(Structure)    

    #Collect inputs
    x = []; y = []
    for (mx, my) in input_data:
        x.append(mx)
        y.append(my)
    inputNum = len(input_data)
    x = (ctypes.c_double * inputNum)(*x)
    y = (ctypes.c_double * inputNum)(*y)

    #Run Estimator
    result = LineCtypes(x, y, inputNum, trial)
    
    #Display result    
    plt.axes().set_aspect('equal')
    plt.xlim(0, rng)
    plt.ylim(0, rng)       

    structure_count = 0
    max_count = maxDisplayStructure
    dict_color = {0:'r', 1:'g', 2:'b', 3:'c', 4:'y', 5:'m'}
    
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize
        plt.plot(*zip(*[input_data[idx] for idx in
                        result[structure_count].StructureIndex[: structure_size]]),
                 marker='o', color= dict_color[structure_count % len(dict_color)], ls='', ms = 5, lw = 0)       

        #Plot TLS lines
        a, b, c = result[structure_count].StructureTLS[: 3]
        print ('a = {}, b = {}, c = {}'.format(a,b,c)) 
        if b !=0:
            lx = np.linspace(0, rng, 2)
            ly = (-lx * a - c)/b
        else:
            lx = -c/b
            ly = np.linspace(0, rng, 2)                
        plt.plot(lx, ly, color=dict_color[structure_count % len(dict_color)], linestyle='-', linewidth=2)
        
        print ("Strength: ", result[structure_count].StructureStrength, \
              "Size: ", structure_size,\
              "Scale: ", result[structure_count].StructureScale)
        
        structure_count += 1
        
    plt.show()

    #Free memory
    dll.FreeMemory(result)
        
if __name__=="__main__":
    for iteration in range(test):        
        print ('\nIteration:', iteration)
        run(iteration)
