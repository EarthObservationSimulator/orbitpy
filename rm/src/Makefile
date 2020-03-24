###############################################################################
# Project:        TATC
# Created by:     Gabriel Apaza
# Date:           2018.10.18

# Modifed by:     Joey Gurganus
# Date:           2019.04.09
###############################################################################


DRIVER = orbitModule

# Define macros for locations
THIRD_PARTY_DIR = ../../../third-party-tools
OC_DIR       = ../../oc
OC_LIB_DIR   = $(OC_DIR)/lib
OC_GMAT_DIR  = $(OC_DIR)/GMATsrc
OC_SRC_DIR   = $(OC_DIR)/src
BOOST_ROOT   = $(THIRD_PARTY_DIR)/boost_1_63_0
GMAT_LIB     = $(OC_LIB_DIR)/libgmat.a
GMAT_OC_LIB  = $(OC_LIB_DIR)/liboc.a

BASE_ROOT    = ..
BIN_DIR      = $(BASE_ROOT)/bin
INC_DIR      = $(BASE_ROOT)/include
TEST_DIR     = $(BASE_ROOT)/test/suites
TEST_EXEC    = $(BASE_ROOT)/test/bin
RM_LIB_DIR   = $(BASE_ROOT)/lib


# Program to make library
RM_LIB = librm.a



EXECUTABLE = $(BIN_DIR)/reductionMetrics

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(INC_DIR) \
-I$(THIRD_PARTY_DIR) \
-I$(OC_SRC_DIR) \
-I$(OC_GMAT_DIR)/base \
-I$(OC_GMAT_DIR)/include \
-I$(OC_GMAT_DIR)/util \
-I$(OC_GMAT_DIR)/util/interpolator \
-I$(OC_GMAT_DIR)/util/matrixoperations \
-I$(OC_GMAT_DIR)/console \
-I$(BOOST_ROOT) \
-I$(BOOST_ROOT)/boost/math/special_functions

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -pthread -std=gnu++11
CPP = g++


# LIB need to compile the EXECUTABLE  
LIB     = -L$(OC_LIB_DIR)
# How they are invoked on the compile  line
LIBS    = -loc -lgmat -lpthread

# Link specific flags
LINK_FLAGS = $(LIB) $(LIBS)
ifeq ($(shell uname -s), Darwin)
    LINK_FLAGS +=  /usr/lib/libstdc++.6.dylib \
                   -headerpad_max_install_names \
                   -lm -v 
endif

OBJECTS = \
    AreaOfInterest.o \
    GridSize.o \
    GroundNetwork.o \
    InstrumentCoverage.o \
    MessageHandler.o \
    Metrics.o \
    OrbitalParameters.o \
    OrbitPropagator.o \
    jsoncpp.o \
    CacheInterface.o \
    $(DRIVER).o
#
# Default suffix rule
.SUFFIXES:
.SUFFIXES: .o .cpp
#
.cpp.o:
	$(CPP) $(CPPFLAGS) -c $< -o $@

# Target definitions
#
all: $(EXECUTABLE) install

install: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) $(GMAT_LIB) $(GMAT_OC_LIB)
	@if [ ! -x $(BIN_DIR) ]; then mkdir $(BIN_DIR); fi 
	$(CPP) $(OBJECTS) $(LINK_FLAGS) -o $@
	@chmod -R 755 $(BIN_DIR)

runtest:
	@echo "Running test.."; \
	cd $(TEST_DIR); \
	make grid; \
	make area;


clean:
	rm -f $(OBJECTS) core
	rm -f $(TEST_DIR)/Test_AreaOfInterest.o
	rm -f $(TEST_DIR)/Test_GridSize.o

bare: clean
	rm -rf $(EXECUTABLE) $(BIN_DIR)
	rm -rf $(TEST_EXEC)
	@find $(BASE_ROOT) -type f -name rmLog.txt -delete
