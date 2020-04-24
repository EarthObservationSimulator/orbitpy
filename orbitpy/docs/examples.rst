.. _examples:

Examples
*********

The :code:`run_mission.py` script can be invoked to execute missions as defined in a customizable JSON configuration file.
Description of the scipt is given below, followed by description of the example scenarios present in the 
directory :code:`orbitpy/examples/`.  

.. automodule:: run_mission
   :members:
   :exclude-members: readable_dir

Example 1
==========

* 3 satellites, 3 plane Walker delta constellation
* Basic Sensor, Nadir pointing, Conical FOV, No Manuverability
* Grid: Auto, Continental USA 
* Custom time-step = 1s
* No inter-satellite comm possible


Example 2
==========

* 2 satellites, Custom constellation 
* Basic Sensor, Rectangular FOV, Side Look, RollOnly Manuverability
* Grid: Custom, Continental USA 
* Custom time-step
  * Warning message displayed

Example 3
==========

* 4 satellites, 2 plane Walker delta constellation
* SAR, Sidelook, Yaw180Roll Manuverability, ScanFOV concept => Correction of access files
* Grid: Auto, India, Germany, Japan
* Auto time-step
* Custom grid-resolution
  * Warning message displayed

Example 4
==========

* 8 satellites, 1 plane Walker delta constellation
* Planet DOVE CCD imager, Rectangular FOV, Nadir pointing, Cone Manuverability
* Custom time step
* Grid: Auto, -5 deg to +5 deg latitudes

Example 5
==========

* 6 satellites, 3 plane Walker delta constellation
* Landsat-8 TIRS, Pushbroom (Rectangular), Nadir pointing, RollOnly, ScanFOV concept (180 km x 185 km scene) => Correction of access files
* Grid: Auto, Continental USA

Running your own case
======================

To create and execute your own mission scenario create a user directory containing the below files, and run the :code:`run_mission.py` 
script with the argument as the path to the user directory. 

* User JSON configuration file which must be mandatorily named as :code:`MissionSpecs.json`. Description of the 
  expected key, value pairs is given in :ref:`user_json_input`.

* Ground station data csv formatted file (see :ref:`groundStations_json_object`).

* Optional coverage grid data file.