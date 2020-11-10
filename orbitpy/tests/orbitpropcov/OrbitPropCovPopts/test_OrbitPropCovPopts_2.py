"""Unit tests for :class:`orbitpy.orbitpropcov.OrbitPropCovPopts` class testing coverage.
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below. Some of the parameters are chosen
   randomly for the tests (and compared with corresponding outputs), hence each test is run with different inputs, and expected 
   outputs. 
'''

import unittest
import json
import numpy
import sys, os, shutil
import subprocess
import copy
import pandas as pd
import random

from orbitpy.orbitpropcov import OrbitPropCovPopts
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach, MathUtilityFunctions

RE = 6378.137 # [km] radius of Earth

class TestOrbitPropCovPOpts(unittest.TestCase):

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
                        sma=RE+random.uniform(350,850), 
                        ecc=0.001, 
                        inc=random.uniform(0,180), 
                        raan=random.uniform(0,360), 
                        aop=random.uniform(0,360), 
                        ta=random.uniform(0,360), 
                        duration=random.random(), 
                        popts_fl=dir_path+"/temp/pOpts", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone=str(random.uniform(5,60)), 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = 0.1+random.random(), 
                        sat_state_fl = dir_path+"/temp/state", 
                        sat_acc_fl = dir_path+"/temp/acc", 
                        do_prop=True,
                        do_cov=True,
                        cov_calcs_app= CoverageCalculationsApproach.PNTOPTS)


        super(TestOrbitPropCovPOpts, self).__init__(*args, **kwargs)
    
    def assertNearlyZeroErrorFraction(self,a,b,fraction=0.01,msg=None):
        if abs(a-b) > abs(fraction*a):
            if msg is None:
                self.fail("The given numbers %s and %s are not near each other."%(a,b))
            else:
                self.fail(msg)

    def produce_pointing_options(self):
        """ Write a pointing options file. """
        dir_path = os.path.dirname(os.path.realpath(__file__))

        pOpts_fl = dir_path + "/temp/pOpts" # coverage grid file path

        with open(pOpts_fl, 'w') as x:
                x.write("Euler (intrinsic) rotations with sequence 1,2,3 assumed, \
                         i.e. R = R3R2R1, with rotation matrix representing rotation of the coordinate system.\n")        
                x.write("index,euler_angle1[deg],euler_angle2[deg],euler_angle3[deg]\n")
                x.write("0,0,0,0\n") # Note: First option has to be (0,0,0) for the tests below to work as intended.
                
                yaw = random.uniform(0,360)
                _d = "1,0,0,"+str(yaw)+"\n"
                x.write(_d)
                _d = "2,0,0,"+str(-yaw)+"\n"
                x.write(_d)

                roll = random.uniform(0,60)
                _d = "3,0,"+str(roll)+",0\n"
                x.write(_d)
                _d = "4,0,"+str(-roll)+",0\n"
                x.write(_d)

    def test_run_1(self):
        """ Test that the pointing euler angles (0,0,x) (where x is variable) corresponds to pointing at the 
            nadir position which shall be the same as the satellite position.
        """ 
        TestOrbitPropCovPOpts.produce_pointing_options(self)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        # run the propagator
        opc_grid = OrbitPropCovPopts(prop_cov_param)
        opc_grid.run()
        
        # read the state file
        sat_state_fl = prop_cov_param.sat_state_fl
        epoch_JDUT1 = pd.read_csv(sat_state_fl, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])
        step_size = prop_cov_param.step_size
      
        state_data = pd.read_csv(sat_state_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        state_data.set_index("TimeIndex")

        alt = prop_cov_param.sma -RE # approximate altitude to be used

        # read the access file        
        sat_acc_fl = prop_cov_param.sat_acc_fl
        acc_data = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        if not acc_data.empty:
            acc_data = acc_data.set_index('pntopti')
            nadir_locs = acc_data.loc[0]
            for k in range(0, len(nadir_locs)):
                lat = nadir_locs.iloc[k]["lat[deg]"]
                lon = nadir_locs.iloc[k]["lon[deg]"]
                accessTimeIndex = nadir_locs.iloc[k]["accessTimeIndex"]
                accessTime = epoch_JDUT1 + accessTimeIndex*step_size*(1/86400)
                [x, y,z] = MathUtilityFunctions.geo2eci([lat, lon, alt], accessTime) # approximate altitude be used
                
                self.assertAlmostEqual(x, state_data.loc[accessTimeIndex]["X[km]"], delta= 10) # approximate altitude used, ehnce almost equal
                self.assertAlmostEqual(y, state_data.loc[accessTimeIndex]["Y[km]"], delta= 10)
                self.assertAlmostEqual(z, state_data.loc[accessTimeIndex]["Z[km]"], delta= 10)
           


    def test_run_2(self):
        """ Test that the pointing for the case of equatorial orbit at randomly chosen altitudes. Pointing to the nadir with any random yaw shall result
            in covering latitude 0 deg always (throught the mission). Pointing with a random roll (only) orientation (at some random altitude) shall result
            in coverage of latitude as defined by the resulting Earth-centric half-angle subtended by twice the roll angle (the same latitude throughout the massion). 
        """ 
        TestOrbitPropCovPOpts.produce_pointing_options(self)       

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        prop_cov_param.sma = RE+random.uniform(350,850)
        prop_cov_param.inc = 0 # orbital plane on the equatorial plane

        popts_fl = prop_cov_param.popts_fl
        pntOpts_data = pd.read_csv(popts_fl, skiprows=[0])

        # run the propagator
        opc_grid = OrbitPropCovPopts(prop_cov_param)
        opc_grid.run()

        alt = prop_cov_param.sma - RE # approximate altitude to be used

        # since orbital plane = equatorial plane, a roll-only pointing produces access at the same latitudes over the mission.
        # the nadir pointing shall always point to latitude = 0

        # read the access file        
        sat_acc_fl = prop_cov_param.sat_acc_fl
        acc_data = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        if not acc_data.empty:
            acc_data = acc_data.set_index('pntopti')
            nadir_locs = acc_data.loc[0]
            for k in range(0, len(nadir_locs)):
                self.assertAlmostEqual(nadir_locs.iloc[k]["lat[deg]"], 0)
            
            nadir_locs = acc_data.loc[1]
            for k in range(0, len(nadir_locs)):
                self.assertAlmostEqual(nadir_locs.iloc[k]["lat[deg]"], 0)

            nadir_locs = acc_data.loc[2]
            for k in range(0, len(nadir_locs)):
                self.assertAlmostEqual(nadir_locs.iloc[k]["lat[deg]"], 0)

            pntOpt3_locs = acc_data.loc[3]
            hfov = pntOpts_data.iloc[3]["euler_angle2[deg]"]
            for k in range(0, len(pntOpt3_locs)):
                self.assertNearlyZeroErrorFraction(pntOpt3_locs.iloc[k]["lat[deg]"], 0.5*MathUtilityFunctions.get_eca(2*hfov, alt), fraction = 0.1)

            pntOpt4_locs = acc_data.loc[4]
            hfov = pntOpts_data.iloc[4]["euler_angle2[deg]"]
            for k in range(0, len(pntOpt4_locs)):
                self.assertNearlyZeroErrorFraction(pntOpt4_locs.iloc[k]["lat[deg]"], 0.5*MathUtilityFunctions.get_eca(2*hfov, alt), fraction = 0.1)
            


