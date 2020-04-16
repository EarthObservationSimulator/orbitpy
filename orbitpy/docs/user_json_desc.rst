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

1. :code:`@type:custom` 

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

2. :code:`@type:Walkerdelta`

Under this option the user can define parameters of a Walker Delta constellation (as given in SMAD 3rd ed.) and the corresponding 
satellite orbits shall be auto-generated. The identifier of the satellites is coded as follows: :code:`satxy` where :code:`x` indicates
the plane number and :code:`y` indicates the satellite number within the orbital plane.
The following fields are expected for the definition of the Walker Delta constellation:

.. csv-table:: Expected parameters
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   numberSatellites, int, , Total number of satellites in the constellation
   numberPlanes, int, kilometers, Number of orbital planes
   relativeSpacing, int,, Factor controlling the spacing between the satellites in the different planes (See SMAD 3rd ed Pg 194).
   ecc,float,, Orbit eccentricity
   inc,float,degrees, Orbit inclination
   aop,float,degrees, Orbit Argument of Perigee
   ta,float,degrees, Orbit True Anomaly

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

.. _grid_json_object:

:code:`grid` JSON object
####################################

.. _settings_json_object:

:code:`settings` JSON object
####################################




settings::customTimeStep
#########################
- *Time step to be used for orbit propagation in seconds (optional entry).* 
- *The output satellite states are also at the same time step.*
- *If the custom time step value is higher than the internally computed time step
  a warning message is displayed.*





