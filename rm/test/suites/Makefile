AREA = $(BIN_DIR)/Test_AreaOfInterest
GRIDSIZE = $(BIN_DIR)/Test_GridSize



# Define macros for locations
THIRD_PARTY_DIR = ../../../../third-party-tools
BASE_ROOT       = ..
BOOST_ROOT      = $(THIRD_PARTY_DIR)/boost_1_63_0
BOOST_LIB_DIR   = $(BOOST_ROOT)/libs
BIN_DIR         = $(BASE_ROOT)/bin
RM_DIR          = ../../
OC_DIR          = ../../../oc
OC_LIB_DIR      = $(OC_DIR)/lib
OC_GMAT_DIR     = $(OC_DIR)/GMATsrc
OC_SRC_DIR      = $(OC_DIR)/src
GMAT_LIB        = $(OC_LIB_DIR)/libgmat.a
GMAT_OC_LIB     = $(OC_LIB_DIR)/liboc.a






# Define macros for the needed includes
HEADERS = -I. \
-I$(RM_DIR)/include \
-I$(OC_SRC_DIR) \
-I$(BOOST_ROOT)/boost/test/included \
-I$(BOOST_ROOT) \
-I$(OC_GMAT_DIR)/base \
-I$(OC_GMAT_DIR)/include \
-I$(OC_GMAT_DIR)/util \
-I$(OC_GMAT_DIR)/util/interpolator \
-I$(OC_GMAT_DIR)/util/matrixoperations \
-I$(OC_GMAT_DIR)/console \
-I$(THIRD_PARTY_DIR) \




# -I$(BOOST_ROOT)/boost/test/included \
# -I$(BOOST_ROOT) \


CPPFLAGS = $(HEADERS) -Wall -g -std=gnu++11
CPP=g++


# LIBs need to compile
LIB     = -L$(OC_LIB_DIR) -L$(BOOST_ROOT)
# How they are invoked on the compile  line
LIBS    = -loc -lgmat

# Link specific flags
LINK_FLAGS = $(LIB) $(LIBS)
ifeq ($(shell uname -s), Darwin)
    LINK_FLAGS +=  /usr/lib/libstdc++.6.dylib \
                   -headerpad_max_install_names \
                   -lm -v
endif




AREA_OBJS = \
	Test_AreaOfInterest.o \
	$(RM_DIR)/src/jsoncpp.o \
	$(RM_DIR)/src/AreaOfInterest.o


GRID_OBJS = \
	Test_GridSize.o \
	$(RM_DIR)/src/jsoncpp.o \
	$(RM_DIR)/src/GridSize.o


#
# Default suffix rule
.SUFFIXES:
.SUFFIXES: .o .cpp
#


%.o: %.cpp
	$(CPP) $(CPPFLAGS) -c $< -o $@


# Target Definitions - GridSize
grid: $(GRIDSIZE)
	$(GRIDSIZE)

$(GRIDSIZE): $(GRID_OBJS)
	@if [ ! -x $(BIN_DIR) ]; then mkdir $(BIN_DIR); fi
	cd $(OC_DIR); make all;
	$(CPP) -Wall -g  -o $(GRIDSIZE) $(GRID_OBJS) $(LINK_FLAGS)



# Target Definitions - AreaOfInterest
area: $(AREA)
	$(AREA)

$(AREA): $(AREA_OBJS)
	@if [ ! -x $(BIN_DIR) ]; then mkdir $(BIN_DIR); fi
	$(CPP) -Wall -g  -o $(AREA) $(AREA_OBJS) $(LINK_FLAGS)

clean:
	rm -f $(AREA_OBJS) core
	rm -f $(GRID_OBJS) core



