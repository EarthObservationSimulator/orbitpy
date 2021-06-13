# Scripts
EXE_DIR := ./exe
MAIN_DIR := ./src/main

# Source Code
BUILD_DIR := ./build
SRC_DIR := ./src

# Tests
T_BUILD_DIR := ./tests/build
T_SRC_DIR := ./tests/new

# External
GMATUTIL_DIR = ../propcov/extern/gmatutil
INCLUDE_DIR = ../propcov/lib/propcov-cpp

SRCS := $(wildcard $(SRC_DIR)/*.cpp)
OBJS := $(SRCS:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
DEPS := $(OBJS:.o=.d)

EXE_SRCS := $(wildcard $(MAIN_DIR)/*.cpp)
EXE_OBJS := $(EXE_SRCS:$(MAIN_DIR)/%.cpp=$(EXE_DIR)/%.o)
EXE_DEPS = $(EXE_OBJS:.o=.d)
EXES = $(EXE_OBJS:.o=.exe)

T_SRCS := $(wildcard $(T_SRC_DIR)/*.cpp)
T_OBJS := $(T_SRCS:$(T_SRC_DIR)/%.cpp=$(T_BUILD_DIR)/%.o)
T_DEPS := $(T_OBJS:.o=.d)
T_EXES = $(T_OBJS:.o=.exe)

# External GMAT dependencies
OBJS2 := $(GMATUTIL_DIR)/base/*.o \
$(GMATUTIL_DIR)/util/*.o \
$(GMATUTIL_DIR)/util/interpolator/*.o \
$(GMATUTIL_DIR)/util/matrixoperations/*.o \
$(INCLUDE_DIR)/*.o

# Define macros for the needed includes
HEADERS =  -I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/util/matrixoperations \
-I$(INCLUDE_DIR) \
-I./src

CPPFLAGS = $(HEADERS) -MMD -MP -std=c++17
LDFLAGS = -std=c++17
TESTFLAGS = -lpthread -lgtest
CXX = g++

all: $(OBJS) $(EXE_OBJS) $(EXES) $(T_OBJS) $(T_EXES)

# Link step for C++ scripts
$(EXES): $(EXE_DIR)/%.exe : $(EXE_DIR)/%.o $(OBJS)
	$(CXX) $(OBJS) $(OBJS2) $< -o $@

# Link step for C++ tests
$(T_EXES): $(T_BUILD_DIR)/%.exe : $(T_BUILD_DIR)/%.o $(OBJS)
	$(CXX) $(OBJS) $(OBJS2) $< -o $@ $(TESTFLAGS)

# Build step for C++ source
$(OBJS) : $(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CPPFLAGS) -c $< -o $@

# Build step for C++ scripts
$(EXE_OBJS): $(EXE_DIR)/%.o: $(MAIN_DIR)/%.cpp
	$(CXX) $(CPPFLAGS) -c $< -o $@

# Build step for C++ tests source
$(T_OBJS): $(T_BUILD_DIR)/%.o: $(T_SRC_DIR)/%.cpp
	$(CXX) $(CPPFLAGS) -c $< -o $@

.PHONY: all clean runtest

runtest:
	for test in $(T_BUILD_DIR)/*.exe ; do \
        $$test ; \
    done

clean:
	rm -rf $(BUILD_DIR)/*
	rm -rf $(EXE_DIR)/*
	rm -rf $(T_BUILD_DIR)/*

-include $(DEPS)
-include $(EXE_DEPS)
-include $(T_DEPS)