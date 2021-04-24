"""Unit tests for orbitpy.mission module.

The following tests are framed to test the different possible ways in which the mission can be framed in the JSON string and called to execute.
In each test, the output is tested with the results as computed on 14 April 2021 (thus representing the "truth" data). 
The truth data is present in the folder ``test_data``.

**Tests:**

* ``test_scenario_1``: 1 satellite, no instrument ; propagation only, auto/ custom-time-step. The mission epoch is same, different from the satellite orbit-state date.
* ``test_scenario_2``: 1 satellite, 1 instrument ; propagation (custom time-step), grid-coverage (2 (auto) grids, default and custom-grid res), data-metrics calculation.
* ``test_scenario_3``: 1 satellite, 1 instrument ; propagation, pointing-options coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_scenario_4``: 1 satellite, 1 instrument ; propagation, pointing-options with grid-coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_scenario_5``: 1 satellite, multiple ground-stations ; propagation, contact-finder (ground-station only).
* ``test_scenario_6``: Multiple satellites from constellation; propagation, contact-finder (ground-station, inter-satellite).
* ``test_scenario_7``: Multiple satellites from constellation, single-instrument per satellite ; propagation, pointing-options-coverage, data-metrics calculation, contact-finder (inter-satellite only).
* ``test_scenario_8``: Multiple satellites from list, multiple instruments per satellite, multiple ground-stations ; propagation, grid-coverage, data-metrics calculation, contact-finder (ground-station and inter-satellite).

"""
import json
import os, shutil
import sys
import unittest
import random
import numpy as np
import pandas as pd

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
        
    '''
    def test_scenario_1(self):
        """  1 satellite, no instrument ; propagation only, auto, custom-time-step. The mission epoch is same, different from the satellite orbit-state date.
        """
        # auto propagation step-size, mission-date different from spacecraft orbitstate date
        mission_json_str = '{  "epoch":{"dateType":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "settings": {"outDir": "tests/temp/"} \
                            }'
        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459299.1292592594)
        self.assertAlmostEqual(mission.duration, 0.1)
        self.assertEqual(len(mission.spacecraft), 1)
        self.assertAlmostEqual(mission.spacecraft[0], Spacecraft.from_dict({ "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}, 
                                                                          "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0},
                                                                                            "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}} 
                                                                        }))
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 Analytical Propagator", "stepSize": 173.31598026839598})) # corresponds to time-step calculated considering horizon angle = 136.0373... deg and time-resolution factor = 0.25
        self.assertIsNone(mission.grid)
        self.assertIsNone(mission.groundStation)
        self.assertAlmostEqual(mission.propagator.stepSize, 173.31598026839598) 
        self.assertEqual(mission.settings.outDir,  "tests/temp/")
        self.assertIsNone(mission.settings.coverageType)
        self.assertEqual(mission.settings.propTimeResFactor, 0.25)
        self.assertEqual(mission.settings.gridResFactor, 0.9)

        out_info = mission.execute()

        # custom propagation step-size, mission-date same as spacecraft orbitstate date, custom propTimeResFactor = 1/8
        mission_json_str = '{  "epoch":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "settings": {"outDir": "tests/temp/", "propTimeResFactor": 0.125} \
                            }'
        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459270.75)
        self.assertAlmostEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 Analytical Propagator", "stepSize": 86.657990134197990})) # corresponds to time-step calculated considering horizon angle = 136.0373... deg and time-resolution factor = 1/8
        self.assertEqual(mission.settings.propTimeResFactor, 1/8)

        out_info = mission.execute()

    
    def test_scenario_2(self):
        """  1 satellite, 1 instrument ; propagation (custom time-step), (field-of-regard) grid-coverage (2 (auto) grids, default and custom-grid res), basic-sensor data-metrics calculation.
        """
        # check warnings are issued.
        mission_json_str = '{  "epoch":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                   "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                            } \
                                    }, \
                                "propagator": {"@type": "J2 Analytical Propagator", "stepSize": 200}, \
                                "settings": {"outDir": "tests/temp/", "coverageType": "Grid COverage"} \
                            }'
        with self.assertWarns(Warning): # check for warning that user specified step-size is greater than auto-calculated step-size.
            mission = Mission.from_json(mission_json_str)

        mission = Mission.from_json(mission_json_str)
        with self.assertWarns(Warning): # check for warning that grid has not been specified.
            out_info = mission.execute()

        # check execution with single grid.
        mission_json_str = '{   "epoch":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                "duration": 0.5, \
                                "spacecraft": [{ \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 30, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                   "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                            } \
                                    }], \
                                "propagator": {"@type": "J2 Analytical Propagator", "stepSize": 60}, \
                                "grid": [{"@type": "autogrid", "@id": "cus", "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180}, {"@type": "autogrid", "@id": "auto", "latUpper":20, "latLower":0, "lonUpper":180, "lonLower":-180, "gridRes": 1}], \
                                "settings": {"outDir": "tests/temp/", "coverageType": "Grid COverage", "gridResFactor": 0.5} \
                            }'

        mission = Mission.from_json(mission_json_str)
 
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 Analytical Propagator", "stepSize": 60}))


        self.assertEqual(len(mission.grid), 2)
        # 0.5917400590151374 is the grid-resolution calculated for the 15 deg FOV sensor at altitude of 500km and gridResFactor = 0.5
        self.assertEqual(mission.grid[0].num_points, 1820) # ~ 4*pi/ (0.5917400590151374*pi/180 * 0.5917400590151374*pi/180) *  ((2*pi)*(2*pi/180))/(4*pi)
        # 1 deg grid resolution is input in the specifications
        self.assertEqual(mission.grid[1].num_points, 7402) # ~ 4*pi/ (pi/180 * pi/180) * ((2*pi)*(20*pi/180)/(4*pi)) 


        out_info = mission.execute()
    
    def test_scenario_3(self):
        """  1 satellite, 1 instrument ; propagation, pointing-options coverage, basic-sensor data-metrics calculation.
        """
        mission_json_str = '{   "epoch":{"dateType":"GREGORIAN_UTC", "year":2021, "month":3, "day":12, "hour":23, "minute":12, "second":12}, \
                                "duration": 0.05, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": [{ "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                   "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight":15, "angleWidth":10 }, \
                                                   "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":0}, \
                                                                      {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":-15}, \
                                                                      {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":15}], \
                                                   "@id":"bs1", "@type":"Basic Sensor" \
                                                  }] \
                                    }, \
                                "settings": {"outDir": "tests/temp/", "coverageType": "Pointing Options COverage"} \
                            }'

        mission = Mission.from_json(mission_json_str)

 
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2459286.4668055554)
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 Analytical Propagator", "stepSize": 6.820899943040534}))

        out_info = mission.execute()
    
    def test_scenario_4(self):
        """ 1 satellite, 1 SAR instrument ; propagation, pointing-options with grid-coverage and access-file correction (since sidelooking instrument with narrow At-fov), SAR data-metrics calculation.
            Using default propagation step-size and grid-resolution. The scene FOV has angleWidth = instrument FOV angleWidth. The scene FOV angleHeight is larger to allow for coarser propagation step-size and gird-resolution.

        """
        mission_json_str = '{   "epoch":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                "duration": 0.1, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":15, "hour":12, "minute":12, "second":12}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                }, \
                                   "instrument": { "@type": "Synthetic Aperture Radar", \
                                                    "@id": "sar1", \
                                                    "orientation": { \
                                                        "convention": "SIDE_LOOK", \
                                                        "sideLookAngle": 20.5 \
                                                    }, \
                                                    "sceneFieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":6.233630110575892}, \
                                                    "pulseWidth": 33.4e-6, \
                                                    "antennaHeight": 10.7, \
                                                    "antennaWidth": 2.16, \
                                                    "antennaApertureEfficiency": 0.6, \
                                                    "operatingFrequency": 1.2757e9, \
                                                    "peakTransmitPower": 1000, \
                                                    "chirpBandwidth": 19e6, \
                                                    "minimumPRF": 1463, \
                                                    "maximumPRF": 1686, \
                                                    "radarLoss": 3.5, \
                                                    "systemNoiseFigure": 5.11, \
                                                    "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":-20.5}, \
                                                                    {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":20.5}] \
                                                    } \
                                    }, \
                                "grid": [{"@type": "autogrid", "@id": 1, "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180}, {"@type": "autogrid", "@id": 2, "latUpper":22, "latLower":20, "lonUpper":180, "lonLower":-180}], \
                                "settings": {"outDir": "tests/temp/", "coverageType": "Pointing Options with Grid COverage"} \
                            }'

        mission = Mission.from_json(mission_json_str)
        self.assertAlmostEqual(mission.epoch.GetJulianDate(), 2458254.0084722224)
        self.assertEqual(mission.propagator, J2AnalyticalPropagator.from_dict({"@type": "J2 Analytical Propagator", "stepSize": 2.2600808214710266}))
        self.assertEqual(mission.grid[0].num_points, 46299)
        self.assertEqual(mission.grid[1].num_points, 43234)

        out_info = mission.execute()
    '''

    def test_scenario_5(self):
        """    1 satellite, multiple ground-stations ; propagation, contact-finder (ground-station only).
        """
        mission_json_str = '{  "epoch":{"dateType":"GREGORIAN_UTC", "year":2021, "month":3, "day":25, "hour":15, "minute":6, "second":8}, \
                                "duration": 0.5, \
                                "spacecraft": { \
                                   "spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                  "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -25} \
                                                } \
                                    }, \
                                "groundStation":[{"name": "TrollSAR", "latitude": -72.0029, "longitude": 2.5257, "altitude":0}, \
                                                 {"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}], \
                                "settings": {"outDir": "tests/temp/"} \
                            }'
        
        mission = Mission.from_json(mission_json_str)
        self.assertEqual(len(mission.groundStation), 2)
        self.assertIsInstance(mission.groundStation[0], GroundStation)
        self.assertEqual(mission.groundStation[0], GroundStation.from_dict({"name": "TrollSAR", "latitude": -72.0029, "longitude": 2.5257, "altitude":0}))
        self.assertIsInstance(mission.groundStation[1], GroundStation)
        self.assertEqual(mission.groundStation[1], GroundStation.from_dict({"name": "CONAE", "latitude": -31.52, "longitude": -64.46, "altitude":0}))

        out_info = mission.execute()

    def test_scenario_6(self):
        """    Multiple satellites from constellation; propagation, contact-finder (inter-satellite only).
        """
        mission_json_str = '{  "epoch":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75}, \
                                "duration": 0.25, \
                                "constellation": { "@type": "Walker Delta Constellation", \
                                        "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}, \
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
                                "settings": {"outDir": "tests/temp/"} \
                            }'
        mission = Mission.from_json(mission_json_str)
        out_info = mission.execute()