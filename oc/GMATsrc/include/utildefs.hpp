#ifndef UTILDEFS_HPP
#define UTILDEFS_HPP


#include <string>               // For std::string
#include <cstring>              // Resolves issues for GCC 4.3
#include <vector>               // For std::vector
#include <map>                  // For std::map
#include <stack>                // for std::stack
#include <list>                 // To fix VS DLL import/export issues

#ifndef GMATUTIL_API
   #define GMATUTIL_API
#endif


typedef double          Real;              // 8 byte float
typedef int             Integer;           // 4 byte signed integer
typedef unsigned char   Byte;              // 1 byte
typedef unsigned int    UnsignedInt;       // 4 byte unsigned integer

typedef std::vector<Real>        RealArray;
typedef std::vector<Integer>     IntegerArray;
typedef std::vector<UnsignedInt> UnsignedIntArray;
typedef std::vector<std::string> StringArray;
typedef std::vector<bool>        BooleanArray;

class GmatBase;        // Forward reference for ObjectArray
class ElementWrapper;  // Forward reference for ElementWrapper
class A1Mjd;           // Forward reference for A1Mjd (epoch)
class Rvector6;        // Forward reference for Rvector6 (ephem state)

typedef std::vector<GmatBase*>                 ObjectArray;
typedef std::vector<ElementWrapper*>           WrapperArray;
typedef std::vector<Rvector6*>                 StateArray;
typedef std::vector<A1Mjd*>                    EpochArray;
typedef std::map<std::string, Integer>         IntegerMap;
typedef std::map<std::string, UnsignedInt>     ColorMap;
typedef std::map<std::string, GmatBase*>       ObjectMap;
typedef std::map<std::string, ElementWrapper*> WrapperMap;
typedef std::stack<ObjectMap*>                 ObjectMapStack;

/// GMAT's epoch representation; eventually a struct holding MJ day & sec of day
typedef Real GmatEpoch;


/// GMAT's Radians representation
typedef Real Radians;


namespace Gmat
{
   /**
    * The list of data types
    *
    * This list needs to be synchronized with the GmatBase::PARAM_TYPE_STRING
    * list found in base/Foundation/GmatBase.cpp
    */
   enum ParameterType
   {
      INTEGER_TYPE,
      UNSIGNED_INT_TYPE,
      UNSIGNED_INTARRAY_TYPE,
      INTARRAY_TYPE,
      REAL_TYPE,
      REAL_ELEMENT_TYPE,
      STRING_TYPE,
      STRINGARRAY_TYPE,
      BOOLEAN_TYPE,
      BOOLEANARRAY_TYPE,
      RVECTOR_TYPE,
      RMATRIX_TYPE,
      TIME_TYPE,
      OBJECT_TYPE,
      OBJECTARRAY_TYPE,
      ON_OFF_TYPE,
      ENUMERATION_TYPE,
      FILENAME_TYPE,
      COLOR_TYPE,
      GMATTIME_TYPE,
      TypeCount,
      UNKNOWN_PARAMETER_TYPE = -1,
      PARAMETER_REMOVED = -3,   // For parameters will be removed in the future
   };

   enum MessageType
   {
      ERROR_ = 10, //loj: cannot have ERROR
      WARNING_,
      INFO_,
      DEBUG_,
      GENERAL_    // Default type for exceptions
   };

   enum RunState
   {
      IDLE = 10000,
      RUNNING,
      PAUSED,
      TARGETING,
      OPTIMIZING,
      ESTIMATING,
      SOLVING,
      SOLVEDPASS,
      WAITING
   };

   enum WrapperDataType
   {
      NUMBER_WT,          // Real, Integer
      MATRIX_WT,          // Rmatrix
      STRING_WT,          // a raw text string
      STRING_OBJECT_WT,   // name of a String Object
      OBJECT_PROPERTY_WT,
      VARIABLE_WT,
      ARRAY_WT,
      ARRAY_ELEMENT_WT,
      PARAMETER_WT,
      OBJECT_WT,
      BOOLEAN_WT,
      INTEGER_WT,
      ON_OFF_WT,
      UNKNOWN_WRAPPER_TYPE = -2
   };

}

typedef std::vector<UnsignedInt>           ObjectTypeArray;
typedef std::vector<Gmat::WrapperDataType> WrapperTypeArray;
typedef std::map<std::string, UnsignedInt> ObjectTypeMap;
typedef std::map<UnsignedInt, StringArray> ObjectTypeArrayMap;

#endif //UTILDEFS_HPP
