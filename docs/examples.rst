.. _examples:

Examples
*********

As described in the :ref:`run` section, OrbitPy functionalities can be accessed by either invoking the ``bin/run_mission.py`` script
on a JSON file describing the mission specifications or the modules be imported into a python script and used to configure a simulation situation.
Examples are available in the ``examples`` folder which illustrate both the approaches. The examples are briefly described below:

Simple Mission 1
=================
This example is based on configuring the mission in a JSON file.
It has been described in the :ref:`run_json_specs_file` section.


SAR Constellation
==================
This example was developed for the DSHIELD project. The example is built by importing the relevant modules from the OrbitPy library.
It simulates 3 satellites carrying L,P band SAR instruments.
The coverage calculations is done differently in this example since:

(1) The grid consisted of more then 1.5 million points, and coupled with the requirement to run the simulation at 1s time-step, 
    the resulting computational load (runtime and data-size) was huge.

(2) The SARs were configured to operate at  *fixed swath*.  Fixed swath implies that irrespective of the illuminated swath 
    (which is determined by the sensor cross-track FOV, which here is determined by the antenna beamwidth), 
    the processed swath size is fixed. Hence coverage calculations using the sensor FOV would have yielded
    erroneous results. (Illuminated swath > fixed swath).
