cmake_minimum_required(VERSION 3.4...3.18)

# THIS HAS TO COME BEFORE THE PROJECT LINE
set(CMAKE_C_COMPILER "gcc-11")
set(CMAKE_CXX_COMPILER "g++-11")
# THIS HAS TO COME BEFORE THE PROJECT LINE

project(propcov)

# Enforce C++ Standard. C++17 is preferred.
SET(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ Standard used for the build. C++17 is preferred")
SET_PROPERTY(CACHE CMAKE_CXX_STANDARD PROPERTY STRINGS 17 14 11)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_EXTENSIONS OFF)


# ====================================================================
add_subdirectory(extern/pybind11)
add_subdirectory(extern/gmatutil)
add_subdirectory(lib/propcov-cpp)

include_directories(BEFORE extern/gmatutil/include/ extern/gmatutil/util/interpolator extern/gmatutil/util/matrixoperations lib/propcov-cpp lib/propcov-cpp/polygon)

pybind11_add_module(propcov MODULE src/main.cpp)

target_link_libraries(propcov PUBLIC GmatUtil PropCovCpp)


################ Perhaps below code is requried for APPLE. TODO: Verify and remove if not needed #############################
if(UNIX AND NOT APPLE)
    set_target_properties(propcov PROPERTIES INSTALL_RPATH "$ORIGIN/relative/path/to/supporting/library_dir")
elseif(APPLE)
    set_target_properties(propcov PROPERTIES INSTALL_RPATH "@loader_path/relative/path/to/supporting/library_dir")
endif()

set_target_properties(propcov PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)
############################################################################################################################

################################  COMMENTS ################################
# target_link_libraries(propcov PRIVATE pybind11::module GmatUtil)