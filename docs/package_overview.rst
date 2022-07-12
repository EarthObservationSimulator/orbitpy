Package Overview
==================

This package contain set of modules to compute *mission-data* of satellites. It can be used to perform the following calculations:

1. Generation of satellite orbits from constellation specifications.
2. Computation of propagated satellite state (position and velocity) data.
3. Generation of grid points at a (user-defined or auto) angular resolution over region of interest.
4. *Grid Coverage*: Computation of satellite access intervals over given set of grid points (*grid-coverage*) for the length of the mission.

        i. With consideration of satellite/sensor pointing (orientation) directions.
        ii. With consideration of sensor field-of-view (FOV) and field-of-regard (FOR).
5. *Pointing-options Coverage:* Computation of coverage in which set of pointing-options of the satellite/instrument are specified and accessed ground-locations (intersection of the pointing-axis with the Earth's surface) is calculated.
6. *Pointing-options with Grid Coverage*: Grid Coverage calculated for different satellite/instrument orientations.
7. *Specular Coverage*: Calculation of specular points and grid points inside the specular regions. Several source (transmitter) satellites may be specified, and the receiver satellite/sensor orientation and FOV is taken into consideration.
8. Computation of inter-satellite communication (line-of-sight) time intervals.
9. Computation of ground-station contact time intervals.
10. Computation of satellite eclipse time-intervals.
11. (Under dev) Sensor pixel-array projection to simulated Level-2 satellite imagery.

The ``orbitpy`` package is built on top of the ``propcov`` package available in the ``propcov`` folder. Please refer to the `README.MD` file within the `propcov` folder for description of the respective package.

**References**

* V. Ravindra, R. Ketzner, S. Nag, *"Earth Observation Simulator (EO-SIM): An Open-Source Software for Observation Systems Design",* IEEE International Geoscience and Remote Sensing Symposium, Brussels Belgium, July 2021.


Glossary of terms used in the package
----------------------------------------

* Satellite and spacecraft are synonymous.
  
* Instrument, payload and sensor are synonymous.

* Grid-point, ground-point and target-point synonymous.

* Data-metrics and Observation-metrics are synonymous.

* Access vs Coverage

      * Sometimes access and coverage are used synonymously.

      * Other times access refers to a target falling under a sensor FOV while coverage includes an additional condition that the satellite
        should be able to be make an observation. 

