import ctypes
import numpy as np
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits.mplot3d import Axes3D
import platform

LIB_FOLDER = '../../../cpp/bin'
LIB_NAME   = 'cylinder'
if platform.system() == 'Windows':
    LIB_EXTENSION = 'dll'
else:
    LIB_EXTENSION = 'so'

###### INPUT DATA ##########
trial = 2000
test = 3
maxDisplayStructure = 4
########################

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))]    

x = []; y = []; z = []
f = open("cloud.txt")
for line in f:    
    mx, my, mz = line.split()[:3]
    x.append(float(mx))
    y.append(float(my))
    z.append(float(mz))
f.close()
npXVals = np.float32(x)
npYVals = np.float32(y)
npZVals = np.float32(z)

print ("Total points: " + str(len(x)))

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
CylinderCtypes = dll.CylinderCtypes
CylinderCtypes.argtypes = (
                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                            ctypes.POINTER(ctypes.c_double),
                            ctypes.c_size_t, ctypes.c_size_t)
CylinderCtypes.restype = ctypes.POINTER(Structure)   

#Collect inputs
inputNum = len(x)
x = (ctypes.c_double * inputNum)(*x)
y = (ctypes.c_double * inputNum)(*y)
z = (ctypes.c_double * inputNum)(*z)    

def run(iteration):  
    result = CylinderCtypes(x, y, z, inputNum, trial)
    
    #Display result      
    fig = pylab.figure()
    ax = Axes3D(fig)
    #ax.set_aspect('equal')
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

        if structure_count < maxDisplayStructure:
            Xin = []; Yin = []; Zin =[]
            for idx in result[structure_count].StructureIndex[: structure_size]:
                mx = x[idx]
                my = y[idx]
                mz = z[idx]
                
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
