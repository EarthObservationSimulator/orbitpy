.DEFAULT_GOAL := all

# Define macros for locations
BASE_ROOT = ..
GMATUTIL_DIR = .

# Program to make library
LIB = libgmatutil.a

OPTIMIZATIONS = -O3 -funroll-loops

# Define macros for the needed includes
HEADERS =   -I. \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/util/matrixoperations 

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) -Wall -g -std=gnu++17
CPP = g++

OBJECTS = \
    $(GMATUTIL_DIR)/base/ExponentialAtmosphere.o \
    $(GMATUTIL_DIR)/util/A1Date.o \
    $(GMATUTIL_DIR)/util/A1Mjd.o \
    $(GMATUTIL_DIR)/util/AttitudeConversionUtility.o \
    $(GMATUTIL_DIR)/util/BaseException.o \
    $(GMATUTIL_DIR)/util/BodyFixedStateConverter.o \
    $(GMATUTIL_DIR)/util/Date.o \
    $(GMATUTIL_DIR)/util/DateUtil.o \
    $(GMATUTIL_DIR)/util/ElapsedTime.o \
    $(GMATUTIL_DIR)/util/EopFile.o \
    $(GMATUTIL_DIR)/util/FileManager.o \
    $(GMATUTIL_DIR)/util/FileUtil.o \
    $(GMATUTIL_DIR)/util/GmatGlobal.o \
    $(GMATUTIL_DIR)/util/GmatTime.o \
    $(GMATUTIL_DIR)/util/GregorianDate.o \
    $(GMATUTIL_DIR)/util/LeapSecsFileReader.o \
    $(GMATUTIL_DIR)/util/Linear.o \
    $(GMATUTIL_DIR)/util/MessageInterface.o \
    $(GMATUTIL_DIR)/util/MessageReceiver.o \
    $(GMATUTIL_DIR)/util/RandomNumber.o \
    $(GMATUTIL_DIR)/util/RealUtilities.o \
    $(GMATUTIL_DIR)/util/Rmatrix.o \
    $(GMATUTIL_DIR)/util/Rmatrix33.o \
    $(GMATUTIL_DIR)/util/Rmatrix66.o \
    $(GMATUTIL_DIR)/util/Rvector.o \
    $(GMATUTIL_DIR)/util/Rvector3.o \
    $(GMATUTIL_DIR)/util/Rvector6.o \
    $(GMATUTIL_DIR)/util/StateConversionUtil.o \
    $(GMATUTIL_DIR)/util/StringTokenizer.o \
    $(GMATUTIL_DIR)/util/StringUtil.o \
    $(GMATUTIL_DIR)/util/TimeSystemConverter.o \
    $(GMATUTIL_DIR)/util/TimeTypes.o \
    $(GMATUTIL_DIR)/util/UtcDate.o \
    $(GMATUTIL_DIR)/util/interpolator/LagrangeInterpolator.o \
    $(GMATUTIL_DIR)/util/interpolator/Interpolator.o \
    $(GMATUTIL_DIR)/util/interpolator/InterpolatorException.o \
    $(GMATUTIL_DIR)/util/matrixoperations/CholeskyFactorization.o \
    $(GMATUTIL_DIR)/util/matrixoperations/LUFactorization.o \
    $(GMATUTIL_DIR)/util/matrixoperations/MatrixFactorization.o \
    $(GMATUTIL_DIR)/util/matrixoperations/QRFactorization.o \
    $(GMATUTIL_DIR)/util/matrixoperations/SchurFactorization.o

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
	ar cru $@ $(OBJECTS)
	@ranlib $@

install: $(LIB)

clean:
	rm -f $(OBJECTS) $(LIB)

bare: clean

runtest:
	@echo "This directory doesn't use testing"
