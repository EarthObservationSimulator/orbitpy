DRIVER =  orbitpropcov_grid genCovGrid orbitpropcov_popts j2_analytical_propagator gp_in_fov_cov_calc pnt_axis_sphere_intsec_cov_calc pnt_opts_with_gp_in_fov_cov_calc sensor_fov_projector

# Define macros for locations
BASE_ROOT = .

GMATUTIL_DIR = $(BASE_ROOT)/../propcov/extern/gmatutil
PROPCOVCPP_DIR = $(BASE_ROOT)/../propcov/lib/propcov-cpp

GMATUTIL_LIB = $(GMATUTIL_DIR)/libgmatutil.a
PROPCOVCPP_LIB = $(PROPCOVCPP_DIR)/libpropcov.a
BIN_DIR = bin

EXECUTABLE = $(patsubst %,$(BIN_DIR)/%,$(DRIVER)) 


DRIVER_SRC = $(patsubst %,%.cpp,$(DRIVER))
DRIVER_OBJ = $(patsubst %,%.o,$(DRIVER))

OPTIMIZATIONS = -O3 -funroll-loops -Wall -g -std=gnu++17

# Define macros for the needed includes
HEADERS =   -I. \
-I$(PROPCOVCPP_DIR) \
-I$(GMATUTIL_DIR)/base \
-I$(GMATUTIL_DIR)/include \
-I$(GMATUTIL_DIR)/util \
-I$(GMATUTIL_DIR)/util/interpolator \
-I$(GMATUTIL_DIR)/util/matrixoperations \
-I$(BASE_ROOT) \

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

$(EXECUTABLE): $(BIN_DIR)/% :%.o $(DRIVER_OBJ) $(GMATUTIL_LIB) $(PROPCOVCPP_LIB)
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


bare: clean
	rm -rf $(BIN_DIR)
	@find $(BASE_ROOT)/../orbitpy -name OClog.txt -delete
