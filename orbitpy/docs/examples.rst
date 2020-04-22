.. _examples:

Examples
*********

.. automodule:: run_mission
   :members:
   :exclude-members: readable_dir

Several examples user directories are available in the :code:`/orbitpy/examples/` directory. The main features of each of the examples 
are given below:

1. Example 1

2. Example 2

3. Example 3

4. Example 4

5. Example 5


To create and execute your own mission scenario create a user directory containing the below files, and run the :code:`run_mission.py` 
script with the argument as the path to the user directory. 

* User JSON configuration file which must be mandatorily named as :code:`MissionSpecs.json`. Description of the 
  expected key, value pairs is given in :ref:`user_json_input`.

* Ground station data csv formatted file (see :ref:`groundStations_json_object`).

* Optional coverage grid data file.