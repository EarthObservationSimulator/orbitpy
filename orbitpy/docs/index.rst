.. OrbitPy documentation master file, created by
   sphinx-quickstart on Tue Feb 11 15:28:03 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OrbitPy's documentation!
===================================
This package contain set of modules to compute orbit data of satellites. It performs the following functions:

1. Computation of satellite state (position and velocity) data.
2. Generation of grid-of-points at a (user-defined or pt9criterion-based) angular resolution.
3. Computation of Field Of Regard (FOR) based on the manueverability and sensor specifications, mounting.
4. Computation of satellite access intervals over given set of grid points for the length of the mission. 
5. Computation of inter-satellite communication time intervals.
6. Computation of ground-station contact time intervals.

To get started see the :ref:`examples` page. 

.. toctree::
   :titlesonly:
   :maxdepth: 2
   :caption: Contents:

   user_json_desc
   api_reference
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Questions?
==========
Please contact Vinay (vinay.ravindra@nasa.gov)