# MISRE
Code/Examples for "A New Approach to Robust Estimation of Parametric Structures"

X. Yang, P. Meer and J. Meer, "A New Approach to Robust Estimation of Parametric Structures," in IEEE Transactions on Pattern Analysis and Machine Intelligence, doi: 10.1109/TPAMI.2020.2994190.

A New Approach to Robust Estimation of Parametric Structures
===============================================================================
Authors: Xiang Yang and Peter Meer and Jonathan Meer

Python/C++ Implementation based on:

X. Yang and P. Meer and J. Meer 

"A New Approach to Robust Estimation of Parametric Structures", IEEE TPAMI 2020. 

Examples for the following applications are provided:
1. 2D lines estimation (in synthetic and real images)
2. 2D ellipses estimation (in synthetic and real images)
3. 3D cylinder estimation (in synthetic and real cloud data)
4. Moving Object Segmentation using Fundamental matrix
5. Homography estimation (with test on Adelaide dataset)
6. 3D sphere estimation (3D point cloud included)
7. 3D plane estimation (3D point cloud included)


===============================================================================
#Notice: 
The latest version of Python (3.8) and 3rd party packages will also work, 
but user should modify the codes accordingly

For general use,
1. Download 64bit Python 2.7.x from https://www.python.org/downloads/windows/.
2. Download 64bit version of the following three site-packages for Python 2.7:
Numpy, OpenCV and Matplotlib from http://www.lfd.uci.edu/~gohlke/pythonlibs/.
3. After installation, locate the python scripts in the folder "x64 python examples\".
The user can run the default setting, or specify the preferred input data at the beginning of each script.
===============================================================================

For modification and recompilation purpose on the C++ source files, go to "cpp\" folder.
The core functions are located in folder "cpp\sources\common". Each folder for different objective functions 
consists of four files, which are modified accordingly to specify the computation of carriers, jacobians and the 
parameters of objective function:
Please refer to the comments in the codes for more details.
===============================================================================

Please report any inconsistencies/bugs/suggestions to:

Xiang Yang
xiang.yang@yahoo.com

NOTE: The code was tested on Windows 7 os, the dlls (64 bit versions) in the folder "cpp\bin" are 
compiled in Visual Studio 2013. Recompilation of the dlls on different platforms may be needed.


Updated on Jun/03/2020
Mr. Josep Ramon Morros provided the compilation support on Linux/MacOSX, and many critical modifications on the codes.
Python 3 and latest version of OpenCV are now supported under his contribution.
We sincerely thank him for his work.
===============================================================================

Compiling on Linux/MacOSX: 
- Install the Eigen library (for instance 'brew install eigen' on OSX, 'sudo apt install libeigen3-dev' in Ubuntu)
- Configure cpp/sources/Makefile for your system
- Go to cpp/source and type 'make ; make install'

Tested on OSX Mojave (10.14.6) and Ubuntu 18.04.2 LTS

For each python example, configure at the beginning of the file the folder where the dynamic 
libaries are installed (should match the Makefile)
