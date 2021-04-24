""" *Unit tests for :class:`orbitpy.datametricscalculator` module.*

* ``test_execute_0_1``: Test format of output datametric files with the GridCoverage access file input.
* ``test_execute_0_2``: Test format of output datametric files with the PointingOptionsCoverage access file input.
* ``test_execute_0_3``: Test format of output datametric files with the PointingOptionsWithGridCoverage access file input.

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
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory
from orbitpy.coveragecalculator import GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
from orbitpy.datametricscalculator import DataMetricsCalculator, DataMetricsOutputInfo, AccessFileInfo

sys.path.append('../')
from tests.util import spc1_json, spc3_json

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
        cls.step_size = 1
        cls.duration = 0.05
        j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": cls.step_size})
        cls.state_cart_file = cls.out_dir + '/test_cov_cart_states.csv'
        j2_prop.execute(spacecraft=cls.spc1, out_file_cart=cls.state_cart_file, duration=cls.duration)

        # make grid object
        cls.grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1})
        
        # make the GridCoverage coverage calculator
        cls.grid_cov_calc = GridCoverage(grid=cls.grid, spacecraft=cls.spc1, state_cart_file=cls.state_cart_file)
        # make the PointingOptionsCoverage coverage calculator
        cls.pnt_opt_calc = PointingOptionsCoverage(spacecraft=cls.spc1, state_cart_file=cls.state_cart_file)
        # make the PointingOptionsWithGridCoverage coverage calculator 
        cls.pnt_opt_with_grid_calc = PointingOptionsWithGridCoverage(grid=cls.grid, spacecraft=cls.spc1, state_cart_file=cls.state_cart_file)


    def test_from_dict(self):
        # Note that the current version does not check if the specified accessFileInfo are 'sensible'
        # test with spc1 spacecraft, single instrument, mode
        spc1 = Spacecraft.from_json(spc1_json)
        mode_id = spc1.instrument[0].get_mode_id()
        o = DataMetricsCalculator.from_dict({"spacecraft": spc1.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv", 
                                             "accessFileInfo": {"instruId": "bs1", "modeId": mode_id[0], "accessFilePath": "C:/workspace/acc.csv"}, # single entry
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
                                             "accessFileInfo": [{"instruId": "bs3", "modeId": 0, "accessFilePath": "C:/workspace/acc3_0.csv"}, # list of entries
                                                                {"instruId": "bs3", "modeId": 1, "accessFilePath": "C:/workspace/acc3_1.csv"}
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
        o1 = DataMetricsCalculator.from_dict({"spacecraft": spc3.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv", 
                                             "accessFileInfo": [{"instruId": "bs3", "modeId": 0, "accessFilePath": "C:/workspace/acc3_0.csv"}],
                                             "@id":"abc"})
        
        # check without adding
        self.assertEqual(o1.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))

        # add info and check
        acc_info = AccessFileInfo("bs3", 1, "C:/workspace/acc3_1.csv")
        o1.add_access_file_info(acc_info) 

        self.assertEqual(o1.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o1.access_file_info[1], ("bs3", 1, "C:/workspace/acc3_1.csv"))

        # add again 
        spc3_bs1_mode_id = spc3.get_instrument('bs1').get_mode_id()[0]
        acc_info = AccessFileInfo("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv")
        o1.add_access_file_info(acc_info) 

        self.assertEqual(o1.access_file_info[0], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o1.access_file_info[1], ("bs3", 1, "C:/workspace/acc3_1.csv"))
        self.assertEqual(o1.access_file_info[2], ("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv"))

        # try with no initial access-file info
        spc3 = Spacecraft.from_json(spc3_json)
        o2 = DataMetricsCalculator.from_dict({"spacecraft": spc3.to_dict(), 
                                              "cartesianStateFilePath": "C:/workspace/state.csv"}
                                             )
        # add modes        
        spc3_bs1_mode_id = spc3.get_instrument('bs1').get_mode_id()[0]
        acc_info = AccessFileInfo("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv")
        o2.add_access_file_info(acc_info)
        acc_info = AccessFileInfo("bs3", 0, "C:/workspace/acc3_0.csv")
        o2.add_access_file_info(acc_info)
        acc_info = AccessFileInfo("bs3", 1, "C:/workspace/acc3_1.csv")
        o2.add_access_file_info(acc_info)

        self.assertEqual(o2.access_file_info[0], ("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv"))
        self.assertEqual(o2.access_file_info[1], ("bs3", 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o2.access_file_info[2], ("bs3", 1, "C:/workspace/acc3_1.csv"))

    def test_search_access_file_info(self):
        spc3 = Spacecraft.from_json(spc3_json)
        o = DataMetricsCalculator.from_dict({"spacecraft": spc3.to_dict(), 
                                             "cartesianStateFilePath": "C:/workspace/state.csv"}
                                             )
        # add modes
        spc3_bs1_mode_id = spc3.get_instrument('bs1').get_mode_id()[0]
        acc_info = AccessFileInfo("bs1", spc3_bs1_mode_id, "C:/workspace/acc1_0.csv")
        o.add_access_file_info(acc_info)
        acc_info = AccessFileInfo("bs3", 0, "C:/workspace/acc3_0.csv")
        o.add_access_file_info(acc_info)
        acc_info = AccessFileInfo("bs3", 1, "C:/workspace/acc3_1.csv")
        o.add_access_file_info(acc_info)
        
        self.assertEqual(o.search_access_file_info(instru_id='bs3', mode_id=0), ('bs3', 0, "C:/workspace/acc3_0.csv"))
        self.assertEqual(o.search_access_file_info(instru_id='bs3', mode_id=1), ('bs3', 1, "C:/workspace/acc3_1.csv"))
        self.assertEqual(o.search_access_file_info(instru_id='bs3', mode_id=None), ('bs3', 0, "C:/workspace/acc3_0.csv"))

        self.assertEqual(o.search_access_file_info(instru_id='bs1', mode_id=None), ('bs1', spc3_bs1_mode_id, "C:/workspace/acc1_0.csv"))
        self.assertEqual(o.search_access_file_info(instru_id='bs1', mode_id=spc3_bs1_mode_id), ('bs1', spc3_bs1_mode_id, "C:/workspace/acc1_0.csv"))

    def test_to_dict(self): #TODO
        pass

    def test_execute_0_1(self):
        """ Check the produced datametrics file format with the GridCoverage access file input.
        
        """        
        # set access output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # set the datametrics file path
        out_file_dm = self.out_dir+'/test_dm.csv'
       
        # run the GridCoverage calculator
        self.grid_cov_calc.execute(instru_id='bs1', mode_id=None, use_field_of_regard=False, out_file_access=out_file_access)

        dm_calc = DataMetricsCalculator.from_dict({"spacecraft": self.spc1.to_dict(), 
                                                   "cartesianStateFilePath": self.state_cart_file, 
                                                   "accessFileInfo": {"instruId": "bs1", "modeId": None, "accessFilePath": out_file_access},
                                                   "@id":123})
        
        out_info = dm_calc.execute(out_datametrics_fl=out_file_dm, instru_id='bs1')

        self.assertEqual(out_info, DataMetricsOutputInfo.from_dict({"spacecraftId": self.spc1._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": None, # note here that modeId is None
                                                                    "accessFile": out_file_access,
                                                                    "dataMetricsFile": out_file_dm,
                                                                    "startDate": 2459270.75,
                                                                    "duration": self.duration, "@id":None}))

        # check the outputs
        epoch_JDUT1 = pd.read_csv(out_file_dm, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459270.75)

        _step_size = pd.read_csv(out_file_dm, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_dm, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(out_file_dm, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"GP index")
        self.assertEqual(column_headers.iloc[0][2],"pnt-opt index")
        self.assertEqual(column_headers.iloc[0][3],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][4],"lon [deg]")

    def test_execute_0_2(self):
        """ Check the produced datametrics file format with the PointingOptions access file input.
        
        """        
        # set access output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # set the datametrics file path
        out_file_dm = self.out_dir+'/test_dm.csv'

        # run the PointingOptionsCoverage calculator
        self.pnt_opt_calc.execute(instru_id=None, mode_id=None, out_file_access=out_file_access)

        dm_calc = DataMetricsCalculator.from_dict({"spacecraft": self.spc1.to_dict(), 
                                                   "cartesianStateFilePath": self.state_cart_file, 
                                                   "accessFileInfo": {"instruId": "bs1", "modeId": None, "accessFilePath": out_file_access},
                                                   "@id":123})

        out_info = dm_calc.execute(out_datametrics_fl=out_file_dm, instru_id='bs1')

        self.assertEqual(out_info, DataMetricsOutputInfo.from_dict({"spacecraftId": self.spc1._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": None, # note here that modeId is None
                                                                    "accessFile": out_file_access,
                                                                    "dataMetricsFile": out_file_dm,
                                                                    "startDate": 2459270.75,
                                                                    "duration": self.duration, "@id":None}))

        # check the outputs
        epoch_JDUT1 = pd.read_csv(out_file_dm, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459270.75)

        _step_size = pd.read_csv(out_file_dm, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_dm, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(out_file_dm, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"GP index")
        self.assertEqual(column_headers.iloc[0][2],"pnt-opt index")
        self.assertEqual(column_headers.iloc[0][3],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][4],"lon [deg]")

    def test_execute_0_3(self):
        """ Check the produced datametrics file format with the PointingOptionsWithGridCoverage access file input.
        
        """        
        # set access output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # set the datametrics file path
        out_file_dm = self.out_dir+'/test_dm.csv'

        # run the PointingOptionsCoverage calculator
        self.pnt_opt_calc.execute(instru_id=None, mode_id=None, out_file_access=out_file_access)

        dm_calc = DataMetricsCalculator.from_dict({"spacecraft": self.spc1.to_dict(), 
                                                   "cartesianStateFilePath": self.state_cart_file, 
                                                   "accessFileInfo": {"instruId": "bs1", "modeId": None, "accessFilePath": out_file_access},
                                                   "@id":123})

        out_info = dm_calc.execute(out_datametrics_fl=out_file_dm, instru_id='bs1')
        self.assertEqual(out_info, DataMetricsOutputInfo.from_dict({"spacecraftId": self.spc1._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": None, # note here that modeId is None
                                                                    "accessFile": out_file_access,
                                                                    "dataMetricsFile": out_file_dm,
                                                                    "startDate": 2459270.75,
                                                                    "duration": self.duration, "@id":None}))
                        
        # check the outputs
        epoch_JDUT1 = pd.read_csv(out_file_dm, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459270.75)

        _step_size = pd.read_csv(out_file_dm, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_dm, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(out_file_dm, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"GP index")
        self.assertEqual(column_headers.iloc[0][2],"pnt-opt index")
        self.assertEqual(column_headers.iloc[0][3],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][4],"lon [deg]")