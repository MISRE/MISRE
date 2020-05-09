#!/usr/bin/env python
'''
This script loads input images and paired data.
Then will try homography estimation.
'''
###### INPUT DATA ##########
filename = "unionhouse"

trial = 2000
maxDisplayStructure = 6
########################

#input image pair
IMG_1 = 'images/' + filename + '_1.JPG'
IMG_2 = 'images/' + filename + '_2.JPG'

# Load paired data
f = open(filename +".txt")
kp_pairs = []
for line in f:
    x1, y1, x2, y2 = line.split()   
    kp_pairs.append([(float(x1), float(y1)),(float(x2), float(y2))])    
f.close()
print 'Total Match:', len(kp_pairs)

import ctypes
import cv2
import numpy as np

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))]     

#Display all matches and collect inputs
img1 = cv2.imread(IMG_1,cv2.IMREAD_COLOR)
img2 = cv2.imread(IMG_2,cv2.IMREAD_COLOR)
h1, w1 = img1.shape[:2]
h2, w2 = img2.shape[:2]
vis = np.zeros((max(h1, h2), w1+w2, 3), np.uint8)
vis[:h1, :w1, :3] = img1
vis[:h2, w1:w1+w2, :3] = img2

x1 = []; y1 = []; x2 = []; y2 = []
for (mx1, my1), (mx2, my2) in kp_pairs:    
    cv2.circle(vis, (int(mx1), int(my1)), 4, (255, 255, 255), -1)
    cv2.circle(vis, (int(mx2) + w1, int(my2)), 4, (255, 255, 255), -1)    
    x1.append(mx1)
    y1.append(my1)
    x2.append(mx2)
    y2.append(my2)          
    
# Convert python lists to ctypes pointers
inputNum = len(kp_pairs)
x1 = (ctypes.c_double * inputNum)(*x1)
y1 = (ctypes.c_double * inputNum)(*y1)
x2 = (ctypes.c_double * inputNum)(*x2)
y2 = (ctypes.c_double * inputNum)(*y2)

def run():    
    #Ctypes
    dll = ctypes.CDLL("Homography.dll")
    HomographyCtypes = dll.HomographyCtypes
    HomographyCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    HomographyCtypes.restype = ctypes.POINTER(Structure)    

    #Estimate multiple inlier structures 
    result = HomographyCtypes(x1, y1, x2, y2, inputNum, trial)   

    #Display different structures
    vis[:h1, :w1, :3] = img1
    vis[:h2, w1:w1+w2, :3] = img2
    
    structure_count = 0
    max_count = maxDisplayStructure
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize
        for input_id in result[structure_count].StructureIndex[: structure_size]:
            (mx1, my1), (mx2, my2) = kp_pairs[input_id]
            cv2.circle(vis, (int(mx1), int(my1)), 4, color[structure_count % len(color)], -1)
            cv2.circle(vis, (int(mx2) + w1, int(my2)), 4, color[structure_count % len(color)], -1)            

        print "Strength: ", result[structure_count].StructureStrength, \
              "Size: ", structure_size,\
              "Scale: ", result[structure_count].StructureScale
        structure_count += 1
        
    #Free memory
    dll.FreeMemory(result)    
    
iteration = 0
color = {0:(0, 0, 255), 1:(0, 255, 0), 2:(255, 0, 0),
         3:(255, 255, 0), 4:(0, 255, 255), 5:(255, 0, 255)}
while(1):
    cv2.imshow('Homography [R]: Run, [Q]: Quit',vis)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('r'):
        print '\nIteration', iteration        
        run()
        iteration += 1
    elif k == ord('q'):
        break    
cv2.destroyAllWindows()
