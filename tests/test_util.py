"""Unit tests for orbitpy.util module.
"""

import json
import os
import sys
import unittest

import numpy
from instrupy.util import SphericalGeometry, Orientation, ViewGeometry, Maneuver, SyntheticDataConfiguration
from orbitpy.util import OrbitState
import propcov

class TestOrbitState(unittest.TestCase):
  
    def test_date_from_dict(self):
        x = OrbitState.date_from_dict({"dateType":"JULIAN_DATE_UT1", "jd":2459270.75})
        self.assertIsInstance(x, propcov.AbsoluteDate)

        y = OrbitState.date_from_dict({"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0})
        self.assertIsInstance(y, propcov.AbsoluteDate)

        self.assertEqual(x, y)

    def test_state_from_dict(self):
        x = OrbitState.state_from_dict({"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6867, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25})
        self.assertIsInstance(x, propcov.OrbitState)

        cart_state = x.GetCartesianState().GetRealArray()

        y = OrbitState.state_from_dict({"stateType": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": cart_state[0], "y": cart_state[1], "z": cart_state[2], "vx": cart_state[3], "vy": cart_state[4], "vz": cart_state[5]})
        self.assertIsInstance(y, propcov.OrbitState) 

        self.assertEqual(x, y)

    def test_date_to_dict(self): #@TODO
        pass

    def test_state_to_dict(self): #@TODO
        pass
    
    def test_get_julian_date(self): #@TODO
        pass
    
    def test_get_cartesian_earth_centered_inertial_state(self): #@TODO
        pass

    def test_get_kepleiran_earth_centered_inertial_state(self): #@TODO
        pass

    def test_from_dict(self):
        # Julian date, Cartesian state
        o = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75}, 
                                  "state":{"stateType": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": 6878.137, "y": 0, "z": 0, "vx": 0, "vy": 7.6126, "vz": 0},
                                  "@id": 123})
        self.assertIsInstance(o, OrbitState)
        self.assertEqual(o._id, 123)
        self.assertEqual(o.date, propcov.AbsoluteDate.fromJulianDate(2459270.75))
        self.assertEqual(o.state, propcov.OrbitState.fromCartesianState(propcov.Rvector6([6878.137,0,0,0,7.6126,0])))

        # Gregorian date, Keplerian state
        o = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, 
                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25},
                                  })
        self.assertIsInstance(o, OrbitState)
        self.assertIsNone(o._id)
        self.assertEqual(o.date, propcov.AbsoluteDate.fromGregorianDate(2021, 2, 25, 6 ,0, 0))
        self.assertEqual(o.state, propcov.OrbitState.fromKeplerianState(6878.137, 0.001, 45, 35, 145, -25))
    
    def test_to_dict(self): #@TODO test Keplerian state output
        # Input: Julian date, Cartesian state
        o = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75}, 
                                  "state":{"stateType": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": 6878.137, "y": 0, "z": 0, "vx": 0, "vy": 7.6126, "vz": 0},
                                 })
        d = o.to_dict()
        self.assertEqual(d["date"]["dateType"], "JULIAN_DATE_UT1")
        self.assertEqual(d["date"]["jd"], 2459270.75)
        self.assertEqual(d["state"]["stateType"], "CARTESIAN_EARTH_CENTERED_INERTIAL")
        self.assertAlmostEqual(d["state"]["x"], 6878.137)
        self.assertEqual(d["state"]["y"], 0)
        self.assertEqual(d["state"]["z"], 0)
        self.assertEqual(d["state"]["vx"], 0)
        self.assertEqual(d["state"]["vy"], 7.6126)
        self.assertEqual(d["state"]["vz"], 0)
        self.assertIsNone(d["@id"])

        # Input: Gregorian date, Keplerian state
        o = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, 
                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25},
                                  "@id": "123"})
        d = o.to_dict()
        date = o.get_julian_date()
        state = o.get_cartesian_earth_centered_inertial_state()
        self.assertEqual(d["date"]["dateType"], "JULIAN_DATE_UT1")
        self.assertEqual(d["date"]["jd"], date)
        self.assertEqual(d["state"]["stateType"], "CARTESIAN_EARTH_CENTERED_INERTIAL")
        self.assertAlmostEqual(d["state"]["x"], state[0])
        self.assertEqual(d["state"]["y"], state[1])
        self.assertEqual(d["state"]["z"], state[2])
        self.assertEqual(d["state"]["vx"], state[3])
        self.assertEqual(d["state"]["vy"], state[4])
        self.assertEqual(d["state"]["vz"], state[5])
        self.assertEqual(d["@id"], "123")
