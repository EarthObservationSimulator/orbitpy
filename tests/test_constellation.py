"""Unit tests for orbitpy.constellation module.
"""

import json
import os
import sys
import unittest
import numpy as np

from orbitpy.util import OrbitState
from orbitpy.constellation import ConstellationFactory, WalkerDeltaConstellation, CustomOrbit, TrainConstellation
import propcov

RE = 6378.137 # radius of Earth in km

def angle_difference(a, b):
    """ Compute angle difference (b-a) in the range of -180 deg to 180 deg.

    :param a: Angle in degrees.
    :paramtype: float

    :param b: Angle in degrees.
    :paramtype b: float:

    :returns: (b-a) in range of -180 deg to 180 deg.
    :rtype: float

    Usage:

    .. code-block:: python

        >> angle_difference(1,3)
        2
        >> angle_difference(1,358)
        -3
        
    """
    c = (b - a) % 360
    if c > 180:
       c -= 360
    return c

class TestConstellationFactory(unittest.TestCase):
  
    class DummyNewConstellation:
        def __init__(self, *args, **kwargs):
            pass
            
        def from_dict(self):
            return TestConstellationFactory.DummyNewConstellation()

    def test___init__(self):
        factory = ConstellationFactory()

        # test the built-in constellation models are registered
        self.assertIn('Walker Delta Constellation', factory._creators)
        self.assertEqual(factory._creators['Walker Delta Constellation'], WalkerDeltaConstellation)
        self.assertIn('Train Constellation', factory._creators)
        self.assertEqual(factory._creators['Train Constellation'], TrainConstellation)
    
    def test_register_constellation_model(self):
        factory = ConstellationFactory()
        factory.register_constellation_model('New Constellation 2021', TestConstellationFactory.DummyNewConstellation)
        self.assertIn('New Constellation 2021', factory._creators)
        self.assertEqual(factory._creators['New Constellation 2021'], TestConstellationFactory.DummyNewConstellation)
        # test the built-in constellation models remain registered after registration of new model
        self.assertIn('Walker Delta Constellation', factory._creators)
        self.assertEqual(factory._creators['Walker Delta Constellation'], WalkerDeltaConstellation)
        self.assertIn('Train Constellation', factory._creators)
        self.assertEqual(factory._creators['Train Constellation'], TrainConstellation)

    def test_get_constellation_model(self):
        
        factory = ConstellationFactory()
        # register dummy constellation model
        factory.register_constellation_model('New Constellation 2021', TestConstellationFactory.DummyNewConstellation)
        
        # test the constellation model classes can be obtained depending on the input specifications
        # Walker Delta Constellation model
        specs = {"@type": 'Walker Delta Constellation', "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}} # in practice additional constellation specs shall be present in the dictionary
        wd_model = factory.get_constellation_model(specs)
        self.assertIsInstance(wd_model, WalkerDeltaConstellation)

        # add test for train constellation   @TODO

        # DummyNewConstellation
        specs = {"@type": 'New Constellation 2021'} # in practice additional constellation specs shall be present in the dictionary
        dc_model = factory.get_constellation_model(specs)
        self.assertIsInstance(dc_model, TestConstellationFactory.DummyNewConstellation)
   
class TestWalkerDeltaConstellation(unittest.TestCase):
    
    factory = ConstellationFactory()

    def test_from_dict(self):
        # typical case
        specs = {"@type": 'Walker Delta Constellation', 
                  "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75},
                  "numberSatellites": 2,
                  "numberPlanes": 1,
                  "relativeSpacing": 1,
                  "alt": 500,
                  "ecc": 0.001,
                  "inc": 45,
                  "aop": 135,
                  "@id": "abc"}
        wd_model = TestWalkerDeltaConstellation.factory.get_constellation_model(specs)
        self.assertIsInstance(wd_model, WalkerDeltaConstellation) 
        self.assertEqual(wd_model._id, "abc")
        self.assertEqual(wd_model._type, "Walker Delta Constellation")
        self.assertEqual(wd_model.date, OrbitState.date_from_dict({"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}))
        self.assertEqual(wd_model.numberSatellites, 2)
        self.assertEqual(wd_model.numberPlanes, 1)
        self.assertEqual(wd_model.relativeSpacing, 1)
        self.assertEqual(wd_model.alt, 500)
        self.assertEqual(wd_model.ecc, 0.001)
        self.assertEqual(wd_model.inc, 45)
        self.assertEqual(wd_model.aop, 135)
        
        # minimal definition, defaults shall be applied
        specs = {"@type": 'Walker Delta Constellation'} 
        wd_model = TestWalkerDeltaConstellation.factory.get_constellation_model(specs)
        self.assertIsInstance(wd_model, WalkerDeltaConstellation) 
        self.assertIsNotNone(wd_model._id)
        self.assertEqual(wd_model._type, "Walker Delta Constellation")
        self.assertEqual(wd_model.date, OrbitState.date_from_dict({"dateType": "JULIAN_DATE_UT1", "jd":2415019.5}))
        self.assertEqual(wd_model.numberSatellites, 3)
        self.assertEqual(wd_model.numberPlanes, 3)
        self.assertEqual(wd_model.relativeSpacing, 1)
        self.assertEqual(wd_model.alt, 500)
        self.assertEqual(wd_model.ecc, 0)
        self.assertEqual(wd_model.inc, 98.22)
        self.assertEqual(wd_model.aop, 135)
    
    def test_to_dict(self): #@TODO
        pass
    
    def test___eq__(self): #@TODO
        pass

    def test_generate_orbits_1(self):
        """ Test the calculation of Keplerian elements of the orbits given the Walker Delta Constellation constellation
            parameters by comparing to the partial truth data from SMAD 4th ed, pg. 274, Table 10.26.
        """
        # partial truth data from SMAD 4th ed, Pg. 274, Table 10.26.
        specs = {"@type": 'Walker Delta Constellation', 
                  "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75},
                  "numberSatellites": 15,
                  "numberPlanes": 5,
                  "relativeSpacing": 1,
                  "alt": 500,
                  "ecc": 0.2,
                  "inc": 54,
                  "aop": 0
                }
        wd_model = TestWalkerDeltaConstellation.factory.get_constellation_model(specs)
        orbits = wd_model.generate_orbits()

        # convert list of propcov.OrbitState objects to list of dictionaries
        orbit_dict = []
        for orb in orbits:
            orbit_dict.append(orb.to_dict(state_type="KEPLERIAN_EARTH_CENTERED_INERTIAL")["state"])
        
        self.assertEqual(len(orbit_dict), 15) # 15 satellites, hence 15 orbits

        # all orbits have the same inclination, altitude and eccentricity
        for orb in orbit_dict:
            self.assertAlmostEqual(orb["inc"], 54)
            self.assertAlmostEqual(orb["sma"], RE+500, delta= 5)
            self.assertAlmostEqual(orb["ecc"], 0.2)
            self.assertAlmostEqual(angle_difference(orb["aop"], 0), 0, 5)
        
        # 3 satellites per plane, consecutive 3 satellites shall have the same RAAN
        plane1_raan = orbit_dict[0]["raan"]
        self.assertAlmostEqual(angle_difference(plane1_raan, orbit_dict[1]["raan"]), 0)
        self.assertAlmostEqual(angle_difference(plane1_raan, orbit_dict[2]["raan"]), 0)

        plane2_raan = orbit_dict[3]["raan"]
        self.assertAlmostEqual(plane2_raan, orbit_dict[4]["raan"])
        self.assertAlmostEqual(plane2_raan, orbit_dict[5]["raan"])

        plane3_raan = orbit_dict[6]["raan"]
        self.assertAlmostEqual(plane3_raan, orbit_dict[7]["raan"])
        self.assertAlmostEqual(plane3_raan, orbit_dict[8]["raan"])

        plane4_raan = orbit_dict[9]["raan"]
        self.assertAlmostEqual(plane4_raan, orbit_dict[10]["raan"])
        self.assertAlmostEqual(plane4_raan, orbit_dict[11]["raan"])

        plane5_raan = orbit_dict[12]["raan"]
        self.assertAlmostEqual(plane5_raan, orbit_dict[13]["raan"])
        self.assertAlmostEqual(plane5_raan, orbit_dict[14]["raan"])

        # the raans are uniformly spaced
        raan_spacing = 36
        self.assertAlmostEqual(plane2_raan-plane1_raan, raan_spacing)
        self.assertAlmostEqual(plane3_raan-plane2_raan, raan_spacing)
        self.assertAlmostEqual(plane4_raan-plane3_raan, raan_spacing)
        self.assertAlmostEqual(plane5_raan-plane4_raan, raan_spacing)
        self.assertAlmostEqual(plane5_raan-plane1_raan, 180 - raan_spacing)

        # check inplane spacing between satellites
        in_plane_spc = 120
        self.assertAlmostEqual(orbit_dict[1]["ta"] - orbit_dict[0]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[2]["ta"] - orbit_dict[1]["ta"], in_plane_spc)

        self.assertAlmostEqual(orbit_dict[4]["ta"] - orbit_dict[3]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[5]["ta"] - orbit_dict[4]["ta"], in_plane_spc)

        self.assertAlmostEqual(orbit_dict[7]["ta"] - orbit_dict[6]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[8]["ta"] - orbit_dict[7]["ta"], in_plane_spc)

        self.assertAlmostEqual(orbit_dict[10]["ta"] - orbit_dict[9]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[11]["ta"] - orbit_dict[10]["ta"], in_plane_spc)

        self.assertAlmostEqual(orbit_dict[13]["ta"] - orbit_dict[12]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[14]["ta"] - orbit_dict[13]["ta"], in_plane_spc)

        # check phase difference between adjacent planes
        phase_diff = 24
        self.assertAlmostEqual(orbit_dict[3]["ta"] - orbit_dict[0]["ta"], phase_diff)
        self.assertAlmostEqual(orbit_dict[6]["ta"] - orbit_dict[3]["ta"], phase_diff)
        self.assertAlmostEqual(orbit_dict[9]["ta"] - orbit_dict[6]["ta"], phase_diff)
        self.assertAlmostEqual(orbit_dict[12]["ta"] - orbit_dict[9]["ta"], phase_diff)
    
    def test_generate_orbits_2(self):
        """ Test the calculation of Keplerian elements of the orbits given the Walker Delta constellation
            parameters using fixed inputs and expected outputs. """
        
        specs = {"@type": 'Walker Delta Constellation', 
                  "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75},
                  "numberSatellites": 6,
                  "numberPlanes": 3,
                  "relativeSpacing": 2,
                  "alt": 700,
                  "ecc": 0.001,
                  "inc": 98,
                  "aop": 10
                }
        wd_model = TestWalkerDeltaConstellation.factory.get_constellation_model(specs)
        orbits = wd_model.generate_orbits()

        # convert list of propcov.OrbitState objects to list of dictionaries
        orbit_dict = []
        for orb in orbits:
            orbit_dict.append(orb.to_dict(state_type="KEPLERIAN_EARTH_CENTERED_INERTIAL")["state"])

        
        self.assertEqual(len(orbit_dict), 6) # 6 satellites, hence 24 orbits
        # all orbits have the same inclination, altitude and eccentrivity
        for orb in orbit_dict:
            self.assertAlmostEqual(orb["inc"], 98)
            self.assertAlmostEqual(orb["sma"], RE+700, delta= 5)
            self.assertAlmostEqual(orb["ecc"], 0.001)
            self.assertAlmostEqual(orb["aop"], 10)
        
        # 3 satellites per plane, consecutive 3 satellites shall have the same RAAN
        plane1_raan = orbit_dict[0]["raan"]
        self.assertAlmostEqual(plane1_raan, orbit_dict[1]["raan"])

        plane2_raan = orbit_dict[2]["raan"]
        self.assertAlmostEqual(plane2_raan, orbit_dict[3]["raan"])

        plane3_raan = orbit_dict[4]["raan"]
        self.assertAlmostEqual(plane3_raan, orbit_dict[5]["raan"])

        # the raans are uniformly spaced
        raan_spacing = 60
        self.assertAlmostEqual(plane2_raan-plane1_raan, raan_spacing)
        self.assertAlmostEqual(plane3_raan-plane2_raan, raan_spacing)
        self.assertAlmostEqual(plane3_raan-plane1_raan, 180 - raan_spacing)

        # check inplane spacing between satellites
        in_plane_spc = 180
        self.assertAlmostEqual(orbit_dict[1]["ta"] - orbit_dict[0]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[3]["ta"] - orbit_dict[2]["ta"], in_plane_spc)
        self.assertAlmostEqual(orbit_dict[5]["ta"] - (-360+orbit_dict[4]["ta"]), in_plane_spc)

        # check phase difference between adjacent planes
        phase_diff = 360/6 * 2
        self.assertAlmostEqual(orbit_dict[2]["ta"] - orbit_dict[0]["ta"], phase_diff)
        self.assertAlmostEqual(orbit_dict[4]["ta"] - orbit_dict[2]["ta"], phase_diff)
  