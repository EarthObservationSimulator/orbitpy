.DEFAULT_GOAL := all

# Define macros for locations
BASE_ROOT = ../../..
GMATUTIL_DIR = $(BASE_ROOT)/extern/gmatutil

# Program to make library
LIB = libpropcov.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/util/matrixoperations \
-I$(GMATUTIL_DIR)/console \
-I..

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -std=gnu++17
CPP = g++

OBJECTS = \
    GMATPolygon.o \
	Polygon.o \
	SlicedPolygon.o \
	Preprocessor.o \
	SliceArray.o \
	SliceTree.o \
	PointInPolygon.o \
	DSPIPCustomSensor.o

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
