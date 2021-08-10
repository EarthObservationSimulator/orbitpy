``orbit.constellation`` --- Constellation Module
===================================================

Description
^^^^^^^^^^^^^

This module allows initialization of constellation (i.e. collection of satellites) from the respective model parameters. The orbits of the satellites in the
constellation can also be generated. Currently only Walker-Delta constellation [1] is supported.

Factory method pattern  is used for initializing the constellation object. Users may additionally define their own constellation objects adherent to the same interface 
functions as in the in-built constellation objects.

References
------------
1. Space Mission Analysis and Design, 3rd ed, Section 7.6, Pg 194, 195.

Examples
^^^^^^^^^


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/

   orbitpy.constellation.ConstellationFactory
   orbitpy.constellation.WalkerDeltaConstellation
   orbitpy.constellation.TrainConstellation

