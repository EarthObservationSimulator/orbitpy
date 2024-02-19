"""Unit tests for orbitpy.coveragecalculator.gridcoverage class.

In case of rectangular sensors, both the methods to evaluate point in spherical polygon: 
(1) 'ProjectedPIP' and (2) 'DirectSphericalPIP' are evaluated.

``TestGridCoverage`` class:

* ``test_execute_0``: Test format of output access files.
* ``test_execute_1``: Roll Circular sensor tests
* ``test_execute_2``: Yaw Circular sensor tests
* ``test_execute_3``: Pitch Circular sensor tests
* ``test_execute_4``: Roll Rectangular sensor tests
* ``test_execute_5``: Pitch Rectangular sensor tests
* ``test_execute_6``: Satellite-bus orientation vs sensor orientation tests
* ``test_execute_7``: Test spacecraft with multiple sensors.
* ``test_execute_8``: Test FOV vs FOR coverage. Coverage of FOR >= Coverage of FOV.
* ``test_execute_9``:  Test coverage with DOUBLE_ROLL_ONLY maneuver will which result in 2 ``ViewGeometry`` objects for the field-of-regard.

TODO: Add tests which checks the filters mid-interval access functionality.

"""

import json
import os, shutil
import sys
import unittest
import pandas as pd
import random
import warnings 
import json 

from orbitpy.coveragecalculator import CoverageOutputInfo, GridCoverage
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory

sys.path.append('../')
from util.spacecrafts import spc1_json, spc4_json, spc5_json

RE = 6378.137 # radius of Earth in kilometers

# method used in coverage calculation involving rectangular sensors. Tests are carried out for each method seperately.
method_list = ['ProjectedPIP', 'DirectSphericalPIP', 'RectangularPIP']

class TestGridCoverage(unittest.TestCase):

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
        o = GridCoverage.from_dict({ "grid":{"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2},
                                     "spacecraft": json.loads(spc1_json),
                                     "cartesianStateFilePath":"../../state.csv",
                                     "@id": 12})
        self.assertEqual(o._id, 12)
        self.assertEqual(o._type, 'GRID COVERAGE')
        self.assertEqual(o.grid, Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2}))
        self.assertEqual(o.spacecraft, Spacecraft.from_json(spc1_json))
        self.assertEqual(o.state_cart_file, "../../state.csv")

    def test_to_dict(self): #TODO
        pass

    #@unittest.skip
    def test_execute_0(self):
        """ Check the produced access file format.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=0.05
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+random.uniform(350,850), 
                            "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                            "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                     }

        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": random.uniform(5,35) }, 
                                           "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, "@id":"bs1", "@type":"Basic Sensor"}

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
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) # the first instrument, mode available in the spacecraft is considered for the coverage calculation.

        # check the outputs
        cov_calc_type = pd.read_csv(out_file_access, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'GRID COVERAGE')

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
        self.assertEqual(column_headers.iloc[0][1],"GP index")
        self.assertEqual(column_headers.iloc[0][2],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][3],"lon [deg]")

        # check that the grid indices are interpreted correctly
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data     
        access_data = access_data.round(3)   
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
            self.assertTrue(lat==access_data['lat [deg]'].tolist())
            self.assertTrue(lon==access_data['lon [deg]'].tolist())
        else:
            warnings.warn('No data was generated in test_execute_0(.). Run the test again.')

    #@unittest.skip
    def test_execute_1(self):
        """ Orient the sensor with roll, and an equatorial orbit and check that the ground-points captured are on either
            side of hemisphere only. (Conical Sensor)
        """ 
        ############ Common attributes for both positive and negative roll tests ############
        duration = 0.1
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                        "ecc": 0.001, "inc": 0, "raan": 20, 
                        "aop": 0, "ta": 120}
                     }

        ############ positive roll ############
        # setup spacecraft with some parameters setup randomly   
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":12.5}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)   
        # set output file path
        out_file_access = self.out_dir+'/test_cov_accessX.csv'
        # run the coverage calculator
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
        out_info = cov.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access)
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": sat.get_instrument(None)._id,
                                                                    "modeId": sat.get_instrument(None).get_mode_id()[0],
                                                                    "usedFieldOfRegard": False,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2458265.00000,
                                                                    "duration": duration, "@id":None}))        
        
        # check the outputs
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
        
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
            self.assertTrue(all(x > 0 for x in lat))
        else:
            warnings.warn('No data was generated in test_execute_1(.) positive roll test. Run the test again.')
        
        ############ negative roll ############
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":-12.5}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
        # no need to rerun propagator, since propagation does not depend on sensor
        # set output file path
        out_file_access = self.out_dir+'/test_cov_accessY.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access)   
        # check the outputs
        access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
        if not access_data.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
            self.assertTrue(all(x < 0 for x in lat))
        else:
            warnings.warn('No data was generated in test_execute_1(.) negative roll test. Run the test again.')
        
    #@unittest.skip
    def test_execute_2(self):
        """ Orient the sensor with varying yaw but same pitch and roll, and test that the captured ground-points remain the same
            (Conical Sensor). 
        """ 
        ####### Common attributes for both simulations #######
        duration = 0.1
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                            "ecc": 0.001, "inc": 0, "raan": 0, 
                            "aop": 0, "ta": 0}
                     }
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 5})
        
        pitch = 15
        roll = 10.5

        ######## Simulation 1 #######
        yaw = random.uniform(0,360)
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": roll, "zRotation": yaw}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
        
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        out_info = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": sat.get_instrument(None)._id,
                                                                    "modeId": sat.get_instrument(None).get_mode_id()[0],
                                                                    "usedFieldOfRegard": False,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2458265.00000,
                                                                    "duration": duration, "@id":None}))

        access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        ######## Simulation 2 ########
        yaw = random.uniform(0,360)
        instrument_dict = {"mode":[{"@id":"m1", "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ",  "xRotation": pitch, "yRotation": roll, "zRotation": yaw}}], 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"sen1", "@type":"Basic Sensor"}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        # no need to rerun propagator, since propagation does not depend on sensor
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # run the coverage calculator
        out_info = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 

        self.assertEqual(out_info, CoverageOutputInfo.from_dict({   "coverageType": "GRID COVERAGE",
                                                                    "spacecraftId": sat._id,
                                                                    "instruId": "sen1",
                                                                    "modeId": "m1",
                                                                    "usedFieldOfRegard": False,
                                                                    "filterMidIntervalAccess": False,
                                                                    "gridId": grid._id,
                                                                    "stateCartFile": state_cart_file,
                                                                    "accessFile": out_file_access,
                                                                    "startDate": 2458265.00000,
                                                                    "duration": duration, "@id":None}))

        access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        ######## compare the results of both the simulations ########    
        if not access_data1.empty:
            (lat1, lon1) = grid.get_lat_lon_from_index(access_data1['GP index'].tolist())
            (lat2, lon2) = grid.get_lat_lon_from_index(access_data2['GP index'].tolist())
            self.assertTrue(lat1==lat2)
        else:
            warnings.warn('No data was generated in test_execute_2(.). Run the test again.')
    
    #@unittest.skip
    def test_execute_3(self):
        """ Orient the sensor with pitch and test that the times the ground-points are captured lag or lead (depending on direction of pitch)
            as compared to the coverage from a zero pitch sensor. (Conical Sensor) 
            Fixed inputs used.
        """ 
        ####### Common attributes for all the simulations #######
        duration = 0.1
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                            "ecc": 0.001, "inc": 45, "raan": 245, 
                            "aop": 0, "ta": 0}
                     }
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 5})
        grid.write_to_file(self.out_dir+'/grid.csv')
        ######## Simulation 1 #######
        pitch = 0
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, out_file_cart=state_cart_file, duration=duration)

        # set output file path
        out_file_access = self.out_dir+'/test_cov_access1.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        
        ######## Simulation 2 #######
        pitch = 25
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # no need to rerun propagator, since propagation does not depend on sensor
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access2.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        ######## Simulation 3 #######
        pitch = -25
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                           "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}

        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # no need to rerun propagator, since propagation does not depend on sensor
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access3.csv'
        # run the coverage calculator
        GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access) 
        
        access_data3 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        ######## compare the results of both the simulations ########   
        # the first gpi in pitch forward pitch case is detected earlier than in the zero pitch case and (both) earlier than the pitch backward case
        self.assertEqual(access_data3["GP index"][0], 1436)
        self.assertEqual(access_data3["time index"][0], 51)

        self.assertEqual(access_data1["GP index"][0], 1436)
        self.assertEqual(access_data1["time index"][0], 91)

        self.assertEqual(access_data2["GP index"][34], 1436)
        self.assertEqual(access_data2["time index"][34], 123)
    
    #@unittest.skip
    def test_execute_4(self):
        """ Orient the sensor with roll, and an equatorial orbit and check that the ground-points captured are on either
            side of hemisphere only. (Rectangular Sensor)
        """ 
        ############ Common attributes for both positive and negative roll tests ############
        duration = 0.1
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                                       "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                                                "ecc": 0.001, "inc": 0, "raan": 20, 
                                                "aop": 0, "ta": 120}
                                       }

        ############ positive roll ############
        # setup spacecraft with some parameters setup randomly   
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":12.6}, 
                                           "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=sat, out_file_cart=state_cart_file, duration=duration)   
        # set output file path
        out_file_access = self.out_dir+'/test_cov_accessX.csv'
        # make and run the coverage calculator
        cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                cov.execute(out_file_access=out_file_access, method=method)
                # check the outputs
                access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
                
                if not access_data.empty:
                    (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
                    self.assertTrue(all(x > 0 for x in lat))
                else:
                    warnings.warn('No data was generated in test_execute_1(.) positive roll test. Run the test again.')
        
        ############ negative roll ############
        instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":-12.6}, 
                                           "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 }, 
                                           "@id":"bs1", "@type":"Basic Sensor"}
        sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
        # no need to rerun propagator, since propagation does not depend on sensor
        # set output file path
        out_file_access = self.out_dir+'/test_cov_accessY.csv'

        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                # run the coverage calculator
                GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access, method=method)   
                # check the outputs
                access_data = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
                if not access_data.empty:
                    (lat, lon) = grid.get_lat_lon_from_index(access_data['GP index'].tolist())
                    self.assertTrue(all(x < 0 for x in lat))
                else:
                    warnings.warn('No data was generated in test_execute_1(.) negative roll test. Run the test again.')        
    
    #@unittest.skip
    def test_execute_5(self):
        """ Orient the sensor with pitch and test that the times the ground-points are captured lag or lead (depending on direction of pitch)
            as compared to the coverage from a zero pitch sensor. (Rectangular Sensor) 
            Fixed inputs used.
        """ 
        ####### Common attributes for all the simulations #######
        duration = 0.1
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                            "ecc": 0.001, "inc": 45, "raan": 245, 
                            "aop": 0, "ta": 0}
                     }
        spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
        # generate grid object
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 5})
        grid.write_to_file(self.out_dir+'/grid.csv')
        
        # run for both the coverage methods
        for method in method_list:
            with self.subTest(msg='running method = ' + method):

                ######## Simulation 1 #######
                pitch = 0
                instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                                "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 },   
                                                "@id":"bs1", "@type":"Basic Sensor"}

                sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

                state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
                # execute propagator
                #factory = PropagatorFactory()
                #prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": 1})
                #prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)
                self.j2_prop.execute(spacecraft=sat, start_date=None, out_file_cart=state_cart_file, duration=duration)

                # set output file path
                out_file_access = self.out_dir+'/test_cov_access1.csv'
                # run the coverage calculator
                GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(out_file_access=out_file_access, method=method) 
                
                access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                
                ######## Simulation 2 #######
                pitch = 25
                instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                                "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 },  
                                                "@id":"bs1", "@type":"Basic Sensor"}

                sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

                state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
                # no need to rerun propagator, since propagation does not depend on sensor
                # set output file path
                out_file_access = self.out_dir+'/test_cov_access2.csv'
                # run the coverage calculator
                GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(instru_id=None, out_file_access=out_file_access, method=method) 
                
                access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                ######## Simulation 3 #######
                pitch = -25
                instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": 0, "zRotation": 0}, 
                                                "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 },  
                                                "@id":"bs1", "@type":"Basic Sensor"}

                sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})

                state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
                # no need to rerun propagator, since propagation does not depend on sensor
                # set output file path
                out_file_access = self.out_dir+'/test_cov_access3.csv'
                # run the coverage calculator
                GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file).execute(mode_id=None, out_file_access=out_file_access, method=method) 
                
                access_data3 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                ######## compare the results of both the simulations ########   
                # the first gpi in pitch forward pitch case is detected earlier than in the zero pitch case and (both) earlier than the pitch backward case
                self.assertEqual(access_data3["GP index"][0], 1436)
                self.assertEqual(access_data3["time index"][0], 58)

                self.assertEqual(access_data1["GP index"][0], 1436)
                self.assertEqual(access_data1["time index"][0], 96)

                self.assertEqual(access_data2["GP index"][25], 1436)
                if method=='ProjectedPIP':
                    self.assertEqual(access_data2["time index"][25], 129)
                elif method=='DirectSphericalPIP' or method=='RectangularPIP':
                    self.assertEqual(access_data2["time index"][25], 128)
    
    #@unittest.skip
    def test_execute_6(self):
        """ Check that (1) simulation with orienting spacecraft-body (bus) w.r.t NADIR_POINTING frame and sensor aligned to spacecraft-body yields the same results as 
            (2) simulation with orienting sensor w.r.t spacecraft-body and spacecraft-body aligned to NADIR_POINTING frame.
        """ 
        ############ Common attributes for both simulations ############
        duration = 0.1
        
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+750, 
                               "ecc": 0.001, "inc": 25, "raan": 120.56, 
                               "aop": 0, "ta": 349}
                    }
        pitch = 12
        roll = -6
        yaw = 240
        # run for both the coverage methods
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                ############ simulation with orienting spacecraft w.r.t NADIR_POINTING frame and sensor aligned to spacecraft body ############        
                spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation": pitch, "yRotation": roll, "zRotation": yaw}}
                instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": 0, "yRotation": 0, "zRotation": 0}, 
                                                "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 }, "@id":"bs1", "@type":"Basic Sensor"}
                sat = Spacecraft.from_dict({"orbitState":orbit_dict, "spacecraftBus": spacecraftBus_dict, "instrument": instrument_dict})
                state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
                # execute propagator
                self.j2_prop.execute(spacecraft=sat, out_file_cart=state_cart_file, duration=duration)   
                # set output file path
                out_file_access = self.out_dir+'/test_cov_access1.csv'
                # run the coverage calculator
                cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
                cov.execute(instru_id='bs1', out_file_access=out_file_access, method=method)     
                # check the outputs
                access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data        
                
                ############ simulation with orienting sensor w.r.t spacecraft and spacecraft aligned to NADIR_POINTING frame ############        
                spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation": 0, "yRotation": 0, "zRotation": 0}}
                instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation": pitch, "yRotation": roll, "zRotation": yaw}, 
                                                "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 }, "@id":"bs1", "@type":"Basic Sensor"}
                sat = Spacecraft.from_dict({"orbitState":orbit_dict, "spacecraftBus": spacecraftBus_dict, "instrument": instrument_dict})
                state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
                # execute propagator
                self.j2_prop.execute(spacecraft=sat, out_file_cart=state_cart_file, duration=duration)   
                # set output file path
                out_file_access = self.out_dir+'/test_cov_access2.csv'
                # run the coverage calculator
                cov = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
                cov.execute(instru_id='bs1', out_file_access=out_file_access, method=method)     
                # check the outputs
                access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data    

                ############ compare both outputs ############
                if not access_data1.empty:
                    self.assertTrue(access_data1.equals(access_data2))
                else:
                    warnings.warn('No data was generated in test_execute_6(.). Run the test again.')
    
    #@unittest.skip
    def test_execute_7(self):
        """ Test spacecraft with multiple sensors. spc4 spacecraft is on equatorial orbit and has 3 instruments with 
            progressively larger CIRCULAR FOVs. The third instrument has 3 modes with roll =0, 25, -25. 

            * Test the coverage of the smaller FOVs is a subset of the coverage from bigger FOVs.
            * Test mode_id specification works by checking sign of latitudes in coverage data when the instrument with roll is simulated.

        """
        duration = 0.1
        
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        spc4 = Spacecraft.from_json(spc4_json)
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=spc4, out_file_cart=state_cart_file, duration=duration)   
        # set output file path
        out_file_access = self.out_dir+'/test_cov_access.csv'
        # form the coverage calculator object
        cov = GridCoverage(grid=grid, spacecraft=spc4, state_cart_file=state_cart_file)

        # run the different simulations
        cov.execute(instru_id='bs1', out_file_access=out_file_access) 
        access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data   
        
        cov.execute(instru_id='bs2', mode_id=101, out_file_access=out_file_access) 
        access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data    

        cov.execute(instru_id='bs3', mode_id=0, out_file_access=out_file_access) 
        access_data3_1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data  

        cov.execute(instru_id='bs3', mode_id="roll_pos", out_file_access=out_file_access) 
        access_data3_2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data  

        cov.execute(instru_id='bs3', mode_id="roll_neg", out_file_access=out_file_access) 
        access_data3_3 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data  

        # compare attributes of the output data from the different simulations
        if not access_data1.empty:
            self.assertTrue(len(access_data1.index) < len(access_data2.index) < len(access_data3_1.index))
            # this test checks if access_data1 Dataframe is subset of access_data2 dataframe. Note that it will not work if there are duplicated rows in any one of the dataframes.
            self.assertEqual(len(access_data1.merge(access_data2)), len(access_data1)) 
            # this test checks if access_data2 Dataframe is subset of access_data3 dataframe. Note that it will not work if there are duplicated rows in any one of the dataframes.
            self.assertEqual(len(access_data2.merge(access_data3_1)), len(access_data2)) 
        else:
            warnings.warn('No data was generated in test_execute_7(.). Run the test again.')

        if not access_data3_2.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data3_2['GP index'].tolist())
            self.assertTrue(all(x > 0 for x in lat))
        else:
            warnings.warn('No data was generated in test_execute_7(.) positive roll test. Run the test again.')
        
        if not access_data3_3.empty:
            (lat, lon) = grid.get_lat_lon_from_index(access_data3_3['GP index'].tolist())
            self.assertTrue(all(x < 0 for x in lat))
        else:
            warnings.warn('No data was generated in test_execute_7(.) negative roll test. Run the test again.')
    
    #@unittest.skip
    def test_execute_8(self):
        """ Test FOV vs FOR coverage. Coverage of FOR >= Coverage of FOV. Use spc1 spacecraft (defined by util.spc1_json). 
            Test the coverage of the FOV is a subset of the coverage from FOR.
        
        """
        duration = 0.1
        
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        spc1 = Spacecraft.from_json(spc1_json)
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=spc1, out_file_cart=state_cart_file, duration=duration)   
        
        # form the coverage calculator object
        cov = GridCoverage(grid=grid, spacecraft=spc1, state_cart_file=state_cart_file)
        
        # run the coverage calculator: FOV considered
        out_file_access = self.out_dir+'/test_cov_access1.csv'
        cov.execute(instru_id='bs1', use_field_of_regard=False, out_file_access=out_file_access)
        access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

        # run the coverage calculator: FOR considered
        out_file_access = self.out_dir+'/test_cov_access2.csv'               
        cov.execute(instru_id='bs1', use_field_of_regard=True, out_file_access=out_file_access) 
        access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

         # compare attributes of the output data from the different simulations
        if not access_data1.empty:
            self.assertTrue(len(access_data1.index) < len(access_data2.index))
            # this test checks if access_data1 Dataframe is subset of access_data2 dataframe. Note that it will not work if there are duplicated rows in any one of the dataframes.
            self.assertEqual(len(access_data1.merge(access_data2)), len(access_data1)) 
        else:
            warnings.warn('No data was generated in test_execute_8(.). Run the test again.')

    #@unittest.skip
    def test_execute_9(self):
        """ Test coverage with DOUBLE_ROLL_ONLY maneuver which will result in 2 ``ViewGeometry`` objects for the 
            field-of-regard.
            Use Spacecraft spc5. 
            Compare results of 3 simulations (1) SINGLE_ROLL_ONLY manuever (positive) (2) SINGLE_ROLL_ONLY manuever (negative) 
            and (3) DOUBLE_ROLL_ONLY maneuver. The results of (3) should be the union of the results of (1) and (2). Note 
            that the coverage from (1) does not intersect the coverage from (2) due to the way the maneuver is configured in spacecraft spc5.

        """
        duration = 0.1
        
        grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 2})
        
        spc5 = Spacecraft.from_json(spc5_json)
        state_cart_file = self.out_dir+'/test_cov_cart_states.csv'
        # execute propagator
        self.j2_prop.execute(spacecraft=spc5, out_file_cart=state_cart_file, duration=duration)          

        # form the coverage calculator object
        cov = GridCoverage(grid=grid, spacecraft=spc5, state_cart_file=state_cart_file)

        # run for both the coverage methods
        for method in method_list:
            with self.subTest(msg='running method = ' + method):
                # run mode with SINGLE_ROLL_ONLY manuever (positive)
                out_file_access = self.out_dir+'/test_cov_access1.csv'
                cov.execute(instru_id="sen1", mode_id=0, use_field_of_regard=True, out_file_access=out_file_access, method=method)
                access_data1 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                # run mode with SINGLE_ROLL_ONLY manuever (negative)
                out_file_access = self.out_dir+'/test_cov_access2.csv'
                cov.execute(instru_id="sen1", mode_id=1, use_field_of_regard=True, out_file_access=out_file_access, method=method)
                access_data2 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                # run mode with DOUBLE_ROLL_ONLY manuever
                out_file_access = self.out_dir+'/test_cov_access3.csv'
                cov.execute(instru_id="sen1", mode_id=2, use_field_of_regard=True, out_file_access=out_file_access, method=method)
                access_data3 = pd.read_csv(out_file_access, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data

                # compare the results from the different simulations
                # join access_data1, access_data_2
                dfs = [access_data1, access_data2]
                df = pd.concat( dfs,axis=0,ignore_index=True)
                self.assertTrue(access_data3.equals(df))





        
    
    

      



