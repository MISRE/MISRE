#!/usr/bin/env python
'''
This script loads input images and matches features using SIFT in OpenCV.
Then will try fundamental matrix estimation.
'''
import ctypes
import cv2
import numpy as np
from match import siftMatch
import platform 

LIB_FOLDER = '../../cpp/bin'
LIB_NAME   = 'fundamental'
if platform.system() == 'Windows':
    LIB_EXTENSION = 'dll'
else:
    LIB_EXTENSION = 'so'

###### INPUT DATA ##########
IMG_1 = 'images/calendar_1.JPG'
IMG_2 = 'images/calendar_2.JPG'

trial = 5000
maxDisplayStructure = 4
########################

class Structure(ctypes.Structure):
    _fields_=[("StructureStrength", ctypes.c_double),                    
                    ("StructureSize", ctypes.c_size_t),
                    ("StructureScale", ctypes.c_double),
                    ("StructureIndex", ctypes.POINTER(ctypes.c_size_t)),
                    ("StructureTLS", ctypes.POINTER(ctypes.c_double))]    

#Match features with SIFT
img1 = cv2.imread(IMG_1, 0)
img2 = cv2.imread(IMG_2, 0)
kp_pairs = siftMatch(img1, img2)
print 'Total Match:', len(kp_pairs)

#Display all matches and collect inputs
img1_c = cv2.imread(IMG_1,cv2.IMREAD_COLOR)
img2_c = cv2.imread(IMG_2,cv2.IMREAD_COLOR)
h1, w1 = img1.shape[:2]
h2, w2 = img2.shape[:2]
vis = np.zeros((max(h1, h2), w1+w2, 3), np.uint8)
vis[:h1, :w1, :3] = img1_c
vis[:h2, w1:w1+w2, :3] = img2_c

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
    dll = ctypes.CDLL("{}/{}.{}".format(LIB_FOLDER, LIB_NAME, LIB_EXTENSION))
    FundMatCtypes = dll.FundMatCtypes
    FundMatCtypes.argtypes = (
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                ctypes.c_size_t, ctypes.c_size_t)
    FundMatCtypes.restype = ctypes.POINTER(Structure)    

    #Estimate multiple inlier structures 
    result = FundMatCtypes(x1, y1, x2, y2, inputNum, trial)   
    
    #Display different structures
    vis[:h1, :w1, :3] = img1_c
    vis[:h2, w1:w1+w2, :3] = img2_c
        
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
    cv2.imshow('Fundamental Matrix [R]: Run, [Q]: Quit',vis)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('r'):
        print '\nIteration', iteration        
        run()
        iteration += 1
    elif k == ord('q'):
        break    
cv2.destroyAllWindows()
