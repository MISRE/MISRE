#!/usr/bin/env python
'''
This script generates input data for testing.
Then will try cylinder estimation.
CYLINDER: [Radius, Height, Center.x, Center.y, Center.z, Sigma, Total amount]
NOISE: [Total amount]
'''
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
import pylab
from mpl_toolkits.mplot3d import Axes3D
import platform

LIB_FOLDER = '../../cpp/bin'
LIB_NAME   = 'cylinder'
if platform.system() == 'Windows':
    LIB_EXTENSION = 'dll'
else:
    LIB_EXTENSION = 'so'

###### INPUT DATA ##########
CYLINDER = [[2, 3, 50, -20, 3, 0.06, 400],
           [3, 5, 45, -25, 0, 0.1, 300]]

NOISE = [500]

trial = 5000
test = 3
maxDisplayStructure = 3
########################

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))] 
    
def input_Gen():
    input_data = []

    #Generate inlier structures
    for radius, height, cx, cy, cz, sigma, amount in CYLINDER:
        #Cylinder
        cylData = []        
        rand_val = np.random.normal(0, sigma, 2 * amount)
        for i in range(amount):
            t = np.random.rand() * 2 * 3.14
            x = float(radius * np.cos(t) + rand_val[i])
            y = float(radius * np.sin(t) + rand_val[amount + i])
            z = float(np.random.rand() * height)
            cylData.append([x, y, z, 1])    
        npCylData = np.float32(cylData)
        
        #Randomly rotate the structure
        kAxis = np.array([np.random.rand(), np.random.rand(),
                          np.random.rand()], dtype = np.float32)
        kAxis = kAxis / np.linalg.norm(kAxis)
        Phi = np.random.rand() * 2 * 3.14
        cosPhi = np.cos(Phi)
        sinPhi = np.sin(Phi)
        Kmat = np.array([[0, -kAxis[2], kAxis[1]],
                         [kAxis[2], 0, -kAxis[0]],
                         [-kAxis[1], kAxis[0], 0]], dtype = np.float32)
        rotMat = np.eye(3) + sinPhi * Kmat + (1 - cosPhi) * Kmat.dot(Kmat)
        
        #Transformation matrix
        tranMat = np.eye(4)
        tranMat[:3,:3] = rotMat[:3,:3]
        tranMat[:3, 3] = [cx, cy, cz]   
        
        cloudData = (tranMat.dot(npCylData.T)).T

        for i in range(len(cloudData)):
            x, y, z = cloudData[i][:3]
            input_data.append((x, y, z))

    #Generate noise
    np_input_data = np.float32(input_data)
    xmin = np_input_data[:, 0].min()
    xrang = np_input_data[:, 0].max() - xmin
    ymin = np_input_data[:, 1].min()
    yrang = np_input_data[:, 1].max() - ymin
    zmin = np_input_data[:, 2].min()
    zrang = np_input_data[:, 2].max() - zmin

    #Generate random noise
    noise = NOISE[0]
    for i in range(noise):
        x = float((np.random.rand() * 1.5 - 0.25) * xrang + xmin)
        y = float((np.random.rand() * 1.5 - 0.25) * yrang + ymin)
        z = float((np.random.rand() * 1.5 - 0.25) * zrang + zmin)
        input_data.append((x, y, z))
        
    #Shuffle input data
    shuffle(input_data)
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
    # ax.set_aspect('equal') #Not implemented in current matplotlib version
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
    CylinderCtypes = dll.CylinderCtypes
    CylinderCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    CylinderCtypes.restype = ctypes.POINTER(Structure)    

    #Collect inputs
    inputNum = len(input_data)
    x = (ctypes.c_double * inputNum)(*x)
    y = (ctypes.c_double * inputNum)(*y)
    z = (ctypes.c_double * inputNum)(*z) 

    #Run Estimator
    result = CylinderCtypes(x, y, z, inputNum, trial)
        
    #Display result      
    fig = pylab.figure()
    ax = Axes3D(fig)
    # ax.set_aspect('equal') #Not implemented in current matplotlib version
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    
    ax.set_xlim(mean_x - max_range, mean_x + max_range)
    ax.set_ylim(mean_y - max_range, mean_y + max_range)
    ax.set_zlim(mean_z - max_range, mean_z + max_range)    
    
    structure_count = 0
    max_count = maxDisplayStructure
    dict_color = {0:'r', 1:'g', 2:'b', 3:'c', 4:'y', 5:'m'}
    
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize

        Xin = []; Yin = []; Zin =[]
        for idx in result[structure_count].StructureIndex[: structure_size]:
            mx, my, mz = input_data[idx][:3]
            Xin.append(mx)
            Yin.append(my)
            Zin.append(mz)
        npXin = np.float32(Xin)
        npYin = np.float32(Yin)
        npZin = np.float32(Zin)

        ax.scatter(npXin, npYin, npZin, s = 5, marker='o', 
                   c= dict_color[structure_count % len(dict_color)], lw = 0)
    
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
