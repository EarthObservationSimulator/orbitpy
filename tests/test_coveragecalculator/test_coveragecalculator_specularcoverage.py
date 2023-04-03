"""Unit tests for orbitpy.coveragecalculator.specularcoverage class.

``TestSpecularCoverage`` class:

* ``test_from_dict``: Check instantiation of the specular grid coverage calculator object from python dictionary.
* ``test_to_dict``: TODO
* ``test_execute_0``: (SKIP) Check the produced access file format. Case of receiving spacecraft without sensor. No grid specified.
* ``test_execute_1``: Check the produced access files format. Case of receiving spacecraft with sensor. Grid specified.
* ``test_execute_2``: Test with the source and receiving satellites as the same. The specular points would be the ground-locations of the satellites. No grid specified.
* ``test_execute_3``: (TBD, instead of large FOV sensor, try with no sensor) Test with the source and receiving satellites (with large FOV sensor) are at the same altitude, but with 180 deg True Anomaly offset (circular orbit). There should be no specular points since there is no line of sight. No grid specified.
* ``test_execute_4``: Test with the source and receiving satellites are separated by 30 deg True Anomaly on an equatorial circular orbit. The specular point would have 0 deg latitude, and longitude defined by the angular separation between the two satellites. No grid specified.
* ``test_execute_5``: Test with the source and receiving satellites are separated by 30 deg True Anomaly on an 90 deg inclination circular orbit. The specular point would have the same or complementary longitude as that of the satellites, and latitude defined by the angular separation between the two satellites. No grid specified.
* ``test_execute_6``: (SKIP) Test coverage calculations with and without a sensor. A 'general' scenario is simulated for which the results with the sensor are a subset of the results without the sensor.
* ``test_execute_7``: (SKIP) Test coverage calculations with and without a sensor. A scenario where the specular points always fall close to the nadir (within the sensor FOV) is simulated. Hence both results should be equal.
* ``test_execute_8``: Test grid access data by asserting that the distance between the calculated grid points and the specular locations is less than the radius of the specular region.

TODO: Add tests which checks the filters mid-interval access functionality.

"""
import json
import os, shutil
import unittest
import numpy as np
import pandas as pd
import random
import json
import orbitpy
import propcov

from orbitpy.coveragecalculator import SpecularCoverage
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory
from orbitpy.grid import Grid

from instrupy import Instrument
from instrupy.util import GeoUtilityFunctions

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
        cls.step_size = 60
        cls.j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": cls.step_size})

        # define test spacecrafts

        # source (transmitting) spacecrafts for specular coverage tests

        # NAVSTAR 79
        cls.navstar79_json = '{"name": "NAVSTAR-79", \
                            "spacecraftBus":{ "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":5, "minute":14, "second":35.273}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 26560.726, "ecc": 0.00211560, "inc": 55.4987, "raan": 87.6401, "aop": 178.443, "ta": 346.190} \
                                        } , \
                            "@id": "navstar79" \
                        }'
        cls.navstar79_state_fl =   cls.out_dir + "/navstar79_state.csv"
        # NAVSTAR 80
        cls.navstar80_json = '{"name": "NAVSTAR-80", \
                            "spacecraftBus":{ "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":17, "minute":58, "second":15.3}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 26560.217, "ecc": 0.00185450, "inc": 54.5899, "raan": 271.4221, "aop": 184.7310, "ta": 336.981} \
                                        } , \
                            "@id": "navstar80" \
                        }'
        cls.navstar80_state_fl =   cls.out_dir +  "/navstar80_state.csv"
        # NAVSTAR 81
        cls.navstar81_json = '{"name": "NAVSTAR-81", \
                            "spacecraftBus":{ "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":17, "minute":2, "second":22.300}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 26559.327, "ecc": 0.00036260, "inc": 55.1689, "raan": 32.3671, "aop": 199.0483, "ta": 117.475} \
                                        } , \
                            "@id": "navstar81" \
                        }'
        cls.navstar81_state_fl =   cls.out_dir +  "/navstar81_state.csv"
        
        # receiving spacecraft (without sensor) for specular coverage tests
        cls.testsat_json = '{  "name": "testsat", \
                            "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.00151280, "inc": 34.9537, "raan": 47.2225, "aop": 162.3608, "ta": 197.700} \
                                        } , \
                             "instrument": {"@type":"Basic Sensor", "@id":"testsen", \
                                            "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":80 } \
                                            }, \
                            "@id": "testsat" \
                        }'
        cls.testsat_state_fl =    cls.out_dir + "/testsat_state.csv"

        # receiving CYGNSS spacecraft (with sensor) for specular coverage tests
        '''        
        cls.cygfm01_json = '{  "name": "cygfm01", \
                            "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                        }, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                        "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.00151280, "inc": 34.9537, "raan": 47.2225, "aop": 162.3608, "ta": 197.700} \
                                        } , \
                            "@id": "cygfm01" \
                        }'
        cls.cygfm01_state_fl =    cls.out_dir + "/cygfm01_state.csv"
        '''
    
    def test_from_dict(self):
        # one source satellite (not in list), no grid
        o = SpecularCoverage.from_dict({ "receiver": {"spacecraft": json.loads(self.testsat_json), "cartesianStateFilePath": self.testsat_state_fl},
                                         "source": {"spacecraft": json.loads(self.navstar79_json), "cartesianStateFilePath": self.navstar79_state_fl},
                                         "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o._type, 'SPECULAR COVERAGE')
        self.assertEqual(o.rx_spc, Spacecraft.from_json(self.testsat_json))
        self.assertEqual(o.rx_state_file, self.out_dir + "/testsat_state.csv")
        self.assertEqual(o.tx_spc, [Spacecraft.from_json(self.navstar79_json)])
        self.assertEqual(o.tx_state_file, [self.out_dir + "/navstar79_state.csv"])

        # one source satellite (in list), no grid
        o = SpecularCoverage.from_dict({ "receiver": {"spacecraft": json.loads(self.testsat_json), "cartesianStateFilePath": self.testsat_state_fl},
                                         "source": [{"spacecraft": json.loads(self.navstar79_json), "cartesianStateFilePath": self.navstar79_state_fl}],
                                         "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o._type, 'SPECULAR COVERAGE')
        self.assertEqual(o.rx_spc, Spacecraft.from_json(self.testsat_json))
        self.assertEqual(o.rx_state_file, self.out_dir + "/testsat_state.csv")
        self.assertEqual(o.tx_spc, [Spacecraft.from_json(self.navstar79_json)])
        self.assertEqual(o.tx_state_file, [self.out_dir + "/navstar79_state.csv"])

        # several source satellites in list, no grid
        o = SpecularCoverage.from_dict({ "receiver": {"spacecraft": json.loads(self.testsat_json), "cartesianStateFilePath": self.testsat_state_fl},
                                         "source": [{"spacecraft": json.loads(self.navstar79_json), "cartesianStateFilePath": self.navstar79_state_fl},
                                                    {"spacecraft": json.loads(self.navstar80_json), "cartesianStateFilePath": self.navstar80_state_fl},
                                                    {"spacecraft": json.loads(self.navstar81_json), "cartesianStateFilePath": self.navstar81_state_fl}],
                                         "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o._type, 'SPECULAR COVERAGE')
        self.assertEqual(o.rx_spc, Spacecraft.from_json(self.testsat_json))
        self.assertEqual(o.rx_state_file, self.out_dir + "/testsat_state.csv")
        self.assertEqual(o.tx_spc[0], Spacecraft.from_json(self.navstar79_json))
        self.assertEqual(o.tx_state_file[0], self.out_dir + "/navstar79_state.csv")
        self.assertEqual(o.tx_spc[1], Spacecraft.from_json(self.navstar80_json))
        self.assertEqual(o.tx_state_file[1], self.out_dir + "/navstar80_state.csv")
        self.assertEqual(o.tx_spc[2], Spacecraft.from_json(self.navstar81_json))
        self.assertEqual(o.tx_state_file[2], self.out_dir + "/navstar81_state.csv")

        # several source satellites in list, with grid
        o = SpecularCoverage.from_dict({ "receiver": {"spacecraft": json.loads(self.testsat_json), "cartesianStateFilePath": self.testsat_state_fl},
                                         "source": [{"spacecraft": json.loads(self.navstar79_json), "cartesianStateFilePath": self.navstar79_state_fl},
                                                    {"spacecraft": json.loads(self.navstar80_json), "cartesianStateFilePath": self.navstar80_state_fl},
                                                    {"spacecraft": json.loads(self.navstar81_json), "cartesianStateFilePath": self.navstar81_state_fl}],
                                         "grid": {"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 0.25},
                                         "@id": 15})
        self.assertEqual(o._id, 15)
        self.assertEqual(o._type, 'SPECULAR COVERAGE')
        self.assertEqual(o.rx_spc, Spacecraft.from_json(self.testsat_json))
        self.assertEqual(o.rx_state_file, self.out_dir + "/testsat_state.csv")
        self.assertEqual(o.tx_spc[0], Spacecraft.from_json(self.navstar79_json))
        self.assertEqual(o.tx_state_file[0], self.out_dir + "/navstar79_state.csv")
        self.assertEqual(o.tx_spc[1], Spacecraft.from_json(self.navstar80_json))
        self.assertEqual(o.tx_state_file[1], self.out_dir + "/navstar80_state.csv")
        self.assertEqual(o.tx_spc[2], Spacecraft.from_json(self.navstar81_json))
        self.assertEqual(o.tx_state_file[2], self.out_dir + "/navstar81_state.csv")
        self.assertEqual(o.grid, Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2}))
    

    def test_to_dict(self): #TODO
        pass

    '''
    def test_execute_0(self):
        """ Check the produced access file format. Case of receiving spacecraft without sensor. No grid specified.
        The test functions below are commented out, until the coverage calculator is modified to accomodate spacecrafts without sensors.
        """        
        # setup spacecraft with some parameters setup randomly     
        duration=1
        
        navstar79 = Spacecraft.from_json(self.navstar79_json)
        navstar80 = Spacecraft.from_json(self.navstar80_json)
        navstar81 = Spacecraft.from_json(self.navstar81_json)
        testsat = Spacecraft.from_json(self.testsat_json)

        # execute propagator
        start_date = propcov.AbsoluteDate.fromGregorianDate(2022, 5, 15, 21 ,0, 0)
        self.j2_prop.execute(spacecraft=navstar79, start_date=start_date, out_file_cart=self.navstar79_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar80, start_date=start_date, out_file_cart=self.navstar80_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar81, start_date=start_date, out_file_cart=self.navstar81_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=testsat, start_date=start_date, out_file_cart=self.testsat_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        out_file_grid_access = self.out_dir+'/test_grid_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=testsat, rx_state_file=self.testsat_state_fl,
                                    tx_spc=[navstar79, navstar80, navstar81], tx_state_file=[self.navstar79_state_fl, self.navstar80_state_fl, self.navstar81_state_fl])
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular, specular_region_dia=25, out_file_grid_access=out_file_grid_access)

        # check the outputs
        cov_calc_type = pd.read_csv(out_file_specular, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'SPECULAR COVERAGE')

        epoch_JDUT1 = pd.read_csv(out_file_specular, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459715.375)

        _step_size = pd.read_csv(out_file_specular, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_specular, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertEqual(_duration, duration)

        column_headers = pd.read_csv(out_file_specular, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"source id")
        self.assertEqual(column_headers.iloc[0][2],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][3],"lon [deg]")

        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)
    '''
    
    def test_execute_1(self):
        """ Check the produced access files format. Case of receiving spacecraft with sensor. Grid specified.
        """
        # setup spacecraft with some parameters setup randomly     
        duration=0.25
        
        navstar79 = Spacecraft.from_json(self.navstar79_json)
        navstar80 = Spacecraft.from_json(self.navstar80_json)
        navstar81 = Spacecraft.from_json(self.navstar81_json)
        testsat = Spacecraft.from_json(self.testsat_json)

        # execute propagator
        start_date = propcov.AbsoluteDate.fromGregorianDate(2022, 5, 15, 21 ,0, 0)
        self.j2_prop.execute(spacecraft=navstar79, start_date=start_date, out_file_cart=self.navstar79_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar80, start_date=start_date, out_file_cart=self.navstar80_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar81, start_date=start_date, out_file_cart=self.navstar81_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=testsat, start_date=start_date, out_file_cart=self.testsat_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        out_file_grid_access = self.out_dir+'/test_grid_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=testsat, rx_state_file=self.testsat_state_fl,
                                    tx_spc=[navstar79, navstar80, navstar81], tx_state_file=[self.navstar79_state_fl, self.navstar80_state_fl, self.navstar81_state_fl],
                                    grid=Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 0.25}))
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular, specular_region_dia=25, out_file_grid_access=out_file_grid_access) # the 1st instrument and the 1st mode is selected.

        # check the outputs
        # check the specular locations output
        cov_calc_type = pd.read_csv(out_file_specular, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'SPECULAR COVERAGE')

        epoch_JDUT1 = pd.read_csv(out_file_specular, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459715.375)

        _step_size = pd.read_csv(out_file_specular, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_specular, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertEqual(_duration, duration)

        column_headers = pd.read_csv(out_file_specular, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"source id")
        self.assertEqual(column_headers.iloc[0][2],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][3],"lon [deg]")

        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)

        # check the grid access output
        cov_calc_type = pd.read_csv(out_file_grid_access, nrows=1, header=None).astype(str) # 1st row contains the coverage calculation type
        cov_calc_type = str(cov_calc_type[0][0])
        self.assertEqual(cov_calc_type, 'SPECULAR COVERAGE GRID ACCESS')

        epoch_JDUT1 = pd.read_csv(out_file_grid_access, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2459715.375)

        _step_size = pd.read_csv(out_file_grid_access, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertEqual(_step_size, self.step_size)

        _duration = pd.read_csv(out_file_grid_access, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertEqual(_duration, duration)

        column_headers = pd.read_csv(out_file_grid_access, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"source id")
        self.assertEqual(column_headers.iloc[0][2],"GP index")
        self.assertEqual(column_headers.iloc[0][3],"lat [deg]")
        self.assertEqual(column_headers.iloc[0][4],"lon [deg]")

        cov_results_df = pd.read_csv(out_file_grid_access, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)

    def test_execute_2(self):
        """ Test with the source and receiving satellites as the same. The specular points would be the ground-locations of the satellites.
            The test scenario satsifies a special condition where the cross product of the position vectors of the source and receiving satellites is the null vector.
            Grid is not specified.
        """
        duration = 0.25 + random.random()
        testsat = Spacecraft.from_json(self.testsat_json)

        # execute propagator
        self.j2_prop.execute(spacecraft=testsat, out_file_cart=self.testsat_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=testsat, rx_state_file=self.testsat_state_fl, tx_spc=testsat, tx_state_file=self.testsat_state_fl)
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular)

        # check the outputs
        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)

        (epoch_JDUT1, step_size, _) = orbitpy.util.extract_auxillary_info_from_state_file(self.testsat_state_fl)
        sat_pos_df = pd.read_csv(self.testsat_state_fl, skiprows = [0,1,2,3])

        for index, row in sat_pos_df.iterrows():
            time_index = int(row['time index'])
            jd_date = epoch_JDUT1 + time_index*step_size*(1.0/86400)
            
            pos_cart = [row['x [km]'], row['y [km]'], row['z [km]']]

            pos_geo = GeoUtilityFunctions.eci2geo(pos_cart, jd_date)
            pos_lat = np.round(pos_geo[0],3)
            pos_lon = np.round(pos_geo[1],3)

            specular_lat = cov_results_df.iloc[index]['lat [deg]']
            specular_lon = cov_results_df.iloc[index]['lon [deg]']

            self.assertEqual(pos_lat, specular_lat)
            self.assertEqual(pos_lon, specular_lon)

    def test_execute_3(self):
        """ Test with the source and receiving satellites (with large FOV sensor) are at the same altitude, but with 180 deg True Anomaly offset (circular orbit).
            There should be no specular points since there is no line of sight. Grid is not specified.

            .. todo:: Instead of large FOV sensor, try with no sensor.

        """
        duration = 0.25 + random.random()

        satX_json = '{ "name": "satX", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.00151280, "inc": 34.9537, "raan": 47.2225, "aop": 162.3608, "ta": 377.7} \
                                   }, \
                       "instrument": { "@type":"Basic Sensor", "@id":"senX", \
                                       "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                       "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":179 }}, \
                       "@id": "satX" \
                    }'
        satX = Spacecraft.from_json(satX_json)
        satX_state_fl = self.out_dir +  "/satX_state.csv"

        satY_json = '{ "name": "satY", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.00151280, "inc": 34.9537, "raan": 47.2225, "aop": 162.3608, "ta": 197.700} \
                                   }, \
                       "@id": "satY" \
                    }'
        satY = Spacecraft.from_json(satY_json)
        satY_state_fl = self.out_dir +  "/satY_state.csv"

        # execute propagator        
        self.j2_prop.execute(spacecraft=satX, out_file_cart=satX_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=satY, out_file_cart=satY_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=satX, rx_state_file=satX_state_fl, tx_spc=satY, tx_state_file=satY_state_fl) # rx_spc (satX) has a large FOV sensor.
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular)

        # check the outputs
        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])

        self.assertTrue(cov_results_df.empty)

    def test_execute_4(self):
        """ Test with the source and receiving satellites are separated by 30 deg True Anomaly on an equatorial circular orbit. 
            Receiving satellite has rectangular FOV geometry sensor.
            The specular point always falls on the 0 deg latitude.
            The longitude of the specular point shall be the longitude of the 'behind' satellite plus half of the angle between the two satellites (about the center of Earth).
            Further note that the angular difference between the two satellites is equal to the difference in the longitudes of the two satellites.
            
            Grid is not specified.
        """
        duration = 0.25 + random.random()

        satA_json = '{ "name": "satA", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.0, "inc": 0, "raan": 47.2225, "aop": 162.3608, "ta": 20.25} \
                                   }, \
                       "instrument": {"@type":"Basic Sensor", "@id":"senA", \
                                      "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                      "fieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":125, "angleWidth": 45 }}, \
                       "@id": "satA" \
                    }'
        satA = Spacecraft.from_json(satA_json)
        satA_state_fl = self.out_dir +  "/satA_state.csv"

        satB_json = '{ "name": "satB", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.0, "inc": 0, "raan": 47.2225, "aop": 162.3608, "ta": 50.25} \
                                   }, \
                       "@id": "satB" \
                    }'
        satB = Spacecraft.from_json(satB_json)
        satB_state_fl = self.out_dir +  "/satB_state.csv"

        satA = Spacecraft.from_json(satA_json)
        satB = Spacecraft.from_json(satB_json)

        # execute propagator
        self.j2_prop.execute(spacecraft=satA, out_file_cart=satA_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=satB, out_file_cart=satB_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=satA, rx_state_file=satA_state_fl, tx_spc=satB, tx_state_file=satB_state_fl)
        spec_cov.execute(instru_id='senA', mode_id=None, out_file_specular=out_file_specular)

        # check the outputs
        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)
        satA_pos_df = pd.read_csv(satA_state_fl, skiprows = [0,1,2,3])
        satB_pos_df = pd.read_csv(satB_state_fl, skiprows = [0,1,2,3])

        (epoch_JDUT1, step_size, _) = orbitpy.util.extract_auxillary_info_from_state_file(out_file_specular)

        for index, row in cov_results_df.iterrows():
            time_index = int(row['time index'])
            jd_date = epoch_JDUT1 + time_index*step_size*(1.0/86400)
            
            specular_lat = row['lat [deg]']
            specular_lon = row['lon [deg]']

            stateA = satA_pos_df.iloc[index]
            posA_cart = [stateA['x [km]'], stateA['y [km]'], stateA['z [km]']]
            posA_geo = GeoUtilityFunctions.eci2geo(posA_cart, jd_date)

            stateB = satB_pos_df.iloc[index]
            posB_cart = np.array([stateB['x [km]'], stateB['y [km]'], stateB['z [km]']])

            angle = np.arccos(np.dot(posA_cart, posB_cart)/(np.linalg.norm(posA_cart)*np.linalg.norm(posB_cart)))
            analyt_spec_longitude = posA_geo[1] + np.rad2deg(0.5*angle)
            if analyt_spec_longitude>=360.0:
                analyt_spec_longitude = analyt_spec_longitude - 360
            analyt_spec_longitude = np.round(analyt_spec_longitude, 3)

            self.assertAlmostEqual(specular_lat, 0)
            self.assertEqual(specular_lon, analyt_spec_longitude)
    
    def test_execute_5(self):
        """ Test with the source and receiving satellites are separated by 30 deg True Anomaly on an 90 deg inclination circular orbit.
            The specular point always falls on the same longitude as that of the two satellite, except when the satellites are over the polar region
            in which case the longitude of one of the satellites shall be complimentary to the longitude of the specular point.

            Since the satellites are on a 90 deg inclination orbit:

                * The latitude of the specular point shall be the latitude of the trailing satellite plus half of the angle between the two satellites (about the center of Earth).
                * Equivalently the latitude of the specular point is mid-way between the latitudes of the two satellites.
                * Further the latitude difference between the two satellites is equal to the angle difference between the two satellites which is equal to the true anomaly seperation.
            
            However it is tricky to bring the analytically calculated latitude of the specular point in the range of -90deg to +90deg. 
            (Problems at the poles when the angle 'wraps' around +/-90deg, require to consider ascending, descending directions of the satellite motion).

            Grid is not specified.

        """
        duration = 0.25 + random.random()

        satA_json = '{ "name": "satA", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.0, "inc": 90, "raan": 47.2225, "aop": 10.5, "ta": 20.25} \
                                   }, \
                       "instrument": {"@type":"Basic Sensor", "@id":"senA", \
                                      "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                      "fieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":135, "angleWidth": 45 }}, \
                       "@id": "satA" \
                    }'
        satA = Spacecraft.from_json(satA_json)
        satA_state_fl = self.out_dir +  "/satA_state.csv"

        satB_json = '{ "name": "satB", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.0, "inc": 90, "raan": 47.2225, "aop": 10.5, "ta": 50.25} \
                                   }, \
                       "@id": "satB" \
                    }'
        satB = Spacecraft.from_json(satB_json)
        satB_state_fl = self.out_dir +  "/satB_state.csv"

        satA = Spacecraft.from_json(satA_json)
        satB = Spacecraft.from_json(satB_json)
        ta_diff = 30 # True Anomaly difference in degrees. Is equal to the latitude difference b/w the two satellites since both orbits are at 90deg inclination.

        # execute propagator
        self.j2_prop.execute(spacecraft=satA, out_file_cart=satA_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=satB, out_file_cart=satB_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=satA, rx_state_file=satA_state_fl, tx_spc=satB, tx_state_file=satB_state_fl)
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular)

        # check the outputs
        cov_results_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])
        self.assertTrue(not cov_results_df.empty)
        satA_pos_df = pd.read_csv(satA_state_fl, skiprows = [0,1,2,3])

        (epoch_JDUT1, step_size, _) = orbitpy.util.extract_auxillary_info_from_state_file(out_file_specular)
        for index, row in cov_results_df.iterrows():

            time_index = int(row['time index'])
            jd_date = epoch_JDUT1 + time_index*step_size*(1.0/86400)
            
            specular_lat = row['lat [deg]']
            specular_lon = row['lon [deg]']

            stateA = satA_pos_df.iloc[index]
            posA_cart = [stateA['x [km]'], stateA['y [km]'], stateA['z [km]']]
            velA_cart = [stateA['vx [km/s]'], stateA['vy [km/s]'], stateA['vz [km/s]']] # required to determine ascending/ descending satellite passes
            posA_geo = GeoUtilityFunctions.eci2geo(posA_cart, jd_date)
            satA_lat = posA_geo[0]
            satA_lon = posA_geo[1]

            over_pole = False
            if velA_cart[2] > 0: # ascending phase of satellite A
                if satA_lat>=0: # satellite in the Northern hemisphere, ascending
                    analyt_spec_latitude = satA_lat + 0.5*ta_diff
                    if analyt_spec_latitude > 90:
                        analyt_spec_latitude = 180 - analyt_spec_latitude
                        over_pole = True
                elif satA_lat<0: # satellite in the Southern hemisphere, ascending
                    analyt_spec_latitude = satA_lat + 0.5*ta_diff
                    
            if velA_cart[2] < 0: # descending phase of satellte A
                if satA_lat>=0: # satellite in the Northern hemisphere, descending
                    analyt_spec_latitude = satA_lat - 0.5*ta_diff
                elif satA_lat<0: # satellite in the Southern hemisphere, descending
                    analyt_spec_latitude = satA_lat - 0.5*ta_diff
                    if analyt_spec_latitude < -90:
                        over_pole = True
                        analyt_spec_latitude = -180 - analyt_spec_latitude

            analyt_spec_latitude = np.round(analyt_spec_latitude, 3)
            self.assertEqual(specular_lat, analyt_spec_latitude)

            # satA (and satB) and the specular point lie on the same or complimentary longitude line.
            if over_pole is False:
                self.assertAlmostEqual(satA_lon, specular_lon, places=3) # accuracy to 3 places due to round-off in the results of the specular coverage
            else:
                if satA_lon <=180: # the specular point longitude shall be complimentary
                    self.assertAlmostEqual(satA_lon + 180, specular_lon, places=3) 
                else:
                    self.assertAlmostEqual(satA_lon - 180, specular_lon, places=3)

    '''
    TBD: The test functions below are commented out, until the coverage calculator is modified to accomodate spacecrafts without sensors.
    def test_execute_6(self):
        """ Test coverage calculations with and without a sensor.
            The number of specular locations from the case of coverage calculations with the instrument must be smaller 
            and should be a subset of the case with no instrument.
        """
        duration = 2
        navstar79 = Spacecraft.from_json(self.navstar79_json) # transmitting satellite
        testsat = Spacecraft.from_json(self.testsat_json) # receiving satellite with no instrument attached to it.
        satX = Spacecraft.from_json(self.testsat_json) # receiving satellite, with instrument.
        instru = Instrument.from_dict({"@type": "Reflectometer",
                        "orientation": {
                           "referenceFrame": "SC_BODY_FIXED",
                            "convention": "REF_FRAME_ALIGNED"
                        },
                        "antenna":{"shape": "CIRCULAR", "diameter": 9e-2, "apertureExcitationProfile": "UNIFORM"},
                        "operatingFrequency": 1575.42e6,
                        "@id": "rtr"
                        })
        satX.add_instrument(instru)
        satX_state_fl = self.out_dir +  "/satX_state.csv"
        antenna_cone_angle = 60.5723 # [deg] antenna cone angle for the above defined antenna 

        # execute propagator
        self.j2_prop.execute(spacecraft=navstar79, out_file_cart=self.navstar79_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=testsat, out_file_cart=self.testsat_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=satX, out_file_cart=satX_state_fl, duration=duration)

        # set output file path
        out_file_specular1 = self.out_dir+'/test_specular_access1.csv'
        out_file_specular2 = self.out_dir+'/test_specular_access2.csv'
        # run the coverage calculator
        spec_cov1 = SpecularCoverage(rx_spc=testsat, rx_state_file=self.testsat_state_fl, tx_spc=navstar79, tx_state_file=self.navstar79_state_fl)
        spec_cov1.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular1)

        spec_cov2 = SpecularCoverage(rx_spc=satX, rx_state_file=satX_state_fl, tx_spc=navstar79, tx_state_file=self.navstar79_state_fl)
        spec_cov2.execute(instru_id="rtr", mode_id=None, out_file_specular=out_file_specular2)

        # check the outputs
        df1 = pd.read_csv(out_file_specular1, skiprows = [0,1,2,3]).set_index('time index')
        df2 = pd.read_csv(out_file_specular2, skiprows = [0,1,2,3]).set_index('time index')

        self.assertTrue(df2.isin(df1).all().all())

        # extract the dataframe entries of the coverage involving satellite with no sensor which are *not* in the dataframe from the coverage involving satellite with the sensor
        extract_idx = list(set(df1.index) - set(df2.index))
        df_extract = df1.loc[extract_idx]

        (epoch_JDUT1, step_size, _) = orbitpy.util.extract_auxillary_info_from_state_file(self.testsat_state_fl)
        df_rx_state = pd.read_csv(self.testsat_state_fl, skiprows = [0,1,2,3]).set_index('time index')

        # iterate over the entries and assert that the specular points are outside the sensor FOV
        for index, row in df_extract.iterrows():

            # get the specular location date in Julian Date UT1
            jd_date = epoch_JDUT1 + index * (step_size/86400.0)
            specular_lat = row['lat [deg]']
            specular_lon = row['lon [deg]']
            specular_pos = GeoUtilityFunctions.geo2eci([specular_lat, specular_lon, 0.0], jd_date)
            specular_pos = np.array(specular_pos)

            # get the position of the receiving satellite at the same time
            rx_state = df_rx_state.iloc[index]
            rx_pos = [rx_state['x [km]'], rx_state['y [km]'], rx_state['z [km]']]
            rx_pos = np.array(rx_pos)

            # calculate the cone angle between the nadir direction and the specular direction
            specular_dir = -1* (rx_pos + specular_pos)
            cone_angle = np.dot(specular_dir, -rx_pos)/(np.linalg.norm(specular_dir)*np.linalg.norm(-rx_pos))
            cone_angle = np.rad2deg(cone_angle)

            self.assertGreater(cone_angle, antenna_cone_angle)

    def test_execute_7(self):
        """ Test coverage calculations with and without a sensor for a orbital scenario where the specular points shall be very near to the nadir position.
            The results of both the cases should be identical, since the sensor FOV shall cover all the specular points (since they fall on the Nadir position).
            
            To ensure that the specular point falls near to the Nadir position, the source and receiving satellites are placed on similar orbits which differ only by 2 deg in the true anomaly.
            
        """
        duration = 1

        ######### Simulate the case with *no* sensor attached to the rx-satellite #########
        satA_json = '{ "name": "satA", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 35.45, "raan": 47.2225, "aop": 10.5, "ta": 20.25} \
                                   }, \
                       "@id": "satA" \
                    }'
        satA = Spacecraft.from_json(satA_json)
        satA_state_fl = self.out_dir +  "/satA_state.csv"

        satB_json = '{ "name": "satB", \
                       "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                   }, \
                       "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2022, "month":5, "day":15, "hour":20, "minute":19, "second":26.748768}, \
                                   "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 35.45, "raan": 47.2225, "aop": 10.5, "ta": 22.25} \
                                   }, \
                       "@id": "satB" \
                    }'
        satB = Spacecraft.from_json(satB_json)
        satB_state_fl = self.out_dir +  "/satB_state.csv"

        satA = Spacecraft.from_json(satA_json)
        satB = Spacecraft.from_json(satB_json)

        # execute propagator
        self.j2_prop.execute(spacecraft=satA, out_file_cart=satA_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=satB, out_file_cart=satB_state_fl, duration=duration)

        # set output file path
        out_file_specular1 = self.out_dir+'/test_specular_access1.csv'
        # run the coverage calculator
        spec_cov1 = SpecularCoverage(rx_spc=satA, rx_state_file=satA_state_fl, tx_spc=satB, tx_state_file=satB_state_fl)
        spec_cov1.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular1)

        # check the outputs
        cov_results_df1 = pd.read_csv(out_file_specular1, skiprows = [0,1,2,3])


        ######### Simulate the case with sensor attached to the rx-satellite #########
        instru = Instrument.from_dict({"@type": "Reflectometer",
                        "orientation": {
                           "referenceFrame": "SC_BODY_FIXED",
                            "convention": "REF_FRAME_ALIGNED"
                        },
                        "antenna":{"shape": "CIRCULAR", "diameter": 9e-2, "apertureExcitationProfile": "UNIFORM"},
                        "operatingFrequency": 1575.42e6,
                        "@id": "rtr"
                        })
        satA.add_instrument(instru)

        out_file_specular2 = self.out_dir+'/test_specular_access2.csv'
        # run the coverage calculator
        spec_cov2 = SpecularCoverage(rx_spc=satA, rx_state_file=satA_state_fl, tx_spc=satB, tx_state_file=satB_state_fl)
        spec_cov2.execute(instru_id="rtr", mode_id=None, out_file_specular=out_file_specular2)

        # check the outputs
        cov_results_df2 = pd.read_csv(out_file_specular2, skiprows = [0,1,2,3])

        # both the results must be the equal
        self.assertTrue(cov_results_df2.equals(cov_results_df1))
    '''
    
    def test_execute_8(self):
        """ Test the grid access. The indicated (accessed) grid points should fall within the circular footprint around the specular point.
            3 source (transmitter) satellites are present, of which the test is done only for the one of the source satellites.

            Also the test is done using two aproaches for calculation of the distance between the specular-point and the grid-point:
            (i) Using the great circle distance formula.
            (ii) Converting to ECI Cartesian vectors and then evaluating the angle beween the two vectors.

            The results are validated within tolerence of 0.01 km.

        """
        duration = 0.25
        navstar79 = Spacecraft.from_json(self.navstar79_json)
        navstar80 = Spacecraft.from_json(self.navstar80_json)
        navstar81 = Spacecraft.from_json(self.navstar81_json)
        testsat = Spacecraft.from_json(self.testsat_json)

        # execute propagator
        start_date = propcov.AbsoluteDate.fromGregorianDate(2022, 5, 15, 21 ,0, 0)
        self.j2_prop.execute(spacecraft=navstar79, start_date=start_date, out_file_cart=self.navstar79_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar80, start_date=start_date, out_file_cart=self.navstar80_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=navstar81, start_date=start_date, out_file_cart=self.navstar81_state_fl, duration=duration)
        self.j2_prop.execute(spacecraft=testsat, start_date=start_date, out_file_cart=self.testsat_state_fl, duration=duration)

        # set output file path
        out_file_specular = self.out_dir+'/test_specular_access.csv'
        out_file_grid_access = self.out_dir+'/test_grid_access.csv'
        # run the coverage calculator
        spec_cov = SpecularCoverage(rx_spc=testsat, rx_state_file=self.testsat_state_fl,
                                    tx_spc=[navstar79, navstar80, navstar81], tx_state_file=[self.navstar79_state_fl, self.navstar80_state_fl, self.navstar81_state_fl],
                                    grid=Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":-20, "lonUpper":180, "lonLower":-180, "gridRes": 0.125}))
        spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular, specular_region_dia=50, out_file_grid_access=out_file_grid_access) # the 1st instrument and the 1st mode is selected.

        specular_df = pd.read_csv(out_file_specular, skiprows = [0,1,2,3])       
        specular_df = specular_df[specular_df['source id'] == 'navstar81']
        specular_df.set_index('time index', inplace=True)

        grid_acc_df = pd.read_csv(out_file_grid_access, skiprows = [0,1,2,3])
        grid_acc_df = grid_acc_df[grid_acc_df['source id'] == 'navstar81']
        grid_acc_df.set_index('time index', inplace=True)

        #### test using the great-circle formula ####
        eps = 0.01 # tolerence in [km]
        # iterate over each time-index
        for time_index, new_df in grid_acc_df.groupby(level=0):
            # get the specular point location
            specular_geocoords = specular_df.loc[[time_index]]
            phi_1 = np.deg2rad(specular_geocoords['lat [deg]'].values[0])
            lambda_1 = np.deg2rad(specular_geocoords['lon [deg]'].values[0])

            # iterate over the grid-points
            for index, row in new_df.iterrows():

                # get the grid point location
                phi_2 = np.deg2rad(row['lat [deg]'])
                lambda_2 = np.deg2rad(row['lon [deg]'])

                # calculate the great-circle distance between the specular point and the grid-point
                # https://en.wikipedia.org/wiki/Great-circle_distance
                delta_sigma = np.arccos(np.sin(phi_1)*np.sin(phi_2) + np.cos(phi_1)*np.cos(phi_2)*np.cos(lambda_2 - lambda_1))
                dis = 6378.137 * delta_sigma # radius of Earth times the central-angle
                # assert dis is less than 50km/2 (the specular regaion radius)
                self.assertLessEqual(dis, 50/2 + eps)

        #### test using the Cartesian vector approach ####
        epoch_JDUT1 = pd.read_csv(out_file_specular, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])

        step_size = pd.read_csv(out_file_specular, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])

        # iterate over each time-index
        for time_index, new_df in grid_acc_df.groupby(level=0):

            # get the time in Julian date UT1
            jd_date = epoch_JDUT1 + time_index*step_size*(1.0/86400)

            # get the specular point location
            specular_geocoords = specular_df.loc[[time_index]]
            specular_cart = GeoUtilityFunctions.geo2eci([specular_geocoords['lat [deg]'].values[0], specular_geocoords['lon [deg]'].values[0], 0], jd_date) # ECI Cartesian coordinates
            specular_cart = np.array(specular_cart)

            # iterate over the grid-points
            for index, row in new_df.iterrows():

                # get the grid point location
                gp_cart = GeoUtilityFunctions.geo2eci([row['lat [deg]'], row['lon [deg]'], 0], jd_date) # ECI Cartesian coordinates
                gp_cart = np.array(gp_cart)

                # calculate the angle between the specular-point and the grid-point           
                x = np.dot(specular_cart, gp_cart)/ (np.linalg.norm(specular_cart)*np.linalg.norm(gp_cart))
                x = np.arccos(x)

                dis = 6378.137 * x # radius of Earth times the central-angle
                # assert dis is less than 50km/2 (the specular regaion radius)
                self.assertLessEqual(dis, 50/2 + eps)
                