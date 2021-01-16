# Project:        TAT-C
# Created by:     Joey Gurganus
# Date:           2019.02.28


.DEFAULT_GOAL := all

# Define macros for locations
BASE_ROOT = ..
GMAT_DIR = .
LIB_DIR = $(BASE_ROOT)/lib

# Program to make library
LIB = libgmat.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(GMAT_DIR)/base \
-I$(GMAT_DIR)/include \
-I$(GMAT_DIR)/util \
-I$(GMAT_DIR)/util/interpolator \
-I$(GMAT_DIR)/util/matrixoperations \
-I$(GMAT_DIR)/console

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -std=gnu++17
CPP = g++

OBJECTS = \ # Note that not all avaialble files are compiled.
    $(GMAT_DIR)/base/ExponentialAtmosphere.o \
    $(GMAT_DIR)/util/A1Date.o \
    $(GMAT_DIR)/util/A1Mjd.o \
    $(GMAT_DIR)/util/AttitudeConversionUtility.o \
    $(GMAT_DIR)/util/BaseException.o \
    $(GMAT_DIR)/util/BodyFixedStateConverter.o \
    $(GMAT_DIR)/util/Date.o \
    $(GMAT_DIR)/util/DateUtil.o \
    $(GMAT_DIR)/util/ElapsedTime.o \
    $(GMAT_DIR)/util/EopFile.o \
    $(GMAT_DIR)/util/FileManager.o \
    $(GMAT_DIR)/util/FileUtil.o \
    $(GMAT_DIR)/util/GmatGlobal.o \
    $(GMAT_DIR)/util/GmatTime.o \
    $(GMAT_DIR)/util/GregorianDate.o \
    $(GMAT_DIR)/util/LeapSecsFileReader.o \
    $(GMAT_DIR)/util/Linear.o \
    $(GMAT_DIR)/util/MessageInterface.o \
    $(GMAT_DIR)/util/MessageReceiver.o \
    $(GMAT_DIR)/util/RandomNumber.o \
    $(GMAT_DIR)/util/RealUtilities.o \
    $(GMAT_DIR)/util/Rmatrix.o \
    $(GMAT_DIR)/util/Rmatrix33.o \
    $(GMAT_DIR)/util/Rmatrix66.o \
    $(GMAT_DIR)/util/Rvector.o \
    $(GMAT_DIR)/util/Rvector3.o \
    $(GMAT_DIR)/util/Rvector6.o \
    $(GMAT_DIR)/util/StateConversionUtil.o \
    $(GMAT_DIR)/util/StringTokenizer.o \
    $(GMAT_DIR)/util/StringUtil.o \
    $(GMAT_DIR)/util/TimeSystemConverter.o \
    $(GMAT_DIR)/util/TimeTypes.o \
    $(GMAT_DIR)/util/UtcDate.o \
    $(GMAT_DIR)/util/interpolator/LagrangeInterpolator.o \
    $(GMAT_DIR)/util/interpolator/Interpolator.o \
    $(GMAT_DIR)/util/interpolator/InterpolatorException.o \
    $(GMAT_DIR)/util/matrixoperations/CholeskyFactorization.o \
    $(GMAT_DIR)/util/matrixoperations/LUFactorization.o \
    $(GMAT_DIR)/util/matrixoperations/MatrixFactorization.o \
    $(GMAT_DIR)/util/matrixoperations/QRFactorization.o \
    $(GMAT_DIR)/util/matrixoperations/SchurFactorization.o

#
# Default suffix rule
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
	@ranlib $@

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
