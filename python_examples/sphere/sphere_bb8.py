#!/usr/bin/env python
import time
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
import pylab
from mpl_toolkits.mplot3d import Axes3D
import platform


LIB_FOLDER = '../../cpp/bin'
LIB_NAME   = 'sphere'
if platform.system() == 'Windows':
    LIB_EXTENSION = 'dll'
else:
    LIB_EXTENSION = 'so'

###### INPUT DATA ##########
trial = 1000
test = 1
maxDisplayStructure = 4
########################

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))] 
    
def input_Gen():
    input_data = []

    f = open("bb8_50k.txt")
    n = 0
    for line in f:
        if n%5 == 0:        
            x, y, z = line.split()[:3]
            input_data.append((float(x), float(y), float(z)))
        n += 1
    f.close()        
    #Shuffle input data
    shuffle(input_data)
    
    #print ("size: ", len(input_data))
    return input_data


def run(iteration):
    input_data = input_Gen()
    
    #Plot input data for testing
    x = []; y = []; z = []
    for (mx, my, mz) in input_data:
        x.append(mx)
        y.append(my)
        z.append(mz)
    
    npXVals = np.float32(x)
    npYVals = np.float32(y)
    npZVals = np.float32(z)
    fig = pylab.figure()
    ax = Axes3D(fig)
    #ax.set_aspect('equal')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    max_range = np.array([npXVals.max()-npXVals.min(), npYVals.max()-npYVals.min(),
                          npZVals.max()-npZVals.min()]).max() / 2.0
    mean_x = npXVals.mean()
    mean_y = npYVals.mean()
    mean_z = npZVals.mean()
    ax.set_xlim(mean_x - max_range, mean_x + max_range)
    ax.set_ylim(mean_y - max_range, mean_y + max_range)
    ax.set_zlim(mean_z - max_range, mean_z + max_range)
    ax.scatter(npXVals, npYVals, npZVals, s = 1)
    plt.show()

    
    #Ctypes
    dll = ctypes.CDLL("{}/{}.{}".format(LIB_FOLDER, LIB_NAME, LIB_EXTENSION))
    SphereCtypes = dll.SphereCtypes
    SphereCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    SphereCtypes.restype = ctypes.POINTER(Structure)    

    #Collect inputs
    inputNum = len(input_data)
    x = (ctypes.c_double * inputNum)(*x)
    y = (ctypes.c_double * inputNum)(*y)
    z = (ctypes.c_double * inputNum)(*z) 

    #Run Estimator
    start_time = time.time()
    result = SphereCtypes(x, y, z, inputNum, trial)
    elapsed_time = time.time() - start_time
    #print ("Time (sec): ", elapsed_time)
    
    #Display result      
    fig = pylab.figure()
    ax = Axes3D(fig)
    #ax.set_aspect('equal')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.axis('off')
    ax.grid(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    ax.set_xlim(mean_x - max_range, mean_x + max_range)
    ax.set_ylim(mean_y - max_range, mean_y + max_range)
    ax.set_zlim(mean_z - max_range, mean_z + max_range)    
    
    
    structure_count = 0
    max_count = maxDisplayStructure
    dict_color = {0:'r', 1:'g', 2:'b', 3:'c', 4:'y', 5:'m', 6:'k'}

    plotted = []
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize

        Xin = []; Yin = []; Zin =[]
        for idx in result[structure_count].StructureIndex[: structure_size]:
            plotted.append(idx)
            mx, my, mz = input_data[idx][:3]
            Xin.append(mx)
            Yin.append(my)
            Zin.append(mz)
        npXin = np.float32(Xin)
        npYin = np.float32(Yin)
        npZin = np.float32(Zin)

        ax.scatter(npXin, npYin, npZin, s = 20, marker='o', 
                   c= dict_color[structure_count % len(dict_color)], lw = 0)
        '''
        print ("Strength: ", result[structure_count].StructureStrength, \
              "Size: ", structure_size,\
              "Scale: ", result[structure_count].StructureScale)
        '''
        structure_count += 1

    Xin_k = []; Yin_k = []; Zin_k =[]
    for idx in range(len(input_data)):
        if not idx in plotted:
            mx, my, mz = input_data[idx][:3]
            Xin_k.append(mx)
            Yin_k.append(my)
            Zin_k.append(mz)
    npXin_k = np.float32(Xin_k)
    npYin_k = np.float32(Yin_k)
    npZin_k = np.float32(Zin_k)
    ax.scatter(npXin_k, npYin_k, npZin_k, s = 1)
    
    plt.show()    

    #Free memory
    dll.FreeMemory(result)
    
    
if __name__=="__main__":
    for iteration in range(test):        
        #print ('\nIteration:', iteration)
        run(iteration)
