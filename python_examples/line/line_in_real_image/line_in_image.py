#!/usr/bin/env python

import ctypes
import cv2
import numpy as np
from random import shuffle
import platform

LIB_FOLDER = '../../../cpp/bin'
LIB_NAME   = 'line'
if platform.system() == 'Windows':
    LIB_EXTENSION = 'dll'
else:
    LIB_EXTENSION = 'so'


###### INPUT DATA ##########
filename = "pole"

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

def input_Gen():
    input_data_list = []
    
    f = open(filename + '.txt')
    for line in f:
        x, y = line.split()
        x = float(x)
        y = float(y)
        input_data_list.append([x, y])    
        
    #Shuffle input data
    shuffle(input_data_list)        
    return input_data_list

input_data = input_Gen()
print ("total input: {}".format(len(input_data)))

def run(iteration):
    img = cv2.imread('images/' + filename + '.jpg')
    h, w = img.shape[:2]
    img_edge = np.zeros((h, w), np.uint8)
    for (mx, my) in input_data:
        cv2.circle(img_edge, (int(mx), int(my)),
                       1, (255,255,255), -1)
    cv2.imshow('edge', img_edge)
    cv2.waitKey()
    cv2.destroyAllWindows()

    #Ctypes
    dll = ctypes.CDLL("{}/{}.{}".format(LIB_FOLDER, LIB_NAME, LIB_EXTENSION))

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
    
    result = LineCtypes(x, y, inputNum, trial)
       
    #Display result 
    structure_count = 0
    max_count = maxDisplayStructure
    dict_color = {0:(0, 0, 255), 1:(0, 255, 0), 2:(255, 0, 0),
                  3:(255, 255, 0), 4:(0, 255, 255), 5:(255, 0, 255)}
    
    while structure_count < max_count and result[structure_count].StructureSize > 0:
        structure_size = result[structure_count].StructureSize

        for idx in result[structure_count].StructureIndex[: structure_size]:            
            cv2.circle(img, (int(input_data[idx][0]), int(input_data[idx][1])),
                       1, dict_color[structure_count % len(dict_color)], -1)                   
        #Plot TLS lines
        a, b, c = result[structure_count].StructureTLS[: 3]
        if b !=0:
            lx = np.linspace(0, w, 2)
            ly = (-lx * a - c)/b
        else:
            lx = -c/b
            ly = np.linspace(0, h, 2)                

        cv2.line(img, (int(lx[0]), int(ly[0])),
                 (int(lx[1]), int(ly[1])), dict_color[structure_count % len(dict_color)], 2)
        
        print ('a = {}, b = {}, c = {}'.format(a,b,c)) 
        print ("Strength: ", result[structure_count].StructureStrength, \
              "Size: ", structure_size,\
              "Scale: ", result[structure_count].StructureScale)
        structure_count += 1

    cv2.imshow('line', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


    #Free memory
    dll.FreeMemory(result)
        
if __name__=="__main__":
    for iteration in range(test):        
        print ('\nIteration:', iteration)
        run(iteration)
