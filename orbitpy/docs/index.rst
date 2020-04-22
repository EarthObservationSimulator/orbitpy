.. OrbitPy documentation master file, created by
   sphinx-quickstart on Tue Feb 11 15:28:03 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OrbitPy's documentation!
===================================
This package contain set of modules to compute orbit data of satellites. It performs the following functions:

1. Computation of satellite state (position and velocity) data.
2. Generation of grid-of-points at a (user-defined or auto) angular resolution.
3. Computation of Field Of Regard (FOR) based on the manueverability and sensor specifications, mounting.
4. Computation of satellite access intervals over given set of grid points for the length of the mission. 
5. Computation of inter-satellite communication time intervals.
6. Computation of ground-station contact time intervals.

To build and install the package:

1. Make sure the :code:`instrupy` package (dependency) has been installed. It can be installed by running :code:`make` in the :code:`instruments/instrupy/` directory.
2. Navigate to the :code:`orbits/oc/` directory and run :code:`make`. 
3. Navigate to the :code:`orbits/orbitpy/` directory and run :code:`make`.
4. Execute :code:`make runtest` to run tests and verify *OK* message. (Currently none.)
5. Run an example, by running the following command from the :code:`orbits` directory: :code:`python orbitpy/bin/run_mission.py orbitpy/examples/example1/`.
   See the results in the :code:`orbitpy/examples/example1/` folder. Description of the examples in given in :ref:`examples` page. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_json_desc
   output_desc
   api_reference
   examples
   miscellaneous

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Questions?
==========
Please contact Vinay (vinay.ravindra@nasa.gov)