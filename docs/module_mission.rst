.. _mission_module:

``orbit.mission`` --- Mission Module
================================================

Description
^^^^^^^^^^^^^

The ``Mission`` object can be used to read in a *mission specifications* json string/ python dict and run all possible OrbitPy functionalities on it.
Each of the acceptable json objects in the mission specifications is described below:

.. csv-table:: Mission specifications description 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   epoch, :ref:`date_json_object`, , Mission epoch (date).
   duration, float, days, Length of mission in days. Eg: :code:`0.25`.
   constellation, :ref:`constellation_json_object`, ,Constellation specifications.
   instrument, "list, *instrument* json object", ,Instrument specifications (please refer :code:`InstruPy` documentation). A list of instruments can be specified.
   spacecraft, "list, :ref:`spacecraft_json_object`", , Spacecraft specifications. A list of spacecrafts can be specified.
   groundStation, "list, :ref:`groundstation_json_object`", , Ground station specifications. A list of ground-stations can be specified.
   grid, "list, :ref:`grid_json_object`", ,Coverage grid specifications. A list of grids can be specified.
   propagator, :ref:`propagator_json_object`, ,Propagator specifications.
   settings, :ref:`settings_json_object`, , General settings.

.. note:: In case of *GRID COVERAGE* calculation, the field-of-regard is used (FOR = sceneFOV if unspecified, and sceneFOV = instrument FOV if unspecified). 

.. note:: *Either* of the ``constellation``, ``instrument`` json objects or the ``spacecraft`` json object should be provided in the mission specifications. Both should not be specified.

.. note:: The valid key/value pairs in building the mission specifications json/ dict is identical to the key/value pairs expected in the obtaining
         the corresponding OrbitPy objects using the ``from_dict`` or ``from_json`` function. E.g. the key/value pair expected for the :ref:`groundstation_json_object` is the same
         as the key/value pairs expected in obtaining a :class:`orbitpy.util.GroundStation` object using the :class:`orbitpy.util.GroundStation.from_dict` function.

.. note:: In case of coverage calculations for the case of sensor FOVs described by spherical-polygon vertices (including Rectangular FOV) the default ``DirectSphericalPIP`` method is used.

.. _date_json_object:

``date`` json object
-----------------------

The ``date`` json object is used to specify a date which can be used for the purpose of defining the mission epoch or the ``date`` field in the orbit-state definitions, etc.
The date type can be either ``GREGORIAN_UTC`` or ``JULIAN_DATE_UT1``.

1. ``GREGORIAN_UTC`` date-type

   .. csv-table:: 
      :header: Parameter, Data type, Units, Description
      :widths: 10,10,5,40

      year, int, year, Year
      month, int, month, Month
      day, int, day, Day
      hour, int, hour, Hour
      minute, int, minute, Minutes
      second, float, second, Seconds
      
2. ``JULIAN_DATE_UT1`` date-type

   .. csv-table:: 
      :header: Parameter, Data type, Units, Description
      :widths: 10,10,5,40

      jd, float, decimal data, Julian date UT1

**Example**

.. code-block:: javascript
   
   "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, 
                                        "hour":6, "minute":0, "second":0}

   'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}  


.. _constellation_json_object:

``constellation`` json object
------------------------------

This json object is used to define constellation parameters. An in-built constellation type is the Walker-Delta constellation (as defined in SMAD 3rd edition, Section 7.6) whose 
accepted key/value pairs are described below:

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   date,:ref:`date_json_object`, , Date at which the constellation specifications are defined.
   numberSatellites, int, , Total number of satellites in the constellation.
   numberPlanes, int, , Number of orbital planes.
   relativeSpacing, int,, Factor controlling the spacing between the satellites in the different planes (See SMAD 3rd ed Pg 194).
   alt, float, kilometers, Orbit Altitude.
   ecc,float,, Orbit eccentricity.
   inc,float,degrees, Orbit inclination.
   aop,float,degrees, Orbit Argument of Perigee.
   @id,str/int, , Unique constellation identifier.

**Notes**

1. The spacecrafts in the constellation are assigned identifiers in the following format: spc_*constellation id*_*xy*
   where *constellation id* is the constellation identifier, *x* indicates the plane number and *y* indicates the satellite number within the orbital plane.

2. If the ``instrument`` json object is defined in the mission specifications, the instrument(s) shall be attached to each of the spacecraft
   in the constellation. Similarly in the case of the :ref:`spacecraftBus_json_object`, each spacecraft of the constellation is assigned a common bus.

**Example**

.. code-block:: javascript
   
   "constellation": { "@type": "Walker Delta Constellation",
      "date":{"@type": "JULIAN_DATE_UT1", "jd":2459270.75},
      "numberSatellites": 8,
      "numberPlanes": 1,
      "relativeSpacing": 1,
      "alt": 700,
      "ecc": 0.001,
      "inc": 45,
      "aop": 135,
      "@id": "abc"
      }

.. _spacecraft_json_object:

``spacecraft`` json object
---------------------------

This json object is used to specify the spacecraft in the mission. The ``spacecraft`` json object is made up of several json objects as described below:

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   name, str, , Spacecraft name.
   @id, str/int, , "Unique identifier. If not specified, a random string is assigned."
   orbitState, :ref:`orbitState_json_object`, , Specifications of the orbit-state of the spacecraft.
   spacecraftBus, :ref:`spacecraftBus_json_object`, , "Specifications of the spacecraft bus. If not specified, a bus with orientation aligned to the nadir-pointing frame is assigned."
   instrument, "list, *instrument* json object", ,Instrument specifications (please refer :code:`InstruPy` documentation). A list of instruments can be specified.

.. _orbitState_json_object:

``orbitState`` json object
..............................
   
This json object defines the spacecraft orbit-state (at a particular time). It consists of defining the :ref:`date_json_object` and the ``state``
json object. In case of the ``state`` json object, there are two acceptable types of state definitions:

* ``KEPLERIAN_EARTH_CENTERED_INERTIAL`` state type
         
   The following key/value pairs apply: 

   .. csv-table:: 
      :header: Parameter, Data type, Units, Description
      :widths: 10,10,5,40

      sma, float, kilometer, Semimajor axis length.
      ecc, float, kilometer, Eccentricity.
      inc, float, degrees, Inclination.
      raan, float, degrees, Right Ascension of Ascending Nod.
      aop, float, degrees, Argument of perigee.
      ta, float, degrees, True Anomaly.

* ``CARTESIAN_EARTH_CENTERED_INERTIAL`` state type 
   
   The following key/value pairs apply: 

   .. csv-table:: 
      :header: Parameter, Data type, Units, Description
      :widths: 10,10,5,40

      x, float, km, satellite x-position.
      y, float, km, satellite y-position.
      z, float, km, satellite z-position.
      vx, float, km/s, satellite x-velocity.
      vy, float, km/s, satellite y-velocity.
      vz, float, km/s, satellite z-velocity.

.. _spacecraftBus_json_object:

``spacecraftBus`` json object
..............................

This json object defines the spacecraft bus. An important attribute is the orientation of the bus, i.e. ``orientation`` which specifies
the bus orientation with respect to a reference frame. By default the orientation is alignment to the nadir-pointing frame. 

.. csv-table:: 
      :header: Parameter, Data type, Units, Description
      :widths: 10,10,5,40

      name, str, , Bus name.
      mass, float, kilogram, Mass of the bus.
      volume, float, meter^3, Volume of the bus.
      orientation, *orientation* json object, , Bus orientation (please refer :code:`InstruPy` documentation).

**Example**

.. code-block:: javascript
   
   /*spacecraft with 1 instrument, GREGORIAN_UTC date-type, KEPLERIAN_EARTH_CENTERED_INERTIAL state-type*/
   "spacecraft": { 
         "@id": "sp1", 
         "name": "Spock",
         "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5,
                        "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                        },
         "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12,
                        "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                        "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 },
                        "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                        "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"},
         "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0},
                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}
                        } \
   
         }

   /*spacecraft with 2 instruments (of different types), JULIAN_DATE_UT1 date-type, CARTESIAN_EARTH_CENTERED_INERTIAL state-type, no identifier specification, no bus specification*/
   "spacecraft": {
         "name": "Saturn",
         "instrument": [
                           {  "name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12,
                              "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"},
                              "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 },
                              "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                              "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"
                           },
                           {  "@type": "Passive Optical Scanner", "name": "FireSat", "mass": 28, "volume": 0.12,"power": 32,
                              "fieldOfViewGeometry": {"shape": "RECTanGULAR", "angleHeight": 0.628, "angleWidth": 115.8 },
                              "scanTechnique": "WhiskBROOM", "orientation": { "referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_loOK", "sideLookAngle": 0},
                              "dataRate": 85, "numberDetectorRows": 256, "numberDetectorCols": 1, "detectorWidth": 30e-6, "focalLength": 0.7,
                              "operatingWavelength": 4.2e-6, "bandwidth": 1.9e-6, "quantumEff": 0.5, "targetBlackBodyTemp": 290,
                              "bitsPerPixel": 8, "opticsSysEff": 0.75, "numOfReadOutE": 25, "apertureDia": 0.26, "Fnum": 2.7, "atmosLossModel": "LOWTRAN7"
                           }
                        ],
         "orbitState": {"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},
                        "state":{'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': -5219.8, 'y': 1473.95, 'z': 4201.35, 'vx': -3.86085, 'vy': -5.99712, 'vz': -2.69806}
                        }
      }   

.. _groundstation_json_object:

``groundstation`` json object
------------------------------

This json object is used to model ground-station. The accepted key/value pairs are as follows:

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   name, str, , Name of the ground-station.
   latitude, float, degrees, Geocentric latitude coordinates.
   longitude, float, degrees, Geocentric longitude coordinates.
   altitude, float, kilometer, "Altitude. If not defined, value of 0km is assigned."
   minimumElevation, float, degrees, "Minimum required elevation (angle from ground-plane to satellite in degrees) for communication with satellite.  If not defined, value of 7 deg is assigned."
   @id, st/int, , "Unique ground-station identifier. If not defined, a random string is assigned."

**Example**

.. code-block:: javascript
   
   "groundStation": [{"name": "Atl", "latitude": -88, "longitude": 25, "minimumElevation":12, "@id": "atl" },
                     {"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0} 
                    ]   
   
.. _grid_json_object:

``grid`` json object
---------------------

This json object is used to define the grid, i.e. the array of grid-points over which coverage, data-metrics calculations shall take place.
Multiple grids, each with their own unique identifiers can be defined in a list. 

There are two types of grid definitions:

``autogrid`` grid-type
........................

In this grid-type the lat/lon bounds of a region are given. An optional grid-resolution can be supplied in which case a grid is generated with points
spaced at the user-defined grid resolution. If the grid-resolution is not given, an appropriate grid-resolution is set according to the
value of the ``gridResFactor`` key in the ``settings`` json field (described in :ref:`settings_json_object`).

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   latUpper, float, degrees, Upper latitude. Default value is 90 deg.
   latLower, float, degrees, Lower latitude. Default value is -90 deg.
   lonUpper, float, degrees, Upper longitude. Default value is 180 deg.
   lonLower, float, degrees, Lower longitude. Default value is -180 deg.
   gridRes, float, degrees, Grid resolution (optional). 
   @id, st/int, , Unique grid-identifier. If absent a random id is assigned.

.. note:: Please specify latitude bounds in the range of -90 deg to +90 deg. Specify longitude bounds in the range of -180 deg to +180 deg.

``custom`` grid-type
......................

In this grid definition, the user supplies the list of grid-points in a data-file (see :ref:`input_grid_file_format`). 

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   covGridFilePath, str, , Filepath (with filename) to the file where the grid-points are stored.
   @id, st/int, , Unique grid-identifier. If absent a random id is assigned.

**Example**

.. code-block:: javascript

      "grid":   { "@type": "autoGrid",
                  "@id":1,
                  "latUpper":20,
                  "latLower":15,
                  "lonUpper":45,
                  "lonLower":0,
                  "gridRes": 0.5               
                }

      "grid": { "@type": "customGrid",
                "@id":101,
                "covGridFilePath": "C:\workspace\covGridUSA.csv"
              }

.. _propagator_json_object:

``propagator`` json object
---------------------------

This json object specifies the propagator to be used for propagation of the satellite states. Currently there is only one in-built propagator, the J2 analytical propagator.
The time step-size of propagation can be specified by the ``stepSize`` key/value pair. If the time step-size is not specified, an appropriate step-size is set according to the
value of the ``propTimeResFactor`` key in the ``settings`` json field (described in :ref:`settings_json_object`).

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   stepSize, float, seconds, Propagation time step-size.

**Example**

.. code-block:: javascript

      "propagator":   { "@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':15}

.. _settings_json_object:

``settings`` json object
--------------------------

This json object is used to specify some common mission settings. Following key/value pairs can be provided:

.. csv-table:: 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   outDir, str, , Path to output directory. Default is the directory in which the ``mission.py`` module is located.
   coverageType, str, , Indicates the coverage calculation type. Accepted values for the in-built coverage calculators are: GRID COVERAGE/ POINTING OPTIONS COVERAGE/ POINTING OPTIONS WITH GRID COVERAGE.
   propTimeResFactor, float, ,  Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`. Default value is 0.25.
   gridResFactor, float, , Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`. Default value is 0.9.
   opaqueAtmosHeight, float, km, Relevant in-case of inter-satellite communications. Height of atmosphere (in kilometers) below which line-of-sight communication between two satellites **cannot** take place. Default value is 0 km.
   midAccessOnly, bool, , Flag to have only the access-times at the middle of access-intervals. The flag is set to `True` when coverage calculations are done for narrow FOV instruments like SAR or pushbroom-optical sensors using a sceneFOV (or FOR defined by a sceneFOV). See :ref:`correction_of_access_files`.

**Example**

.. code-block:: javascript

   "settings": {"outDir": "temp/", "coverageType": "GRID COVERAGE", "gridResFactor": 0.5, "midAccessOnly": true} 

Output
^^^^^^^

After initialization of the mission, it can be executed by calling the ``Mission.execute`` function. All the results of the various calculations are written in the directory specified in the ``outDir`` key/value pair of the :ref:`settings_json_object`.
Description of the location, naming-convention and data-format of the results is in the table below:

.. csv-table:: 
   :header: File/directory, Location, Naming Convention, (File) Data format
   :widths: 10,10,20,10

   Main output-directory, ``outDir`` key/value pair, ,
   Auto-generated grid files, main output-directory, "*gridN*, where *N* is the grid index", :ref:`input_grid_file_format` 
   Satellite folder, main output-directory, "*satN*, where *N* is the index of the satellite",
   State files, respective satellite folder, *state_cartesian.csv* and *state_keplerian.csv*, :ref:`Propagated state file format<propagated_state_file_format>`
   Access files (results of the coverage calculations), respective satellite folder, "*access_instruN_modeM_gridK.csv*, where *N* is the instrument index, *M* is the mode index and *K* is the grid index", :ref:`Grid cov o/p file format<grid_coverage_output_file_format>` (or) :ref:`Pointing options o/p file format<pointing_options_coverage_output_file_format>` (or) :ref:`Pointing options with grid cov o/p file format<pointing_options_with_grid_coverage_output_file_format>`
   Datametrics files, respective satellite folder,"*datametrics_instruN_modeM_gridK.csv*, where *N* is the instrument index, *M* is the mode index and *K* is the grid index", :ref:`Datametrics file format<datametrics_file_format>`
   Groundstation communication files, respective satellite folder, "*gndStnN_contacts.csv*, where *N* is the groundstation index", :ref:`Contact data file format<contacts_file_format>` (``INTERVAL`` format)
   Intersatellite communication directory, main output-directory, *comm*, 
   Intersatellite communication files, intersatellite communication directory, "*satM_to_satN_contacts.csv*, where *M* and *N* are the indices of the two satellites between which contacts are evaluated", :ref:`Contact data file format<contacts_file_format>` (``INTERVAL`` format)

As seen above, the index of a satellite, instrument, etc is used in the folder/file names. The name or the identifier of the entity is **not** used. A mapping between the
folder/file names to the identifiers is available from the list of ``...OutputInfo`` objects returned upon running the  ``execute`` function on the ``Mission`` object.
For example if the mission involved propagation of a satellite, a :class:`orbitpy.propagator.PropagatorOutputInfo` object shall be present in the list of ``...OutputInfo`` objects.

Examples
^^^^^^^^^

1. Example with a single spacecraft. Only propagation and eclipses are found. Note that a random identifier is assigned to the spacecraft.

   .. code-block:: bash

      from orbitpy.mission import Mission
            
      mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                              "duration": 0.1, \
                              "spacecraft": { \
                                 "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                             }, \
                                 "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                             "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                             } \
                                 }, \
                              "settings": {"outDir": "out1/"} \
                              }'
      mission = Mission.from_json(mission_json_str)
      out_info = mission.execute()
      print(out_info)

      >> [PropagatorOutputInfo.from_dict({'@type': 'PROPAGATOR OUTPUT INFO', 'propagatorType': 'J2 ANALYTICAL PROPAGATOR', 
            'spacecraftId': '1bfa9331-7013-45bd-8991-de552f4837a2', 'stateCartFile': 'out1//sat0/state_cartesian.csv', 
            'stateKeplerianFile': 'out1//sat0/state_keplerian.csv', 'startDate': 2459299.1292592594, 'duration': 0.1, '@id': None}), 
          EclipseFinderOutputInfo.from_dict({'@type': 'ECLIPSE FINDER OUTPUT INFO', 'spacecraftId': '1bfa9331-7013-45bd-8991-de552f4837a2', 
            'stateCartFile': 'out1//sat0/state_cartesian.csv', 'eclipseFile': 'out1//sat0/eclipses.csv', 'outType': 'INTERVAL', 
            'startDate': 2459299.1292592594, 'duration': 0.1, '@id': None})]

      
      Output directory structure
      ---------------------------
      out1
         ├───comm
         └───sat0
               state_cartesian.csv
               state_keplerian.csv
               eclipses.csv

2. Example with a constellation and ground-station. All the 8 spacecrafts are propagated, eclipses calculated, inter-satellite contact periods calculated and the ground-station
   contacts calculated.
   
.. code-block:: bash

      from orbitpy.mission import Mission
            
      mission_json_str = '{  "epoch":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75}, \
                                    "duration": 0.25, \
                                    "constellation": { "@type": "Walker Delta Constellation", \
                                             "date":{"@type": "JULIAN_DATE_UT1", "jd":2459270.75}, \
                                             "numberSatellites": 8, \
                                             "numberPlanes": 1, \
                                             "relativeSpacing": 1, \
                                             "alt": 700, \
                                             "ecc": 0.001, \
                                             "inc": 45, \
                                             "aop": 135, \
                                             "@id": "abc" \
                                          }, \
                                    "groundStation":{"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}, \
                                    "settings": {"outDir": "out2/"} \
                                 }'

      mission = Mission.from_json(mission_json_str)
      out_info = mission.execute()

      Output directory structure
      ---------------------------
      out2/
         ├───comm
         │       sat0_to_sat1.csv
         │       sat0_to_sat2.csv
         │       sat0_to_sat3.csv
         │       sat0_to_sat4.csv
         │       sat0_to_sat5.csv
         │       sat0_to_sat6.csv
         │       sat0_to_sat7.csv
         │       sat1_to_sat2.csv
         │       sat1_to_sat3.csv
         │       sat1_to_sat4.csv
         │       sat1_to_sat5.csv
         │       sat1_to_sat6.csv
         │       sat1_to_sat7.csv
         │       sat2_to_sat3.csv
         │       sat2_to_sat4.csv
         │       sat2_to_sat5.csv
         │       sat2_to_sat6.csv
         │       sat2_to_sat7.csv
         │       sat3_to_sat4.csv
         │       sat3_to_sat5.csv
         │       sat3_to_sat6.csv
         │       sat3_to_sat7.csv
         │       sat4_to_sat5.csv
         │       sat4_to_sat6.csv
         │       sat4_to_sat7.csv
         │       sat5_to_sat6.csv
         │       sat5_to_sat7.csv
         │       sat6_to_sat7.csv
         │
         ├───sat0
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat1
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat2
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat3
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat4
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat5
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         ├───sat6
         │       eclipses.csv
         │       gndStn0_contacts.csv
         │       state_cartesian.csv
         │       state_keplerian.csv
         │
         └───sat7
                  eclipses.csv
                  gndStn0_contacts.csv
                  state_cartesian.csv
                  state_keplerian.csv

API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.mission.Settings
   orbitpy.mission.Mission