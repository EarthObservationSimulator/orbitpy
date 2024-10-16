.. _user_json_input:

****************************
User JSON Input Description
****************************

.. csv-table:: Input parameter description 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   epoch, str,"year, month, day, hour, month, seconds", "Mission epoch (date and time) in UT1 Gregorian. Comma seperated values. Eg: :code:`'2017, 1, 15, 22, 30, 20.111'`"
   duration, float, days, Length of mission in days. Eg: :code:`0.25`
   constellation, :ref:`constellation_json_object`, ,Constellation specifications.
   instrument, list *instrument JSON object*, ,Instrument specifications (please refer :code:`InstruPy` documentation). A list of instruments is to be specified.
   satellite, :ref:`satellite_json_object`, ,Satellite specifications  
   groundStations, :ref:`groundstations_json_object`, ,Ground station specifications.
   grid, :ref:`grid_json_object`, ,Coverage grid specifications. 
   pointingOptions, :ref:`popts_json_object`, ,Set of pointing options. 
   propagator, :ref:`propagator_json_object`, ,Propagator related items.

*Note that either :code:`grid` OR the :code:`pointingOptions` JSON object is to be defined, corresponding to grid-based coverage calculations
or pointing-options based coverage caclulations.*

.. note:: Whenever list of JSON objects is required, please specify as a list (i.e. within square brackets "[..]") even in the case only 
          one object is to be specified.


:code:`constellation` JSON object
##################################
Constellation specifications. Two types of constellation are accepted: `custom`, `Walkerdelta` and should be indicated 
in the :code:`@type` name, value pair. 

1. :code:`"@type":"custom"` 

A list of satellites is to be specified with each satellite orbit described by it's corresponding Keplerian elements. 
The following fields are expected per satellite:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   idn, str or int, , Unique satellite identifier. The names of the output files are based on this field.
   sma,float, kilometers, Length of the orbit semi-major axis
   ecc,float,, Orbit eccentricity
   inc,float,degrees, Orbit inclination
   raan,float,degrees, Orbit Right Ascension of Ascending Node
   aop,float,degrees, Orbit Argument of Perigee
   ta,float,degrees, Orbit True Anomaly

Example:

.. code-block:: javascript
   
   "constellation":{
        "@type": "Custom",
        "orbit":[{
            "idn": 11,
            "sma": 7078.137,
            "ecc": 0.0,
            "inc": 96.67657116,
            "raan": 327.55,
            "aop": 0,
            "ta": 0
        },
        {
            "idn": 12,
            "sma": 6878.137,
            "ecc": 0.0,
            "inc": 88.67657116,
            "raan": 127.55,
            "aop": 0,
            "ta": 0
        }]
    }

Note that the individual orbits are specified as a list (within square brackets) in the :code:`orbit` name, value pair.

2. :code:`"@type":"Walkerdelta"`

Under this option the user can define parameters of a Walker Delta constellation (as given in SMAD 3rd ed.) and the corresponding 
satellite orbits shall be auto-generated. The identifier of the satellites is coded as follows: :code:`xy` where :code:`x` indicates
the plane number and :code:`y` indicates the satellite number within the orbital plane.
The following fields are expected for the definition of the Walker Delta constellation:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   numberSatellites, int, , Total number of satellites in the constellation
   numberPlanes, int, , Number of orbital planes
   relativeSpacing, int,, Factor controlling the spacing between the satellites in the different planes (See SMAD 3rd ed Pg 194).
   alt, float, kilometers, Orbit Altitude
   ecc,float,, Orbit eccentricity
   inc,float,degrees, Orbit inclination
   aop,float,degrees, Orbit Argument of Perigee

Example:

.. code-block:: javascript
   
   "constellation":{
        "@type": "Walkerdelta",
        "numberSatellites": 4,
        "numberPlanes": 2,
        "relativeSpacing":3,
        "inc":56,
        "alt": 700,
        "ecc": 0.0001,
        "aop": 0
    }

The satellites generated by use of the :code:`constellation` object are all equipped with the list of instruments specified in the 
:code:`instrument` JSON object. 

.. _satellite_json_object:

:code:`satellite` JSON object
##############################

The satellites in the mission can be specified directly as a list of :code:`orbit` -> :code:`@type:"Custom"` and list of :code:`instrument` JSON objects. This allows for
an heterogneous distribution of different instruments among the satellites in the mission. 

Example:

.. code-block:: javascript

   "satellite":    [{
        "orbit": { "@id": 1,
                   "sma": 6878.137,
                   "ecc": 0.0,
                   "inc": 96.67657116,
                   "raan": 60,
                   "aop": 0,
                   "ta": 0},
        "instrument": [{ "@type": "Basic Sensor",
                         "@id": "pay1_1",  
                         ...
                         ...       
                        },
                        { "@type": "Basic Sensor",
                            "@id": "pay1_2",  
                            ...
                            ...
                        }
                       ]
        },
        {  
        "orbit": { "@id": 2,
                   "sma": 6878.137,
                   "ecc": 0.0,
                   "inc": 96.67657116,
                   "raan": 60,
                   "aop": 0,
                   "ta": 0},
        "instrument": [{ "@type": "Basic Sensor",
                         "@id": "pay2_1",  
                         ...
                         ...
                        }
                       ]


.. _groundStations_json_object:

:code:`groundStations` JSON object
####################################

The ground station data can be specifed in two ways: 

1. :code:`stationInfo` JSON object

Within the :code:`stationInfo` JSOn field, a *list* of ground-stations can be specifyed. The required parameters for each region are:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   @id, str, ,Unique ground-station identifier
   name, str, degrees, (Optional) name of the ground-station
   lat, float, degrees, Latitude
   lon,float, degrees, Longitude
   alt,float, km, (Optional) Altitude. Default is 0km.
   minimumElevation, float, degrees, Minimum elevation beyond which the ground-station cane see the satellite.

.. code-block:: javascript
   
   "groundStations":{
        "stationInfo":[
            { "@id": "gs1",
              "name": "Tacos",
              "latitude": 1,
              "longitude": 1.5,
              "altitude": 0,
              "minimumElevation": 7
            },
            { "@id": "gs2",
                "name": "Hilly",
                "latitude": 89,
                "longitude": -10,
                "altitude": 20,
                "minimumElevation": 7
            }
        ]
    }

2. :code:`gndStnFileName` or :code:`gndStnFilePath`

By means of a data file containing the ground station info. In case the 
:code:`gndStnFileName` key, value pair is specified, the file has to be present in the user directory. Otherwise a :code:`gndStnFilePath`
key, value pair may be used to give the complete path to the data-file.
An example of the data file (name: *groundStations*) is given below. The column headers 
need to be as indicated.

Example:

.. code-block:: javascript
   
   "groundStations":{
        "gndStnFileName":"groundStations"
    }

.. code-block:: javascript
   
   "groundStations":{
        "gndStnFilePath":"C:\workspace\groundStations"
    }

.. csv-table:: Example of the ground station data file.
   :header: index,name,lat[deg],lon[deg],alt[km],minElevation[deg]
   :widths: 10,10,10,10,10,10

   1,Svalbard,78.23,15.40,0,0
   2,TrollSat,-72.01,2.53,10,5





:code:`grid` JSON object
####################################

There are two ways to specify the grid:

1. :code:`"@type":"autoGrid"` 

Within the :code:`autoGrid` JSOn field, a *list* of regions can be specified. The required parameters for each region are:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   @id, str, , Unique region identifier
   latUpper, float, degrees, Upper latitude in degrees
   latLower, float, degrees, Lower latitude in degrees
   lonUpper,float, degrees, Upper longitude in degrees
   lonLower,float, degrees, Lower longitude in degrees

A file named as :code:`covGrid` containing the grid points is created within the user directory.

In addition to the region specifications, optionally two more parameters can be specified, which control the resolution of 
the generated grid.

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   customGridRes, float, degrees, (Optional) Grid resolution. A warning is issued if the internal computed grid resolution is coarser than the user specified grid resolution. 
   customGridResFactor, float, , (Optional) Custom grid-resolution factor used to determine the grid-resolution. (Default value is 0.9.)

Example:

.. code-block:: javascript
  
   "grid":{
        "@type": "autoGrid",
        "regions":[{
            "@id":1,
            "latUpper":20,
            "latLower":15,
            "lonUpper":75,
            "lonLower":0                
        },
        {
            "@id":2,
            "latUpper":-30,
            "latLower":-35,
            "lonUpper":45,
            "lonLower":20
        }
        ],
        customGridResFactor = 0.5
    }

2. :code:`"@type":"customGrid"` option

In this option the user supplies the grid points in a data file. If the :code:`covGridFileName` key, value pair is used, 
the file has to be present in the user directory. 
If the :code:`covGridFilePath` key, value pair is used, the entire path to the file needs to be supplied.

Example:

.. code-block:: javascript
  
   "grid":{
        "@type": "customGrid",
        "covGridFileName": "covGridUSA"
    }

.. code-block:: javascript
  
   "grid":{
        "@type": "customGrid",
        "covGridFilePath": "C:\workspace\covGridUSA.csv"
    }

The datafile needs to be of CSV format as indicated in the example below. 
*lat[deg]* is the latitude in degrees, and *lon[deg]* is the longitude in degrees. 
The grid-points are referred by indices starting from 0.

.. csv-table:: Example of the coverage grid data file.
   :header:lat[deg],lon[deg]
   :widths: 10,10
   
    9.9,20
    9.9,20.1015
    9.9,20.203
    -49.1,21.9856
    -49.1,22.1383
    -49.1,22.291
    -49.1,22.4438
    -49.1,22.5965
    -49.1,22.7493
    -49.1,22.902

.. note:: Please specify latitudes in the range of -90 deg to +90 deg and longitudes in the range of -180 deg to +180 deg. Do *NOT* 
          specify the longitudes in range of 0 deg to 360 deg.

.. _popts_json_object:

:code:`pointingOptions` JSON object
####################################

This JSON object contains specifications of the pointing-options to be used to calculate the coverage. It contains a list of JSON fields, with each
field having a format as follows:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   instrumentID, str, , The instrument identifier to which the corresponding pointing-options data-file is to be used. Multiple IDs separated by commas are allowed.
   referenceFrame, str, , Currently only the :code:`NadirRefFrame` is supported.
   pntOptsFileName, str, , Name of the data-file containing the set of pointing options. This file has to be present in the user-directory.
   pntOptsFilePath, str, , Path to the data-file containing the set of pointing options. (Specify :code:`pntOptsFilePath` **or** :code:`pntOptsFileName`) 

.. warning:: In the case when the pointing-options approach is used for coverage calculations, the instrument identifier becomes a
             compulsory attribute of the :code:`Instrument` JSON field, since it is needed to reference the pointing-options files.

.. warning:: The name of the data-file containing the pointing-options should not have any whitespaces. The pointing-otions indicated in the file 
             are strictly indexed from *0* onwards. 

Example:

.. code-block:: javascript

   "pointingOptions":[
       {
       "instrumentID": "sen1",
       "referenceFrame": "NadirRefFrame",
       "pntOptsFileName":"pOpts_sen1"              
       },
       {
       "instrumentID": "sen2",
       "referenceFrame": "NadirRefFrame",
       "pntOptsFilePath":"C:\workspace\sen2_pOpts"              
       },
    ],

Example of the data-file:

.. code-block:: javascript

    Euler (intrinsic) rotations with sequence 1,2,3 assumed, i.e. R = R3R2R1, with rotation matrix representing rotation of the coordinate system.
    index,euler_angle1[deg],euler_angle2[deg],euler_angle3[deg] 
    0,0,0,0
    1,0,20,0
    2,0,-20,0


:code:`propagator` JSON object
####################################

This JSON object contains items relating to the propagator. 

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   customTimeStep, float, seconds, (Optional) Orbit propagation time-step. A warning is issued if the internal computed time-step is coarser than the user specified time-step.
   customTimeResFactor, float, seconds, (Optional) Custom time-resolution factor used to determine the propagation time-step. (Default value is 0.25.)




