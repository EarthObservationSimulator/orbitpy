User JSON Input Description
****************************



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

