.. _examples:

Examples
*********

As described in the :ref:`run` section, OrbitPy functionalities can be accessed by either invoking the ``bin/run_mission.py`` script
on a JSON file describing the mission specifications or the modules be imported into a python script and used to configure a simulation situation.
Examples are available in the ``examples`` folder which illustrate both the approaches.
The examples are briefly described below.

Simple Mission 1
=================
This example available in the folder ``examples/simple_mission_1`` is based on configuring the mission in a JSON file.
It has been described in the :ref:`run_json_specs_file` section.


SAR Constellation
==================
This example (available in ``examples/sar_constellation/``) was developed for the DSHIELD project. 
The example is built by importing the relevant modules from the OrbitPy library.
It simulates 3 satellites carrying L,P band SAR instruments.
The coverage calculations is done differently in this example since:

(1) The grid consisted of more then 1.5 million points, and coupled with the requirement to run the simulation at 1 second time-step, 
    the resulting computational load (runtime and data-size) was huge.

(2) The SARs were configured to operate at  *fixed swath*.  Fixed swath implies that irrespective of the illuminated swath 
    (which is determined by the sensor cross-track FOV, which here is determined by the antenna beamwidth), 
    the processed swath size is fixed. Hence coverage calculations using the sensor FOV would have yielded
    erroneous results. (Illuminated swath > fixed swath).

For detailed description please refer the ``dshield_mission.py`` script. The script can be executed from the repo directory 
with the command ``python examples/sar_constellation/dshield_mission.py``.


Landsat-8, SeaHawk-1, (hypothetical) SeaHawk-2
=================================================
The examples in the folders ``landsat_seahawk_1`` and ``landsat_seahawk_2`` execute the same missions. 

The first folder contains a ``MissionSpecs.json`` file which has the mission configuration which can be executed from the repo directory 
using the command: ``python bin/run_mission.py examples/landsat_seahawk_1/``

In the second folder a python script configures the mission using modules imported from OrbitPy. 
It can be executed from the repo directory using the command ``python examples/landsat_seahawk_2/landsat_seahawk.py``

In the first method the execution produces satellite propagation, coverage, datametrics, eclipse periods and intersatellite communication periods.
In the second method the script is built to produce only the propagation, coverage and datametrics.

The example simulates SeaHawks with different modes of operation with each mode as a pointing-option (i.e. a different satellite orientation). 
The instruments of the satellites (TIRS, OLI and HawkEye are modeled) and corresponding data-metrics calculated for access-events over the mission duration.
Since the instruments have a narrow FOV in the along-track direction, and if these FOV were considered, the coverage calculations would need to done with very small propagation step-size. Hence a sceneFOV is defined which has a larger 
along-track dimension (cross-track dimension is same as the instrument FOV).
For detailed description of the mission please refer the ``landsat_seahawk.py`` script.
