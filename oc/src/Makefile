# Project:        TAT-C
# Created by:     Joey Gurganus
# Date:           2019.02.28


.DEFAULT_GOAL := all

# Define macros for locations
THIRD_PARTY_DIR = ../../../third-party-tools
BASE_ROOT = ..
GMAT_DIR = $(BASE_ROOT)/GMATsrc
LIB_DIR = $(BASE_ROOT)/lib

BOOST_ROOT = $(THIRD_PARTY_DIR)/boost_1_63_0

# Program to make library
LIB = liboc.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(GMAT_DIR)/base \
-I$(GMAT_DIR)/include \
-I$(GMAT_DIR)/util \
-I$(GMAT_DIR)/util/interpolator \
-I$(GMAT_DIR)/console \
-I$(BOOST_ROOT) \
-I$(BOOST_ROOT)/boost/math/special_functions

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -std=gnu++11
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
    VisiblePOIReport.o 

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
all: $(LIB) install

$(LIB): $(OBJECTS)
	@if [ ! -x $(LIB_DIR) ]; then mkdir $(LIB_DIR); fi 
	ar cru $@ $(OBJECTS)

install: $(LIB_DIR)/$(LIB)

$(LIB_DIR)/$(LIB): $(LIB)
	cp $(LIB) $(LIB_DIR)/.
	chmod -R 755 $(LIB_DIR)

clean:
	rm -f $(OBJECTS) $(LIB) core

bare: clean
	rm -f $(LIB_DIR)/$(LIB)

runtest:
	@echo "This directory doesn't use testing"
