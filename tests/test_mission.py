"""Unit tests for orbitpy.mission module.

The following tests are framed to test the different possible ways in which the mission can be framed in the JSON string and called to execute.

TODO: In each test, the output is tested with the results as computed on July 2021 (thus representing the "truth" data). The truth data is to be present in the folder ``test_data``.

**Tests:**

* ``test_scenario_1``: 1 satellite, no instrument ; propagation only, auto/ custom-time-step. The mission epoch is same, different from the satellite orbit-state date.
* ``test_scenario_2``: 1 satellite, 1 instrument ; propagation (custom time-step), grid-coverage (2 (auto) grids, default and custom-grid res), data-metrics calculation.
* ``test_scenario_3``: 1 satellite, 1 instrument ; propagation, pointing-options coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_scenario_4``: 1 satellite, 1 instrument ; propagation, pointing-options with grid-coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_scenario_5``: 1 satellite, multiple ground-stations ; propagation, contact-finder (ground-station only).
* ``test_scenario_6``: Multiple satellites from constellation; propagation, contact-finder (ground-station, inter-satellite).
* ``test_scenario_7``: Multiple satellites from constellation, single-instrument per satellite ; propagation, pointing-options-coverage, data-metrics calculation, contact-finder (inter-satellite only).
* TODO ``test_scenario_8``: Multiple satellites from list, multiple instruments per satellite, multiple ground-stations ; propagation, grid-coverage, data-metrics calculation, contact-finder (ground-station and inter-satellite).

"""
import os, shutil
import unittest
import pandas as pd

import orbitpy
from orbitpy.mission import Mission
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.util import Spacecraft, GroundStation

class TestSettings(unittest.TestCase): #TODO
    pass

class TestMission(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)
        
    def test_scenario_1(self):
        """  1 satellite, no instrument ; propagation only, auto, custom-time-step. The mission epoch is same, different from the satellite orbit-state date.
        """
        # auto propagation step-size, mission-date different from spacecraft orbitstate date
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "settings": {"outDir": "temp/", "opaqueAtmosHeight":30} \
                            }'
        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459299.1292592594)
        self.assertAlmostEqual(mission.duration, 0.1)
        self.assertEqual(len(mission.spacecraft), 1)
        self.assertAlmostEqual(mission.spacecraft[0], Spacecraft.from_dict({ "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}, 
                                                                          "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0},
                                                                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}} 
                                                                        }))
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 173.31598026839598})) # corresponds to time-step calculated considering horizon angle = 136.0373... deg and time-resolution factor = 0.25
        self.assertIsNone(mission.grid)
        self.assertIsNone(mission.groundStation)
        self.assertAlmostEqual(mission.propagator.stepSize, 173.31598026839598) 
        self.assertEqual(mission.settings.outDir,  "temp/")
        self.assertIsNone(mission.settings.coverageType)
        self.assertEqual(mission.settings.propTimeResFactor, 0.25)
        self.assertEqual(mission.settings.gridResFactor, 0.9)
        self.assertEqual(mission.settings.opaqueAtmosHeight, 30)

        out_info = mission.execute()

        # custom propagation step-size, mission-date same as spacecraft orbitstate date, custom propTimeResFactor = 1/8
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "settings": {"outDir": "temp/", "propTimeResFactor": 0.125} \
                            }'
        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459270.75)
        self.assertAlmostEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 86.657990134197990})) # corresponds to time-step calculated considering horizon angle = 136.0373... deg and time-resolution factor = 1/8
        self.assertEqual(mission.settings.propTimeResFactor, 1/8)

        out_info = mission.execute()
    
    def test_scenario_2(self):
        """  1 satellite, 1 instrument ; propagation (custom time-step), (field-of-regard) grid-coverage (2 (auto) grids, default and custom-grid res), basic-sensor data-metrics calculation.
        """
        # check warnings are issued.
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                   "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                            } \
                                    }, \
                                "propagator": {"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 200}, \
                                "settings": {"outDir": "temp/", "coverageType": "GRID COVERAGE"} \
                            }'
        with self.assertWarns(Warning): # check for warning that user specified step-size is greater than auto-calculated step-size.
            mission = Mission.from_json(mission_json_str)

        mission = Mission.from_json(mission_json_str)
        with self.assertWarns(Warning): # check for warning that grid has not been specified.
            out_info = mission.execute()

        # check execution with single grid.
        mission_json_str = '{   "epoch":{"@type":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                "duration": 0.5, \
                                "spacecraft": [{ \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 30, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                   "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                            } \
                                    }], \
                                "propagator": {"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 60}, \
                                "grid": [{"@type": "autogrid", "@id": "cus", "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180}, {"@type": "autogrid", "@id": "auto", "latUpper":20, "latLower":0, "lonUpper":180, "lonLower":-180, "gridRes": 1}], \
                                "settings": {"outDir": "temp/", "coverageType": "GRID COVERAGE", "gridResFactor": 0.5} \
                            }'

        mission = Mission.from_json(mission_json_str)
 
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 60}))


        self.assertEqual(len(mission.grid), 2)
        # 0.5917400590151374 is the grid-resolution calculated for the 15 deg FOV sensor at altitude of 500km and gridResFactor = 0.5
        self.assertEqual(mission.grid[0].num_points, 1820) # ~ 4*pi/ (0.5917400590151374*pi/180 * 0.5917400590151374*pi/180) *  ((2*pi)*(2*pi/180))/(4*pi)
        # 1 deg grid resolution is input in the specifications
        self.assertEqual(mission.grid[1].num_points, 7402) # ~ 4*pi/ (pi/180 * pi/180) * ((2*pi)*(20*pi/180)/(4*pi)) 

        out_info = mission.execute()
    
    def test_scenario_3(self):
        """  1 satellite, 1 instrument ; propagation, pointing-options coverage, basic-sensor data-metrics calculation.
        """
        mission_json_str = '{   "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":12, "hour":23, "minute":12, "second":12}, \
                                "duration": 0.05, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": [{ "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight":15, "angleWidth":10 }, \
                                                   "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":0}, \
                                                                      {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":-15}, \
                                                                      {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":15}], \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                                  }] \
                                    }, \
                                "settings": {"outDir": "temp/", "coverageType": "POINTING OPTIONS COVERAGE"} \
                            }'

        mission = Mission.from_json(mission_json_str)

 
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459286.4668055554)
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 6.820899943040534}))

        out_info = mission.execute()
    
    def test_scenario_4(self):
        """ 1 satellite, 1 SAR instrument ; propagation, pointing-options with grid-coverage and access-file correction (since sidelooking instrument with narrow At-fov), SAR data-metrics calculation.
            Using default propagation step-size and grid-resolution. The scene FOV has angleWidth = instrument FOV angleWidth. The scene FOV angleHeight is larger to allow for coarser propagation step-size and gird-resolution.

        """
        mission_json_str = '{   "epoch":{"@type":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "@type": "Synthetic Aperture Radar", "@id": "sar1", \
                                                    "orientation": { "convention": "SIDE_LOOK", "sideLookAngle": 20.5 }, \
                                                    "antenna":{"shape": "RECTANGULAR", "height": 10.7, "width": 2.16, "apertureEfficiency": 0.6, "apertureExcitation": "UNIFORM"}, \
                                                    "sceneFieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":6.233630110575892}, \
                                                    "pulseWidth": 33.4e-6, \
                                                    "operatingFrequency": 1.2757e9, "peakTransmitPower": 1000, "chirpBandwidth": 19e6, \
                                                    "minimumPRF": 1463, "maximumPRF": 1686, "radarLoss": 3.5, "systemNoiseFigure": 5.11, \
                                                    "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":-20.5}, \
                                                                    {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":20.5}] \
                                                    } \
                                    }, \
                                "grid": [{"@type": "autogrid", "@id": 1, "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180}, {"@type": "autogrid", "@id": 2, "latUpper":22, "latLower":20, "lonUpper":180, "lonLower":-180}], \
                                "settings": {"outDir": "temp/", "coverageType": "POINTING OPTIONS WITH GRID COVERAGE"} \
                            }'

        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2458254.0084722224)
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 2.2600808214710266}))
        self.assertEqual(mission.grid[0].num_points, 2906)
        self.assertEqual(mission.grid[1].num_points, 2710)

        out_info = mission.execute()

    def test_scenario_5(self):
        """    1 satellite, multiple ground-stations ; propagation, contact-finder (ground-station only).
        """
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                                "duration": 0.5, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "groundStation":[{"name": "TrollSAR", "latitude": -72.0029, "longitude": 2.5257, "altitude":0}, \
                                                 {"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}], \
                                "settings": {"outDir": "temp/"} \
                            }'
        
        mission = Mission.from_json(mission_json_str)
        self.assertEqual(len(mission.groundStation), 2)
        self.assertIsInstance(mission.groundStation[0], GroundStation)
        self.assertEqual(mission.groundStation[0], GroundStation.from_dict({"name": "TrollSAR", "latitude": -72.0029, "longitude": 2.5257, "altitude":0}))
        self.assertIsInstance(mission.groundStation[1], GroundStation)
        self.assertEqual(mission.groundStation[1], GroundStation.from_dict({"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}))

        out_info = mission.execute()
    
    def test_scenario_6(self):
        """    Multiple satellites from constellation, common instrument; propagation, contact-finder (ground-station, inter-satellite only).
        """
        mission_json_str = '{  "epoch":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75}, \
                                "duration": 0.25, \
                                "constellation": { "@type": "Walker Delta Constellation", \
                                        "date":{"@type": "JULIAN_DATE_UT1", "jd":2459270.75}, \
                                        "numberSatellites": 8, \
                                        "numberPlanes": 1, \
                                        "relativeSpacing": 1, \
                                        "alt": 700, \
                                        "ecc": 0.001, \
                                        "inc": 45, \
                                        "aop": 135, \
                                        "@id": "abc" \
                                    }, \
                                "groundStation":{"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}, \
                                "settings": {"outDir": "temp/"} \
                            }'
        mission = Mission.from_json(mission_json_str)
        self.assertEqual(len(mission.spacecraft), 8)   
        # check the assigned spacecraft's ids.
        self.assertEqual(mission.spacecraft[0]._id, "spc_abc_11")   
        self.assertEqual(mission.spacecraft[1]._id, "spc_abc_12") 
        self.assertEqual(mission.spacecraft[2]._id, "spc_abc_13") 
        self.assertEqual(mission.spacecraft[3]._id, "spc_abc_14") 
        self.assertEqual(mission.spacecraft[4]._id, "spc_abc_15") 
        self.assertEqual(mission.spacecraft[5]._id, "spc_abc_16") 
        self.assertEqual(mission.spacecraft[6]._id, "spc_abc_17") 
        self.assertEqual(mission.spacecraft[7]._id, "spc_abc_18")   

        out_info = mission.execute()

        # test the satellites initial Keplerian states to confirm that the constellation is generated correctly.
        state_sat0_fl = self.out_dir + '/sat0/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat0_fl)
        state_sat0_row0 = pd.read_csv(state_sat0_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat0_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat0_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat0_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat0_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat0_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat0_row0['ta [deg]'][0]%360, 0.0)

        state_sat1_fl = self.out_dir + '/sat1/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat1_fl)
        state_sat1_row0 = pd.read_csv(state_sat1_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat1_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat1_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat1_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat1_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat1_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat1_row0['ta [deg]'][0]%360, 45)

        state_sat2_fl = self.out_dir + '/sat2/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat2_fl)
        state_sat2_row0 = pd.read_csv(state_sat2_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat2_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat2_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat2_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat2_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat2_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat2_row0['ta [deg]'][0]%360, 90)

        state_sat3_fl = self.out_dir + '/sat3/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat3_fl)
        state_sat3_row0 = pd.read_csv(state_sat3_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat3_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat3_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat3_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat3_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat3_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat3_row0['ta [deg]'][0]%360, 135)

        state_sat4_fl = self.out_dir + '/sat4/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat4_fl)
        state_sat4_row0 = pd.read_csv(state_sat4_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat4_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat4_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat4_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat4_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat4_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat4_row0['ta [deg]'][0]%360, 180, delta=0.001)

        state_sat5_fl = self.out_dir + '/sat5/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat5_fl)
        state_sat5_row0 = pd.read_csv(state_sat5_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat5_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat5_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat5_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat5_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat5_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat5_row0['ta [deg]'][0]%360, 225)

        state_sat6_fl = self.out_dir + '/sat6/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat6_fl)
        state_sat6_row0 = pd.read_csv(state_sat6_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat6_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat6_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat6_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat6_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat6_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat6_row0['ta [deg]'][0]%360, 270)

        state_sat7_fl = self.out_dir + '/sat7/state_keplerian.csv'        
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_sat7_fl)
        state_sat7_row0 = pd.read_csv(state_sat7_fl, skiprows=4, nrows=2)
        self.assertEqual(epoch_JDUT1, 2459270.75)
        self.assertAlmostEqual(step_size, 211.50955372780942)
        self.assertEqual(duration, 0.25)
        self.assertAlmostEqual(state_sat7_row0['sma [km]'][0], 7078.137)
        self.assertAlmostEqual(state_sat7_row0['ecc'][0], 0.001)
        self.assertAlmostEqual(state_sat7_row0['inc [deg]'][0], 45)
        self.assertAlmostEqual(state_sat7_row0['raan [deg]'][0]%360, 0)
        self.assertAlmostEqual(state_sat7_row0['aop [deg]'][0], 135.0)
        self.assertAlmostEqual(state_sat7_row0['ta [deg]'][0]%360, 315)
    

    def test_scenario_7(self):
        """ Multiple satellites from list, multiple instruments per satellite ; propagation, grid-coverage, data-metrics calculation, contact-finder (inter-satellite).

            Spacecraft #1 : No instruments.
            Spacecraft #2 : 1 instrument (Basic Sensor).
            Spacecraft #3 : 2 instruments (Passive Optical Scanner, SAR)

        """
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                               "duration": 0.1, \
                               "spacecraft": [{ \
                                  "@id": "spc1", \
                                  "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                  }, \
                                  "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                 "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                               } \
                                   }, \
                                   { \
                                    "@id": "spc2", \
                                    "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -35} \
                                                }, \
                                    "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight":15, "angleWidth":10 }, \
                                                   "@id":"bs", "@type":"Basic Sensor" } \
                                    }, \
                                    { \
                                    "@id": "spc3", \
                                    "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -145} \
                                                }, \
                                    "instrument": [{"@type": "Passive Optical Scanner", "@id": "opt1",\
                                                    "fieldOfViewGeometry": { "shape": "RECTanGULAR", "angleHeight": 0.628, "angleWidth": 115.8 }, \
                                                    "sceneFieldOfViewGeometry": { "shape": "RECTanGULAR", "angleHeight": 5, "angleWidth": 115.8 }, \
                                                    "scanTechnique": "WhiskBROOM", \
                                                    "orientation": { "referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_loOK", "sideLookAngle": 0 }, \
                                                    "numberDetectorRows": 256, "numberDetectorCols": 1, \
                                                    "detectorWidth": 30e-6, "focalLength": 0.7, "operatingWavelength": 4.2e-6, "bandwidth": 1.9e-6, \
                                                    "quantumEff": 0.5, "targetBlackBodyTemp": 290, "bitsPerPixel": 8, "opticsSysEff": 0.75, \
                                                    "numOfReadOutE": 25, "apertureDia": 0.26, "Fnum": 2.7, "atmosLossModel": "LOWTRAN7" \
                                                   }, \
                                                   {"@type": "Synthetic Aperture Radar", "@id": "sar1", \
                                                    "orientation": { "convention": "SIDE_LOOK", "sideLookAngle": 20.5 }, \
                                                    "antenna":{"shape": "RECTANGULAR", "height": 10.7, "width": 2.16, "apertureEfficiency": 0.6, "apertureExcitation": "UNIFORM"}, \
                                                    "sceneFieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":6.233630110575892}, \
                                                    "pulseWidth": 33.4e-6, \
                                                    "operatingFrequency": 1.2757e9, "peakTransmitPower": 1000, "chirpBandwidth": 19e6, \
                                                    "minimumPRF": 1463, "maximumPRF": 1686, "radarLoss": 3.5, "systemNoiseFigure": 5.11 \
                                                    }] \
                                    }], \
                                "grid": [{"@type": "autogrid", "@id": 1, "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180, "gridRes": 1}, {"@type": "autogrid", "@id": 2, "latUpper":22, "latLower":20, "lonUpper":180, "lonLower":-180, "gridRes": 1}], \
                                "settings": {"outDir": "temp/", "coverageType": "GRID COVERAGE"} \
                            }'

        mission = Mission.from_json(mission_json_str)
        self.assertEqual(len(mission.spacecraft), 3)        

        out_info = mission.execute()
    
    '''
    def test_scenario_x(self):
        """ Hydrology paper """
        mission_json_str = '{  "epoch":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":27, "hour":18, "minute":43, "second":5}, \
                                "duration": 3, \
                                "constellation": { "@type": "Walker Delta Constellation", \
                                        "date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":27, "hour":18, "minute":43, "second":5}, \
                                        "numberSatellites": 8, \
                                        "numberPlanes": 1, \
                                        "relativeSpacing": 1, \
                                        "alt": 705, \
                                        "ecc": 0.0001, \
                                        "inc": 98.2, \
                                        "aop": 302.6503 \
                                    }, \
                                "groundStation":{"name": "AtMetro", "latitude": 33, "longitude": -98, "altitude":0, "minimumElevation":35}, \
                                "propagator": {"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 4}, \
                                "settings": {"outDir": "temp/"} \
                            }'
        mission = Mission.from_json(mission_json_str)
        out_info = mission.execute()
    '''


        