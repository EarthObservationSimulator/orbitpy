""" *Unit tests for :class:`orbitpy.propagate.J2AnalyticalPropagator` covering checks on orbit state data when compared to STK output.*

:code:`/temp/` folder contains temporary files produced during the run of the tests below.

Expected output:

running test_run_1
Max Difference: 
4.69315597729782
.running test_run_2
Max Difference: 
4.689415839943152
.running test_run_3
Max Difference: 
3.815186670455347
.running test_run_4
Max Difference: 
3.3283995083671414
.running test_run_5
Max Difference: 
4.187096058800876
.running test_run_6
Max Difference: 
1.4851594443143767e-06
.running test_run_7
Max Difference: 
0.009143580793676165
.running test_run_8
Max Difference: 
0.009159691231587885
.

"""

import unittest
import numpy as np
import os, shutil
import copy

from orbitpy.propagator import PropagatorFactory, J2AnalyticalPropagator
import orbitpy.propagator
from orbitpy.util import OrbitState, Spacecraft

class TestPropagation(unittest.TestCase):
        
    @classmethod
    def setUpClass(cls):
        """Set up test directories and default propagation coverage parameters for all tests."""
        # Create new directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_dir = os.path.join(dir_path, 'temp')
        
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        out_dir2 = os.path.join(dir_path,'temp/test_propagation_with_STK')
        if os.path.exists(out_dir2):
            shutil.rmtree(out_dir2)
        os.makedirs(out_dir2)
        
        # store directory path
        cls.dir_path = dir_path        
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
        print('running test_run_1')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/01/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        # run the propagator
        orbit = OrbitState.from_dict(self.default_orbit_dict)
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_cart = self.dir_path+"/temp/test_propagation_with_STK/01/state"
        self.j2_prop.execute(spacecraft, None, out_file_cart, None, self.duration)
        
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/01/states.txt"
        # read in state data to numpy array
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_cart)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestPropagation.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
       
    def test_run_2(self):
        """Test all states = 1, except for size and eccentricity."""
        print('running test_run_2')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/02/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        orbit_dict['state']['raan'] = 1
        orbit_dict['state']['inc'] = 1
        orbit_dict['state']['aop'] = 1
        orbit_dict['state']['ta'] = 1
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_cart = self.dir_path+"/temp/test_propagation_with_STK/02/state"
        self.j2_prop.execute(spacecraft, None, out_file_cart, None, self.duration)
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/02/states.txt"
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_cart)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)   
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestPropagation.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
    
    def test_run_3(self):
        """Test middle values for all states, except for size and eccentricity."""
        print('running test_run_3')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/03/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        orbit_dict['state']['raan'] = 180
        orbit_dict['state']['inc'] = 90
        orbit_dict['state']['aop'] = 180
        orbit_dict['state']['ta'] = 180
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_cart = self.dir_path+"/temp/test_propagation_with_STK/03/state"
        self.j2_prop.execute(spacecraft, None, out_file_cart, None, self.duration)
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/03/states.txt"
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_cart)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)  
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestPropagation.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_4(self):
        """Test decimal values for all states, except for eccentricity"""
        print('running test_run_4')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/04/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)
        orbit_dict['state']['sma'] = 7578.378
        orbit_dict['state']['raan'] = 98.8797
        orbit_dict['state']['inc'] = 45.7865
        orbit_dict['state']['aop'] = 75.78089
        orbit_dict['state']['ta'] = 277.789
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_cart = self.dir_path+"/temp/test_propagation_with_STK/04/state"
        self.j2_prop.execute(spacecraft, None, out_file_cart, None, self.duration)
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/04/states.txt"
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_cart)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestPropagation.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
       
    def test_run_5(self):
        """Test a retrograde orbit."""
        print('running test_run_5')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/05/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)

        orbit_dict['state']['sma'] = 7578.378
        orbit_dict['state']['raan'] = 98.8797
        orbit_dict['state']['inc'] = 180
        orbit_dict['state']['aop'] = 75.78089
        orbit_dict['state']['ta'] = 277.789
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_cart = self.dir_path+"/temp/test_propagation_with_STK/05/state"
        self.j2_prop.execute(spacecraft, None, out_file_cart, None, self.duration)
        
        # Read in state data to numpy array
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/05/states.txt"
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_cart)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        result = np.allclose(orbitpyData,stkData,atol=6)
        
        #Print Result
        TestPropagation.printMaxDiff(stkData,orbitpyData)
        
        self.assertEqual(True,result)
        
    def test_run_6(self):
        """Test a polar orbit to verify RAAN doesn't move."""
        print('running test_run_6')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/06/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)

        orbit_dict['state']['sma'] = 7000
        orbit_dict['state']['raan'] = 98.8797
        orbit_dict['state']['inc'] = 90
        orbit_dict['state']['aop'] = 75.78089
        orbit_dict['state']['ta'] = 277.789
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_kep = self.dir_path+"/temp/test_propagation_with_STK/06/state"
        self.j2_prop.execute(spacecraft, None, None, out_file_kep, self.duration)
        
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/06/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_kep)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestPropagation.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)

    def test_run_7(self):
        """Test RAAN regression of low inclination prograde orbit."""
        print('running test_run_7')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/07/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)

        orbit_dict['state']['sma'] = 7000
        orbit_dict['state']['raan'] = 98.8797
        orbit_dict['state']['inc'] = 10
        orbit_dict['state']['aop'] = 75.78089
        orbit_dict['state']['ta'] = 277.789
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_kep = self.dir_path+"/temp/test_propagation_with_STK/07/state"
        self.j2_prop.execute(spacecraft, None, None, out_file_kep, self.duration)
                
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/07/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_kep)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestPropagation.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)
    
    def test_run_8(self):
        """Test RAAN precession of low inclination retrograde orbit."""
        print('running test_run_8')
        # Prepare the output directory
        out_dir = os.path.join(self.dir_path,'temp/test_propagation_with_STK/08/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # set orbit
        orbit_dict = copy.deepcopy(self.default_orbit_dict)

        orbit_dict['state']['sma'] = 7000
        orbit_dict['state']['raan'] = 98.8797
        orbit_dict['state']['inc'] = 170
        orbit_dict['state']['aop'] = 75.78089
        orbit_dict['state']['ta'] = 277.789
        orbit = OrbitState.from_dict(orbit_dict)
        # execute
        spacecraft = Spacecraft(orbitState=orbit)
        out_file_kep = self.dir_path+"/temp/test_propagation_with_STK/07/state"
        self.j2_prop.execute(spacecraft, None, None, out_file_kep, self.duration)
        
        stk_sat_state_fl = self.dir_path + "/STK/test_propagation_with_STK/08/kepler_states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestPropagation.orbitpyStateArray(out_file_kep)
        stkData = TestPropagation.stkStateArray(stk_sat_state_fl)
        
        pyRAAN = orbitpyData[:,4]
        stkRAAN = stkData[:,4]
        
        result = np.allclose(pyRAAN,stkRAAN,atol=.015)
        
        #Print Result
        TestPropagation.printMaxDiff(pyRAAN,stkRAAN)
        
        self.assertEqual(True,result)
        

        
if __name__ == '__main__':
    unittest.main()
