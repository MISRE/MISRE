# Configure:

# Linux
EIGEN_INCLUDE_DIR = /usr/include/eigen3
# Mac OSX
#EIGEN_INCLUDE_DIR = /usr/local/Cellar/eigen/3.3.7/include/eigen3

# Where the library files are copied
INSTALLDIR  = ../bin

# End configuration ---------------------------------------------

ifeq ($(OS),Windows_NT)
	$(error Do not use make to compile on Windows. You need a Visual Studio project)
endif

# Specify extensions of files to delete when cleaning
CLEANEXTS   = o so

# Specify the source files, the target files, 
# and the install directory 
COMMON      = common/Estimate.cpp common/Expand.cpp common/MahaDist.cpp common/MeanShiftKDE.cpp common/Normalize.cpp common/RandomSet.cpp 
LINE        = line/Functions.cpp line/LineCtypes.cpp
ELLIPSE     = ellipse/EllipseCtypes.cpp ellipse/Functions.cpp
HOMOGRAPHY  = homography/Functions.cpp homography/HomographyCtypes.cpp
CYLINDER    = cylinder/CylinderCtypes.cpp cylinder/Functions.cpp
FUNDAMENTAL = fundamental_matrix/Functions.cpp fundamental_matrix/FundMatCtypes.cpp
#PLANE       = plane/

SOURCES1    = $(COMMON) $(LINE)
SOURCES2    = $(COMMON) $(ELLIPSE)
SOURCES3    = $(COMMON) $(HOMOGRAPHY)
SOURCES4    = $(COMMON) $(CYLINDER)
SOURCES5    = $(COMMON) $(FUNDAMENTAL)
#SOURCES6    = $(COMMON) $(PLANE)


OUTPUTFILE1  = line.so
OUTPUTFILE2  = ellipse.so
OUTPUTFILE3  = homography.so
OUTPUTFILE4  = cylinder.so
OUTPUTFILE5  = fundamental.so
#OUTPUTFILE6  = plane.so

INCLUDE_DIRS = -I$(EIGEN_INCLUDE_DIR) -Icommon -Iline

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
#	CCFLAGS += $(INCLUDE_DIRS) -std=c++11 
	CPPFLAGS += $(INCLUDE_DIRS) -std=c++11 -fPIC
endif
ifeq ($(UNAME_S),Darwin)
	CCFLAGS += $(INCLUDE_DIRS) -std=c++11 -stdlib=libc++
endif


.PHONY: all
all: $(OUTPUTFILE1) $(OUTPUTFILE2) $(OUTPUTFILE3) $(OUTPUTFILE4) $(OUTPUTFILE5) # $(OUTPUTFILE6) 

$(OUTPUTFILE1): $(subst .cpp,.o,$(SOURCES1)) 
	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^

$(OUTPUTFILE2): $(subst .cpp,.o,$(SOURCES2)) 
	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^

$(OUTPUTFILE3): $(subst .cpp,.o,$(SOURCES3)) 
	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^

$(OUTPUTFILE4): $(subst .cpp,.o,$(SOURCES4)) 
	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^

$(OUTPUTFILE5): $(subst .cpp,.o,$(SOURCES5)) 
	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^

#$(OUTPUTFILE6): $(subst .cpp,.o,$(SOURCES6)) 
#	$(CXX) -shared -fPIC $(INCLUDE_DIRS) $(LDFLAGS) -o $@ $^


.PHONY: install
install:
	mkdir -p $(INSTALLDIR)
	mv -i $(OUTPUTFILE1) $(INSTALLDIR)
	mv -i $(OUTPUTFILE2) $(INSTALLDIR)
	mv -i $(OUTPUTFILE3) $(INSTALLDIR)
	mv -i $(OUTPUTFILE4) $(INSTALLDIR)
	mv -i $(OUTPUTFILE5) $(INSTALLDIR)
#	mv -i $(OUTPUTFILE6) $(INSTALLDIR)

.PHONY: clean 
clean:
	for file in $(CLEANEXTS); do rm -f *.$$file; done

# Generate dependencies of .ccp files on .hpp files
include $(subst .cpp,.d,$(SOURCES))

%.d: %.cpp
	$(CC) -M $(CCFLAGS)  $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
rm -f $@.$$$$
