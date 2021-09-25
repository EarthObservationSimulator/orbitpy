""" *Unit tests for :class:`orbitpy.grid` module.*
"""
import unittest
import numpy as np
import os, shutil
import copy
import pandas as pd
import random

import propcov
from orbitpy.grid import Grid
import orbitpy.grid 
from orbitpy.util import OrbitState, Spacecraft
from instrupy import Instrument

class TestGridModuleFunction(unittest.TestCase):

    def test_compute_grid_res(self):
        """Test that the grid-resolution computed with precomputed for fixed values of orbit altitute and a sensor FOV (not the FOR)"""

        RE = 6378.137 # radius of Earth in kilometers
        instru1 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 20}}')
        instru2 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 5}}')
        instru3 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 15}}')
        instru4 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 25}}')
        instru5 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight":2, "angleWidth": 20}}')
        instru6 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfView": {"shape": "Rectangular", "angleHeight": 25, "angleWidth": 25}}')
        instru7 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 30, "angleWidth": 35}}')
        instru8 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 25, "angleWidth": 55}}')
        instru9 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 150, "angleWidth": 180}}')

        orbit1 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+700, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit2 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+710, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit3 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+510, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit4 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+1000, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit5 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+1100, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})

        # Test single sat, single instrument. The smallest fov dimension must be chosen.
        sats = [Spacecraft(orbitState=orbit1, instrument=[instru1])]
        self.assertAlmostEqual(orbitpy.grid.compute_grid_res(sats, 1), 1.100773132953890, delta = 0.01)

        # test with multiple satellites, choose smallest grid resolution.
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1]),
                Spacecraft(orbitState=orbit2, instrument=[instru2, instru3]),
                Spacecraft(orbitState=orbit3, instrument=[instru4]),
                Spacecraft(orbitState=orbit3, instrument=[instru5])]
        x = orbitpy.grid.compute_grid_res(sats, 1)
        sats = [Spacecraft(orbitState=orbit3, instrument=[instru5])]
        y = orbitpy.grid.compute_grid_res(sats, 1)
        self.assertAlmostEqual(x, y)

        # test with non-unitary grid-resolution factor
        sats = [Spacecraft(orbitState=orbit5, instrument=[instru6, instru7, instru8])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.grid.compute_grid_res(sats, f), 4.4012*f, delta = 0.01)

        # test when along-track fov is larger than the horizon angle = 119.64321275051853 deg
        sats = [Spacecraft(orbitState=orbit4,  instrument=[instru9])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.grid.compute_grid_res(sats, f), 60.3568*f, delta = 1)
        
class TestGrid(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

    def test_from_autogrid_dict(self):
        # typical case
        o = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 1)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 169)
        self.assertIsNone(o.filepath)

        #  case using default values
        o = Grid.from_autogrid_dict({"@type": "autogrid"})
        self.assertEqual(o._type, "Grid")
        self.assertIsNotNone(o._id)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 41252)
        self.assertIsNone(o.filepath)

    def test_from_custom_grid(self):
        # check with data file in the ``test_data``` folder
        covGridFilePath = self.dir_path+'/test_data/gridData.csv'
        o = Grid.from_customgrid_dict({"@type": "customGRID", "covGridFilePath": covGridFilePath, "@id": 5})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 5)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 140)
        self.assertEqual(o.filepath, covGridFilePath)

        true_data = pd.read_csv(covGridFilePath)
        test_data = o.get_lat_lon()

        self.assertEqual(len(true_data['lat [deg]']), len(test_data.latitude))

        for idx, val in enumerate(test_data.latitude):
            self.assertAlmostEqual(true_data['lat [deg]'][idx], test_data.latitude[idx], places=2) # places = 2 because data is rounded of to 3 decimal places
            self.assertAlmostEqual(true_data['lon [deg]'][idx], test_data.longitude[idx], places=2)
    
    def test_write_to_file(self):
        # typical case involving autoGrid
        out_file = self.out_dir+'/grid_test_write_to_file.csv'
        o = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        out_info = o.write_to_file(out_file)
        self.assertEqual(o.filepath, out_file)
        self.assertEqual(out_info.gridId, 1)
        self.assertEqual(out_info.gridFile, out_file)
        self.assertEqual(out_info._type, 'GridOutputInfo')
        self.assertIsNone(out_info._id)
        # check written data
        data = pd.read_csv(out_file)
        self.assertEqual(data.columns[0], 'lat [deg]')
        self.assertEqual(data.columns[1], 'lon [deg]')
        self.assertEqual(len(data['lat [deg]']), len(data['lon [deg]']))
        self.assertEqual(len(data['lat [deg]']), 169)
        self.assertTrue((data['lat [deg]']<=20).all()) 
        self.assertTrue((data['lat [deg]']>=15).all()) 
        self.assertTrue((data['lon [deg]']<=80).all())
        self.assertTrue((data['lon [deg]']>=45).all())  

    def test_from_dict(self):
        # AutoGrid
        o = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 1)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 169)
        self.assertIsNone(o.filepath)

        # CustomGrid
        o = Grid.from_customgrid_dict({"@type": "customGRID", "covGridFilePath": self.dir_path+'/test_data/gridData.csv', "@id": 5})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 5)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 140)
        self.assertEqual(o.filepath, self.dir_path+'/test_data/gridData.csv')

    def test_to_dict(self):
        o = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        out_file = self.out_dir + '/grid_test_to_dict.csv'
        o.write_to_file(out_file)
        d = o.to_dict()
        self.assertEqual(d['@type'], 'CUSTOMGRID')
        self.assertEqual(d['covGridFilePath'][-21:], 'grid_test_to_dict.csv')
        # check if file is written and is in proper format
        data = pd.read_csv(out_file)
        self.assertEqual(data.columns[0], 'lat [deg]')
        self.assertEqual(data.columns[1], 'lon [deg]')
        self.assertEqual(len(data['lat [deg]']), len(data['lon [deg]']))
        self.assertEqual(len(data['lat [deg]']), 169)
        self.assertTrue((data['lat [deg]']<=20).all()) 
        self.assertTrue((data['lat [deg]']>=15).all()) 
        self.assertTrue((data['lon [deg]']<=80).all())
        self.assertTrue((data['lon [deg]']>=45).all())

    def test_get_lat_lon_from_index(self):
        o = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})

        cdata = o.get_lat_lon() # complete data
        # single input index
        self.assertEqual(o.get_lat_lon_from_index(0), (cdata.latitude[0], cdata.longitude[0]))
        self.assertEqual(o.get_lat_lon_from_index(10), (cdata.latitude[10], cdata.longitude[10]))
        self.assertEqual(o.get_lat_lon_from_index([100]), (cdata.latitude[100], cdata.longitude[100]))
        # multiple input indices
        self.assertEqual(o.get_lat_lon_from_index([0,1,2]), ([cdata.latitude[0], cdata.latitude[1], cdata.latitude[2]], 
                                                             [cdata.longitude[0], cdata.longitude[1], cdata.longitude[2]]))
        self.assertEqual(o.get_lat_lon_from_index([10,1,5]), ([cdata.latitude[10], cdata.latitude[1], cdata.latitude[5]], 
                                                             [cdata.longitude[10], cdata.longitude[1], cdata.longitude[5]]))

    def test_get_lat_lon(self): #TODO
        pass

class TestGridOutputInfo(unittest.TestCase): #TODO
    pass
