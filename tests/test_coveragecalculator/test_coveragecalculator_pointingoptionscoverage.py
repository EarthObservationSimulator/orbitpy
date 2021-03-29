"""Unit tests for orbitpy.coveragecalculator.pointingoptionscoverage class.

``TestPointingOptionsCoverage`` class:

* ``test_execute_0``: Test format of output access files.
* ``test_execute_1``: For a random circular orbit, test that pointing of the Euler angles, sequence (0,0,x,1,2,3) shall yield access points equal to the satellite position.
* ``test_execute_2``: For a equatorial orbit, test the accessed ground-points against an analytical result.

TODO: tests to check behavior with multiple sensors, modes

"""

import json
import os, shutil
import sys
import unittest
import numpy as np
import pandas as pd
import random
import warnings 
import json 

import propcov
from orbitpy.coveragecalculator import CoverageCalculatorFactory, PointingOptionsCoverage
import orbitpy.coveragecalculator
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus
from orbitpy.propagator import PropagatorFactory

from instrupy.util import ViewGeometry, Orientation, SphericalGeometry, GeoUtilityFunctions
from instrupy import Instrument

sys.path.append('../')
from tests.util import spc1_json, spc2_json, spc3_json, spc4_json, spc5_json

RE = 6378.137 # radius of Earth in kilometers
    
class TestPointingOptionsCoverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

        # make propagator
        factory = PropagatorFactory()
        cls.step_size = 1
        cls.j2_prop = factory.get_propagator({"@type": 'J2 Analytical Propagator', "stepSize": cls.step_size})

    def test_from_dict(self):
        o = PointingOptionsCoverage.from_dict({ "spacecraft": json.loads(spc1_json),
                                                "cartesianStateFilePath":"../../state.csv",
                                                "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o.spacecraft, Spacecraft.from_json(spc1_json))
        self.assertEqual(o.state_cart_file, "../../state.csv")

    def test_to_dict(self): #TODO
        pass

    def test_execute_0(self):
        """ Check the produced access file format.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=random.random()
        orbit_dict = {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
                            "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                            "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                     }

        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, 
                                           "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":2.5, "zRotation":0},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-2.5, "zRotation":0}],
                                           "@id":"bs1", "@type":"Basic Sensor"}

        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        PointingOptionsCoverage(spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # check the outputs
        cov_calc_type = pd.read_csv(out_file_access, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'Pointing Options Coverage')

        epoch_JDUT1 = pd.read_csv(out_file_access, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.0)

        _step_size = pd.read_csv(out_file_access, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_access, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, duration)

        column_headers = pd.read_csv(out_file_access, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"pnt-opt index")
        self.assertEqual(column_headers.iloc[0][2],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][3],"lon [deg]")
    
    def test_execute_1(self):
        """ Test that the pointing euler-angles, euler-sequence (0,0,x, 1,2,3) (where x is variable) corresponds to pointing at the 
            nadir position which shall be the same as the satellite position.
        """ 
        # setup spacecraft with some parameters setup randomly     
        duration=0.1
        sma = RE+random.uniform(350,850)
        orbit_dict = {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": sma, 
                            "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                            "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                     }

        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":random.uniform(0,360)},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":random.uniform(0,360)},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":random.uniform(0,360)},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":random.uniform(0,360)},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":random.uniform(0,360)}],
                                           "@id":"bs1", "@type":"Basic Sensor"}

        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
      
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        PointingOptionsCoverage(spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # extract satellite position data from state file
        epoch_JDUT1 = pd.read_csv(out_file_access, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        step_size = pd.read_csv(out_file_access, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])

        states_df = pd.read_csv(state_cart_file, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        states_df.set_index("time index")        

        sat_lat = []
        sat_lon = []
        for idx, state in states_df.iterrows():
            [lat,lon,alt] = GeoUtilityFunctions.eci2geo([state['x [km]'], state['y [km]'], state['z [km]']], 
                                                         epoch_JDUT1 + state['time index']*step_size*(1.0/86400.0))
            sat_lat.append(round(lat, 2))
            sat_lon.append(round(lon, 2))
        # compare the results of the coverage calculation with the satellite position data
        access_data_df = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        # iterate over each pointing-option
        access_data_grp = access_data_df.groupby('pnt-opt index') # group according to ground-point indices
        # iterate over all the groups (ground-point indices)
        for name, group in access_data_grp:
            access_lat = group['lat [deg]'].to_numpy()
            access_lon = group['lon [deg]'].to_numpy()
            self.assertTrue(np.allclose(sat_lat, access_lat))
            self.assertTrue(np.allclose(sat_lon, access_lon))
    
    def test_execute_2(self):
        """ Test that the pointing for the case of equatorial orbit at randomly chosen altitudes. Pointing to the nadir with any random yaw shall result
            in covering latitude 0 deg always (throughout the mission). Pointing with a random roll (only) orientation (at some random altitude) shall result
            in coverage of latitude as defined by the resulting Earth-centric half-angle subtended by twice the roll angle (the same latitude throughout the massion). 

        """ 
        # setup spacecraft with some parameters setup randomly     
        duration=0.1
        sma = RE+random.uniform(350,850)
        alt = sma - RE
        orbit_dict = {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": sma, 
                            "ecc": 0, "inc": 0, "raan": random.uniform(0,360), 
                            "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                     }

        # 1st pointing-opt has random yaw, second and third pointing options have random rolls
        yaw_po1 = random.uniform(0,360)
        roll_po2 = random.uniform(0,30)
        roll_po3 = random.uniform(0,-30)
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":0, "zRotation":yaw_po1},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":roll_po2, "zRotation":0},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":roll_po3, "zRotation":0}
                                                            ],
                                           "@id":"bs1", "@type":"Basic Sensor"}

        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
      
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        PointingOptionsCoverage(spacecraft=sat, state_cart_file=state_cart_file).execute(sensor_id=None, mode_id=None, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # perform checks on the output access data
        access_data_df = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        # iterate over each pointing-option
        access_data_grp = access_data_df.groupby('pnt-opt index') # group according to ground-point indices
        
        # pointing option with random yaw yaw_po1
        group0 = access_data_grp.get_group(0)
        group0_truth = np.zeros((len(group0),1))
        self.assertTrue(np.allclose(group0['lat [deg]'].to_numpy(), group0_truth))
        # pointing option with random roll roll_po2
        group1 = access_data_grp.get_group(1)
        group1_truth = np.zeros((len(group1),))  + round(0.5*GeoUtilityFunctions.get_eca(2*roll_po2, alt),2)        
        self.assertTrue(np.allclose(group1['lat [deg]'].to_numpy(), group1_truth))
        # pointing option with random roll roll_po3
        group2 = access_data_grp.get_group(2) 
        group2_truth = np.zeros((len(group2),)) + round(0.5*GeoUtilityFunctions.get_eca(2*roll_po3, alt), 2)
        self.assertTrue(np.allclose(group2['lat [deg]'].to_numpy(), group2_truth))

     

        