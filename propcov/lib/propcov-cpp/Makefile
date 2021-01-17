.DEFAULT_GOAL := all

# Define macros for locations
THIRD_PARTY_DIR = ../../../third-party-tools
BASE_ROOT = ..
GMATUTIL_DIR = $(BASE_ROOT)/gmatutil

BOOST_ROOT = $(THIRD_PARTY_DIR)/boost_1_72_0

# Program to make library
LIB = libpropcov.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/console \
-I$(BOOST_ROOT) \
-I$(BOOST_ROOT)/boost/math/special_functions

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
    DiscretizedSensor.o

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
