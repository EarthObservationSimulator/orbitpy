# This makefile allows to build the test sources followed by linking to generate the test executables.

# Tests
T_SRC_DIR := ./tests-cpp
T_BUILD_DIR := ./build

# Source Code
PROPCOVCPP_DIR = ./../lib/propcov-cpp

# External
GMATUTIL_DIR = ./../extern/gmatutil


T_SRCS := $(wildcard $(T_SRC_DIR)/*.cpp)
T_OBJS := $(T_SRCS:$(T_SRC_DIR)/%.cpp=$(T_BUILD_DIR)/%.o)
T_DEPS := $(T_OBJS:.o=.d)
T_EXES = $(T_OBJS:.o=.exe)

# PROPCOV-CPP
OBJS1 := $(PROPCOVCPP_DIR)/*.o \
$(PROPCOVCPP_DIR)/polygon/*.o

# External GMAT dependencies
OBJS2 := $(GMATUTIL_DIR)/base/*.o \
$(GMATUTIL_DIR)/util/*.o \
$(GMATUTIL_DIR)/util/interpolator/*.o \
$(GMATUTIL_DIR)/util/matrixoperations/*.o


# Define macros for the needed includes
HEADERS =  -I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/util/matrixoperations \
-I$(PROPCOVCPP_DIR) \
-I$(PROPCOVCPP_DIR)/polygon

CPPFLAGS = $(HEADERS) -MMD -MP -std=c++17
LDFLAGS = -std=c++17
TESTFLAGS = -lpthread -lgtest
CXX = g++

all: clean gmatutil propcovcpp $(T_OBJS) $(T_EXES)

gmatutil: gmatutil_clean # Build the gmatutil source
	-X=`pwd`; \
	echo '<<<' $$GMATUTIL_DIR '>>>'; cd $$X; cd $(GMATUTIL_DIR); make all;

gmatutil_clean: 
	-X=`pwd`; \
	echo '<<<' $$GMATUTIL_DIR '>>>'; cd $$X; cd $(GMATUTIL_DIR); make clean;

propcovcpp: propcovcpp_clean # Build the propcovcpp source
	-X=`pwd`; \
	echo '<<<' $$PROPCOVCPP_DIR '>>>'; cd $$X; cd $(PROPCOVCPP_DIR); make all;

propcovcpp_clean: 
	-X=`pwd`; \
	echo '<<<' $$PROPCOVCPP_DIR '>>>'; cd $$X; cd $(PROPCOVCPP_DIR); make clean;


# Build step for C++ tests source
$(T_OBJS): $(T_BUILD_DIR)/%.o: $(T_SRC_DIR)/%.cpp
	$(CXX) $(CPPFLAGS) -c $< -o $@

# Link step for C++ tests
$(T_EXES): $(T_BUILD_DIR)/%.exe : $(T_BUILD_DIR)/%.o $(OBJS)
	$(CXX) $(OBJS1) $(OBJS2) $< -o $@ $(TESTFLAGS)

.PHONY: all clean runtest

runtest:
	for test in $(T_BUILD_DIR)/*.exe ; do \
        $$test ; \
    done

clean: gmatutil_clean propcovcpp_clean
	rm -rf $(T_BUILD_DIR)/*

-include $(DEPS)
-include $(EXE_DEPS)
-include $(T_DEPS)
