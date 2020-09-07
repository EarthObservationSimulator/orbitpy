""" *Unit tests for :class:`orbitpy.orbitpropcov.OrbitPropCovGrid` covering checks on orbit state data when compared to STK output.*
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below.
'''

import unittest
import numpy as np
import os, shutil
import subprocess
import copy

from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

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
        
        out_dir2 = os.path.join(dir_path,'temp/test_STK_propagation')
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
                        duration=1.0, 
                        cov_grid_fl=dir_path+"/temp/test_STK_propagation/covGrid", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone="12.5", 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = 1.0, 
                        sat_state_fl = dir_path+"/temp/test_STK_propagation/state", 
                        sat_acc_fl = dir_path+"/temp/test_STK_propagation/acc", 
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)
        
        
        cls.produce_cov_grid(1, 0, -10, 10, 0, 1)
                
    @classmethod
    def produce_cov_grid(cls, sat_id, latUpper, latLower, lonUpper, lonLower, grid_res):
        """ Write a coverage grid file."""
        
        prc_args = [os.path.join(cls.dir_path,'..', '..', 'oci', 'bin', 'genCovGrid')] 

        cov_grid_fl = cls.dir_path + "/temp/test_STK_propagation/covGrid" # coverage grid file path
        
        prc_args.append(cov_grid_fl)

        prc_args.append(str(sat_id)+','+str(latUpper)+','+str(latLower)+
                            ','+str(lonUpper)+','+str(lonLower)+','+str(grid_res) # same grid resolution for all regions
                            )
        print("Entered Coverage Function in test file.")
        result = subprocess.run(prc_args, check= True)
    
    @staticmethod
    def orbitpyStateArray(sat_state_fl):
        """Read OrbitPy text output into a numpy array"""
        
        data = np.genfromtxt(sat_state_fl, delimiter=",",skip_header = 5) # 5th row header, 6th row onwards contains the data
        return data
    
    @staticmethod
    def stkStateArray(sat_state_fl):
        """Read STK text output into a numpy array"""
        
        data = np.genfromtxt(sat_state_fl, skip_header = 6)
        return data
    
    @staticmethod
    def printMaxDiff(stk,gmat):
        """Print absolute value of the maximum difference in the states passed."""
        
        diff = np.absolute(stk - gmat)
        result = np.max(diff)
        
        print("Max Difference: ")
        print(str(result))
        
        
    def test_run_1(self):
        """Test propagation of 7000 SMA orbit with all other kepler states = 0.""" 
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/01/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/01/state"
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/01/states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(prop_cov_param.sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_2(self):
        """Test all states = 1, except for size and eccentricity."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/02/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup input parameters
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/02/state"
        prop_cov_param.raan = 1
        prop_cov_param.inc = 1
        prop_cov_param.aop = 1
        prop_cov_param.ta = 1
        
        # Run the simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/02/states.txt"
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(prop_cov_param.sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)   
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
    
    def test_run_3(self):
        """Test middle values for all states, except for size and eccentricity."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/03/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup input parameters
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/03/state"
        prop_cov_param.raan = 180
        prop_cov_param.inc = 90
        prop_cov_param.aop = 180
        prop_cov_param.ta = 180
        
        # Run the simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/03/states.txt"
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(prop_cov_param.sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)  
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_4(self):
        """Test decimal values for all states, except for eccentricity"""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/04/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup input parameters
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sma = 7578.378
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/04/state"
        prop_cov_param.raan = 98.8797
        prop_cov_param.inc = 45.7865
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        
        # Run the simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/04/states.txt"
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(prop_cov_param.sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_5(self):
        """Test a retrograde orbit."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/05/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup input parameters
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sma = 7578.378
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/05/state"
        prop_cov_param.raan = 98.8797
        prop_cov_param.inc = 180
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        
        # Run the simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/05/states.txt"
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(prop_cov_param.sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_6(self):
        """Test a polar orbit to verify RAAN doesn't move."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/06/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # Setup input parameters
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.sma = 7000
        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/06/state"
        prop_cov_param.raan = 98.8797
        prop_cov_param.inc = 90
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        
        # Run the simulation
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        sat_state_fl = self.dir_path + "/temp/test_STK_propagation/06/state_Keplerian"
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/06/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)
    
    def test_run_8(self):
        """Test RAAN precession of low inclination retrograde orbit."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/08/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        prop_cov_param = copy.deepcopy(self.default_pcp)

        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/08/state"
        prop_cov_param.inc = 170
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        prop_cov_param.raan = 98.8797
        
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        sat_state_fl = self.dir_path + "/temp/test_STK_propagation/08/state_Keplerian"
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/08/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)
        
    def test_run_7(self):
        """Test RAAN regression of low inclination prograde orbit."""
        
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_STK_propagation/07/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        prop_cov_param = copy.deepcopy(self.default_pcp)

        prop_cov_param.sat_state_fl = self.dir_path + "/temp/test_STK_propagation/07/state"
        prop_cov_param.inc = 10
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        prop_cov_param.raan = 98.8797
        
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        sat_state_fl = self.dir_path + "/temp/test_STK_propagation/07/state_Keplerian"
        stk_sat_state_fl = self.dir_path + "/STK/test_STK_propagation/07/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(sat_state_fl)
        stkData = TestOrbitPropCovGrid.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestOrbitPropCovGrid.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)
        
if __name__ == '__main__':
    unittest.main()
