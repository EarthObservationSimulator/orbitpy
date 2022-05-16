import json
import os, shutil
import sys
import unittest
import numpy as np
import pandas as pd
import random
import json 

from orbitpy.coveragecalculator import CoverageOutputInfo, SpecularCoverage
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory

RE = 6378.137 # radius of Earth in kilometers

class TestSpecularCoverage(unittest.TestCase):

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
        cls.j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": cls.step_size})

        # define test spacecrafts

        # source (transmitting) spacecraft for specular coverage tests
        cls.navstar80_json = '{ "name": "NAVSTAR 80", \
                            "spacecraftBus":{ "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": { "date":{"@type":"GREGORIAN_UT1", "year":2022, "month":05, "day":15, "hour":17, "minute":58, "second":15.3}, \
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 26560.217, "ecc": 0.00185450, "inc": 54.5899, "raan": 271.4221, "aop": 184.7310, "ta": 336.981} \
                                        }, \
                            "@id": "navstar80" \
                        }'

        # receiving spacecraft for specular coverage tests
        cls.satX_json = '{  "name": "satX", \
                        "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                        "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                        "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":3, "day":18, "hour":12, "minute":10, "second":0}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -225} \
                                        } \
                        }'
        
        #navstar80 = Spacecraft.from_json(navstar80_json)
        #cls.satX = Spacecraft.from_json(satX_json)
    
    
    def test_from_dict(self):
        o = SpecularCoverage.from_dict({ "receiver": {"spacecraft": json.loads(self.satX_json), "cartesianStateFilePath":"../../state.csv"},
                                         "source": {"spacecraft": json.loads(self.satX_json), "cartesianStateFilePath":"../../state.csv"},
                                         "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o._type, 'SPECULAR COVERAGE')
        self.assertEqual(o.rx_spc, Spacecraft.from_json(self.satX_json))
        self.assertEqual(o.rx_state_file, "../../state.csv")
    

    def test_to_dict(self): #TODO
        pass

    def test_execute_0(self):
        """ Check the produced access file format.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=random.random()
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
                            "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                            "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                     }

        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                                           "@id":"bs1", "@type":"Basic Sensor"}

        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict, "@id":"satX"})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        SpecularCoverage(rx_spc=sat, rx_state_file=state_cart_file, tx_spc=sat, tx_state_file=state_cart_file).execute(instru_id=None, mode_id=None, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # check the outputs
        cov_calc_type = pd.read_csv(out_file_access, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'SPECULAR COVERAGE')

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
        self.assertEqual(column_headers.iloc[0][1],"source id")
        self.assertEqual(column_headers.iloc[0][2],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][3],"lon [deg]")