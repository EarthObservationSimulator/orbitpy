.. _user_json_input:

****************************
User JSON Input Description
****************************

.. csv-table:: Input parameter description 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   epoch, str,"year, month, day, hour, month, seconds", "Mission epoch (date and time) in UTC Gregorian. Comma seperated values. Eg: :code:`'2017, 1, 15, 22, 30, 20.111'`"
   duration, float, days, Length of mission in days. Eg: :code:`0.25`
   constellation, :ref:`constellation_json_object`, ,Constellation specifications.
   instrument, *instrument JSON object*, ,Instrument specifications (please refer :code:`InstruPy` documentation).
   groundStations, :ref:`groundstations_json_object`, ,Ground station specifications.
   grid, :ref:`grid_json_object`, ,Coverage grid specifications.
   settings, :ref:`settings_json_object`, ,Settings

  
.. _constellation_json_object:

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
        "orbits":[{
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

Note that the individual orbits are specified as a list (within square brackets) in the :code:`orbits` name, value pair.

2. :code:`"@type":"Walkerdelta"`

Under this option the user can define parameters of a Walker Delta constellation (as given in SMAD 3rd ed.) and the corresponding 
satellite orbits shall be auto-generated. The identifier of the satellites is coded as follows: :code:`satxy` where :code:`x` indicates
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

.. _groundStations_json_object:

:code:`groundStations` JSON object
####################################

The ground station data can be specifed by specifying the name of the CSV file with the ground station data. The file has to be
present in the user directory. An example of the data file (name: *groundStations*) is given below. The column headers 
need to be as indicated.

Example:

.. code-block:: javascript
   
   "groundStations":{
        "gndStnFn":"groundStations"
    }

.. csv-table:: Example of the ground station data file.
   :header: index,name,lat[deg],lon[deg],alt[km],minElevation[deg]
   :widths: 10,10,10,10,10,10

   1,Svalbard,78.23,15.40,0,0
   2,TrollSat,-72.01,2.53,10,5

.. _grid_json_object:

:code:`grid` JSON object
####################################

There are two ways to specify the grid:

1. :code:`"@type":"autoGrid"` 

Within the :code:`autoGrid` JSOn field, a *list* of regions can be specifyed. The required parameters for each region are:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   @id, str, , Unique region identifier
   latUpper, int,, Upper latitude in degrees
   latLower, float, kilometers, Lower latitude in degrees
   lonUpper,float,, Upper longitude in degrees
   lonLower,float,degrees, Lower longitude in degrees

A file named as :code:`covGrid` containing the grid points is created within the user directory. If a :code:`customGridRes` parameter
is specified in the :code:`settings` JSON object, that grid resolution is user, else the grid resolution is decided based on the smallest 
sensor footprint angular dimension (see :ref:`grid_res_determination`).

Example:

.. code-block:: javascript
  
   "grid":{
        "@type": "autoGrid",
        "regions":[{
            "@id":1,
            "latUpper":20,
            "latLower":15,
            "lonUpper":360,
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
    }

2. :code:`"@type":"customGrid"` option

In this option the user supplies the grid points in a data file. The file has to be present in the user directory and
the name can needs to be supplied in the :code:`covGridFn` key, value pair.

Example:

.. code-block:: javascript
  
   "grid":{
        "@type": "customGrid",
        "covGridFn": "covGridUSA"
    }

The datafile needs to be of CSV format as indicated in the example below. *regi* is the region index, *gpi* is the grid point index,
*lat[deg]* is the latitude in degrees, and *lon[deg]* is the longitude in degrees. **gpi must start from 0 and increment by 1 as shwon 
in the example.**

.. csv-table:: Example of the coverage grid data file.
   :header: regi,gpi,lat[deg],lon[deg]
   :widths: 10,10,10,10
   
    1,0,9.9,20
    1,1,9.9,20.1015
    1,2,9.9,20.203
    2,3,-49.1,21.9856
    2,4,-49.1,22.1383
    2,5,-49.1,22.291
    2,6,-49.1,22.4438
    2,7,-49.1,22.5965
    2,8,-49.1,22.7493
    2,9,-49.1,22.902

.. note:: Please specify latitudes in the range of -90 deg to +90 deg and longitudes in the range of -180 deg to +180 deg. Do *NOT* 
          specify the longitudes inr ange of 0 deg to 360 deg.

.. _settings_json_object:

:code:`settings` JSON object
####################################

This JSON object contains items which can be used to configure some of the orbit propagation and coverage parameters. 

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   customTimeStep, float, seconds, (Optional) Orbit propagation time-step. A warning is issued if the internal computed time-step is smaller than the user specified time-step.
   customGridRes, float, degrees, (Optional) Grid resolution 





