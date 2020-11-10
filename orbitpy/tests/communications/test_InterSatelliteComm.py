""" Unit tests for :class:`orbitpy.communications.GroundStationComm`.
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
import numpy as np
import pandas as pd
import random

from orbitpy.communications import InterSatelliteComm
from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach
from orbitpy.preprocess import PreProcess, OrbitParameters

RE = 6378.137 # [km] radius of Earth

class TestInterSatelliteComm(unittest.TestCase):

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
                        epoch="2019,7,2,11,0,0", 
                        sma=RE+random.uniform(350,850), 
                        ecc=0.001, 
                        inc=random.uniform(82,98), 
                        raan=60, 
                        aop=0, 
                        ta=0,
                        duration=1, 
                        cov_grid_fl=dir_path+"/temp/covGrid", 
                        sen_fov_geom="CONICAL", 
                        sen_orien="1,2,3,0,0,0",
                        sen_clock="0", 
                        sen_cone="25", 
                        purely_sidelook = 0, 
                        yaw180_flag = 0, 
                        step_size = 0.1+random.random(), 
                        sat_state_fl = dir_path+"/temp/state", 
                        sat_acc_fl = dir_path+"/temp/access", 
                        do_prop=True,
                        do_cov=True,
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)


        super(TestInterSatelliteComm, self).__init__(*args, **kwargs)

    def produce_cov_grid(self):
        """ Write a coverage grid file. 
            Coverage grid contains the same locations as that of the ground-stations (with matching indices).
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))

        cov_grid_fl = dir_path + "/temp/covGrid" # coverage grid file path

        with open(cov_grid_fl, 'w') as x:
                x.write("regi,gpi,lat[deg],lon[deg]\n")
                x.write("0,0,0,0\n")
                x.write("0,1,78.229772,15.407786\n")
                x.write("0,2,-72.0167,2.5333\n")

    def produce_walker_constellation(self, num_sats, num_planes, rel_spc, alt, ecc, inc, aop):
        # produce an uniform walker constellation with the satellite state and access files written in the temp directory
        data = { 'numberSatellites': num_sats,
                 'numberPlanes': num_planes,
                 'relativeSpacing': rel_spc,
                 'alt': alt,
                 'ecc': ecc,
                 'inc': inc,
                 'aop': aop
                }

        orbits = PreProcess.walker_orbits(data)

        dir_path = os.path.dirname(os.path.realpath(__file__))

        for orb in orbits:
            prop_cov_param = copy.deepcopy(self.default_pcp)
            prop_cov_param.duration = 0.5
            prop_cov_param.step_size = 5
            prop_cov_param.sat_id = orb._id
            prop_cov_param.sat_state_fl = dir_path + "/temp/sat" + str(orb._id) +"/state"
            prop_cov_param.sat_acc_fl = dir_path +  "/temp/sat" + str(orb._id) +"/access"
            prop_cov_param.sen_cone = "25"
            prop_cov_param.sma = orb.sma 
            prop_cov_param.inc = orb.inc
            prop_cov_param.raan = orb.raan
            prop_cov_param.aop = orb.aop
            prop_cov_param.ta = orb.ta
            prop_cov_param.cc = orb.ecc

            out_dir = dir_path + "/temp/sat" + str(orb._id) + "/"
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)
            os.makedirs(out_dir)

            opc_grid = OrbitPropCovGrid(prop_cov_param)
            opc_grid.run()

    def test_compute_all_contacts_1(self):
        """ Check format of produced output files (filenames included)."""

        dir_path = os.path.dirname(os.path.realpath(__file__))
        # create temporary directory
        out_dir = os.path.join(dir_path, 'temp/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        TestInterSatelliteComm.produce_cov_grid(self)
        TestInterSatelliteComm.produce_walker_constellation(self, 5, 1, 1, 700, 0, 98, 0) # make 5 satellite single plane constellation

        dir_path = os.path.dirname(os.path.realpath(__file__))
        isc = InterSatelliteComm([dir_path+"/temp/sat11/state", dir_path+"/temp/sat12/state", dir_path+"/temp/sat13/state", dir_path+"/temp/sat14/state", dir_path+"/temp/sat15/state"],
                                 dir_path+"/temp/",
                                 30)
        isc.compute_all_contacts()

        concise_fls = [dir_path+"/temp/sat11_to_sat12_concise",
                       dir_path+"/temp/sat11_to_sat14_concise",
                       dir_path+"/temp/sat11_to_sat15_concise",
                       dir_path+"/temp/sat12_to_sat13_concise",
                       dir_path+"/temp/sat12_to_sat14_concise",
                       dir_path+"/temp/sat12_to_sat15_concise",
                       dir_path+"/temp/sat13_to_sat14_concise",
                       dir_path+"/temp/sat13_to_sat15_concise",
                       dir_path+"/temp/sat14_to_sat15_concise" ]
        detailed_fls = [dir_path+"/temp/sat11_to_sat12_detailed",
                       dir_path+"/temp/sat11_to_sat14_detailed",
                       dir_path+"/temp/sat11_to_sat15_detailed",
                       dir_path+"/temp/sat12_to_sat13_detailed",
                       dir_path+"/temp/sat12_to_sat14_detailed",
                       dir_path+"/temp/sat12_to_sat15_detailed",
                       dir_path+"/temp/sat13_to_sat14_detailed",
                       dir_path+"/temp/sat13_to_sat15_detailed",
                       dir_path+"/temp/sat14_to_sat15_detailed" ]

        # check the names of the produced files
        for _fl in concise_fls:
            self.assertTrue(os.path.isfile(_fl))
        for _fl in detailed_fls:
            self.assertTrue(os.path.isfile(_fl))    

        # check the contents of the files
        _fref = dir_path+"/temp/sat11/state"
        _row2 = pd.read_csv(_fref, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        _row3 = pd.read_csv(_fref, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the step size
        _timeIndex = pd.read_csv(_fref, skiprows = [0,1,2,3])["TimeIndex"]
        for _fl in concise_fls:

            _eprow = pd.read_csv(_fl, nrows=1, header=None).astype(str) # 1st row contains the epoch
            _ssrow = pd.read_csv(_fl, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the step size
            _col_h = pd.read_csv(_fl, nrows=1, skiprows = [0,1], header=None) # time index column 

            self.assertTrue((_row2.iloc[0]==_eprow.iloc[0]).all())
            self.assertTrue((_row3.iloc[0]==_ssrow.iloc[0]).all())
            self.assertEqual(_col_h.iloc[0][0],"AccessFromIndex")
            self.assertEqual(_col_h.iloc[0][1],"AccessToIndex")

        for _fl in detailed_fls:

            _eprow = pd.read_csv(_fl, nrows=1, header=None).astype(str) # 1st row contains the epoch
            _ssrow = pd.read_csv(_fl, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the step size
            _col_h = pd.read_csv(_fl, skiprows = [0,1], nrows=1, header=None)  # column headers
            _ti = pd.read_csv(_fl, skiprows = [0,1])["TimeIndex"]  # time index column 

            self.assertTrue((_row2.iloc[0]==_eprow.iloc[0]).all())
            self.assertTrue((_row3.iloc[0]==_ssrow.iloc[0]).all())
            self.assertEqual(_col_h.iloc[0][0],"TimeIndex")
            self.assertEqual(_col_h.iloc[0][1],"AccessOrNoAccess")
            self.assertEqual(_col_h.iloc[0][2],"Range[km]")
            pd.testing.assert_series_equal(_timeIndex,_ti)


    def test_compute_all_contacts_2(self):
        """ Check that the adjacent satellites in plane containing 8 satellites at an altitude 
            of 700km shall always (throughout the mission duration) have connectivity with constant and equal Range
            while the non-adjacent satellites will never have connectivity. 
        """

        TestInterSatelliteComm.produce_cov_grid(self)
        alt = 700 #random.uniform(600,1100) 
        TestInterSatelliteComm.produce_walker_constellation(self, 8, 1, 1, alt, 0, random.uniform(0,180), random.uniform(0,360)) # make 5 satellite single plane constellation with some Keplerian elements chosen randomly

        dir_path = os.path.dirname(os.path.realpath(__file__))
        isc = InterSatelliteComm([dir_path+"/temp/sat11/state", dir_path+"/temp/sat12/state", dir_path+"/temp/sat13/state", dir_path+"/temp/sat14/state", dir_path+"/temp/sat15/state", dir_path+"/temp/sat16/state", dir_path+"/temp/sat17/state", dir_path+"/temp/sat18/state"],
                                 dir_path+"/temp/",
                                 30)
        isc.compute_all_contacts()

        
        num_time_steps = pd.read_csv(dir_path+"/temp/sat11/state", skiprows = [0,1,2,3])["TimeIndex"].size

        adj_sat_concise_fls = [dir_path+"/temp/sat11_to_sat12_concise",
                               dir_path+"/temp/sat12_to_sat13_concise",
                               dir_path+"/temp/sat13_to_sat14_concise", 
                               dir_path+"/temp/sat14_to_sat15_concise",
                               dir_path+"/temp/sat15_to_sat16_concise",
                               dir_path+"/temp/sat16_to_sat17_concise",
                               dir_path+"/temp/sat17_to_sat18_concise",
                               dir_path+"/temp/sat11_to_sat18_concise"]

        adj_sat_detailed_fls = [dir_path+"/temp/sat11_to_sat12_detailed",
                                dir_path+"/temp/sat12_to_sat13_detailed",
                                dir_path+"/temp/sat13_to_sat14_detailed", 
                                dir_path+"/temp/sat14_to_sat15_detailed",
                                dir_path+"/temp/sat15_to_sat16_detailed",
                                dir_path+"/temp/sat16_to_sat17_detailed",
                                dir_path+"/temp/sat17_to_sat18_detailed",
                                dir_path+"/temp/sat11_to_sat18_detailed"]       

        # calculate range between adjacent satellites by using the fact that the two satellites and the center of Earth
        # form a triangle where the length of two sides of the triangle is known and one of the angles is known
        _angle = 2*np.pi/8
        _side = RE + alt
        _range = np.sqrt(_side*_side + _side*_side - 2*_side*_side*np.cos(_angle))
        
        for _fl in adj_sat_detailed_fls:
            _data = pd.read_csv(_fl, skiprows = [0,1]) 
            self.assertTrue((_data["AccessOrNoAccess"] == True).all())
            self.assertAlmostEqual(_data["Range[km]"][0],_range, delta = 20)
            for k in range(1,_data["Range[km]"].size):
                self.assertAlmostEqual(_data["Range[km]"][0],_data["Range[km]"][k], delta = 20) # all elements almost equal since circular orbit with equi-angular spaced satellites

        
        for _fl in adj_sat_concise_fls:
            _data = pd.read_csv(_fl, skiprows = [0,1])
            self.assertEqual(_data["AccessFromIndex"][0], 0)
            self.assertEqual(_data["AccessToIndex"][0], num_time_steps-1)

        
        non_adj_sat_concise_fls = [dir_path+"/temp/sat11_to_sat13_concise", dir_path+"/temp/sat11_to_sat14_concise",
                                    dir_path+"/temp/sat11_to_sat15_concise", dir_path+"/temp/sat11_to_sat16_concise",
                                    dir_path+"/temp/sat11_to_sat17_concise", dir_path+"/temp/sat12_to_sat14_concise",
                                    dir_path+"/temp/sat12_to_sat15_concise", dir_path+"/temp/sat12_to_sat16_concise",
                                    dir_path+"/temp/sat12_to_sat17_concise", dir_path+"/temp/sat12_to_sat18_concise",
                                    dir_path+"/temp/sat13_to_sat15_concise", dir_path+"/temp/sat13_to_sat16_concise",
                                    dir_path+"/temp/sat13_to_sat17_concise", dir_path+"/temp/sat13_to_sat18_concise",
                                    dir_path+"/temp/sat14_to_sat16_concise", dir_path+"/temp/sat14_to_sat17_concise",
                                    dir_path+"/temp/sat14_to_sat18_concise", dir_path+"/temp/sat15_to_sat17_concise",
                                    dir_path+"/temp/sat15_to_sat18_concise", dir_path+"/temp/sat16_to_sat18_concise"]
        
        non_adj_sat_detailed_fls = [dir_path+"/temp/sat11_to_sat13_detailed", dir_path+"/temp/sat11_to_sat14_detailed",
                                    dir_path+"/temp/sat11_to_sat15_detailed", dir_path+"/temp/sat11_to_sat16_detailed",
                                    dir_path+"/temp/sat11_to_sat17_detailed", dir_path+"/temp/sat12_to_sat14_detailed",
                                    dir_path+"/temp/sat12_to_sat15_detailed", dir_path+"/temp/sat12_to_sat16_detailed",
                                    dir_path+"/temp/sat12_to_sat17_detailed", dir_path+"/temp/sat12_to_sat18_detailed",
                                    dir_path+"/temp/sat13_to_sat15_detailed", dir_path+"/temp/sat13_to_sat16_detailed",
                                    dir_path+"/temp/sat13_to_sat17_detailed", dir_path+"/temp/sat13_to_sat18_detailed",
                                    dir_path+"/temp/sat14_to_sat16_detailed", dir_path+"/temp/sat14_to_sat17_detailed",
                                    dir_path+"/temp/sat14_to_sat18_detailed", dir_path+"/temp/sat15_to_sat17_detailed",
                                    dir_path+"/temp/sat15_to_sat18_detailed", dir_path+"/temp/sat16_to_sat18_detailed"]
    
        for _fl in non_adj_sat_detailed_fls:
            _data = pd.read_csv(_fl, skiprows = [0,1]) 
            self.assertTrue((_data["AccessOrNoAccess"] == False).all())

        for _fl in non_adj_sat_concise_fls:
            _data = pd.read_csv(_fl, skiprows = [0,1]) 
            self.assertEqual(_data["AccessFromIndex"].size, 0) # no entries
            self.assertEqual(_data["AccessToIndex"].size, 0)





        
  
