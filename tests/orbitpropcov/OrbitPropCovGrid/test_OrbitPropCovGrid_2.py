"""Unit tests for :class:`orbitpy.orbitpropcov.OrbitPropCovGrid` class covering checks on coverage by conical sensors.
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

from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

RE = 6378.137 # [km] radius of Earth

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
                        sma=6378+random.uniform(350,850), 
                        ecc=0.001, 
                        inc=random.uniform(0,180), 
                        raan=random.uniform(0,360), 
                        aop=random.uniform(0,360), 
                        ta=random.uniform(0,360), 
                        duration=random.random(), 
                        cov_grid_fl=dir_path+"/temp/covGrid", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone="12.5", 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = random.random(), 
                        sat_state_fl = dir_path+"/temp/state", 
                        sat_acc_fl = dir_path+"/temp/acc", 
                        do_prop=True,
                        do_cov=True,
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)


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

    def test_run_1(self):
        """ Orient the sensor with roll, and an equatorial orbit and check that the ground-points captured are on either
            side of hemisphere only. (Conical Sensor)
        """ 
        TestOrbitPropCovGrid.produce_cov_grid(self, 1, 25, -25, 180, -180, 5)

        #### positive roll ####
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        prop_cov_param.inc = 0.0 # equatorial orbit
        prop_cov_param.sen_orien = "1,2,3,0," + str(random.uniform(12.5,90)) + ",0" # randomly orient with positive roll
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        if not data.empty:
            self.assertTrue((data["lat[deg]"]>0).all())

        #### negative roll ####
        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        prop_cov_param.inc = 0.0 # equatorial orbit
        prop_cov_param.sen_orien = "1,2,3,0," + str(random.uniform(-12.5,-90)) + ",0" # randomly orient with negative roll
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        if not data.empty:
            self.assertTrue((data["lat[deg]"]<0).all())

    def test_run_2(self):
        """ Orient the sensor with varying yaw but same pitch and roll, and test that the captured ground-points remain the same
            (Conical Sensor). 
        """ 
        TestOrbitPropCovGrid.produce_cov_grid(self, 1, 90, -90, 180, -180, 5)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        # pitch and roll remain the same 
        pitch = random.uniform(-90,90)
        roll = random.uniform(-90,90)

        #### random yaw each turn ####
        yaw = random.uniform(0,360)
        prop_cov_param.sen_orien = "1,2,3," +  str(pitch) + "," + str(roll) + "," + str(yaw) 
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data1 = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        #### random yaw each turn ####
        yaw = random.uniform(0,360)
        prop_cov_param.sen_orien = "1,2,3,"  +  str(pitch) + "," + str(roll) +  "," + str(yaw) 
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data2 = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        
        self.assertTrue((data1["lat[deg]"]==data2["lat[deg]"]).all())
        self.assertTrue((data1["lon[deg]"]==data2["lon[deg]"]).all())

    def test_run_3(self):
        """ Orient the sensor with pitch and test that the times the ground-points are captured lag or lead (depending on direction of pitch)
            as compared to the coverage from a zero pitch sensor. (Conical Sensor) 
            Fixed inputs used.
        """ 
        TestOrbitPropCovGrid.produce_cov_grid(self, 1, 90, -90, 180, -180, 5)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 0.1 # for faster computation
        prop_cov_param.sen_cone = 12.5
        prop_cov_param.step_size = 1
        prop_cov_param.sma = RE+500
        prop_cov_param.ta = 0
        prop_cov_param.aop = 0
        prop_cov_param.inc = 45
        prop_cov_param.raan = 245

        # zero pitch
        prop_cov_param.sen_orien = "1,2,3,0,0,0" # randomly orient with positive roll
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data1 = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        #### random positive pitch=> sensor points backwards ####        
        prop_cov_param.sen_orien = "1,2,3,25,0,0" # randomly orient with positive pitch
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data2 = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        #### random negative pitch=> sensor points forwards ####        
        prop_cov_param.sen_orien = "1,2,3,-25,0,0" # randomly orient with negative pitch
        # run the propagator
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()
        sat_acc_fl = prop_cov_param.sat_acc_fl
        data3 = pd.read_csv(sat_acc_fl, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        # the first gpi in pitch forward pitch case is detected earlier than in the zero pitch case and (both) earlier than the pitch backward case
        self.assertEqual(data3["gpi"][0], 1436)
        self.assertEqual(data3["accessTimeIndex"][0], 51)

        self.assertEqual(data1["gpi"][0], 1436)
        self.assertEqual(data1["accessTimeIndex"][0], 91)

        self.assertEqual(data2["gpi"][34], 1436)
        self.assertEqual(data2["accessTimeIndex"][34], 123)




