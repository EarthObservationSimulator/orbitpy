# $Id$
# 
# GMAT: General Mission Analysis Tool.
# 
# CMAKE script file for GMAT Util library
# 
#
# Author: Darrel J. Conway
#  
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING!
#

#################### Modifications from the original file from the Gmat2020a repository. ########################################
# 
# Romved all the content from and including the following comment onwards "Add source/header files to IDE-based project source groups".
# 
# Modified to include 'gmatutil/base' folder (containing `ExponentialAtmosphere.hpp` and `ExponentialAtmosphere.cpp`). 
#
# Addition of 'gmatdefs.cpp' file in the 'gmatutil/include' folder.
# 
# removed 'util/datawriter' folder in list of directories containing the source/header files, and the list of source files.
#
# Modified from building shared to static library with flags POSITION_INDEPENDENT_CODE ON.
# 
###########################################################################################################################################

MESSAGE("==============================")
MESSAGE("GmatUtil setup " ${VERSION}) 

SET(TargetName GmatUtil)

# Add preprocessor definitions
ADD_DEFINITIONS("-D_DYNAMICLINK")
ADD_DEFINITIONS("-DEXP_STL")

# ====================================================================
# list of directories containing source/header files
SET(GMATUTIL_DIRS
  include
  util
  util/interpolator
  util/matrixoperations
  base
  )

# ====================================================================
# source files
SET(GMATUTIL_SRCS
    util/A1Date.cpp
    util/A1Mjd.cpp
    util/AngleUtil.cpp
    util/AttitudeConversionUtility.cpp
    util/AttitudeUtil.cpp
    util/BaseException.cpp
    util/BodyFixedStateConverter.cpp
    util/CalculationUtilities.cpp
    util/CCSDSAEMEulerAngleSegment.cpp
    util/CCSDSAEMQuaternionSegment.cpp
    util/CCSDSAEMReader.cpp
    util/CCSDSAEMSegment.cpp
    util/CCSDSEMReader.cpp
    util/CCSDSEMSegment.cpp
    util/CCSDSEMWriter.cpp
    util/CCSDSOEMSegment.cpp
    util/CCSDSOEMWriter.cpp
    util/Code500EphemerisFile.cpp
    util/ColorDatabase.cpp
    util/CubicSpline.cpp
    util/Date.cpp
    util/DateUtil.cpp
    util/ElapsedTime.cpp
    util/Ephemeris.cpp
    util/EopFile.cpp
    util/FileManager.cpp
    util/FileUtil.cpp
    util/GmatGlobal.cpp
    util/GmatTime.cpp
    util/GravityFileUtil.cpp
    util/GregorianDate.cpp
    util/IFileUpdater.cpp
    util/LeapSecsFileReader.cpp
    util/Linear.cpp
    util/MemoryTracker.cpp
    util/MessageInterface.cpp
    util/MessageReceiver.cpp
    util/NumericJacobian.cpp
    util/NPlateHistoryFileReader.cpp
    util/RandomNumber.cpp
    util/RealUtilities.cpp
    util/RgbColor.cpp
    util/Rmatrix33.cpp
    util/Rmatrix66.cpp
    util/Rmatrix.cpp
    util/Rvector3.cpp
    util/Rvector6.cpp
    util/Rvector.cpp
    util/SPADFileReader.cpp
    util/StateConversionUtil.cpp
    util/STKEphemerisFile.cpp
    util/StringTokenizer.cpp
    util/StringUtil.cpp
    util/TextParser.cpp
    util/TimeSystemConverter.cpp
    util/TimeTypes.cpp
    util/UtcDate.cpp
    util/interpolator/InterpolatorException.cpp
    util/interpolator/Interpolator.cpp
    util/interpolator/BrentDekkerZero.cpp
    util/interpolator/CubicSplineInterpolator.cpp
    util/interpolator/HermiteInterpolator.cpp
    util/interpolator/LinearInterpolator.cpp
    util/interpolator/NotAKnotInterpolator.cpp
    util/interpolator/LagrangeInterpolator.cpp
    util/matrixoperations/CholeskyFactorization.cpp
    util/matrixoperations/LUFactorization.cpp
    util/matrixoperations/MatrixFactorization.cpp
    util/matrixoperations/QRFactorization.cpp
    util/matrixoperations/SchurFactorization.cpp
    util/Frozen.cpp
    util/OrbitDesignerTime.cpp
    util/RepeatSunSync.cpp
    util/RepeatGroundTrack.cpp
    util/SunSync.cpp
    base/ExponentialAtmosphere.cpp
)

# ====================================================================
# Recursively find all include files, which will be added to IDE-based
# projects (VS, XCode, etc.)
FILE(GLOB_RECURSE GMATUTIL_HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.hpp)

# ====================================================================
# add the install targets

# Create GmatUtil as a static library
ADD_LIBRARY(${TargetName} STATIC ${GMATUTIL_SRCS} ${GMATUTIL_HEADERS})
SET_TARGET_PROPERTIES(${TargetName} PROPERTIES DEFINE_SYMBOL "GMATUTIL_EXPORTS" POSITION_INDEPENDENT_CODE ON)

# Add necessary include directories
TARGET_INCLUDE_DIRECTORIES(${TargetName} PUBLIC ${GMATUTIL_DIRS})
IF(GMAT_USE_BOOST_VARIANT)
  TARGET_INCLUDE_DIRECTORIES(${TargetName} PUBLIC ${Boost_INCLUDE_DIR})
ENDIF()

# Library name should start with "lib"
# This is always true for Mac/Linux, but needs to be specified for Windows
SET_TARGET_PROPERTIES(${TargetName} PROPERTIES PREFIX "lib")

