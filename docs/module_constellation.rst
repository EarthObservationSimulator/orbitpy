.. _module_constellation:

``orbit.constellation`` --- Constellation Module
===================================================

Description
^^^^^^^^^^^^^

This module allows initialization of constellation (i.e. collection of satellites) from the respective model parameters. The orbits of the satellites in the
constellation can also be generated. Currently only Walker-Delta constellation [1] is supported.

Factory method pattern is used for initializing the constellation object [2]. Users may additionally define their own constellation classes
adherent to the same interface functions (``from_dict(.)``, ``to_dict(.)``, ``generate_orbits(.)``, ``__eq__(.)``) as in the in-built constellation classes.

References
------------
1. Space Mission Analysis and Design, 3rd ed, Section 7.6, Pg 194, 195.
2. https://realpython.com/factory-method-python/#supporting-additional-formats

Examples
^^^^^^^^^

1. Working with a Walker Delta Constellation.

   .. code-block:: python

         from orbitpy.constellation import ConstellationFactory

         factory = ConstellationFactory()
         specs = {"@type": 'Walker Delta Constellation', "date":{"@type": "JULIAN_DATE_UT1", "jd":2459270.75}, "numberSatellites": 2, "numberPlanes": 1,
                           "relativeSpacing": 1, "alt": 500, "ecc": 0.001, "inc": 45, "aop": 135, "@id": "abc"}
         wd_model = factory.get_constellation_model(specs) # initialization
         print(wd_model.generate_orbits())

         >> [OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': -4858.713737315466, 'y': 3435.629431500001, 'z': 3435.6294315, 'vx': -5.388312480793739, 'vy': -3.8101122943213612, 'vz': -3.810112294321361}, '@id': 'abc_11'}), 
             OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 4868.440891944725, 'y': -3442.5075685000006, 'z': -3442.5075685, 'vx': 5.377546621691256, 'vy': 3.8024996823446955, 'vz': 3.8024996823446946}, '@id': 'abc_12'})]


   .. code-block:: python

         from orbitpy.constellation import ConstellationFactory
         from orbitpy.util import OrbitState

         date =  OrbitState.date_from_dict({"@type": "JULIAN_DATE_UT1", "jd":2459270.75})
         wd_model = WalkerDeltaConstellation( date=date, numberSatellites=2, numberPlanes=1, relativeSpacing=1, alt=500, ecc=0.001, inc=45, aop=135, _id="abc")
         print(wd_model.generate_orbits())

         >> [OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': -4858.713737315466, 'y': 3435.629431500001, 'z': 3435.6294315, 'vx': -5.388312480793739, 'vy': -3.8101122943213612, 'vz': -3.810112294321361}, '@id': 'abc_11'}), 
             OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 4868.440891944725, 'y': -3442.5075685000006, 'z': -3442.5075685, 'vx': 5.377546621691256, 'vy': 3.8024996823446955, 'vz': 3.8024996823446946}, '@id': 'abc_12'})]


2. Working with a custom constellation.

   Register and initialize a constellation object ``NewConstellation2021`` with the label *New Constellation 2021*. The constellation consists of only 1 satellite with all Keplerian elements
   equal to 0 except the altitude which is supplied by the user.

   .. code-block:: python

         import propcov
         from orbitpy.util import OrbitState
         from orbitpy.constellation import ConstellationFactory

         class NewConstellation2021():
            def __init__(self, alt):
               self.alt = alt
               
            @staticmethod
            def from_dict(d):
               return NewConstellation2021(alt = d.get('alt', 0))
            
            def __eq__(self, other):
               if(isinstance(self, other.__class__)):
                     return (self.alt==other.alt)
               else:
                     return NotImplemented 
            
            def generate_orbits(self):

               orbits = []
               date = propcov.AbsoluteDate()
               state_dict = {"@type":"KEPLERIAN_EARTH_CENTERED_INERTIAL",  "sma": 6378 + self.alt, "ecc": 0, "inc": 0, "raan": 0, "aop": 0, "ta": 0}
               state = OrbitState.state_from_dict(state_dict)
               orbits.append(OrbitState(date, state, 0))

               return orbits

         factory = ConstellationFactory()
         factory.register_constellation_model('New Constellation 2021', NewConstellation2021) # register user defined constellation
         specs = {'@type': 'New Constellation 2021', 'alt': 700}
         const1 = factory.get_constellation_model(specs) # initialization of the constellation object const1
         print(const1.generate_orbits())

         >> [OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': -4858.713737315466, 'y': 3435.629431500001, 'z': 3435.6294315, 'vx': -5.388312480793739, 'vy': -3.8101122943213612, 'vz': -3.810112294321361}, '@id': 'abc_11'}), OrbitState.from_dict({'date': {'@type': 'JULIAN_DATE_UT1', 'jd': 2459270.75}, 'state': {'@type': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 4868.440891944725, 'y': -3442.5075685000006, 'z': -3442.5075685, 'vx': 5.377546621691256, 'vy': 3.8024996823446955, 'vz': 3.8024996823446946}, '@id': 'abc_12'})]



API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.constellation.ConstellationFactory
   orbitpy.constellation.WalkerDeltaConstellation
   orbitpy.constellation.TrainConstellation

