""" *Tests for :class:`orbitpy.orbitpropcov.OrbitPropCovGrid` covering checks on coverage calculations.*
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below.
'''

import unittest
import numpy as np
import os, shutil
import copy

from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
helper_dir = os.path.join(dir_path, '../../util/')
sys.path.append(helper_dir)

from coverage import Coverage

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
        
        # store directory path
        cls.dir_path = dir_path
        
        cls.default_pcp = PropagationCoverageParameters(
                        sat_id="1", 
                        epoch="2018,5,26,12,0,0", # JD: 2458265.00000
                        sma=7000, 
                        ecc=0, 
                        inc=0, 
                        raan=0, 
                        aop=0, 
                        ta=0, 
                        duration=1, 
                        cov_grid_fl=dir_path+"/temp/test_STK_coverage_OrbitPropCovGrid/grid", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone="10", 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = 1.0, 
                        do_prop=True,
                        do_cov=True,
                        sat_state_fl = dir_path+"/temp/test_STK_coverage_OrbitPropCovGrid/state", 
                        sat_acc_fl = dir_path+"/temp/test_STK_coverage_OrbitPropCovGrid/acc", 
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)
        
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

        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/01/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/01/acc"
        
        # Run simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_1.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/01/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        atFOV = 15*2
        ctFOV = 10*2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
        
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/02/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/02/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_2.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/02/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.inc = 1
        prop_cov_param.raan = 1
        prop_cov_param.aop = 1
        prop_cov_param.ta = 1
        
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/03/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/03/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Global_Grid_3.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/03/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.inc = 90
        prop_cov_param.raan = 180
        prop_cov_param.aop = 180
        prop_cov_param.ta = 180
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        atFOV = 15*2
        ctFOV = 10*2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
        
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/04/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/04/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_4.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/04/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7578.378
        prop_cov_param.inc = 45.7865
        prop_cov_param.raan = 98.8797
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/05/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/05/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_5.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/05/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7578.378
        prop_cov_param.inc = 45.7865
        prop_cov_param.raan = 98.8797
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        atFOV = 15*2
        ctFOV = 10*2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/06/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/06/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_6.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/06/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/07/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/07/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_7.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/07/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup sensor parameters
        prop_cov_param.sen_orien = "1,2,3,-30,25,5"
        prop_cov_param.sen_orien = "2,1,3,-30,-25,5"
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/08/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/08/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_8.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/08/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        prop_cov_param.sen_orien = "1,2,3,30,-24,-6"
        prop_cov_param.sen_orien = "2,1,3,30,24,-6"
        atFOV = 10 * 2
        ctFOV = 15 * 2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/09/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/09/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/Equatorial_Grid_9.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/09/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        atFOV = 15 * 2
        ctFOV = 10 * 2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/10/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/10/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_10.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/10/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        prop_cov_param.sen_orien = "1,2,3,-30,25,5"
        prop_cov_param.sen_orien = "2,1,3,-30,-25,5"
        atFOV = 10*2
        ctFOV = 15*2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/11/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/11/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_11.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/11/acc',prop_cov_param.cov_grid_fl)
        
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
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # Setup orbit parameters
        prop_cov_param.sma = 7080.48 
        prop_cov_param.inc = 98.22
        prop_cov_param.raan = 0
        prop_cov_param.aop = 0
        prop_cov_param.ta = 0
        
        # Setup sensor parameters
        prop_cov_param.sen_fov_geom = "RECTANGULAR"
        prop_cov_param.sen_orien = "1,2,3,30,-24,-6"
        prop_cov_param.sen_orien = "2,1,3,30,24,-6"
        atFOV = 15*2
        ctFOV = 10*2
        prop_cov_param.sen_clock,prop_cov_param.sen_cone = TestOrbitPropCovGrid.getClockAngles(atFOV,ctFOV)
                
        # Setup IO file paths
        prop_cov_param.cov_grid_fl = self.dir_path + "/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid"
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/12/state"
        prop_cov_param.sat_acc_fl = self.dir_path + "/temp/test_STK_coverage_OrbitPropCovGrid/12/acc"
        
        # Run Simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
         # Construct coverage objects to verify output
        STKCoverage = Coverage.STKCoverage(self.dir_path + '/STK/test_STK_coverage_OrbitPropCovGrid/Accesses/US_Grid_12.cvaa')
        OrbitPyCoverage = Coverage.OrbitPyCoverage(self.dir_path + '/temp/test_STK_coverage_OrbitPropCovGrid/12/acc',prop_cov_param.cov_grid_fl)
        
        # Check truth
        m1,m2,m3,m4 = TestOrbitPropCovGrid.generateMetrics(STKCoverage,OrbitPyCoverage)
    
        result = m1 <= self.m1 and m2 <= self.m2 and m3 <= self.m3 and m4 <= self.m4
        self.assertTrue(result)
        
if __name__ == '__main__':
    unittest.main()
