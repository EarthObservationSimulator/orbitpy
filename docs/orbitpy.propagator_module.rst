.. _propagator_module:

``orbit.propagator`` --- Propagator Module
===========================================

Description
^^^^^^^^^^^^^

Module providing classes and functions to handle orbit propagation. The module provides for an J2 analytical propagator model 
which has been validated with the STK J2 analytical propagator.

Factory method pattern is used for initializing the propagator object [2]. Users may additionally define their own propagator 
classes (models) adherent to the same interface functions (``from_dict(.)``, ``to_dict(.)``, ``execute(.)``, ``__eq__(.)``) 
as in the in-built propagator objects.

References
------------
1. https://realpython.com/factory-method-python/#supporting-additional-formats

.. todo:: Add additional propagator models (SGP4, etc) and also provide support to read-in propagated data from GMAT, STK.

Examples
^^^^^^^^^

1. Working with a Walker Delta Constellation.

   .. code-block:: python

         factory = ConstellationFactory()
         specs = {"@type": 'Walker Delta Constellation', "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}, "numberSatellites": 2, "numberPlanes": 1,
                           "relativeSpacing": 1, "alt": 500, "ecc": 0.001, "inc": 45, "aop": 135, "@id": "abc"}
         wd_model = factory.get_constellation_model(specs) # initialization
         print(wd_model.generate_orbits())

         >> [OrbitState.from_dict({'date': {'dateType': 'JULIAN_DATE_UT1', 'jd': 2451545.0}, 'state': {'stateType': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 7078.0, 'y': 0.0, 'z': 0.0, 'vx': -0.0, 'vy': 7.504359112788965, 'vz': 0.0}, '@id': 0})]     

   .. code-block:: python

         date =  OrbitState.date_from_dict({"dateType": "JULIAN_DATE_UT1", "jd":2459270.75})
         wd_model = WalkerDeltaConstellation( date=date, numberSatellites=2, numberPlanes=1, relativeSpacing=1, alt=500, ecc=0.001, inc=45, aop=135, _id="abc")
         print(wd_model.generate_orbits())

         >> [OrbitState.from_dict({'date': {'dateType': 'JULIAN_DATE_UT1', 'jd': 2451545.0}, 'state': {'stateType': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 7078.0, 'y': 0.0, 'z': 0.0, 'vx': -0.0, 'vy': 7.504359112788965, 'vz': 0.0}, '@id': 0})]     


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.grid.PropagatorFactory
   orbitpy.grid.PropagatorType
   orbitpy.grid.J2AnalyticalPropagator
   orbitpy.grid.PropagatorOutputInfo

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.grid.compute_time_step