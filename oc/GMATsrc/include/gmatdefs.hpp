#ifndef GMATDEFS_HPP
#define GMATDEFS_HPP


#include <string>               // For std::string
#include <cstring>              // Resolves issues for GCC 4.3
#include <vector>               // For std::vector
#include <map>                  // For std::map
#include <stack>                // for std::stack
#include <list>                 // To fix VS DLL import/export issues

#include "utildefs.hpp"

#ifndef GMAT_API
   #define GMAT_API
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

/// Forward reference to the event handler class used to plug in GUI components
class GmatEventHandler;

typedef struct geoparms
{
   Real xtemp;  /// minimum global exospheric temperature (degrees K)
   Real tkp;    /// geomagnetic index

} GEOPARMS;

/// GMAT's epoch representation; eventually a struct holding MJ day & sec of day
typedef Real GmatEpoch;


// GMAT's Radians representation
typedef Real Radians;

// Macros defining default NULL behavior for RenameRefObject and HasLocalClones
#define DEFAULT_TO_NO_CLONES virtual bool HasLocalClones() { return false; }
#define DEFAULT_TO_NO_REFOBJECTS virtual bool RenameRefObject( \
      const UnsignedInt type, const std::string &oldName, \
      const std::string &newName) { return true; }


namespace Gmat
{
   /**
    * The list of object types
    *
    * This list needs to be synchronized with the GmatBase::OBJECT_TYPE_STRING
    * list found in base/Foundation/GmatBase.cpp
    */
   enum ObjectType
   {
      SPACECRAFT= 101,
      FORMATION,
      SPACEOBJECT,
      GROUND_STATION,
      BURN,
      
      IMPULSIVE_BURN,
      FINITE_BURN,
      COMMAND,
      PROPAGATOR,
      ODE_MODEL,
      
      PHYSICAL_MODEL,
      TRANSIENT_FORCE,
      INTERPOLATOR,
      SOLAR_SYSTEM,
      SPACE_POINT,
      
      CELESTIAL_BODY,
      CALCULATED_POINT,
      LIBRATION_POINT,
      BARYCENTER,
      ATMOSPHERE,
      
      PARAMETER,
      VARIABLE,
      ARRAY,
      STRING,
      STOP_CONDITION,
      
      SOLVER,
      SUBSCRIBER,
      REPORT_FILE,
      XY_PLOT,
      ORBIT_VIEW,
      DYNAMIC_DATA_DISPLAY,
      
      EPHEMERIS_FILE,
      PROP_SETUP,
      FUNCTION,
      FUEL_TANK,
      THRUSTER,
      
      CHEMICAL_THRUSTER,
      ELECTRIC_THRUSTER,
      CHEMICAL_FUEL_TANK,
      ELECTRIC_FUEL_TANK,

      POWER_SYSTEM,        // for PowerSystems
      SOLAR_POWER_SYSTEM,
      NUCLEAR_POWER_SYSTEM,

      HARDWARE,            // Tanks, Thrusters, Antennae, Sensors, etc.
      COORDINATE_SYSTEM,
      AXIS_SYSTEM,
      ATTITUDE,
      MATH_NODE,
      
      MATH_TREE,
      BODY_FIXED_POINT,
      EVENT,
      EVENT_LOCATOR,
      DATAINTERFACE_SOURCE,

      // Estimation types
      MEASUREMENT_MODEL,   // May be replaced by TrackingSystem
//      CORE_MEASUREMENT,    // For the measurement primitives
      ERROR_MODEL,         // Error model used in a measurement
      
//      TRACKING_DATA,
//      TRACKING_SYSTEM,
      DATASTREAM,          // For DataFile container objects      
      DATA_FILE,           // For DataFile objects
      OBTYPE,              // For the specific observation types

      // Data filters
      DATA_FILTER,         // for data filter
      
      INTERFACE,           // MatlabInterface and other Interfaces
      MEDIA_CORRECTION,    // For media correction model
      SENSOR,              // For RFHardwares and Antennas
      RF_HARDWARE,
      ANTENNA,
      
      USER_DEFINED_OBJECT, // Used for user defined objects that do not fall
                           // into any of the above categories, and for 
                           // internal objects that users don't access
      
      USER_OBJECT_ID_NEEDED = USER_DEFINED_OBJECT + 500,

      /// @todo: DJC - Do we need this for backwards compatibility?
      GENERIC_OBJECT,      // Used for user defined objects that do not fall 
                           // into any of the above categories, and for 
                           // internal objects that users don't access
      

      UNKNOWN_OBJECT
   };


   enum WriteMode
   {
      SCRIPTING,
      SHOW_SCRIPT,
      OWNED_OBJECT,
      MATLAB_STRUCT,
      EPHEM_HEADER,
      NO_COMMENTS,
      GUI_EDITOR,
      OBJECT_EXPORT
   };
   
   enum StateElementId 
   {
      UNKNOWN_STATE = -1,
      CARTESIAN_STATE = 3700,          // Integrable state representations
      EQUINOCTIAL_STATE,
      ORBIT_STATE_TRANSITION_MATRIX,   // STM for the orbit
      ORBIT_A_MATRIX,
      MASS_FLOW,                       // m dot
      PREDEFINED_STATE_MAX,
      USER_DEFINED_BEGIN = 3800,
      USER_DEFINED_END = 3999          // Allow up to 200 dynamic entries
   };

   typedef struct PluginResource
   {
      PluginResource()
      {
         trigger = -1;
         firstId = -1;
         lastId  = -1;
         handler = NULL;
      }
      std::string  nodeName;         // Identifier for the resource
      std::string  parentNodeName;   // Owning type identifier, if any
      ObjectType   type;             // Core type
      std::string  subtype;          // Subtype off of the core

      // GUI plugin elements; ignore if not needed
      std::string  toolkit;          // Toolkit used to create the widget
      std::string  widgetType;       // String identifying the widget to open
      Integer      trigger;          // Event ID/type triggering the call
      Integer      firstId;          // Starting ID for event handling
      Integer      lastId;           // Ending ID for event handling

      // Hook that provides the toolkit specific functions for GUI interfaces
      GmatEventHandler *handler;
   } PLUGIN_RESOURCE;

}


#endif //GMATDEFS_HPP
