"""Unit tests for orbitpy.coveragecalculator module.

``TestGridCoverage`` class:

* ``test_execute_0``: Test format of output access files.
* ``test_execute_1``: Roll Circular sensor tests
* ``test_execute_2``: Yaw Circular sensor tests
* ``test_execute_3``: Pitch Circular sensor tests
* ``test_execute_1``: Roll Rectangular sensor tests
* ``test_execute_3``: Pitch Rectangular sensor tests

"""
import os, shutil
import sys
import unittest
import pandas as pd

from orbitpy.coveragecalculator import CoverageCalculatorFactory, GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
import orbitpy.coveragecalculator
from orbitpy.util import Spacecraft

from instrupy.util import ViewGeometry, Orientation

sys.path.append('../')
from util.spacecrafts import spc1_json, spc2_json, spc3_json

RE = 6378.137 # radius of Earth in kilometers

class TestCoverageCalculatorFunctions(unittest.TestCase):   
                                
    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

    def test_helper_extract_coverage_parameters_of_spacecraft(self):
        
        # spc1 spacecraft, 1 instrument, 1 mode 
        spc1 = Spacecraft.from_json(spc1_json)
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc1)
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0].instru_id, 'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertEqual(x[0].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[0].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 15.0, '@id': None}})])
        self.assertEqual(x[0].pointing_option, [Orientation.from_dict({"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":2.5, "zRotation":0}),
                                                Orientation.from_dict({"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-2.5, "zRotation":0})])

        # spc2 spacecraft, no instruments 
        spc2 = Spacecraft.from_json(spc2_json)
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc2)
        self.assertEqual(x,[])

        # spc3 spacecraft, 3 instruments, 1st and 2nd instrument have 1 mode and 3rd instrument has 3 modes 
        spc3 = Spacecraft.from_json(spc3_json)
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc3)
        self.assertEqual(len(x), 5)
        # instrument 1        
        self.assertEqual(x[0].instru_id, 'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertEqual(x[0].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[0].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 15.0, '@id': None}})])
        self.assertIsNone(x[0].pointing_option)
        # instrument 2             
        self.assertIsNotNone(x[1].instru_id)
        self.assertEqual(x[1].mode_id, 101)
        self.assertEqual(x[1].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[1].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                          "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}})])
        self.assertEqual(x[1].pointing_option, [Orientation.from_dict({"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":10}),
                                                Orientation.from_dict({"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":15})])
        # instrument 3, mode 1         
        self.assertEqual(x[2].instru_id, 'bs3')
        self.assertEqual(x[2].mode_id, 0)
        
        self.assertEqual(x[2].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}}))
        self.assertEqual(x[2].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                                [
                                    ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                                 "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}}), 
                                    ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 347.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                                 "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}})
                                ]
                        )
        self.assertIsNone(x[2].pointing_option)
        # instrument 3, mode 2
        self.assertEqual(x[3].instru_id, 'bs3')
        self.assertEqual(x[3].mode_id, 1)        
        self.assertEqual(x[3].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 25.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}}))
        self.assertEqual(x[3].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                                [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}}), 
                                 ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 347.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}})]
                        )
        self.assertIsNone(x[3].pointing_option)
        # instrument 3, mode 3
        self.assertEqual(x[4].instru_id, 'bs3')
        self.assertIsNotNone(x[4].mode_id)        
        self.assertEqual(x[4].scene_field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': -25.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}}))
        self.assertEqual(x[4].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                                [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}}), 
                                 ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 347.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}})]
                        )
        self.assertIsNone(x[4].pointing_option)
      
    
    def test_find_in_cov_params_list(self):
        # spc1 spacecraft, 1 instrument, 1 mode
        spc1 = Spacecraft.from_json(spc1_json) 
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc1)
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs1', mode_id='0'), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id=None, mode_id=None), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs1', mode_id=None), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id=None, mode_id='0'), 
                         cov_param_list[0])
        with self.assertRaises(Exception):
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='axe', mode_id='1') # invalid sensor-id
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs1', mode_id='1') # invalid mode-id

        # spc2 spacecraft, no instruments 
        spc2 = Spacecraft.from_json(spc2_json)
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc2)
        with self.assertRaises(Exception):
            self.assertIsNone(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list)) # empty cov_param_list since spc2 has no instruments

        # spc3 spacecraft, 3 instruments, 1st and 2nd instrument have 1 mode and 3rd instrument has 3 modes 
        spc3 = Spacecraft.from_json(spc3_json)
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc3)
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs3', mode_id=1), 
                         cov_param_list[3])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs3', mode_id=None), 
                         cov_param_list[2])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id=None, mode_id=None), 
                         cov_param_list[0])
        with self.assertRaises(Exception):
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='axe', mode_id='1') # invalid sensor-id
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, instru_id='bs1', mode_id='1') # invalid mode-id

    def test_filter_mid_interval_access(self):
        """ Check the behavior of this function is as expected using pre-run results.
        """
        
        # file input, file output
        inp_acc_fl = self.dir_path + '/../test_data/accessData.csv'
        out_acc_fl = self.out_dir + '/test_filter_mid_interval_access.csv' 
        true_mid_interval_acc_fl = self.dir_path + '/../test_data/midIntervalAccessData.csv'
        orbitpy.coveragecalculator.filter_mid_interval_access(inp_acc_fl=inp_acc_fl, out_acc_fl=out_acc_fl)
        result_df = pd.read_csv(out_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        truth_df = pd.read_csv(true_mid_interval_acc_fl, skiprows = [0,1,2,3])
        self.assertTrue(result_df.equals(truth_df))
        
        # dataframe input, dataframe output
        inp_data = { 'time index': [ 0,  1,  2,  3,  4,  4,  4,  5,  5,  6,  6,  7,  8], 
                     'GP index'  : [10, 11, 11, 11, 12, 13, 14, 12, 13, 12, 10, 10, 11],
                     'lat [deg]' : [10.0, 11.0, 11.0, 11.0, 12.0, 13.0, 14.0, 12.0, 13.0, 12.0, 10.0, 10.0, 11.0],
                     'lon [deg]':  [10.0, 11.0, 11.0, 11.0, 12.0, 13.0, 14.0, 12.0, 13.0, 12.0, 10.0, 10.0, 11.0]}    
        inp_acc_df = pd.DataFrame(data = inp_data) 
        truth_df = pd.DataFrame({ 'time index': [  0,  2,  4,  4,  5,   7,  8 ], 
                                  'GP index'  : [ 10, 11, 13,  14, 12, 10, 11 ],
                                   'lat [deg]' : [10.0, 11.0, 13.0,  14.0, 12.0, 10.0, 11.0],
                                   'lon [deg]' : [10.0, 11.0, 13.0,  14.0, 12.0, 10.0, 11.0]})
        result_df = orbitpy.coveragecalculator.filter_mid_interval_access(inp_acc_df=inp_acc_df)
        self.assertTrue(result_df.equals(truth_df))

    def test_extract_auxillary_info_from_state_file(self): #TODO
        pass

class TestCoverageCalculatorFactory(unittest.TestCase):
  
    class DummyNewCoverageCalculator:
        def __init__(self, *args, **kwargs):
            pass
            
        def from_dict(self):
            return TestCoverageCalculatorFactory.DummyNewCoverageCalculator()

    def test___init__(self):
        factory = CoverageCalculatorFactory()

        # test the built-in coverage calculators are registered
        # GRID COVERAGE
        self.assertIn('GRID COVERAGE', factory._creators)
        self.assertEqual(factory._creators['GRID COVERAGE'], GridCoverage)
        # POINTING OPTIONS COVERAGE
        self.assertIn('POINTING OPTIONS COVERAGE', factory._creators)
        self.assertEqual(factory._creators['POINTING OPTIONS COVERAGE'], PointingOptionsCoverage)
        # POINTING OPTIONS WITH GRID COVERAGE
        self.assertIn('POINTING OPTIONS WITH GRID COVERAGE', factory._creators)
        self.assertEqual(factory._creators['POINTING OPTIONS WITH GRID COVERAGE'], PointingOptionsWithGridCoverage)

    def test_register_coverage_calculator(self):
        factory = CoverageCalculatorFactory()
        factory.register_coverage_calculator('New Cov Calc', TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        self.assertIn('New Cov Calc', factory._creators)
        self.assertEqual(factory._creators['New Cov Calc'], TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        # test the built-in coverage calculator remain registered after registration of new coverage calculator
        # GRID COVERAGE
        self.assertIn('GRID COVERAGE', factory._creators)
        self.assertEqual(factory._creators['GRID COVERAGE'], GridCoverage)
        # POINTING OPTIONS COVERAGE
        self.assertIn('POINTING OPTIONS COVERAGE', factory._creators)
        self.assertEqual(factory._creators['POINTING OPTIONS COVERAGE'], PointingOptionsCoverage)
        # POINTING OPTIONS WITH GRID COVERAGE
        self.assertIn('POINTING OPTIONS WITH GRID COVERAGE', factory._creators)
        self.assertEqual(factory._creators['POINTING OPTIONS WITH GRID COVERAGE'], PointingOptionsWithGridCoverage)

    def test_get_coverage_calculator(self):
        
        factory = CoverageCalculatorFactory()
        # register dummy coverage calculator
        factory.register_coverage_calculator('New Coverage Calc', TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        
        # test the coverage calculator model classes can be obtained depending on the input specifications
        # GRID COVERAGE
        specs = {"@type": 'GRID COVERAGE'} # in practice additional coverage calculator specs shall be present in the dictionary
        grid_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(grid_cov, GridCoverage)
        # POINTING OPTIONS COVERAGE
        specs = {"@type": 'POINTING OPTIONS COVERAGE'} # in practice additional coverage calculator specs shall be present in the dictionary
        popt_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(popt_cov, PointingOptionsCoverage)
        # POINTING OPTIONS WITH GRID COVERAGE
        specs = {"@type": 'POINTING OPTIONS WITH GRID COVERAGE'} # in practice additional coverage calculator specs shall be present in the dictionary
        popt_with_grid_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(popt_with_grid_cov, PointingOptionsWithGridCoverage)

        # DummyNewCoverageCalculator
        specs = {"@type": 'New Coverage Calc'} # in practice additional coverage calculator specs shall be present in the dictionary
        new_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(new_cov, TestCoverageCalculatorFactory.DummyNewCoverageCalculator)

class TestCoverageOutputInfo(unittest.TestCase): #TODO
    pass