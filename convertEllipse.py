#!/usr/bin/env python

'''This function is used to convert ellipse to a standard form, which can be found at
    http://ringwa.lt/2013/08/converting-ellipse-general-form-to-standard-form-in-python/
    Thanks for Dan Ringwalt's Code'''

import numpy as np

def ellipse_general_to_standard(A, B, D, C, E, F):    
    A, B, C, D, E, F = map(float, [A, B, C, D, E, F])
    AQ = np.array([[A, B/2, D/2], [B/2, C, E/2], [D/2, E/2, F]])
    A33 = AQ[0:2, 0:2]
    x0, y0 = np.linalg.inv(A33).dot([-D/2, -E/2])
    evals, evecs = np.linalg.eigh(A33)
    a, b = np.sqrt(-np.linalg.det(AQ)/(np.linalg.det(A33)*evals))
    t = np.arctan2(evecs[1,0], evecs[0,0])
    if b > a:
        a, b = b, a
        t += np.pi/2
    if t < -np.pi/2: t += np.pi
    elif t >  np.pi/2: t -= np.pi
    return (x0, y0, a, b, t)
