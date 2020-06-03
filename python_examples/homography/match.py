#!/usr/bin/env python
import cv2
import numpy as np

def siftMatch(img1, img2, ratio = 0.8):
    FLANN_INDEX_KDTREE = 0
    detector = cv2.SIFT()
    flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    matcher = cv2.FlannBasedMatcher(flann_params, search_params)    
    kp1, desc1 = detector.detectAndCompute(img1, None)
    kp2, desc2 = detector.detectAndCompute(img2, None)

    raw_matches = matcher.knnMatch(desc1, desc2, k = 2)
    mkp1, mkp2 = [], []
    for m in raw_matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append(kp1[m.queryIdx])
            mkp2.append(kp2[m.trainIdx])
    mkp1 = [np.float32(kp.pt) for kp in mkp1]
    mkp2 = [np.float32(kp.pt) for kp in mkp2]
    kp_pairs = zip(mkp1, mkp2)
    return kp_pairs
