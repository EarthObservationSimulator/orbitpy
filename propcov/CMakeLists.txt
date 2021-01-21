cmake_minimum_required(VERSION 3.4...3.18)

project(propcov)

# Enforce C++ Standard. C++17 is preferred.
SET(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ Standard used for the build. C++17 is preferred")
SET_PROPERTY(CACHE CMAKE_CXX_STANDARD PROPERTY STRINGS 17 14 11)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_EXTENSIONS OFF)


# Generate Python module
add_subdirectory(lib/pybind11)
add_subdirectory(lib/gmatutil)




####################################################################################
pybind11_add_module(propcov src/Rvector_py.cpp)

# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
target_compile_definitions(propcov PRIVATE VERSION_INFO=${PROPCOV_VERSION_INFO})
