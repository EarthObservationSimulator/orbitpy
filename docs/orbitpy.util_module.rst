``orbitpy.util`` --- Util Module
===================================================

Description
^^^^^^^^^^^^^

This module is a collection of utility classes and functions used by the :code:`orbitpy` package.


``StateType``
^^^^^^^^^^^^^^

This is an enumeration class listing the allowed state types for representing the spacecrafts position and velocity. The allowed types
are the: ``KEPLERIAN_EARTH_CENTERED_INERTIAL``, ``CARTESIAN_EARTH_CENTERED_INERTIAL``, ``CARTESIAN_EARTH_FIXED``. The Cartesian representations
use the equatorial plane (not the ecliptic plane) as the XY plane. 

``DateType``
^^^^^^^^^^^^^^

This is an enumeration class listing the allowed date types. ``GREGORIAN_UTC`` refers to the date taken from the Gregorian calender
and the time scale as the Universal Coordinate Time (UTC). 
``JULIAN_DATE_UT1`` refers to the number of days elapsed on the Julian calender (with the fractional part included) 
and the time scale as Universal TIme (UT1).

``OrbitState``
^^^^^^^^^^^^^^^

This class is used to store and handle the orbit state (i.e. the date, position and velocity of satellite). The ``from_dict(.)`` and 
``to_dict(.)`` functions can be used to convert from/to python dictionary representations. The :class:`propcov.AbsoluteDate` and 
:class:`propcov.OrbitState` objects are used to maintain the date and state respectively. 
Note that :class:`propcov.OrbitState` and :class:`orbitpy.util.OrbitState` classes are different. 
The class also provides several staticmethods to convert date, orbit-state propcov-class representations to/from inbuilt python datatypes.

Examples
----------

.. code-block:: python

      from orbitpy.util import OrbitState
      import propcov

      # initialize orbit-state using Julian Date UT1 and Cartesian state coordinates
      x = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75}, 
                              "state":{"stateType": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": 6878.137, "y": 0, "z": 0, "vx": 0, "vy": 7.6126, "vz": 0},
                              "@id": 123})

      # Convert the OrbitState object to a python dict representation. Specify the state as Keplerian. 
      print(x.to_dict(state_type=StateType.KEPLERIAN_EARTH_CENTERED_INERTIAL))
      >> {'date': {'dateType': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 
          'state': {'stateType': 'KEPLERIAN_EARTH_CENTERED_INERTIAL', 'sma': 6878.122235888328, 'ecc': 2.1465323187573002e-06, 
                    'inc': 0.0, 'raan': 0.0, 'aop': 180.0, 'ta': 180.0}, '@id': 123}


      # initialize orbit-state using Gregorian UTC and Keplerian state coordinates
      x = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, 
                              "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25},
                              })

      # Get the propcov object representation of date from a python dictionary
      x = OrbitState.date_from_dict({"dateType":"JULIAN_DATE_UT1", "jd":2459270.75})
      print(x)
      >> AbsoluteDate.fromJulianDate(2459270.750000)
      
      # convert the propcov orbit-state object to a python dict
      x = OrbitState.state_to_dict(propcov.OrbitState.fromCartesianState(propcov.Rvector6([-5219.8,1473.95,4201.35,-3.86085,-5.99712,-2.69806])))
      >> {'stateType': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': -5219.8, 'y': 1473.95, 'z': 4201.35, 'vx': -3.86085, 'vy': -5.99712, 'vz': -2.69806}
      
``Orientation``
^^^^^^^^^^^^^^^^^^

This class is used to specify the orientation of an entity in an reference frame. It is imported from the InstruPy package. Please refer to the
documentation of the class :class:`instrupy.util.Orientation`.

``SpacecraftBus``
^^^^^^^^^^^^^^^^^^

This class is used to model the spacecraft-bus. An important attribute is the orientation of the bus, i.e. ``SpacecraftBus.orientation`` which specifies
the bus orientation with respect to a reference frame. By default the orientation is alignment to the nadir-pointing frame (see :class:`instrupy.util.ReferenceFrame`). 

Example
---------

.. code-block:: python

      from orbitpy.util import SpacecraftBus

      # initialize spacecraft bus at 10 deg rotation about x-axis, followed by 20 degree rotation about y-axis, of the Earth centered inertial frame. 
      sb = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, 
                                     "orientation":{"referenceFrame": "EARTH_CENTERED_INERTIAL", \
                                                    "convention": "XYZ","xRotation":10,"yRotation":20,"zRotation":0}, "@id":123}')


``Spacecraft``
^^^^^^^^^^^^^^^^^^

This class is used to model a spacecraft. The attributes of this class are the: name of the spacecraft, unique identifier, spacecraft-bus (:class:`orbitpy.util.SpacecraftBus`), 
orbit-state (:class:`orbitpy.util.OrbitState`) and a **list** of instruments (:class:`instrupy.base.Instrument`).

*An unique identifier is assigned to the ``Spacecraft`` object if the user doe not provide one.*

Example
---------

.. code-block:: python

      from orbitpy.util import Spacecraft

      # Initialize spacecraft with 1 instrument. By default without a SpacecraftBus specification, a bus aligned to the nadir-pointing frame is assigned.
      spc1 = Spacecraft.from_json('{"@id": "sp1", "name": "Mars", \
                                    "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                          "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                          "pointingOption": [{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":2.5, "zRotation":0}, \
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-2.5, "zRotation":0}  \
                                                            ], \
                                          "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                   "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                   } \
                                       }')
      # initialize spacecraft with multiple, heterogenous instruments
      spc2 = Spacecraft.from_dict({ "name": "Saturn",
                              "instrument": [
                                 {   "name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12,
                                    "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"},
                                    "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 },
                                    "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                                    "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"
                                 },
                                 {"@type": "Passive Optical Scanner", "name": "FireSat", "mass": 28, "volume": 0.12,"power": 32,
                                 "fieldOfViewGeometry": {"shape": "RECTanGULAR", "angleHeight": 0.628, "angleWidth": 115.8 },
                                 "scanTechnique": "WhiskBROOM", "orientation": { "referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_loOK", "sideLookAngle": 0},
                                 "dataRate": 85, "numberDetectorRows": 256, "numberDetectorCols": 1, "detectorWidth": 30e-6, "focalLength": 0.7,
                                 "operatingWavelength": 4.2e-6, "bandwidth": 1.9e-6, "quantumEff": 0.5, "targetBlackBodyTemp": 290,
                                 "bitsPerPixel": 8, "opticsSysEff": 0.75, "numOfReadOutE": 25, "apertureDia": 0.26, "Fnum": 2.7, "atmosLossModel": "LOWTRAN7"
                                 }],
                              "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0},
                                          "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}
                                          }
                              }             
                           )

``GroundStation``
^^^^^^^^^^^^^^^^^^

This class is used to store and handle ground-station attributes: name, unique-identifier, position (geocentric lat/lon coords and altitude) and minimum elevation angle at
which communication from satellite can take place. 

*An unique identifier is assigned to the ``GroundStation`` object if the user does not provide one.*

Example
---------

.. code-block:: python

      from orbitpy.util import GroundStation

      gs = GroundStation.from_dict({"name": "Atl", "latitude": -88, "longitude": 25, "minimumElevation":12 })
      print(gs)

      # note a unique random identifier is assigned
      >> GroundStation.from_dict({'name': 'Atl', 'latitude': -88.0, 'longitude': 25.0, 'altitude': 0.0, 'minimumElevation': 12.0, 
                                  '@id': UUID('bd96e327-36e5-4ffb-8da6-864322621e21')})


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.util.StateType
   orbitpy.util.DateType
   orbitpy.util.OrbitState
   orbitpy.util.SpacecraftBus
   orbitpy.util.Spacecraft
   orbitpy.util.GroundStation

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.util.helper_extract_spacecraft_params
   orbitpy.util.extract_auxillary_info_from_state_file
   orbitpy.util.dictionary_list_to_object_list
   orbitpy.util.object_list_to_dictionary_list
   orbitpy.util.initialize_object_list
