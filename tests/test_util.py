"""Unit tests for orbitpy.util module.
"""
import unittest

import numpy as np
from instrupy.util import Orientation
from instrupy import Instrument
from orbitpy.util import OrbitState, SpacecraftBus, Spacecraft
import orbitpy.util
import propcov

from util.spacecrafts import spc1_json, spc2_json, spc3_json

class TestOrbitState(unittest.TestCase):
  
    def test_date_from_dict(self):
        x = OrbitState.date_from_dict({"@type":"JULIAN_DATE_UT1", "jd":2459270.75})
        self.assertIsInstance(x, propcov.AbsoluteDate)

        y = OrbitState.date_from_dict({"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0})
        self.assertIsInstance(y, propcov.AbsoluteDate)

        with self.assertRaises(Exception): # Invalid Date Type shall raise Exception
            OrbitState.date_from_dict({"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0})
        

        self.assertEqual(x, y)

    def test_state_from_dict(self):
        x = OrbitState.state_from_dict({"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6867, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25})
        self.assertIsInstance(x, propcov.OrbitState)

        cart_state = x.GetCartesianState().GetRealArray()

        y = OrbitState.state_from_dict({"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": cart_state[0], "y": cart_state[1], "z": cart_state[2], "vx": cart_state[3], "vy": cart_state[4], "vz": cart_state[5]})
        self.assertIsInstance(y, propcov.OrbitState) 

        self.assertEqual(x, y)
 
    def test_date_to_dict(self): #@TODO
        pass

    def test_state_to_dict(self): #@TODO
        pass
    
    def test_get_julian_date(self): #@TODO
        pass
    
    def test_get_cartesian_earth_centered_inertial_state(self): #@TODO
        pass

    def test_get_keplerian_earth_centered_inertial_state(self): #@TODO
        pass

    def test_from_dict(self):
        # Julian date, Cartesian state
        o = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75}, 
                                  "state":{"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": 6878.137, "y": 0, "z": 0, "vx": 0, "vy": 7.6126, "vz": 0},
                                  "@id": 123})
        self.assertIsInstance(o, OrbitState)
        self.assertEqual(o._id, 123)
        self.assertEqual(o.date, propcov.AbsoluteDate.fromJulianDate(2459270.75))
        self.assertEqual(o.state, propcov.OrbitState.fromCartesianState(propcov.Rvector6([6878.137,0,0,0,7.6126,0])))

        # Gregorian date, Keplerian state
        o = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, 
                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25},
                                  })
        self.assertIsInstance(o, OrbitState)
        self.assertIsNone(o._id)
        self.assertEqual(o.date, propcov.AbsoluteDate.fromGregorianDate(2021, 2, 25, 6 ,0, 0))
        self.assertEqual(o.state, propcov.OrbitState.fromKeplerianState(6878.137, 0.001, np.deg2rad(45), np.deg2rad(35), np.deg2rad(145), np.deg2rad(-25)))
    
    def test_state_from_dict_tle(self):
  
        d = {   "@type": "TLE",
                "tle_line0": "AQUA",
                "tle_line1": "1 27424U 02022A   24052.86568623  .00001525  00000-0  33557-3 0  9991",
                "tle_line2": "2 27424  98.3176   1.9284 0001998  92.8813 328.6214 14.58896689159754",
                "@id": 123}
        
        o = OrbitState.from_dict(d)
        self.assertIsInstance(o, OrbitState)

        self.assertEqual(o._id, 123)
        self.assertAlmostEqual(o.get_julian_date(), 2460362.365686, places=6)
        state_dict = OrbitState.state_to_dict(o.state, state_type='CARTESIAN_EARTH_CENTERED_INERTIAL')

        self.assertAlmostEqual(state_dict["x"], 3417.50458485)
        self.assertAlmostEqual(state_dict["y"], -802.52409303)
        self.assertAlmostEqual(state_dict["z"], 6134.36342655)
        self.assertAlmostEqual(state_dict["vx"], -6.5733887)
        self.assertAlmostEqual(state_dict["vy"], -0.70421461)
        self.assertAlmostEqual(state_dict["vz"], 3.56159903)

        # Terra SAR-X
        # Compare against the mean Keplerian elements given in the Orbit Mean-Elements Message (OMM) from www.space-track.org. 
        # Note that the TLE info is also sourced from the same OMM. 
        d = {"@type": "TLE",
             "tle_line0": "Terra SAR X",
             "tle_line1":   "1 31698U 07026A   24099.48501970  .00001689  00000-0  83603-4 0  9998",
             "tle_line2":   "2 31698  97.4452 107.6258 0001796  88.6052 271.5388 15.19151402932479",
             "@id": 123}
        
        o = OrbitState.from_dict(d)
        self.assertIsInstance(o, OrbitState)

        self.assertEqual(o._id, 123)
        self.assertAlmostEqual(o.get_julian_date(), 2460408.985020, places=6)
        state_dict = OrbitState.state_to_dict(o.state, state_type='KEPLERIAN_EARTH_CENTERED_INERTIAL')

        self.assertAlmostEqual(state_dict["sma"], 6886.541, delta=10e3) # 10k error tolerance
        self.assertAlmostEqual(state_dict["ecc"], 0.00017960, delta=0.0012) # TODO: This appears to be a large error....
        self.assertAlmostEqual(state_dict["inc"], 97.4452, delta = 0.2)
        self.assertAlmostEqual(state_dict["raan"], 107.6258, delta = 0.4)

        # The AOP has large errors, which maybe OK for near-circular orbits in which the AOP is not defined well. 
        # AOP + TA shall give the satellite position wrt the ascending node. 
        # Note that the Mean ANnomaly value is given in the OMM (i.e. 88.6052 degrees), which is ~ TA since the orbit is nearly circular
        self.assertAlmostEqual(state_dict["ta"] + state_dict["aop"], 271.5388 + 88.6052, delta = 0.2)

    def test_state_from_dict_omm(self):

        # Terra SAR-X
        d = {"@type": "OMM",
             "omm": {
                        "CCSDS_OMM_VERS": "2.0", "COMMENT": "GENERATED VIA SPACE-TRACK.ORG API",
                        "CREATION_DATE": "2024-04-08T19:28:18", "ORIGINATOR": "18 SPCS",
                        "OBJECT_NAME": "TERRA SAR X", "OBJECT_ID": "2007-026A",
                        "CENTER_NAME": "EARTH", "REF_FRAME": "TEME",
                        "TIME_SYSTEM": "UTC", "MEAN_ELEMENT_THEORY": "SGP4",
                        "EPOCH": "2024-04-08T11:38:25.702080", "MEAN_MOTION": "15.19151402",
                        "ECCENTRICITY": "0.0001796", "INCLINATION": "97.4452",
                        "RA_OF_ASC_NODE": "107.6258", "ARG_OF_PERICENTER": "88.6052",
                        "MEAN_ANOMALY": "271.5388", "EPHEMERIS_TYPE": "0",
                        "CLASSIFICATION_TYPE": "U", "NORAD_CAT_ID": "31698",
                        "ELEMENT_SET_NO": "999", "REV_AT_EPOCH": "93181",
                        "BSTAR": "0.000083603", "MEAN_MOTION_DOT": "0.00001689",
                        "MEAN_MOTION_DDOT": "0",
                        "TLE_LINE0": "0 TERRA SAR X",
                        "TLE_LINE1": "1 31698U 07026A   24099.48501970  .00001689  00000-0  83603-4 0  9998",
                        "TLE_LINE2": "2 31698  97.4452 107.6258 0001796  88.6052 271.5388 15.19151402931816",
                        "SEMIMAJOR_AXIS": "6886.541", "PERIOD": "94.790", "APOAPSIS": "509.643", "PERIAPSIS": "507.169",
                        "OBJECT_TYPE": "PAYLOAD", "DECAYED": "0"
                    },
             "@id": 123}
        
        o = OrbitState.from_dict(d)
        self.assertIsInstance(o, OrbitState)

        self.assertEqual(o._id, 123)
        self.assertAlmostEqual(o.get_julian_date(), 2460408.985020, places=6)
        state_dict = OrbitState.state_to_dict(o.state, state_type='KEPLERIAN_EARTH_CENTERED_INERTIAL')

        # Compare against the mean Keplerian elements given in the Orbit Mean-Elements Message (OMM) from www.space-track.org
        # Note that the TLE info is also sourced from the same OMM. 
        self.assertAlmostEqual(state_dict["sma"], 6886.541, delta=10e3) # 10k error tolerance
        self.assertAlmostEqual(state_dict["ecc"], 0.00017960, delta=0.0012) # TODO: This appears to be a large error....
        self.assertAlmostEqual(state_dict["inc"], 97.4452, delta = 0.2)
        self.assertAlmostEqual(state_dict["raan"], 107.6258, delta = 0.4)

        # The AOP has large errors, which maybe OK for near-circular orbits in which the AOP is not defined well. 
        # AOP + TA shall give the satellite position wrt the ascending node. 
        # Note that the Mean Anomaly value is given in the OMM (i.e. 88.6052 degrees), which is ~ TA since the orbit is nearly circular
        self.assertAlmostEqual(state_dict["ta"] + state_dict["aop"], 271.5388 + 88.6052, delta = 0.2)

    def test_to_dict(self): #@TODO test Keplerian state output
        # Input: Julian date, Cartesian state
        o = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75}, 
                                  "state":{"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": 6878.137, "y": 0, "z": 0, "vx": 0, "vy": 7.6126, "vz": 0},
                                 })
        d = o.to_dict()
        self.assertEqual(d["date"]["@type"], "JULIAN_DATE_UT1")
        self.assertEqual(d["date"]["jd"], 2459270.75)
        self.assertEqual(d["state"]["@type"], "CARTESIAN_EARTH_CENTERED_INERTIAL")
        self.assertAlmostEqual(d["state"]["x"], 6878.137)
        self.assertEqual(d["state"]["y"], 0)
        self.assertEqual(d["state"]["z"], 0)
        self.assertEqual(d["state"]["vx"], 0)
        self.assertEqual(d["state"]["vy"], 7.6126)
        self.assertEqual(d["state"]["vz"], 0)
        self.assertIsNone(d["@id"])

        # Input: Gregorian date, Keplerian state
        o = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, 
                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25},
                                  "@id": "123"})
        d = o.to_dict()
        date = o.get_julian_date()
        state = o.get_cartesian_earth_centered_inertial_state()
        self.assertEqual(d["date"]["@type"], "JULIAN_DATE_UT1")
        self.assertEqual(d["date"]["jd"], date)
        self.assertEqual(d["state"]["@type"], "CARTESIAN_EARTH_CENTERED_INERTIAL")
        self.assertAlmostEqual(d["state"]["x"], state[0])
        self.assertEqual(d["state"]["y"], state[1])
        self.assertEqual(d["state"]["z"], state[2])
        self.assertEqual(d["state"]["vx"], state[3])
        self.assertEqual(d["state"]["vy"], state[4])
        self.assertEqual(d["state"]["vz"], state[5])
        self.assertEqual(d["@id"], "123")

class TestSpacecraftBus(unittest.TestCase):

    def test_from_json(self):
        # typical case
        o = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED", "@id": "abc"}, "@id":123}')
        self.assertEqual(o.name, "BlueCanyon")
        self.assertEqual(o.mass, 20)
        self.assertEqual(o.volume, 0.5)
        self.assertEqual(o.orientation, Orientation.from_dict({"referenceFrame":"Nadir_pointing", "convention": "REF_FRAME_ALIGNED", "@id": "abc"}))
        self.assertIsNone(o.solarPanelConfig)
        self.assertEqual(o._id, 123)

        # check default orientation
        o = SpacecraftBus.from_json('{"name": "Microsat", "mass": 100, "volume": 1}')
        self.assertEqual(o.name, "Microsat")
        self.assertEqual(o.mass, 100)
        self.assertEqual(o.volume, 1)
        self.assertEqual(o.orientation, Orientation.from_dict({"referenceFrame":"Nadir_pointing", "convention": "REF_FRAME_ALIGNED"}))
        self.assertIsNone(o.solarPanelConfig)
        self.assertIsNone(o._id)

        # side look orientation
        o = SpacecraftBus.from_json('{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":-10}, "@id":123}')
        self.assertIsNone(o.name)
        self.assertIsNone(o.mass)
        self.assertIsNone(o.volume)
        self.assertEqual(o.orientation, Orientation.from_dict({"referenceFrame":"Nadir_pointing", "convention": "SIDE_LOOK", "sideLookAngle":-10}))
        self.assertIsNone(o.solarPanelConfig)
        self.assertEqual(o._id, 123)

        # Euler rotation specification, ECI frame
        o = SpacecraftBus.from_json('{"orientation":{"referenceFrame": "EARTH_CENTERED_INERTIAL", "convention": "XYZ","xRotation":10,"yRotation":-10.4,"zRotation":20.78}}')
        self.assertIsNone(o.name)
        self.assertIsNone(o.mass)
        self.assertIsNone(o.volume)
        self.assertEqual(o.orientation, Orientation.from_dict({"referenceFrame":"EARTH_CENTERED_INERTIAL", "convention": "XYZ","xRotation":10,"yRotation":-10.4,"zRotation":20.78}))
        self.assertIsNone(o.solarPanelConfig)
        self.assertIsNone(o._id)

    def test_to_dict(self):
        # typical case
        o = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED", "@id": "abc"}, "@id":123}')
        o_dict = o.to_dict()
        self.assertEqual(o_dict['name'], 'BlueCanyon')
        self.assertEqual(o_dict['mass'], 20)
        self.assertEqual(o_dict['volume'], 0.5)
        self.assertIsNone(o_dict['solarPanelConfig'])
        self.assertEqual(o_dict['orientation']['eulerAngle1'], 0)
        self.assertEqual(o_dict['orientation']['eulerAngle2'], 0)
        self.assertEqual(o_dict['orientation']['eulerAngle3'], 0)
        self.assertEqual(o_dict['orientation']['eulerSeq1'], 1)
        self.assertEqual(o_dict['orientation']['eulerSeq2'], 2)
        self.assertEqual(o_dict['orientation']['eulerSeq3'], 3)
        self.assertEqual(o_dict['orientation']['@id'], 'abc')
        self.assertEqual(o_dict['@id'], 123)

    def test___eq_(self):
        # typical case, note that "@id" can be different.
        o1 = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED", "@id": "abc"}, "@id":123}')
        o2 = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED", "@id": "abc"}, "@id":"abc"}')
        self.assertEqual(o1, o2)
        o2 = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 10, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED", "@id": "abc"}, "@id":123}')
        self.assertNotEqual(o1, o2)

        # Equivalent orientation specifications in different input format 
        o1 = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "REF_FRAME_ALIGNED"}, "@id":123}')
        o2 = SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, "orientation":{"referenceFrame": "NADIR_POINTING", \
                                      "convention": "XYZ","xRotation":0,"yRotation":0,"zRotation":0}, "@id":123}')
        self.assertEqual(o1, o2)

class TestSpacecraft(unittest.TestCase):

    def test_from_json(self):
        spc1 = Spacecraft.from_json(spc1_json)  
        spc2 = Spacecraft.from_json(spc2_json)  
        spc3 = Spacecraft.from_json(spc3_json)  

        # typical case 1 instrument      
        self.assertEqual(spc1.name, "Mars")
        self.assertEqual(spc1.spacecraftBus, SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }'))
        self.assertEqual(spc1.instrument, [Instrument.from_json('{"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}')])
        self.assertEqual(spc1.orbitState, OrbitState.from_json('{"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                              "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}}'))
        self.assertEqual(spc1._id, "sp1")

        # no instruments        
        self.assertEqual(spc2.name, "Jupyter")
        self.assertEqual(spc2.spacecraftBus, SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }'))
        self.assertIsNone(spc2.instrument)
        self.assertEqual(spc2.orbitState, OrbitState.from_json('{"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                              "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}}'))
        self.assertEqual(spc2._id, 12)

        # 3 instruments with multiple modes, no spacecraft id assignment        
        self.assertEqual(spc3.name, "Saturn")
        self.assertEqual(spc3.spacecraftBus, SpacecraftBus.from_json('{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }'))
        self.assertEqual(len(spc3.instrument), 3)
        # 1st instrument
        self.assertEqual(spc3.instrument[0].get_id(), 'bs1')
        self.assertEqual(spc3.instrument[0].get_mode_id()[0], '0')
        # 2nd instrument
        self.assertIsNotNone(spc3.instrument[1].get_id())
        self.assertIsNotNone(spc3.instrument[1].get_mode_id()[0], '0')
        # 3rd instrument
        self.assertEqual(spc3.instrument[2].get_id(), 'bs3')
        self.assertEqual(spc3.instrument[2].get_mode_id()[0], 0)
        self.assertEqual(spc3.instrument[2].get_mode_id()[1], 1)
        self.assertIsNotNone(spc3.instrument[2].get_mode_id()[2])
        self.assertEqual(spc3.orbitState, OrbitState.from_json('{"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                              "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}}'))
        self.assertIsNotNone(spc3._id)

    
    def test_get_instrument(self):
        spc1 = Spacecraft.from_json(spc1_json)  
        spc2 = Spacecraft.from_json(spc2_json)  
        spc3 = Spacecraft.from_json(spc3_json)

        # spc1 has 1 instrument with id 'bs1'
        self.assertEqual(spc1.get_instrument(sensor_id='bs1'), spc1.instrument[0])
        self.assertEqual(spc1.get_instrument(), spc1.instrument[0]) # no sensor_id specification
        self.assertIsNone(spc1.get_instrument('bs2')) # wrong sensor_id
        
        # spc2 has no instruments
        self.assertIsNone(spc2.get_instrument())

        # spc3 has three instruments
        self.assertEqual(spc3.get_instrument(sensor_id='bs1'), spc3.instrument[0])
        self.assertEqual(spc3.get_instrument(), spc3.instrument[0])
        self.assertEqual(spc3.get_instrument(sensor_id='bs3'), spc3.instrument[2])

    def test_add_instrument(self): #TODO
        pass
    
    def test_add_to_list(self): #TODO
        pass

    def test_get_id(self): #TODO
        pass
    
    def test_to_dict(self): #TODO
        pass
        
    '''
    def test___eq__(self):
        o1 = Spacecraft.from_json('{"@id": "sp1", "name": "Spock", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        o2 = Spacecraft.from_json('{"@id": "sp1", "name": "Spock", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        self.assertEqual(o1, o2)
        # spacecraft bus different (orientation)
        o2 = Spacecraft.from_json('{"@id": "sp1", "name": "Spock", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame":"Nadir_pointing", "convention": "SIDE_LOOK", "sideLookAngle":-1} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        self.assertNotEqual(o1, o2)
        # instrument different (fieldOfViewGeometry)
        o2 = Spacecraft.from_json('{"@id": "sp1", "name": "Spock", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame":"Nadir_pointing", "convention": "SIDE_LOOK", "sideLookAngle":-1} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        self.assertNotEqual(o1, o2)
        # orbitState different (date)
        o2 = Spacecraft.from_json('{"@id": "sp1", "name": "Spock", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame":"Nadir_pointing", "convention": "SIDE_LOOK", "sideLookAngle":-1} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":3, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        self.assertNotEqual(o1, o2)
    '''

class TestUtilModuleFunction(unittest.TestCase):

    def test_helper_extract_spacecraft_params(self):

        # 1 instrument, 1 mode
        o1 = Spacecraft.from_json('{"@id": "sp1", "name": "Mars", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                   "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                  "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                  "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                  "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                  "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor"}, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        # no instruments
        o2 = Spacecraft.from_json('{"@id": 12, "name": "Jupyter", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        # 3 instruments with multiple modes, no spacecraft id assignment
        o3 = Spacecraft.from_json('{"name": "Saturn", \
                                   "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                                    "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                                   }, \
                                     "instrument": [ \
                                                    {   "name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                        "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                        "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                        "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                        "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor" \
                                                    }, \
                                                    {   "name": "Beta", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                        "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                                        "maneuver":{"maneuverType": "SINGLE_ROLL_ONLY", "A_rollMin":10, "A_rollMax":15}, \
                                                        "mode": [{"@id":101, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}} \
                                                                ], \
                                                        "numberDetectorRows":5, "numberDetectorCols":10, "@type":"Basic Sensor" \
                                                    }, \
                                                    {   "name": "Gamma", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                        "fieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":10 }, \
                                                        "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":10, "A_rollMax":15, "B_rollMin":-15, "B_rollMax":-10}, \
                                                        "mode": [{"@id":0, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}}, \
                                                                {"@id":1, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": 25}}, \
                                                                { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": -25}}  \
                                                                ], \
                                                        "numberDetectorRows":5, "numberDetectorCols":10, "@id": "bs3", "@type":"Basic Sensor" \
                                                    } \
                                                  ], \
                                    "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                                    "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                                  } \
                                  }')
        
        # single sc tests
        x = orbitpy.util.helper_extract_spacecraft_params([o1])
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0].sc_id, 'sp1')
        self.assertEqual(x[0].instru_id,'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertAlmostEqual(x[0].sma, 6878.136999999998)
        self.assertAlmostEqual(x[0].fov_height, 5.0)
        self.assertAlmostEqual(x[0]. fov_width, 5.0)
        self.assertAlmostEqual(x[0].for_height, 15.0) 
        self.assertAlmostEqual(x[0].for_width, 15.0)

        # spacecraft with no instruments
        x = orbitpy.util.helper_extract_spacecraft_params([o2])
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0].sc_id, 12)
        self.assertIsNone(x[0].instru_id)
        self.assertIsNone(x[0].mode_id)
        self.assertAlmostEqual(x[0].sma, 6878.136999999998)
        self.assertIsNone(x[0].fov_height)
        self.assertIsNone(x[0]. fov_width)
        self.assertIsNone(x[0].for_height) 
        self.assertIsNone(x[0].for_width)

        x = orbitpy.util.helper_extract_spacecraft_params([o3])
        self.assertEqual(len(x), 8)
        self.assertIsNotNone(x[0].sc_id)
        self.assertIsNotNone(x[1].sc_id)
        self.assertIsNotNone(x[2].sc_id)
        self.assertIsNotNone(x[3].sc_id)
        self.assertIsNotNone(x[4].sc_id)
        self.assertIsNotNone(x[5].sc_id)
        self.assertIsNotNone(x[6].sc_id)
        self.assertIsNotNone(x[7].sc_id)

        self.assertEqual(x[0].instru_id,'bs1')
        self.assertIsNotNone(x[1].instru_id)
        self.assertEqual(x[2].instru_id,'bs3')
        self.assertEqual(x[3].instru_id,'bs3')
        self.assertEqual(x[4].instru_id,'bs3')
        self.assertEqual(x[5].instru_id,'bs3')
        self.assertEqual(x[6].instru_id,'bs3')
        self.assertEqual(x[7].instru_id,'bs3')

        self.assertEqual(x[0].mode_id, '0')
        self.assertEqual(x[1].mode_id, 101)
        self.assertEqual(x[2].mode_id, 0)
        self.assertEqual(x[3].mode_id, 0)
        self.assertEqual(x[4].mode_id, 1)
        self.assertEqual(x[5].mode_id, 1)
        self.assertIsNotNone(x[6].mode_id)
        self.assertIsNotNone(x[7].mode_id)

        self.assertAlmostEqual(x[0].sma, 6878.136999999998)
        self.assertAlmostEqual(x[1].sma, 6878.136999999998)
        self.assertAlmostEqual(x[2].sma, 6878.136999999998)
        self.assertAlmostEqual(x[3].sma, 6878.136999999998)
        self.assertAlmostEqual(x[4].sma, 6878.136999999998)
        self.assertAlmostEqual(x[5].sma, 6878.136999999998)
        self.assertAlmostEqual(x[6].sma, 6878.136999999998)
        self.assertAlmostEqual(x[7].sma, 6878.136999999998)

        self.assertAlmostEqual(x[0].fov_height, 5.0)
        self.assertAlmostEqual(x[1].fov_height, 5.0)
        self.assertAlmostEqual(x[2].fov_height, 5.0)
        self.assertAlmostEqual(x[3].fov_height, 5.0)
        self.assertAlmostEqual(x[4].fov_height, 5.0)
        self.assertAlmostEqual(x[5].fov_height, 5.0)
        self.assertAlmostEqual(x[6].fov_height, 5.0)

        self.assertAlmostEqual(x[0]. fov_width, 5)
        self.assertAlmostEqual(x[1]. fov_width, 5)
        self.assertAlmostEqual(x[2]. fov_width, 10.0)
        self.assertAlmostEqual(x[3]. fov_width, 10.0)
        self.assertAlmostEqual(x[4]. fov_width, 10.0)
        self.assertAlmostEqual(x[5]. fov_width, 10.0)
        self.assertAlmostEqual(x[6]. fov_width, 10.0)
        self.assertAlmostEqual(x[7]. fov_width, 10.0)

        self.assertAlmostEqual(x[0].for_height, 15.0) 
        self.assertAlmostEqual(x[1].for_height, 5.0) 
        self.assertAlmostEqual(x[2].for_height, 5.0) 
        self.assertAlmostEqual(x[3].for_height, 5.0) 
        self.assertAlmostEqual(x[4].for_height, 5.0) 
        self.assertAlmostEqual(x[5].for_height, 5.0) 
        self.assertAlmostEqual(x[6].for_height, 5.0) 
        self.assertAlmostEqual(x[7].for_height, 5.0) 

        self.assertAlmostEqual(x[0].for_width, 15.0)
        self.assertAlmostEqual(x[1].for_width, 10.0)
        self.assertAlmostEqual(x[2].for_width, 15.0)
        self.assertAlmostEqual(x[3].for_width, 15.0)
        self.assertAlmostEqual(x[4].for_width, 15.0)
        self.assertAlmostEqual(x[5].for_width, 15.0)
        self.assertAlmostEqual(x[6].for_width, 15.0)
        self.assertAlmostEqual(x[7].for_width, 15.0)

        # test multiple spacecraft list, test first and last element of the resultant list
        x = orbitpy.util.helper_extract_spacecraft_params([o1, o2, o3])
        self.assertEqual(len(x), 10)
        self.assertEqual(x[0].sc_id, 'sp1')     
        self.assertEqual(x[0].instru_id,'bs1')
        self.assertEqual(x[0].mode_id, '0')
        self.assertAlmostEqual(x[0].sma, 6878.136999999998)
        self.assertAlmostEqual(x[0].fov_height, 5.0)
        self.assertAlmostEqual(x[0]. fov_width, 5.0)
        self.assertAlmostEqual(x[0].for_height, 15.0) 
        self.assertAlmostEqual(x[0].for_width, 15.0)

        self.assertEqual(x[1].sc_id, 12)

        self.assertIsNotNone(x[2].sc_id)       
        self.assertEqual(x[3].sc_id, x[2].sc_id)
        self.assertEqual(x[4].sc_id, x[2].sc_id)
        self.assertEqual(x[5].sc_id, x[2].sc_id)
        self.assertEqual(x[6].sc_id, x[2].sc_id)
        self.assertEqual(x[7].sc_id, x[2].sc_id) 
        self.assertEqual(x[8].sc_id, x[2].sc_id)
        self.assertEqual(x[9].sc_id, x[2].sc_id)
        self.assertEqual(x[9].instru_id,'bs3')
        self.assertIsNotNone(x[9].mode_id)
        self.assertAlmostEqual(x[9].sma, 6878.136999999998)
        self.assertAlmostEqual(x[9].fov_height, 5.0)
        self.assertAlmostEqual(x[9]. fov_width, 10.0)
        self.assertAlmostEqual(x[9].for_height, 5.0) 
        self.assertAlmostEqual(x[9].for_width, 15.0)       

    
    def test_extract_auxillary_info_from_state_file(self): # TODO
        pass

class TestGroundStation(unittest.TestCase): #TODO
    pass

class TestUtilFunctions(unittest.TestCase):

    def test_dictionary_list_to_object_list(self): #TODO
        pass

    def test_object_list_to_dictionary_list(self): #TODO
        pass

    def test_initialize_object_list(self): #TODO
        pass

    def test_add_to_list(self): #TODO
        pass

class TestOutputInfoUtility(unittest.TestCase): #TODO
    pass


