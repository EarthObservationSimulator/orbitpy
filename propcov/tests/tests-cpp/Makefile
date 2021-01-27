DRIVER = SystemTest_Analysis

# Define macros for locations
BASE_ROOT = ../..

GMATUTIL_DIR = $(BASE_ROOT)/extern/gmatutil
PROPCOVCPP_DIR = $(BASE_ROOT)/lib/propcov-cpp

GMATUTIL_LIB = $(GMATUTIL_DIR)/libgmatutil.a
PROPCOVCPP_LIB = $(PROPCOVCPP_DIR)/libpropcov.a

BIN_DIR = bin

EXECUTABLE = $(BIN_DIR)/$(DRIVER)

DRIVER_SRC = $(DRIVER).cpp
DRIVER_OBJ = $(DRIVER).o

# How they are invoked on the compile  line
LIBS    = -lpropcov -lgmatutil

OPTIMIZATIONS = -O3 -funroll-loops -Wall -g -std=gnu++17

# Define macros for the needed includes
HEADERS =   -I. \
-I$(PROPCOVCPP_DIR) \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/console

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) $(TESTFLAGS) #TODO: Remove TESTFLAGS
CPP = g++

# Link specific flags
LINK_FLAGS = -L$(PROPCOVCPP_DIR) -L$(GMATUTIL_DIR) -lpropcov -lgmatutil
ifeq ($(shell uname -s), Darwin)
    LINK_FLAGS += /usr/lib/libstdc++.6.dylib \
                -headerpad_max_install_names \
                -lm -v 
endif
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

$(EXECUTABLE): $(DRIVER_OBJ) $(GMATUTIL_LIB) $(PROPCOVCPP_LIB)
	@if [ ! -x $(BIN_DIR) ]; then mkdir $(BIN_DIR); fi 
	$(CPP) $< $(LINK_FLAGS) -o $@
	@chmod -R 755 $(BIN_DIR)

# Object modules for library
$(DRIVER_OBJ):  $(DRIVER_SRC)
	$(CPP) $(CPPFLAGS) -c $< -o $@

runtest: $(EXECUTABLE)
	@echo "Running test.."
	./$(EXECUTABLE)

clean:
	rm -f $(DRIVER_OBJ) core

bare: clean
	rm -rf $(EXECUTABLE) $(BIN_DIR)
	@find $(BASE_ROOT) -name GmatLog.txt -delete
