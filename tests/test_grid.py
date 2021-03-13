""" *Unit tests for :class:`orbitpy.grid` module.*
"""
import unittest
import numpy as np
import os, shutil
import copy
import pandas as pd

import propcov
from orbitpy.grid import Grid
from orbitpy.grid import compute_grid_res

RE = 6378.137 # radius of Earth in kilometers
class TestPropagatorModuleFunction(unittest.TestCase):

    def test_compute_grid_res(self):
        pass
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

        #  case using default values
        o = Grid.from_autogrid_dict({"@type": "autogrid"})
        self.assertEqual(o._type, "Grid")
        self.assertIsNone(o._id)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 41252)

    def test_from_custom_grid(self):
        # check with data file in the ``test_data``` folder
        covGridFilePath = self.dir_path+'/test_data/gridData.csv'
        o = Grid.from_customgrid_dict({"@type": "customGRID", "covGridFilePath": covGridFilePath, "@id": 5})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 5)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 140)

        true_data = pd.read_csv(covGridFilePath)
        test_data = o.get_lat_lon()

        self.assertEqual(len(true_data['lat [deg]']), len(test_data.latitude))

        for idx, val in enumerate(test_data.latitude):
            self.assertAlmostEqual(true_data['lat [deg]'][idx], test_data.latitude[idx], places=1) # places = 2 because data is rounded of to 2 decimal places
            self.assertAlmostEqual(true_data['lon [deg]'][idx], test_data.longitude[idx], places=1)
    
    def test_write_to_file(self):
        # typical case involving autoGrid
        out_file = self.out_dir+'/grid_test_write_to_file.csv'
        o = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        o.write_to_file(out_file)
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

        # CustomGrid
        o = Grid.from_customgrid_dict({"@type": "customGRID", "covGridFilePath": self.dir_path+'/test_data/gridData.csv', "@id": 5})
        self.assertEqual(o._type, "Grid")
        self.assertEqual(o._id, 5)
        self.assertIsInstance(o.point_group, propcov.PointGroup)
        self.assertEqual(o.num_points, 140)

    def test_to_dict(self):
        o = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
        out_file = self.out_dir + '/grid_test_to_dict.csv'
        d = o.to_dict(out_file)
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

    def test_get_lat_lon(self): #TODO
        pass


