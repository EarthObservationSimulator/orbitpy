""" *Unit tests for :class:`orbitpy.datametricscalculator` module.*
"""
import unittest
import numpy as np
import sys
import os, shutil
import copy
import pandas as pd
import random
from collections import namedtuple

import propcov
from orbitpy.grid import Grid
import orbitpy.grid 
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus
from orbitpy.propagator import PropagatorFactory
from orbitpy.coveragecalculator import GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
from orbitpy.datametricscalculator import DataMetricsCalculator, AccessFileInfo

from instrupy.util import ViewGeometry, Orientation, SphericalGeometry
from instrupy import Instrument

sys.path.append('../')
from tests.util import spc1_json, spc2_json, spc3_json, spc4_json, spc5_json

class TestDataMetricCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

        # make and run the propagator for the spc1 spacecraft
        factory = PropagatorFactory()
        cls.spc1 = Spacecraft.from_json(spc1_json)
        step_size = 1
        duration = 0.05
        j2_prop = factory.get_propagator({"@type": 'J2 Analytical Propagator', "stepSize": step_size})
        cls.state_cart_file = cls.out_dir + '/test_cov_cart_states.csv'
        j2_prop.execute(spacecraft=cls.spc1, out_file_cart=cls.state_cart_file, duration=duration)

        # make grid object
        cls.grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1})
        
        # make the GridCoverage coverage calculator
        cls.grid_cov_calc = GridCoverage(grid=cls.grid, spacecraft=cls.spc1, state_cart_file=cls.state_cart_file)


    def test_from_dict(self):
        # Note that the current version does not check if the specified accessFileInfo are 'sensible'
        # test with spc1 spacecraft, single instrument, mode
        spc1 = Spacecraft.from_json(spc1_json)
        mode_id = spc1.instrument[0].get_mode_id()
        o = DataMetricsCalculator.from_dict({"spacecraft": spc1.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv", 
                                             "accessFileInfo": {"sensorId": "bs1", "modeId": mode_id[0], "accessFilePath": "C:/workspace/acc.csv"}, # single entry
                                             "@id":123})
        self.assertEqual(o.spacecraft, spc1)
        self.assertEqual(o.state_cart_file, "C:/workspace/state.csv")
        self.assertEqual(o.access_file_info[0], ("bs1", mode_id[0], "C:/workspace/acc.csv"))
        self.assertEqual(o._id, 123)
        self.assertEqual(o._type, "Data Metrics Calculator")

        # test with spc3 spacecraft, 3 instruments where 1,2 instruments have 1 mode each and the 3rd instrument has 3 modes
        spc3 = Spacecraft.from_json(spc3_json)
        o = DataMetricsCalculator.from_dict({"spacecraft": spc3.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv", 
                                             "accessFileInfo": [{"sensorId": "bs3", "modeId": 0, "accessFilePath": "C:/workspace/acc3_0.csv"}, # list of entries
                                                                {"sensorId": "bs3", "modeId": 1, "accessFilePath": "C:/workspace/acc3_1.csv"}
                                                                ],
                                             })
        self.assertEqual(o.spacecraft, spc3)
        self.assertEqual(o.state_cart_file, "C:/workspace/state.csv")
        self.assertEqual(o.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o.access_file_info[1], ("bs3", 1, "C:/workspace/acc3_1.csv"))
        self.assertIsNone(o._id)
        self.assertEqual(o._type, "Data Metrics Calculator")

    def test_add_access_file_info(self):
        
        spc3 = Spacecraft.from_json(spc3_json)
        o = DataMetricsCalculator.from_dict({"spacecraft": spc3.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv", 
                                             "accessFileInfo": [{"sensorId": "bs3", "modeId": 0, "accessFilePath": "C:/workspace/acc3_0.csv"}],
                                             "@id":"abc"})
        
        # check without adding
        self.assertEqual(o.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))

        # add info and check
        acc_info = AccessFileInfo("bs3", 1, "C:/workspace/acc3_1.csv")
        o.add_access_file_info(acc_info) 

        self.assertEqual(o.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o.access_file_info[1], ("bs3", 1, "C:/workspace/acc3_1.csv"))

        # add again 
        spc3_bs1_mode_id = spc3.get_instrument('bs1').get_mode_id()[0]
        acc_info = AccessFileInfo("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv")
        o.add_access_file_info(acc_info) 

        self.assertEqual(o.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o.access_file_info[1], ("bs3", 1, "C:/workspace/acc3_1.csv"))
        self.assertEqual(o.access_file_info[2], ("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv"))


    def test_search_access_file_info(self):
        pass

    def test_to_dict(self): #TODO
        pass

    '''
    def test_execute_0(self):
        """ Check the produced datametrics file format.
        
        """        

        

        # set access output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        self.grid_cov_calc.execute(sensor_id='bs1', mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.
        
        dm_calc = DataMetricsCalculator.from_dict({"spacecraft": self.spc1.to_dict(), 
                                                   "cartesianStateFilePath": self.state_cart_file, 
                                                   "accessFileInfo": {"sensorId": "bs1", "modeId": None, "accessFilePath": out_file_access},
                                                   "@id":123})

        # set the datametrics file path
        out_file_dm = self.out_dir+'/test_dm.csv'
        dm_calc.execute(out_datametrics_fl=out_file_dm, sensor_id='bs1')
    '''