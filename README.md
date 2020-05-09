# MISRE
Code/Examples for A New Approach to Robust Estimation of Parametric Structures

===============================================================================
Robust Estimation of Multiple Inlier Structures
Authors: Xiang Yang and Peter Meer
Robust Image Understanding Laboratory, Rutgers University
===============================================================================

===============================================================================
Python/C++ Implementation based on:
[1] X. Yang and P. Meer "Robust Estimation of Multiple Inlier Structures", 2017. 

We present a method to robustly estimate multiple inlier structures with different scales in the presence of noise. 
The estimation is done iteratively with the objective function transformed into a higher dimensional linear space 
by carrier vectors. An initial set consisting of a small number of points that has the minimum sum of Mahalanobis 
distances is detected from the trials based on elemental subsets. The region of interest is defined by applying an 
expansion criteria to an increasing sequence of sets of points which begins with the initial set and increases
until the set cannot expand.The largest expansion in this region gives the scale estimate. The original mean shift 
is applied to all remaining input points to re-estimate the structure. After all data are processed, the segmented 
structures are sorted by strengths with the strongest inlier structures at the front.

Examples for the following applications are provided:
1. 2D lines estimation (in synthetic and real images)
2. 2D ellipses estimation (in synthetic and real images)
3. 3D cylinder estimation (in synthetic and real cloud data)
4. Moving Object Segmentation using Fundamental matrix
5. Homography estimation
===============================================================================

===============================================================================
For general use,
1. Download 64bit Python 2.7.x from https://www.python.org/downloads/windows/.
2. Download 64bit version of the following three site-packages for Python 2.7:
Numpy, OpenCV and Matplotlib from http://www.lfd.uci.edu/~gohlke/pythonlibs/.
3. After installation, locate the python scripts in the folder "x64 python examples\".
The user can run the default setting, or specify the preferred input data at the beginning of each script.
4. For 32bit Python, replace all dlls with the win32 versions in "cpp\bin\win32". 
===============================================================================

===============================================================================
For modification and recompilation purpose on the C++ source files, go to "cpp\" folder.
The core functions are located in folder "cpp\sources\common". Each folder for different objective functions 
consists of four files, which are modified accordingly to specify the computation of carriers, jacobians and the 
parameters of objective function:
Please refer to the comments in the codes for more details.
===============================================================================

Please report any inconsistencies/bugs/suggestions to:

Xiang Yang
xiang.yang@rutgers.edu

Robust Image Understanding Laboratory
http://coewww.rutgers.edu/riul

NOTE: The code was only tested on Windows 7 os, the dlls (both 32/64 bit versions) in the folder "cpp\bin" are 
compiled in Visual Studio 2013. Recompilation of the dlls on different platforms may be needed.
