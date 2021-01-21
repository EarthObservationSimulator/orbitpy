cmake_minimum_required(VERSION 2.8.12)

SET(TargetName gmatutil)

# ====================================================================
# list of directories containing source/header files
SET(SRC_DIRS
  include
  base
  util  
  util/interpolator
  util/matrixoperations
  )

# ====================================================================
# source files
SET(SRCS
    util/Rvector.cpp
)

# ====================================================================
# Recursively find all include files, which will be added to IDE-based
# projects (VS, XCode, etc.)
FILE(GLOB_RECURSE SRC_HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.hpp)


# ====================================================================
# add the install targets

# Create GmatUtil as a shared library
ADD_LIBRARY(${TargetName} SHARED ${SRCS} ${SRC_HEADERS})
#SET_TARGET_PROPERTIES(${TargetName} PROPERTIES LINKER_LANGUAGE CXX)

# Add necessary include directories
TARGET_INCLUDE_DIRECTORIES(${TargetName} PUBLIC ${SRC_DIRS})

# Library name should start with "lib"
# This is always true for Mac/Linux, but needs to be specified for Windows
SET_TARGET_PROPERTIES(${TargetName} PROPERTIES PREFIX "lib")

