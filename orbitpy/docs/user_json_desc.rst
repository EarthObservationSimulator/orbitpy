****************************
User JSON Input Description
****************************

.. csv-table:: Input parameter description 
   :header: Parameter, Data type, Units, Description
   :widths: 10,10,5,40

   epoch, str,"year, month, day, hour, month, seconds", Mission epoch (date and time) in UTC Gregorian. Comma seperated values. 
   duration, float, days, Length of mission in days. 
   constellation, :ref:`constellation_json_object`, ,Constellation specifications.
   
.. _constellation_json_object:

:code:`constellation` JSON object
##################################
Constellation specifications. Two types of constellation are accepted: `custom`, `Walkerdelta`. 

:code:`custom` constellation type
**********************************
A list of satellites is to be specified with each satellite orbit described by it's corresponding Keplerian elements.

epoch
######
*Mission epoch (date and time) in UTC Gregorian* 

=========  =====
Data Type  str
Format     Comma separted values
\          'year, month, day, hour, month, seconds'
Example    '2017, 1, 15, 22, 30, 20.111'
Required?  yes
Default    none
=========  =====


settings::customTimeStep
#########################
- *Time step to be used for orbit propagation in seconds (optional entry).* 
- *The output satellite states are also at the same time step.*
- *If the custom time step value is higher than the internally computed time step
  a warning message is displayed.*

=========  =====
Data Type  float
Format     value
Example    2
Required?  No
Default    none
=========  =====

maneuverability
################
*Total maneuverability of payload pointing (combining satellite and payload maneuverability)*

@type
******
*Only 'FIXED' or 'CONE' or 'ROLLONLY' types are supported*

=========  =====
Data Type  str
Format     'FIXED' or 'CONE' or 'ROLLONLY' value
Example    CONE
Required?  Yes
Default    none
=========  =====

@type = FIXED
^^^^^^^^^^^^^^
'FIXED' implies that the payload pointing cannot be changed. 
No other fields are necessary.




