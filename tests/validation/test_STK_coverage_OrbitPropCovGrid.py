""" *Tests for :class:`orbitpy.orbitpropcov.OrbitPropCovGrid` covering checks on coverage calculations.*
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below.
'''

import unittest
import numpy as np
import os, shutil
import copy

import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
helper_dir = os.path.join(dir_path, '../../util/')
sys.path.append(helper_dir)

from coverage import Coverage

# Updated imports
from orbitpy.propagator import PropagatorFactory
from orbitpy.util import Spacecraft

from orbitpy.grid import Grid
from orbitpy.coveragecalculator import GridCoverage


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
        
        out_dir2 = os.path.join(dir_path,'temp/test_STK_coverage_OrbitPropCovGrid')
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
        cls.default_orbit_dict = {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                                       "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7000, 
                                                "ecc": 0, "inc": 0, "raan": 0, "aop": 0, "ta": 0}
                                     }
        
        # Default sensor parameters
        cls.instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": 0, "yRotation": 0, "zRotation": 0}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 20 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        
        cls.spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        
        # Establish thresholds for each metric
        cls.m1 = .1
        cls.m2 = .05
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
        
        # Metric 2: The percent difference in total ammount of access time,
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
    
    @staticmethod
    def getClockAngles(atFOV,ctFOV):
        """Get clock angles from along track, cross track FOV in degrees."""
        
        alongTrackFieldOfView = np.deg2rad(atFOV)

        crossTrackFieldOfView = np.deg2rad(ctFOV)

        cosCone = np.cos(alongTrackFieldOfView/2.0)*np.cos(crossTrackFieldOfView/2.0)
        
        cone = np.arccos(cosCone)

        sinClock =  np.sin(alongTrackFieldOfView/2.0) / np.sin(cone)

        clock = np.arcsin(sinClock)
        
        cone_deg = str(np.rad2deg(cone))
        clock_deg = np.rad2deg(clock)
        
        
        coneAngles_deg = cone_deg + ',' + cone_deg + ',' + cone_deg + ',' + cone_deg
        clockAngles_deg = str(clock_deg) + ',' +str(180.0-clock_deg)+ ',' + str(180.0+clock_deg) + ',' + str(-clock_deg)
        
        return clockAngles_deg,coneAngles_deg
        
    def test_run_1(self):
        """Test an equatorial orbit on a global grid with a 5 degree conical sensor.""" 
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/01/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/01/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/01/acc"

        grid_dict = {"covGridFilePath":grid_fl}
        grid = Grid.from_customgrid_dict(grid_dict)
        sat = Spacecraft.from_dict({"orbitState":self.default_orbit_dict, "instrument":self.instrument_dict, "spacecraftBus":self.spacecraftBus_dict})
        
        # Execute propagation and coverage
        self.j2_prop.execute(sat, None,state_fl, None)
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_fl)
        cov.execute(out_file_access=acc_fl)     
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_1.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/01/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    def test_run_2(self):
        """Test an equatorial orbit on a global grid with a 15 deg AT, 10 deg CT sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/02/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/02/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/02/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_2.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/02/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
       
    def test_run_3(self):
        """Test a near-equatorial orbit on a global grid with a 5 deg conical sensor."""
        
         # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/03/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
    
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/03/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/03/acc"

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
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_3.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/03/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    def test_run_4(self):
        """Test a polar orbit on a US grid with a 15 deg AT, 10 deg CT sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/04/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/04/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/04/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_4.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/04/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    def test_run_5(self):
        """Test an inclined orbit on a US grid with a 5 degree conical sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/05/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/05/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/05/acc"
        
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
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_5.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/05/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    def test_run_6(self):
        """Test an inclined orbit on a US grid with a 15 deg AT, 10 deg CT sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/06/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/06/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/06/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_6.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/06/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
      
    def test_run_7(self):
        """Test a sun-sync orbit on an equatorial grid with a 5 deg conical sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/07/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/07/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/07/acc"
        
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
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_7.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/07/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    def test_run_8(self):
        """Test a sun-sync orbit on an equatorial grid with a 5 deg pointed conical sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/08/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/08/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/08/acc"
        
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
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_8.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/08/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    def test_run_9(self):
        """Test a sun-sync orbit on an equatorial grid with a 10 deg AT, 15 deg CT pointed sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/09/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/09/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/09/acc"
        
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
        cov.execute(out_file_access=acc_fl)

        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_9.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/09/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
    def test_run_10(self):
        """Test a sun-sync orbit on a US grid with a 15 deg AT, 10 deg CT sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/10/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/10/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/10/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_10.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/10/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")
    def test_run_11(self):
        """Test a sun-sync orbit on a US grid with a 10 deg AT, 15 deg CT pointed sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/11/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
                
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/11/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/11/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_11.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/11/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
    
    #@unittest.skip("Pointed tests are broken and must be fixed.")    
    def test_run_12(self):
        """Test a sun-sync orbit on a US grid with a 15 deg AT, 10 deg CT pointed sensor."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_coverage_OrbitPropCovGrid/12/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup IO file paths
        grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/12/state"
        acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/12/acc"
        
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
        cov.execute(out_file_access=acc_fl)
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_12.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/12/acc',grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()
