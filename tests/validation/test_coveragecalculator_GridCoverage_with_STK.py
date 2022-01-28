""" *Tests for :class:`orbitpy.coveragecalculator.GridCoverage` covering checks on coverage calculations.*

   :code:`/temp/` folder contains temporary files produced during the run of the tests below.

   In case of rectangular sensors, both the methods to evaluate point in spherical polygon: 
   (1) 'ProjectedSphericalPointInPolygon' and (2) 'DirectSphericalPointInPolygon' are evaluated.


Expected output:

running test_run_1
    Metric 1 = 0.0
    Metric 2 = 0.032552316222500446
    Metric 3 = 0.0
    /mnt/hgfs/Workspace/orbits/tests/validation/test_coveragecalculator_GridCoverage_with_STK.py:126: RuntimeWarning: invalid value encountered in true_divide
    percentDiff = (val1 - val2) / ((val1 + val2)/2)
    Metric 4 = 0.03254995104368853
.running test_run_2
    Metric 1 = 0.0
    Metric 2 = 0.027351619401828606
    Metric 3 = 0.0
    Metric 4 = 0.027360240923878468
    Metric 1 = 0.0
    Metric 2 = 0.0349644952145724
    Metric 3 = 0.0
    Metric 4 = 0.034972028697688215
    Metric 1 = 0.0
    Metric 2 = 0.0349644952145724
    Metric 3 = 0.0
    Metric 4 = 0.034972028697688215
.running test_run_3
    Metric 1 = 0.011299435028248588
    Metric 2 = 0.0487277728657039
    Metric 3 = 0.0
    Metric 4 = 0.048785100840058895
.running test_run_4
    Metric 1 = 0.06567164179104477
    Metric 2 = 0.024124363026510998
    Metric 3 = 0.03793335778447373
    Metric 4 = 0.09644321627687324
    Metric 1 = 0.06567164179104477
    Metric 2 = 0.004983707111366686
    Metric 3 = 0.02290187259347255
    Metric 4 = 0.08815447786159897
    Metric 1 = 0.06567164179104477
    Metric 2 = 0.004983707111366686
    Metric 3 = 0.02290187259347255
    Metric 4 = 0.08815447786159897
.running test_run_5
    Metric 1 = 0.014388489208633094
    Metric 2 = 0.0031863458154967237
    Metric 3 = 0.00021791009457724432
    Metric 4 = 0.07603155144354741
.running test_run_6
    Metric 1 = 0.027906976744186046
    Metric 2 = 0.011098242896627185
    Metric 3 = 0.006512338499127888
    Metric 4 = 0.06387346139311226
    Metric 1 = 0.02177293934681182
    Metric 2 = 0.004905830607871885
    Metric 3 = 0.00796079059695783
    Metric 4 = 0.05950197935907679
    Metric 1 = 0.02177293934681182
    Metric 2 = 0.004905830607871885
    Metric 3 = 0.00796079059695783
    Metric 4 = 0.05950197935907679
.running test_run_7
    Metric 1 = 0.028985507246376812
    Metric 2 = 0.0181360201511335
    Metric 3 = 0.007297669101346621
    Metric 4 = 0.16895302213006513
.running test_run_8
    Metric 1 = 0.01818181818181818
    Metric 2 = 0.019172021489518593
    Metric 3 = 0.008317239324106392
    Metric 4 = 0.03505963044704963
.running test_run_9
    Metric 1 = 0.02570694087403599
    Metric 2 = 0.033531429675798426
    Metric 3 = 0.008346624779592682
    Metric 4 = 0.18750643736786
    Metric 1 = 0.02570694087403599
    Metric 2 = 0.051606108478146395
    Metric 3 = 0.020229898909291343
    Metric 4 = 0.18419062875395892
    Metric 1 = 0.02570694087403599
    Metric 2 = 0.051606108478146395
    Metric 3 = 0.020229898909291343
    Metric 4 = 0.18419062875395892
..running test_run_10
    Metric 1 = 0.08284023668639054
    Metric 2 = 0.014835102133972385
    Metric 3 = 0.022065168404711993
    Metric 4 = 0.158437778889485
    Metric 1 = 0.08284023668639054
    Metric 2 = 0.0011321181931393638
    Metric 3 = 0.0068187464465237655
    Metric 4 = 0.14977532476218797
    Metric 1 = 0.08284023668639054
    Metric 2 = 0.0011321181931393638
    Metric 3 = 0.0068187464465237655
    Metric 4 = 0.14977532476218797
.running test_run_11
    Metric 1 = 0.0035149384885764497
    Metric 2 = 0.004649320682589155
    Metric 3 = 0.011625970590382005
    Metric 4 = 0.061990025361950384
    Metric 1 = 0.0035149384885764497
    Metric 2 = 0.023032433077986112
    Metric 3 = 0.027677453427470747
    Metric 4 = 0.06486607660238537
    Metric 1 = 0.0035149384885764497
    Metric 2 = 0.023032433077986112
    Metric 3 = 0.027677453427470747
    Metric 4 = 0.06486607660238537
.running test_run_12
    Metric 1 = 0.0030441400304414
    Metric 2 = 0.023835051546391754
    Metric 3 = 0.012280177278458697
    Metric 4 = 0.25664036683286595
    Metric 1 = 0.0030534351145038168
    Metric 2 = 0.0012640936244826392
    Metric 3 = 0.032688511755585715
    Metric 4 = 0.2518871970909668
    Metric 1 = 0.0030534351145038168
    Metric 2 = 0.0012640936244826392
    Metric 3 = 0.032688511755585715
    Metric 4 = 0.2518871970909668
"""


import unittest
import numpy as np
import os, shutil
import copy

import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
helper_dir = os.path.join(dir_path, '../../util/')
sys.path.append(helper_dir)

from orbitpy.propagator import PropagatorFactory
from orbitpy.util import Spacecraft

from orbitpy.grid import Grid
from orbitpy.coveragecalculator import GridCoverage

sys.path.append('../')
from util.coverage import Coverage

# method used in coverage calculation involving rectangular sensors. Tests are carried out for each method seperately.
method_list = ['ProjectedSphericalPointInPolygon', 'DirectSphericalPointInPolygon','DirectPointInRectangularPolygon']
class TestOrbitPropCovGrid(unittest.TestCase):
        
    @classmethod
    def setUpClass(cls):
        """Set up test directories and default propagation coverage parameters for all tests."""
        # Create new directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_dir = os.path.join(dir_path, 'temp')
        
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        out_dir2 = os.path.join(dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK')
        if os.path.exists(out_dir2):
            shutil.rmtree(out_dir2)
        os.makedirs(out_dir2)
        
        # Store directory path
        cls.dir_path = dir_path
        
        # Default propagation parameters
        factory = PropagatorFactory()
        step_size = 1
        specs = {"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize': step_size } 
        cls.j2_prop = factory.get_propagator(specs)
        cls.duration=1        
        # circular orbit
        cls.default_orbit_dict = {"date":{"@type":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                                       "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7000, 
                                                "ecc": 0, "inc": 0, "raan": 0, "aop": 0, "ta": 0}
                                     }
        
        # Default sensor parameters
        cls.instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": 0, "yRotation": 0, "zRotation": 0}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 20 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        
        cls.spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        
        # Establish thresholds for each metric
        cls.m1 = .1
        cls.m2 = .052 # threshold for 'ProjectedSphericalPointInPolygon' is 0.5
        cls.m3 = .05
        cls.m4 = .3
    
    @staticmethod
    def percentDifference(val1,val2):
        """Evaluate the absolute value of the percent difference between two numbers."""
        
        percentDiff = (val1 - val2) / ((val1 + val2)/2)
        return abs(percentDiff)
        
    @staticmethod
    def generateMetrics(STKCov,OPCov):
        """Generate the test case data metrics for the output data."""
        
        # Metric 1: The percent difference in total number of points accessed 
        # should be less than +-10%
        
        STKSumAccesses = sum(STKCov.accesses)
        OPSumAccesses = sum(OPCov.accesses)
        
        metric1 = TestOrbitPropCovGrid.percentDifference(STKSumAccesses,OPSumAccesses)
        print('Metric 1 = ' + str(metric1))
        
        # Metric 2: The percent difference in total amount of access time,
        # across all points, should be less than +-5%
        
        STKSumTime = sum(STKCov.timeAccessed)
        OPSumTime = sum(OPCov.timeAccessed)
        
        metric2 = TestOrbitPropCovGrid.percentDifference(STKSumTime,OPSumTime)
        print('Metric 2 = ' + str(metric2))
        
        # Metric 3: The percent difference between the average number of points 
        # accessed per time step should be less than +-5%
        
        STKPointsPerStep = np.sum(STKCov.coverage[:,1:], axis = 1)
        OPPointsPerStep = np.sum(OPCov.coverage[:,1:],axis = 1)
        
        avgSTK = sum(STKPointsPerStep)/len(STKPointsPerStep)
        avgOP = sum(OPPointsPerStep)/len(OPPointsPerStep)
        
        metric3 = TestOrbitPropCovGrid.percentDifference(avgSTK,avgOP)
        print('Metric 3 = ' + str(metric3))
        
        # Metric 4: The percent difference of total access time between 
        # points accessed by both softwares, averaged across the points, should
        # be less than +-30%
        
        percentDiff =  TestOrbitPropCovGrid.percentDifference(STKCov.timeAccessed,OPCov.timeAccessed)
        
        # Remove Nans, which signify points accessed by neither program
        percentDiff = percentDiff[~np.isnan(percentDiff)]
        
        # Remove 2s and -2s, which signify points accessed by only one program
        percentDiff = percentDiff[percentDiff != 2]
        percentDiff = percentDiff[percentDiff != -2]
        
        metric4 = np.sum(percentDiff)/np.size(percentDiff)
        print('Metric 4 = ' + str(metric4))
        
        return metric1,metric2,metric3,metric4
        
    #@unittest.skip("skip test_run_1")
    def test_run_1(self):
        """Test an equatorial orbit on a global grid with a 20 degree diameter conical sensor.                
        """ 
        print('running test_run_1')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/01/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/01/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/01/acc"

        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        sat = Spacecraft.from_dict({"orbitState":self.default_orbit_dict, "instrument":self.instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        
        cov.execute(out_file_access=acc_fl)     
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid_1.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/01/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
    #@unittest.skip("skip test_run_1")    
    def test_run_2(self):
        """Test an equatorial orbit on a global grid with a 30 deg AT, 20 deg CT sensor."""
        print('running test_run_2')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/02/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/02/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/02/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 30
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 20

        sat = Spacecraft.from_dict({"orbitState":self.default_orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)

        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid_2.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/02/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
       
    #@unittest.skip("skip test_run_3")
    def test_run_3(self):
        """Test a near-equatorial orbit on a global grid with a 20 degree diameter conical sensor."""
        print('running test_run_3')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/03/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
    
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/03/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/03/acc"

        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["inc"] = 1
        orbit_dict["state"]["raan"] = 1
        orbit_dict["state"]["aop"] = 1
        orbit_dict["state"]["ta"] = 1
        
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":self.instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Global_Grid_3.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/03/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    #@unittest.skip("skip test_run_4")
    def test_run_4(self):
        """Test a polar orbit on a US grid with a 30 deg AT, 20 deg CT sensor."""
        print('running test_run_4')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/04/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/04/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/04/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 30
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 20
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["inc"] = 90
        orbit_dict["state"]["raan"] = 180
        orbit_dict["state"]["aop"] = 180
        orbit_dict["state"]["ta"] = 180

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_4.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/04/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
        
    #@unittest.skip("skip test_run_5")
    def test_run_5(self):
        """Test an inclined orbit on a US grid with a 20 degree diameter conical sensor."""
        print('running test_run_5')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/05/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/05/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/05/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7578.378
        orbit_dict["state"]["inc"] = 45.7865
        orbit_dict["state"]["raan"] = 98.8797
        orbit_dict["state"]["aop"] = 75.78089
        orbit_dict["state"]["ta"] = 277.789

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":self.instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_5.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/05/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    #@unittest.skip("skip test_run_6")
    def test_run_6(self):
        """Test an inclined orbit on a US grid with a 30 deg AT, 20 deg CT sensor."""
        print('running test_run_6')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/06/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/06/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/06/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7578.378
        orbit_dict["state"]["inc"] = 45.7865
        orbit_dict["state"]["raan"] = 98.8797
        orbit_dict["state"]["aop"] = 75.78089
        orbit_dict["state"]["ta"] = 277.789
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 30
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 20

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_6.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/06/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
      
    #@unittest.skip("skip test_run_7")
    def test_run_7(self):
        """Test a sun-sync orbit on an equatorial grid with a 20 degree diameter conical sensor."""
        print('running test_run_7')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/07/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/07/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/07/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":self.instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        cov.execute(out_file_access=acc_fl)
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid_7.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/07/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    #@unittest.skip("skip test_run_8")
    def test_run_8(self):
        """Test a sun-sync orbit on an equatorial grid with a 20 degree diameter pointed conical sensor."""
        print('running test_run_8')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/08/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/08/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/08/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["orientation"]["convention"] = 'EULER'
        instrument_dict["orientation"]["eulerSeq1"] = 2
        instrument_dict["orientation"]["eulerSeq2"] = 1
        instrument_dict["orientation"]["eulerSeq3"] = 3
        instrument_dict["orientation"]["eulerAngle1"] = -30
        instrument_dict["orientation"]["eulerAngle2"] = -25
        instrument_dict["orientation"]["eulerAngle3"] = 5

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid_8.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/08/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    #@unittest.skip("skip test_run_9")
    def test_run_9(self):
        """Test a sun-sync orbit on an equatorial grid with a 20 deg AT, 30 deg CT pointed sensor."""
        print('running test_run_9')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/09/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/09/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/09/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 20
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 30
        instrument_dict["orientation"]["convention"] = 'EULER'
        instrument_dict["orientation"]["eulerSeq1"] = 2
        instrument_dict["orientation"]["eulerSeq2"] = 1
        instrument_dict["orientation"]["eulerSeq3"] = 3
        instrument_dict["orientation"]["eulerAngle1"] = 30
        instrument_dict["orientation"]["eulerAngle2"] = 24
        instrument_dict["orientation"]["eulerAngle3"] = -6

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)

                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/Equatorial_Grid_9.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/09/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
        
    #@unittest.skip("skip test_run_10")
    def test_run_10(self):
        """Test a sun-sync orbit on a US grid with a 30 deg AT, 20 deg CT sensor."""
        print('running test_run_10')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/10/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/10/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/10/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 30
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 20

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_10.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/10/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    #@unittest.skip("skip test_run_11")
    def test_run_11(self):
        """Test a sun-sync orbit on a US grid with a 20 deg AT, 30 deg CT pointed sensor."""
        print('running test_run_11')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/11/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/11/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/11/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {
                        "covGridFilePath":grid_fl
                    }
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 20
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 30
        instrument_dict["orientation"]["convention"] = 'EULER'
        instrument_dict["orientation"]["eulerSeq1"] = 2
        instrument_dict["orientation"]["eulerSeq2"] = 1
        instrument_dict["orientation"]["eulerSeq3"] = 3
        instrument_dict["orientation"]["eulerAngle1"] = -30
        instrument_dict["orientation"]["eulerAngle2"] = -25
        instrument_dict["orientation"]["eulerAngle3"] = 5

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_11.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/11/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")    
    #@unittest.skip("skip test_run_12")
    def test_run_12(self):
        """Test a sun-sync orbit on a US grid with a 30 deg AT, 20 deg CT pointed sensor."""
        print('running test_run_12')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_coveragecalculator_GridCoverage_with_STK/12/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/12/state"
        acc_fl = self.dir_path + "/temp/test_coveragecalculator_GridCoverage_with_STK/12/acc"
        
        # Define propagation and coverage parameters
        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        
        
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        
        orbit_dict["state"]["sma"] = 7080.48 
        orbit_dict["state"]["inc"] = 98.22
        
        instrument_dict = copy.deepcopy(self.instrument_dict)
        instrument_dict["fieldOfViewGeometry"]["shape"] = "RECTANGULAR"
        instrument_dict["fieldOfViewGeometry"]["angleHeight"] = 30
        instrument_dict["fieldOfViewGeometry"]["angleWidth"] = 20
        instrument_dict["orientation"]["convention"] = 'EULER'
        instrument_dict["orientation"]["eulerSeq1"] = 2
        instrument_dict["orientation"]["eulerSeq2"] = 1
        instrument_dict["orientation"]["eulerSeq3"] = 3
        instrument_dict["orientation"]["eulerAngle1"] = 30
        instrument_dict["orientation"]["eulerAngle2"] = 24
        instrument_dict["orientation"]["eulerAngle3"] = -6

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=acc_fl, method=method)
                
                # Construct coverage objects to verify output
                STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_coveragecalculator_GridCoverage_with_STK/Accesses/US_Grid_12.cvaa')
                OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_coveragecalculator_GridCoverage_with_STK/12/acc',grid_fl)
                
                # Check truth
                m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
            
                result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
                self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()
