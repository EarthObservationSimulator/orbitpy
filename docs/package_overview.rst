Package Overview
==================

This package contain set of modules to compute *mission-data* of satellites. It can be used to perform the following calculations:

1. Generation of satellite orbits from constellation specifications.
2. Computation of propagated satellite state (position and velocity) data.
3. Generation of grid-of-points at a (user-defined or auto) angular resolution over region of interest.
4. *Grid Coverage:* Computation of satellite access intervals over given set of grid points (grid-coverage) for the length of the mission.
   
   i. Consideration of sensor pointing directions.
   ii. Consideration of sensor field-of-view (FOV) and field-of-regard (FOR).

5. *Pointing-options Coverage:* Computation of coverage in which set of pointing-options of the instrument are specified and accessed ground-locations are calculated.
6. *Pointing-options with Grid Coverage.*
7. Computation of inter-satellite communication (line-of-sight) time intervals.
8. Computation of ground-station contact time intervals.
9.  Computation of satellite eclipse time-intervals.
10. Sensor pixel-array projection.

The ``orbitpy`` package is built on top of the ``propcov`` package available in the ``propcov`` folder. Please refer to the README.MD file within the `propcov` folder for description of the respective package.

**References**

* V. Ravindra, R. Ketzner, S. Nag, *"Earth Observation Simulator (EO-SIM): An Open-Source Software for Observation Systems Design",* IEEE International Geoscience and Remote Sensing Symposium, Brussels Belgium, July 2021.


Glossary of terms used in the package
----------------------------------------

* Satellite and spacecraft are synonymous.
  
* Instrument, payload and sensor are synonymous.

* Grid-point, ground-point and target-point synonymous.

* Access vs Coverage

      * Sometimes access and coverage are used synonymously.

      * Other times access refers to a target falling under a sensor FOV while coverage includes an additional condition that the satellite
        should be able to be make an observation. 

