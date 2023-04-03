"""Unit tests for orbitpy.coveragecalculator.pointingoptionswithgridcoverage class.

``TestPointingOptionsWithGridCoverage`` class:

* ``test_execute_0``: Test format of output access files.
* ``test_execute_1``: Test PointingOptionsWithGridCoverage output with separate runs of GridCoverage calculator. 

TODO: tests to check behavior with multiple sensors, modes
TODO: Add tests which checks the filters mid-interval access functionality.

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

from orbitpy.coveragecalculator import CoverageOutputInfo, PointingOptionsWithGridCoverage, GridCoverage
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory

sys.path.append('../')
from util.spacecrafts import spc1_json

RE = 6378.137 # radius of Earth in kilometers
    
class TestPointingOptionsWithGridCoverage(unittest.TestCase):

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

    def test_from_dict(self):
        o = PointingOptionsWithGridCoverage.from_dict({ "grid":{"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2},
                                     "spacecraft": json.loads(spc1_json),
                                     "cartesianStateFilePath":"../../state.csv",
                                     "@id": 12})
        self.assertEqual(o._id, 12)
        self.assertEqual(o._type, 'POINTING OPTIONS WITH GRID COVERAGE')
        self.assertEqual(o.grid, Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2}))
        self.assertEqual(o.spacecraft, Spacecraft.from_json(spc1_json))
        self.assertEqual(o.state_cart_file, "../../state.csv")

    def test_to_dict(self): #TODO
        pass

    
    def test_execute_0(self):
        """ Check the produced access file format.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=0.005
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
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
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1})
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        out_info = PointingOptionsWithGridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "POINTING OPTIONS WITH GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": sat.get_instrument(None)._id,
                                                                    "modeId": sat.get_instrument(None).get_mode_id()[0],
                                                                    "usedFieldOfRegard": None,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2458265.00000,
                                                                    "duration": duration, "@id":None}))

        # check the outputs
        cov_calc_type = pd.read_csv(out_file_access, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'POINTING OPTIONS WITH GRID COVERAGE')

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
        self.assertEqual(column_headers.iloc[0][2],"GP index")
        self.assertEqual(column_headers.iloc[0][3],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][4],"lon [deg]")

        # check that the grid indices are interpreted correctly
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
        access_data = access_data.round(3)
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
            self.assertTrue(lat==access_data['lat [deg]'].tolist())
            self.assertTrue(lon==access_data['lon [deg]'].tolist())
        else:
            warnings.warn('No data was generated in test_execute_0(.). Run the test again.')
    
    def test_execute_1(self):
        """ Test the result of PointingOptionsWithGridCoverage with separate runs of GridCoverage.
        """
        
        duration=random.random()
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":8, "day":30, "hour":16, "minute":0, "second":0}, # JD: 2459457.1666666665
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+750, 
                            "ecc": 0, "inc": 60, "raan": 240, 
                            "aop": 10, "ta": 320}
                     }
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1})

        # simulation-1 with PointingOptionsWithGridCoverage
        instrument_dict = [{"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, 
                                           "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":10, "yRotation":2.5, "zRotation":320},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":-5, "yRotation":-25, "zRotation":20}],
                                           "@id":"bs1", "@type":"Basic Sensor"},
                            {"orientation": {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":10, "yRotation":2.5, "zRotation":320}, 
                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                            "@id":"bs2", "@type":"Basic Sensor"},
                            {"orientation": {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":-5, "yRotation":-25, "zRotation":20}, 
                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                            "@id":"bs3", "@type":"Basic Sensor"}
                           ]
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access1.csv'
        # run the coverage calculator, bs1 instrument
        out_info = PointingOptionsWithGridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id='bs1', mode_id=None, out_file_access=out_file_access)
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "POINTING OPTIONS WITH GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": sat.get_instrument('bs1').get_mode_id()[0],
                                                                    "usedFieldOfRegard": None,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2459457.1666666665,
                                                                    "duration": duration, "@id":None}))

        access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data 
        access_data1_grp = access_data1.groupby('pnt-opt index') # group according to ground-point indices
        group0 = access_data1_grp.get_group(0)
        group1 = access_data1_grp.get_group(1)
        
        # simulation-2 with GridCoverage
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access2.csv'
        # run the coverage calculator, bs2 instrument
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id='bs2', out_file_access=out_file_access)
        access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data 

        # simulation-3 with GridCoverage
   
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access3.csv'
        # run the coverage calculator, bs3 instrument
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id='bs3', out_file_access=out_file_access)
        access_data3 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data 

        # compare results
        # group0 == access_data2, group1 == access_data3
        self.assertTrue(np.allclose(group0['time index'].to_numpy(), access_data2['time index'].to_numpy()))
        self.assertTrue(np.allclose(group0['GP index'].to_numpy(), access_data2['GP index'].to_numpy()))

        self.assertTrue(np.allclose(group1['time index'].to_numpy(), access_data3['time index'].to_numpy()))
        self.assertTrue(np.allclose(group1['GP index'].to_numpy(), access_data3['GP index'].to_numpy()))
    

    def test_execute_3(self):
        """ Test with the `mid_access_only` flag set to 'True' in PointingOptionsWithGridCoverage.  
        """
        
        duration = 0.0025
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":8, "day":30, "hour":16, "minute":0, "second":0}, # JD: 2459457.1666666665
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+750, 
                            "ecc": 0, "inc": 60, "raan": 240, 
                            "aop": 10, "ta": 320}
                     }
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1})

        instrument_dict = [{"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, 
                                           "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":10, "yRotation":2.5, "zRotation":320},
                                                             {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":-5, "yRotation":-25, "zRotation":20}],
                                           "@id":"bs1", "@type":"Basic Sensor"},
                            {"orientation": {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":10, "yRotation":2.5, "zRotation":320}, 
                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                            "@id":"bs2", "@type":"Basic Sensor"},
                            {"orientation": {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":-5, "yRotation":-25, "zRotation":20}, 
                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 10}, 
                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                            "@id":"bs3", "@type":"Basic Sensor"}
                           ]
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)

        out_file_access = self.out_dir+'/test_cov_access1.csv'
        # run the coverage calculator, bs1 instrument
        out_info = PointingOptionsWithGridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id='bs1', mode_id=None, out_file_access=out_file_access, mid_access_only=False)
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "POINTING OPTIONS WITH GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": sat.get_instrument('bs1').get_mode_id()[0],
                                                                    "usedFieldOfRegard": None,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2459457.1666666665,
                                                                    "duration": duration, "@id":None}))
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access2.csv'
        # run the coverage calculator, bs1 instrument
        out_info = PointingOptionsWithGridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id='bs1', mode_id=None, out_file_access=out_file_access, mid_access_only=True)
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "POINTING OPTIONS WITH GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": 'bs1',
                                                                    "modeId": sat.get_instrument('bs1').get_mode_id()[0],
                                                                    "usedFieldOfRegard": None,
                                                                    "filterMidIntervalAccess": True,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2459457.1666666665,
                                                                    "duration": duration, "@id":None}))
    
        