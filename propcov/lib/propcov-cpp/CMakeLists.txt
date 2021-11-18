MESSAGE("==============================")
MESSAGE("propcov-cpp setup " ${VERSION}) 

SET(TargetName PropCovCpp)

# Add preprocessor definitions
ADD_DEFINITIONS("-D_DYNAMICLINK")
ADD_DEFINITIONS("-DEXP_STL")

# list of directories containing source/header files
SET(PROPCOVCPP_DIRS
  polygon
  )

# ====================================================================
# source files
SET(PROPCOVCPP_SRCS
    AbsoluteDate.cpp
    Attitude.cpp
    ConicalSensor.cpp
    CoverageChecker.cpp
    CustomSensor.cpp
    Earth.cpp
    IntervalEventReport.cpp
    KeyValueStatistics.cpp
    LinearAlgebra.cpp
    NadirPointingAttitude.cpp
    OrbitState.cpp
    PointGroup.cpp
    Propagator.cpp
    RectangularSensor.cpp
    Sensor.cpp
    Spacecraft.cpp
    TATCException.cpp
    VisibilityReport.cpp
    VisiblePOIReport.cpp
    Projector.cpp
    DiscretizedSensor.cpp
    polygon/GMATPolygon.cpp
    polygon/PointInPolygon.cpp
    polygon/Polygon.cpp
    polygon/Preprocessor.cpp
    polygon/SliceArray.cpp
    polygon/SlicedPolygon.cpp
    polygon/SliceTree.cpp
    polygon/SphericalSensor.cpp
    testclass.cpp
       
)

# Recursively find all include files
FILE(GLOB_RECURSE PROPCOVCPP_HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.hpp)

# Create as a static library
ADD_LIBRARY(${TargetName} STATIC ${PROPCOVCPP_SRCS} ${PROPCOVCPP_HEADERS})
target_link_libraries(${TargetName} PUBLIC GmatUtil)
SET_TARGET_PROPERTIES(${TargetName} PROPERTIES DEFINE_SYMBOL "PROPCOVCPP_EXPORTS" POSITION_INDEPENDENT_CODE ON)
TARGET_INCLUDE_DIRECTORIES(${TargetName} PUBLIC ${Boost_INCLUDE_DIR} ${GMATUTIL_DIRS} ${PROPCOVCPP_DIRS})

# Library name should start with "lib"
# This is always true for Mac/Linux, but needs to be specified for Windows
SET_TARGET_PROPERTIES(${TargetName} PROPERTIES PREFIX "lib")

