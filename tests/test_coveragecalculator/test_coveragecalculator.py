"""Unit tests for orbitpy.coveragecalculator module.

``TestGridCoverage`` class:

* ``test_execute_0``: Test format of output access files.
* ``test_execute_1``: Roll Circular sensor tests
* ``test_execute_2``: Yaw Circular sensor tests
* ``test_execute_3``: Pitch Circular sensor tests
* ``test_execute_1``: Roll Rectangular sensor tests
* ``test_execute_3``: Pitch Rectangular sensor tests

"""

import json
import os, shutil
import sys
import unittest
import numpy as np
import pandas as pd
import random
import warnings 

import propcov
from orbitpy.coveragecalculator import CoverageCalculatorFactory, GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
import orbitpy.coveragecalculator
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus
from orbitpy.propagator import PropagatorFactory

from instrupy.util import ViewGeometry, Orientation, SphericalGeometry
from instrupy import Instrument

sys.path.append('../')
from tests.util import spc1, spc2, spc3

RE = 6378.137 # radius of Earth in kilometers

class TestCoverageCalculatorFunctions(unittest.TestCase):   
                                
    def test_helper_extract_coverage_parameters_of_spacecraft(self):
        
        # spc1 spacecraft, 1 instrument, 1 mode 
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc1)
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0].instru_id, 'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertEqual(x[0].field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[0].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 15.0, '@id': None}})])
        
        # spc2 spacecraft, no instruments 
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc2)
        self.assertEqual(x,[])

        # spc3 spacecraft, 3 instruments, 1st and 2nd instrument have 1 mode and 3rd instrument has 3 modes 
        x = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc3)
        self.assertEqual(len(x), 5)
        # instrument 1        
        self.assertEqual(x[0].instru_id, 'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertEqual(x[0].field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[0].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 15.0, '@id': None}})])
        # instrument 2             
        self.assertIsNotNone(x[1].instru_id)
        self.assertEqual(x[1].mode_id, 101)
        self.assertEqual(x[1].field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 0.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'CIRCULAR', 'diameter': 5.0, '@id': None}}))
        self.assertEqual(x[1].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                            [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                          "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}})])
        # instrument 3, mode 1         
        self.assertEqual(x[2].instru_id, 'bs3')
        self.assertEqual(x[2].mode_id, 0)
        
        self.assertEqual(x[2].field_of_view, 
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
        # instrument 3, mode 2
        self.assertEqual(x[3].instru_id, 'bs3')
        self.assertEqual(x[3].mode_id, 1)        
        self.assertEqual(x[3].field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 25.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}}))
        self.assertEqual(x[3].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                                [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}}), 
                                 ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 347.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}})]
                        )
        # instrument 3, mode 3
        self.assertEqual(x[4].instru_id, 'bs3')
        self.assertIsNotNone(x[4].mode_id)        
        self.assertEqual(x[4].field_of_view, 
                            ViewGeometry.from_dict({"orientation":{'referenceFrame': 'SC_BODY_FIXED', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': -25.0, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                         "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5.0, 'angleWidth': 10, '@id': None}}))
        self.assertEqual(x[4].field_of_regard, # note that the field-of-regard is a list of ViewGeometry objects
                                [ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 12.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}}), 
                                 ViewGeometry.from_dict({"orientation":{'referenceFrame': 'NADIR_POINTING', 'convention': 'EULER', 'eulerAngle1': 0.0, 'eulerAngle2': 347.5, 'eulerAngle3': 0.0, 'eulerSeq1': 1, 'eulerSeq2': 2, 'eulerSeq3': 3, '@id': None}, 
                                              "sphericalGeometry":{'shape': 'RECTANGULAR', 'angleHeight': 5, 'angleWidth': 15, '@id': None}})]
                        )
      
    
    def test_find_in_cov_params_list(self):
        # spc1 spacecraft, 1 instrument, 1 mode 
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc1)
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs1', mode_id='0'), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id=None, mode_id=None), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs1', mode_id=None), 
                         cov_param_list[0])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id=None, mode_id='0'), 
                         cov_param_list[0])
        with self.assertRaises(Exception):
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='axe', mode_id='1') # invalid sensor-id
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs1', mode_id='1') # invalid mode-id

        # spc2 spacecraft, no instruments 
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc2)
        self.assertIsNone(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list))

        # spc3 spacecraft, 3 instruments, 1st and 2nd instrument have 1 mode and 3rd instrument has 3 modes 
        cov_param_list = orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft(spc3)
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs3', mode_id=1), 
                         cov_param_list[3])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs3', mode_id=None), 
                         cov_param_list[2])
        self.assertEqual(orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id=None, mode_id=None), 
                         cov_param_list[0])
        with self.assertRaises(Exception):
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='axe', mode_id='1') # invalid sensor-id
            orbitpy.coveragecalculator.find_in_cov_params_list(cov_param_list=cov_param_list, sensor_id='bs1', mode_id='1') # invalid mode-id

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
        # Grid Coverage
        self.assertIn('Grid Coverage', factory._creators)
        self.assertEqual(factory._creators['Grid Coverage'], GridCoverage)
        # Pointing Options Coverage
        self.assertIn('Pointing Options Coverage', factory._creators)
        self.assertEqual(factory._creators['Pointing Options Coverage'], PointingOptionsCoverage)
        # Pointing Options With Grid Coverage
        self.assertIn('Pointing Options With Grid Coverage', factory._creators)
        self.assertEqual(factory._creators['Pointing Options With Grid Coverage'], PointingOptionsWithGridCoverage)

    def test_register_coverage_calculator(self):
        factory = CoverageCalculatorFactory()
        factory.register_coverage_calculator('New Cov Calc', TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        self.assertIn('New Cov Calc', factory._creators)
        self.assertEqual(factory._creators['New Cov Calc'], TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        # test the built-in coverage calculator remain registered after registration of new coverage calculator
        # Grid Coverage
        self.assertIn('Grid Coverage', factory._creators)
        self.assertEqual(factory._creators['Grid Coverage'], GridCoverage)
        # Pointing Options Coverage
        self.assertIn('Pointing Options Coverage', factory._creators)
        self.assertEqual(factory._creators['Pointing Options Coverage'], PointingOptionsCoverage)
        # Pointing Options With Grid Coverage
        self.assertIn('Pointing Options With Grid Coverage', factory._creators)
        self.assertEqual(factory._creators['Pointing Options With Grid Coverage'], PointingOptionsWithGridCoverage)

    def test_get_coverage_calculator(self):
        
        factory = CoverageCalculatorFactory()
        # register dummy coverage calculator
        factory.register_coverage_calculator('New Coverage Calc', TestCoverageCalculatorFactory.DummyNewCoverageCalculator)
        
        # test the coverage calculator model classes can be obtained depending on the input specifications
        # Grid Coverage
        specs = {"@type": 'Grid Coverage'} # in practice additional coverage calculator specs shall be present in the dictionary
        grid_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(grid_cov, GridCoverage)
        # Pointing Options Coverage
        specs = {"@type": 'Pointing Options Coverage'} # in practice additional coverage calculator specs shall be present in the dictionary
        grid_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(grid_cov, PointingOptionsCoverage)
        # Pointing Options With Grid Coverage
        specs = {"@type": 'Pointing Options With Grid Coverage'} # in practice additional coverage calculator specs shall be present in the dictionary
        grid_cov = factory.get_coverage_calculator(specs)
        self.assertIsInstance(grid_cov, PointingOptionsWithGridCoverage)

        # DummyNewCoverageCalculator
        specs = {"@type": 'New Coverage Calc'} # in practice additional coverage calculator specs shall be present in the dictionary
        new_prop = factory.get_coverage_calculator(specs)
        self.assertIsInstance(new_prop, TestCoverageCalculatorFactory.DummyNewCoverageCalculator)