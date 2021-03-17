"""Unit tests for orbitpy.coveragecalculator module.
"""

import json
import os, shutil
import sys
import unittest
import numpy as np
import pandas as pd
import random

import propcov
from orbitpy.coveragecalculator import CoverageCalculatorFactory, GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
import orbitpy.coveragecalculator
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus
from orbitpy.propagator import PropagatorFactory

from instrupy.util import ViewGeometry, Orientation, SphericalGeometry
from instrupy import Instrument

from .util import spc1, spc2, spc3

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
    
class TestGridCoverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

        # make propagator
        factory = PropagatorFactory()
        cls.step_size = random.uniform(10,60)
        cls.j2_prop = factory.get_propagator({"@type": 'J2 Analytical Propagator', "stepSize": cls.step_size})

    def test_from_dict(self):
        pass

    def test_execute_1(self):
        """ Check the produced access file format.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=random.random()
        orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                                       "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
                                                "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                                                "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                                       })

        instrument = Instrument.from_dict({"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": random.uniform(5,35) }, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, "@id":"bs1", "@type":"Basic Sensor"})

        spacecraftBus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}})

        sat = Spacecraft(orbitState=orbit, instrument=instrument, spacecraftBus=spacecraftBus)

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":0, "latLower":-10, "lonUpper":10, "lonLower":0, "gridRes": 1})
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # check the outputs
        epoch_JDUT1 = pd.read_csv(out_file_access, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.0)

        _step_size = pd.read_csv(out_file_access, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_access, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, duration)

        column_headers = pd.read_csv(out_file_access, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"GP index")

    def test_execute_2(self):
        """ Orient the sensor with roll, and an equatorial orbit and check that the ground-points captured are on either
            side of hemisphere only. (Conical Sensor)
        """ 
        ############ positive roll ############
        # setup spacecraft with some parameters setup randomly     
        duration = 0.25
        orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                                       "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
                                                "ecc": 0, "inc": 0, "raan": random.uniform(0,360), 
                                                "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                                       })

        instrument = Instrument.from_dict({"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":15}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, "@id":"bs1", "@type":"Basic Sensor"})

        spacecraftBus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}})

        sat = Spacecraft(orbitState=orbit, instrument=instrument, spacecraftBus=spacecraftBus)

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 5})
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        # check the outputs
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
       
        ############ negative roll ############
        # no need to run the propagator again
        instrument = Instrument.from_dict({"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":-15}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, "@id":"bs1", "@type":"Basic Sensor"})

        sat = Spacecraft(orbitState=orbit, instrument=instrument, spacecraftBus=spacecraftBus)

        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        # check the outputs
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
            self.assertTrue(all(x < 0 for x in lat))



        
    
    

      



