.. OrbitPy documentation master file, created by
   sphinx-quickstart on Tue Feb 11 15:28:03 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OrbitPy's documentation!
===================================

Install
========
*Requires:* Unix-like operating system (currently tested in Ubuntu 18.04.03), :code:`python 3.8`, :code:`gcc`, :code:`gfortran`

1. Make sure the :code:`instrupy` package (dependency) has been installed. It can be installed by running :code:`make` in the :code:`instruments/instrupy/` directory.
2. Navigate to the :code:`orbits/oc/` directory and run :code:`make`. 
3. Navigate to the :code:`orbits/orbitpy/` directory and run :code:`make`.
4. Execute :code:`make runtest` to run tests and verify *OK* message.
5. Run an example, by running the following command from the :code:`orbits` directory: :code:`python orbitpy/bin/run_mission.py orbitpy/examples/example1/`.
   See the results in the :code:`orbitpy/examples/example1/` folder. Description of the examples in given in :ref:`examples` page. 

Find the documentation in: :code:`/orbitpy/docs/_build/html/index.html`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_json_desc
   output_desc
   api_reference
   examples
   miscellaneous

Description
===========

This package contain set of modules to compute orbit data of satellites. It performs the following functions:

1. Computation of satellite state (position and velocity) data.
2. Generation of grid-of-points at a (user-defined or auto) angular resolution.
3. Computation of Field Of Regard (FOR) based on the manueverability and sensor specifications, mounting.
4. Computation of satellite access intervals over given set of grid points for the length of the mission. 
5. Computation of inter-satellite communication time intervals.
6. Computation of ground-station contact time intervals.

With respect to integration in DSHIELD, the outputs/ functions of the package are used by other modules
of DSHIELD as follows:

.. csv-table:: Integration to other modules
   :header: "Data output", "the other module"
   :widths: 20, 20

   "Satellite States, Grid Points", "ACS module"
   "Intersatellite comms", "Comm Module"
   "Ground-station comms", "Ground module"
   "Access Opps with Observation quality", "Planner"

The input to the first three items is straightforward and can be used directly from the current implementation. The last item
however has issues. The raw access outputs are naive, and need to be filtered, post-processed to imaging opportunities (**raw access vs imaging opps**).     

Issue #1
^^^^^^^^
Consider a 5 second mission, the desired output from the Orbits to the Planner would be as follows:

.. code-block:: bash

   Time, (Grid-points, Observation Quality)
   1,    (10,2) (45,1) (100,1) (210,4) 
   2,    (10,3) (45,2) (100,2) (210,3) 
   3,    (10,4) (45,3) (100,3) (210,2) 
   4,    (10,3)        (100,4) (210,1) 
   5,    (10,1)        (100,5)  


Where a observation is defined as taking an image/ reading around the respective ground-point:

.. figure:: valid_vs_invalid_obs.png
    :scale: 75 %
    :align: center

    Valid vs Invalid observations

In order to deal with the above issue, the observation is deemed to be made with the pointing axis pointed to the GP
(and hence the missle of the observation). While this flows naturally when calculating coverage from pointing-options,
it is not natural for the case of coverage calculated from grid-points. See :ref:`corr_acc_files`.

Issue #2
^^^^^^^^
A similar issue exists in the time domain:

.. code-block:: bash

   Time,Access,Imaging Opp
   98,No, No     
   99,No, No   
   100,Yes, No   
   101,Yes, No   
   102,Yes, No
   103,Yes, Yes iff t= 104, are free
   104,Yes, Yes iff t= 103, 105 are free
   105,Yes, Yes iff t=103, 104, 106 are free
   .,.,,
   .,.,,
   .,.,,
   .,.,,
   115, Yes,No
   116, No,No

.. figure:: outlier_times.png
    :scale: 75 %
    :align: center

    Valid vs Invalid obs times

To deal with the above issue, a constraint condition such as that shown in the table is implicit in the provided imaging oppurtunities
table.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Questions?
==========
Please contact Vinay (vinay.ravindra@nasa.gov)