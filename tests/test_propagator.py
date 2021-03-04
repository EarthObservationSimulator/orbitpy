"""Unit tests for orbitpy.propagator module.
"""
import json
import os
import sys
import unittest
import random

import numpy as np
from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import PropagatorFactory, J2AnalyticalPropagator
import orbitpy.propagator
import propcov
from instrupy import Instrument

class TestPropagatorModuleFunction(unittest.TestCase):

    def test_compute_time_step(self):
        """ Test that the time-step computed with precomputed values for fixed orbit altitude and sensor Along-Track **FOR** """
        RE = 6378.137 # radius of Earth in kilometers 

        # FOR = FOV for the below cases since default "FIXED" manueverability is used. The crosstrack FOV does not influence the results.
        instru1 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 15, "angleWidth": 0.01}}')
        instru2 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 25, "angleWidth": 0.01}}')
        instru3 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 35, "angleWidth": 0.01}}')
        instru4 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 150, "angleWidth": 0.01}}')

        orbit1 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit2 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+710, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit3 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+510, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit4 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+1000, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})

        # single satellite, multiple instruments
        sats = [Spacecraft(orbitState=orbit1, instrument=[instru1, instru2])]
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, 1), 18.6628, places=4)

        # single satellite, single instrument
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1])]
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, 1), 27.7324, places=4)

        # test with multiple satellites.
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1]),
                Spacecraft(orbitState=orbit2, instrument=[instru1, instru2, instru3]),
                Spacecraft(orbitState=orbit3, instrument=[instru2]),
                Spacecraft(orbitState=orbit3, instrument=[instru1])]
        x = orbitpy.propagator.compute_time_step(sats, 1)        

        sats = [Spacecraft(orbitState=orbit3, instrument=[instru1])]
        y = orbitpy.propagator.compute_time_step(sats, 1)
        self.assertAlmostEqual(x, y)

        # test with non-unitary time-resolution factor
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, f), 27.7324*f, places=4)

        # test when along-track fov is larger than the horizon angle = 119.64321275051853 deg
        sats = [Spacecraft(orbitState=orbit4, instrument=[instru4])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, f), 1057.437400519928*f)

class TestPropagatorFactory(unittest.TestCase):
  
    class DummyNewPropagator:
        def __init__(self, *args, **kwargs):
            pass
            
        def from_dict(self):
            return TestPropagatorFactory.DummyNewPropagator()

    def test___init__(self):
        factory = PropagatorFactory()

        # test the built-in propagators are registered
        self.assertIn('J2 Analytical Propagator', factory._creators)
        self.assertEqual(factory._creators['J2 Analytical Propagator'], J2AnalyticalPropagator)

    def test_register_propagator(self):
        factory = PropagatorFactory()
        factory.register_propagator('New Propagator', TestPropagatorFactory.DummyNewPropagator)
        self.assertIn('New Propagator', factory._creators)
        self.assertEqual(factory._creators['New Propagator'], TestPropagatorFactory.DummyNewPropagator)
        # test the built-in propagators remain registered after registration of new propagator
        self.assertIn('J2 Analytical Propagator', factory._creators)
        self.assertEqual(factory._creators['J2 Analytical Propagator'], J2AnalyticalPropagator)

    def test_get_propagator(self):
        
        factory = PropagatorFactory()
        # register dummy propagator
        factory.register_propagator('New Propagator', TestPropagatorFactory.DummyNewPropagator)
        
        # test the constellation model classes can be obtained depending on the input specifications
        # Walker Delta Constellation model
        specs = {"@type": 'J2 Analytical Propagator'} # in practice additional propagator specs shall be present in the dictionary
        j2_prop = factory.get_propagator(specs)
        self.assertIsInstance(j2_prop, J2AnalyticalPropagator)

        # DummyNewPropagator
        specs = {"@type": 'New Propagator'} # in practice additional propagator specs shall be present in the dictionary
        new_prop = factory.get_propagator(specs)
        self.assertIsInstance(new_prop, TestPropagatorFactory.DummyNewPropagator)
   