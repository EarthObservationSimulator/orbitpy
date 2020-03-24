DRIVER = orbitpropcov genCovGrid

# Define macros for locations
BASE_ROOT = ../../oc
LIB_DIR = $(BASE_ROOT)/lib
GMAT_LIB = $(LIB_DIR)/libgmat.a
GMAT_OC_LIB = $(LIB_DIR)/liboc.a
BIN_DIR = bin

EXECUTABLE = $(patsubst %,$(BIN_DIR)/%,$(DRIVER)) 


DRIVER_SRC = $(patsubst %,%.cpp,$(DRIVER))
DRIVER_OBJ = $(patsubst %,%.o,$(DRIVER))


# LIB need to compile the EXECUTABLE  
LIB     = -L$(LIB_DIR)
# How they are invoked on the compile  line
LIBS    = -loc -lgmat

OPTIMIZATIONS = -O3 -funroll-loops -Wall -g -std=gnu++11

# Define macros for the needed includes
HEADERS =   -I. \
-I$(BASE_ROOT)/src \
-I$(BASE_ROOT)/GMATsrc/base \
-I$(BASE_ROOT)/GMATsrc/include \
-I$(BASE_ROOT)/GMATsrc/util \
-I$(BASE_ROOT)/GMATsrc/util/interpolator \
-I$(BASE_ROOT)/GMATsrc/util/matrixoperations \
-I$(BASE_ROOT)/GMATsrc/console \
-I$(BASE_ROOT)/../orbitpy/oci/oci_util.h \

CPPFLAGS = $(HEADERS) $(OPTIMIZATIONS) $(TESTFLAGS) #TODO: Remove TESTFLAGS
CPP = g++

# Link specific flags
LINK_FLAGS = $(LIB) $(LIBS) 
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

$(EXECUTABLE): $(BIN_DIR)/% :%.o $(DRIVER_OBJ) $(GMAT_LIB) $(GMAT_OC_LIB)
	@if [ ! -x $(BIN_DIR) ]; then mkdir $(BIN_DIR); fi 
	$(CPP) $< $(LINK_FLAGS) -o $@
	@chmod -R 755 $(BIN_DIR)

# Object modules for library
$(DRIVER_OBJ):  %.o: %.cpp $(DRIVER_SRC)
	$(CPP) $(CPPFLAGS) -c $< -o $@

runtest: $(EXECUTABLE)
	@echo "Running test.."
	./$(EXECUTABLE)

clean:
	$(patsubst %,rm -f %,$(DRIVER_OBJ)) 
	$(patsubst %,rm -f %,$(EXECUTABLE)) 
	rm -f core


bare: clean
	rm -rf $(BIN_DIR)
	@find $(BASE_ROOT)/../orbitpy -name OClog.txt -delete
