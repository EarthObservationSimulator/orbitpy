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

from orbitpy.communications import GroundStationComm
from orbitpy.orbitpropcov import OrbitPropCovGrid
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

RE = 6378.137 # [km] radius of Earth

class TestGroundStationComm(unittest.TestCase):

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
                        cov_calcs_app= CoverageCalculationsApproach.GRIDPNTS)


        super(TestGroundStationComm, self).__init__(*args, **kwargs)

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

    def produce_gndstn_data(self, min_elv):
        """ Write ground-stations file. """
        dir_path = os.path.dirname(os.path.realpath(__file__))

        gndstn_fl = dir_path + "/temp/groundStations" # coverage grid file path

        with open(gndstn_fl, 'w') as x:
                x.write("index,name,lat[deg],lon[deg],alt[km],minElevation[deg]\n")
                x.write("100,Zero,0,0,0,"+ str(min_elv) + "\n")
                x.write("101,Svalbard,78.229772,15.407786,0,"+ str(min_elv) + "\n")
                x.write("102,TrollSat,-72.0167,2.5333,0,"+ str(min_elv) + "\n")

    def test_compute_all_contacts_1(self):
        """ Check format of produced output files (filenames included)."""
        # Make 3 satellite mission. With 3 ground-stations. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # create temporary directory
        out_dir = os.path.join(dir_path, 'temp/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        os.makedirs(os.path.join(out_dir, 'sat11/'))
        os.makedirs(os.path.join(out_dir, 'sat21/'))
        os.makedirs(os.path.join(out_dir, 'sat31/'))

        TestGroundStationComm.produce_cov_grid(self)

        prop_cov_param = copy.deepcopy(self.default_pcp)
        prop_cov_param.duration = 1
        prop_cov_param.step_size = 5
        prop_cov_param.sat_id = str(11)
        prop_cov_param.sat_state_fl = dir_path + "/temp/sat11/state"
        prop_cov_param.sat_acc_fl = dir_path + "/temp/sat11/access"
        prop_cov_param.sen_cone = "90" # large sensor cone angle to capture entire horizon irrespective of satellite altitude
        prop_cov_param.sma = RE+random.uniform(350,850) # random altitude
        prop_cov_param.inc = random.uniform(82,98) # so that the polar ground-stations can be seen

        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()

        prop_cov_param.sat_id = str(21)
        prop_cov_param.raan = 120
        prop_cov_param.ta = 120
        prop_cov_param.sat_state_fl = dir_path + "/temp/sat21/state"
        prop_cov_param.sat_acc_fl = dir_path + "/temp/sat21/access"
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()

        prop_cov_param.sat_id = str(31)
        prop_cov_param.raan = 240
        prop_cov_param.ta = 240
        prop_cov_param.sat_state_fl = dir_path + "/temp/sat31/state"
        prop_cov_param.sat_acc_fl = dir_path + "/temp/sat31/access"
        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()

        TestGroundStationComm.produce_gndstn_data(self, 0)

        
        gsc = GroundStationComm([dir_path+"/temp/sat11/",
                                 dir_path+"/temp/sat21/",
                                 dir_path+"/temp/sat31/" ], 
                                 dir_path + "/temp/groundStations")
        gsc.compute_all_contacts()

        # check the names of the produced files
        sats = ["sat11", "sat21","sat31"]
        gndstns = ["100","101","102"]

        for _s in sats:
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn100_contact_concise"))
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn100_contact_detailed"))
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn101_contact_concise"))
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn101_contact_detailed"))
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn102_contact_concise"))
            self.assertTrue(os.path.isfile(dir_path+"/temp/" + _s + "/gndStn102_contact_detailed"))

        # check the contents of the files
        _fref = dir_path+"/temp/sat11/state"
        _row2 = pd.read_csv(_fref, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        _row3 = pd.read_csv(_fref, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the step size
        _timeIndex = pd.read_csv(_fref, skiprows = [0,1,2,3])["TimeIndex"]

        for _s in sats:

            for _gs in gndstns:

                _f1 = dir_path+"/temp/" + _s + "/gndStn" + _gs +"_contact_concise"
                _eprow = pd.read_csv(_f1, nrows=1, header=None).astype(str) # 1st row contains the epoch
                _ssrow = pd.read_csv(_f1, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the step size
                _col_h = pd.read_csv(_f1, nrows=1, skiprows = [0,1], header=None) # column headers

                self.assertTrue((_row2.iloc[0]==_eprow.iloc[0]).all())
                self.assertTrue((_row3.iloc[0]==_ssrow.iloc[0]).all())
                self.assertEqual(_col_h.iloc[0][0],"AccessFromIndex")
                self.assertEqual(_col_h.iloc[0][1],"AccessToIndex")

                _f2 = dir_path+"/temp/" + _s + "/gndStn" + _gs +"_contact_detailed"
                _eprow = pd.read_csv(_f2, nrows=1, header=None).astype(str) # 1st row contains the epoch
                _ssrow = pd.read_csv(_f2, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the step size
                _col_h = pd.read_csv(_f2, skiprows = [0,1], header=None)  # column headers
                _ti = pd.read_csv(_f2, skiprows = [0,1])["TimeIndex"]  # time index column 
                pd.testing.assert_series_equal(_timeIndex,_ti)

                self.assertTrue((_row2.iloc[0]==_eprow.iloc[0]).all())
                self.assertTrue((_row3.iloc[0]==_ssrow.iloc[0]).all())
                self.assertEqual(_col_h.iloc[0][0],"TimeIndex")
                self.assertEqual(_col_h.iloc[0][1],"AccessOrNoAccess")
                self.assertEqual(_col_h.iloc[0][2],"Range[km]")
                self.assertEqual(_col_h.iloc[0][3],"Elevation[deg]")           

    def test_compute_all_contacts_2(self):
        """ Test only one satellite case. Compare the access data from coverage calculations (at the same locations as that of
            the ground-stations) with the produced ground-station contact intervals.
        """

        TestGroundStationComm.produce_cov_grid(self) # coverage grid contains the same locations as that of the ground-stations
        

        prop_cov_param = copy.deepcopy(self.default_pcp)
        
        # create directory to house the satellite files
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_dir = os.path.join(dir_path, 'temp/sat1/')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        prop_cov_param.duration = 1
        prop_cov_param.step_size = 5
        prop_cov_param.sat_id = str(1)
        prop_cov_param.sat_state_fl = dir_path + "/temp/sat1/state"
        prop_cov_param.sat_acc_fl = dir_path + "/temp/sat1/access"
        prop_cov_param.sen_cone = "90" # large sensor cone angle to capture entire horizon irrespective of satellite altitude
        prop_cov_param.sma = RE+random.uniform(350,850) # random altitude
        prop_cov_param.inc = random.uniform(82,98) # so that the polar ground-stations can be seen

        opc_grid = OrbitPropCovGrid(prop_cov_param)
        opc_grid.run()

        TestGroundStationComm.produce_gndstn_data(self, 0)

        gsc = GroundStationComm([dir_path+"/temp/sat1/"], dir_path + "/temp/groundStations")
        gsc.compute_all_contacts()

        # check that the ground-stations contact at the middle of the contact intervals are also
        # present as being accessed in the access files
        acc_data = pd.read_csv(dir_path+"/temp/sat1/access", skiprows=[0,1,2,3])        
        acc_data = acc_data.set_index("gpi")

        for gpi in [0,1,2]:
            gndstn_data = pd.read_csv(dir_path+"/temp/sat1/gndStn"+str(100+gpi)+"_contact_concise", skiprows=[0,1]) # '+100' cause corresponding (to the gp's) indices of ground stations are 100, 101, 102       

            for index, row in gndstn_data.iterrows():
                mid_contact_time = int(row["AccessFromIndex"] + 0.5*(row["AccessToIndex"] - row["AccessFromIndex"]))
                self.assertIn(mid_contact_time, acc_data.loc[gpi]["accessTimeIndex"].tolist()) 
