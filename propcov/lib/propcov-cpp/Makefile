.DEFAULT_GOAL := all

# Define macros for locations
BASE_ROOT = ../..
GMATUTIL_DIR = $(BASE_ROOT)/extern/gmatutil

# Program to make library
LIB = libpropcov.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I./polygon \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/console \


CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -std=gnu++17
CPP = g++

OBJECTS = \
    AbsoluteDate.o \
    Attitude.o \
    ConicalSensor.o \
    CoverageChecker.o \
    CustomSensor.o \
    Earth.o \
    IntervalEventReport.o \
    KeyValueStatistics.o \
    LinearAlgebra.o \
    NadirPointingAttitude.o \
    OrbitState.o \
    PointGroup.o \
    Propagator.o \
    RectangularSensor.o \
    Sensor.o \
    Spacecraft.o \
    TATCException.o \
    VisibilityReport.o \
    VisiblePOIReport.o \
    Projector.o \
    DiscretizedSensor.o \
    polygon/GMATPolygon.o \
    polygon/PointInPolygon.o \
    polygon/Polygon.o \
    polygon/Preprocessor.o \
    polygon/SliceArray.o \
    polygon/SlicedPolygon.o \
    polygon/SliceTree.o \
    polygon/SphericalSensor.o \

#
# Default suffix rule
.SUFFIXES:
.SUFFIXES: .o .cpp
#
.cpp.o:
	$(CPP) $(CPPFLAGS) -c $< -o $@ 
#
.PHONY: all install clean bare runtest
###############################################################################################
# Target definitions
#
all: bare $(LIB) install

$(LIB): $(OBJECTS)
	@if [ ! -x $(LIB_DIR) ]; then mkdir $(LIB_DIR); fi 
	ar cru $@ $(OBJECTS)

install: $(LIB)

clean:
	rm -f $(OBJECTS) $(LIB)

bare: clean
	rm -f $(LIB)

runtest:
	@echo "This directory doesn't use testing"
