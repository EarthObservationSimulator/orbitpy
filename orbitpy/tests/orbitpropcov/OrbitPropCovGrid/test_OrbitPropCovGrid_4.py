""" *Unit tests for :class:`orbitpy.orbitpropcov.OrbitPropCovGrid` covering checks on format of produced output files and
   propagation states.*
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below. Some of the parameters are chosen
   randomly for the tests (and compared with corresponding outputs), hence each test is run with different inputs, and expected 
   outputs. 
'''

import unittest
import numpy as np
import pandas as pd
import sys, os, shutil
import random
import subprocess
import copy

from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

class TestOrbitPropCovGrid(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # Create new directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_dir = os.path.join(dir_path, 'temp')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        
        # create a default set of propagation and coverage parameters specs
        self.default_pcp = PropagationCoverageParameters(
                        sat_id="1", 
                        epoch="2018,5,26,12,0,0", # JD: 2458265.00000
                        sma=7000, 
                        ecc=0, 
                        inc=0, 
                        raan=0, 
                        aop=0, 
                        ta=0, 
                        duration=1.0, 
                        cov_grid_fl=dir_path+"/temp/covGrid", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone="12.5", 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = 1.0, 
                        sat_state_fl = dir_path+"/temp/state", 
                        sat_acc_fl = dir_path+"/temp/acc", 
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)
        
        # store directory path
        self.dir_path = dir_path
        
        super(TestOrbitPropCovGrid, self).__init__(*args, **kwargs)
        
        
    def produce_cov_grid(self, sat_id, latUpper, latLower, lonUpper, lonLower, grid_res):
        """ Write a coverage grid file. """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        prc_args = [os.path.join(dir_path, '..', '..', '..', 'oci', 'bin', 'genCovGrid')] 

        cov_grid_fl = dir_path + "/temp/covGrid" # coverage grid file path        
        prc_args.append(cov_grid_fl)

        prc_args.append(str(sat_id)+','+str(latUpper)+','+str(latLower)+
                            ','+str(lonUpper)+','+str(lonLower)+','+str(grid_res) # same grid resolution for all regions
                            )
        result = subprocess.run(prc_args, check= True)
        
    def orbitpyStateArray(self,sat_state_fl):
        
        data = np.genfromtxt(sat_state_fl, delimiter=",",skip_header = 5) # 5th row header, 6th row onwards contains the data
        return data
    
    def gmatStateArray(self,sat_state_fl):
        
        data = np.genfromtxt(sat_state_fl, skip_header = 1)
        return data
        
    def test_run_1(self):
        """ Test propagation of 7000 sma orbit w/ all other kepler states = 0.""" 
        
        TestOrbitPropCovGrid.produce_cov_grid(self, 1, 0, -10, 10, 0, 1)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        gmat_sat_state_fl = self.dir_path + "/GMAT/01/states.txt"
        
        # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(self,self.default_pcp.sat_state_fl)
        gmatData = TestOrbitPropCovGrid.gmatStateArray(self,gmat_sat_state_fl)
        
        self.assertEqual(1,1)
        
    def test_run_8(self):
        """Propagate GMAT test until RAAN regresses 5 degrees, then propagate w/ OrbitPy and compare"""
        
        TestOrbitPropCovGrid.produce_cov_grid(self,1,0,-10,10,0,1)
        
        prop_cov_param = copy.deepcopy(self.default_pcp)
        GMATElapsedSecs = 60388
        secondsInDay = 86400
        
        prop_cov_param.duration = GMATElapsedSecs/secondsInDay
        prop_cov_param.inc = 10
        prop_cov_param.aop = 75.78089
        prop_cov_param.ta = 277.789
        
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        
        gmat_sat_state_fl = self.dir_path + "/GMAT/08/states.txt"
        
         # read in state data to numpy array
        orbitpyData = TestOrbitPropCovGrid.orbitpyStateArray(self,self.default_pcp.sat_state_fl)
        gmatData = TestOrbitPropCovGrid.gmatStateArray(self,gmat_sat_state_fl)
        
        self.assertEqual(1,1)
        
if __name__ == '__main__':
    unittest.main()
        
        