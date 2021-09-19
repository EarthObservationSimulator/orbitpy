from orbitpy.util import Spacecraft

################## Initialize some spacecrafts to be be used by the tests  ##################
# 1 instrument, 1 mode (no mode id)
spc1_json = '{"@id": "sp1", "name": "Mars", \
                            "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                            "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                            }, \
                            "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                            "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 }, \
                                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                            "numberDetectorRows":5, "numberDetectorCols":10, \
                                            "pointingOption": [{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":2.5, "zRotation":0}, \
                                            {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-2.5, "zRotation":0}  \
                                            ], \
                                            "@id":"bs1", "@type":"Basic Sensor"}, \
                            "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                            } \
                   }'

# no instruments
spc2_json = '{"@id": 12, "name": "Jupyter", \
              "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                               "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                              }, \
              "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                             "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                            } \
            }'
# 3 instruments with multiple modes, no spacecraft id assignment
spc3_json = '{"name": "Saturn", \
                            "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                            "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                            }, \
                            "instrument": [ {   "name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
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
                                                "pointingOption": [{"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":10}, \
                                                                   {"referenceFrame": "NADIR_POINTING", "convention": "SIDE_LOOK", "sideLookAngle":15}  \
                                                                  ], \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@type":"Basic Sensor" \
                                            }, \
                                            {   "name": "Gamma", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                "fieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":0.25, "angleWidth":10 }, \
                                                "sceneFieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":10 }, \
                                                "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":10, "A_rollMax":15, "B_rollMin":-15, "B_rollMax":-10}, \
                                                "mode": [{"@id":0, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}}, \
                                                        {"@id":1, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": 25}}, \
                                                        { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": -25}}  \
                                                        ], \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@id": "bs3", "@type":"Basic Sensor" \
                                            } \
                                            ], \
                            "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25} \
                                            } \
                            }'

# 3 instruments with multiple modes, no spacecraft id assignment, equatorial orbit
spc4_json = '{"name": "PlanetX", \
                            "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                            "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                            }, \
                                "instrument": [ \
                                            {   "name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":15 }, \
                                                "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}, \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs1", "@type":"Basic Sensor" \
                                            }, \
                                            {   "name": "Beta", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":25 }, \
                                                "maneuver":{"maneuverType": "SINGLE_ROLL_ONLY", "A_rollMin":10, "A_rollMax":15}, \
                                                "mode": [{"@id":101, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}} \
                                                        ], \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@id":"bs2", "@type":"Basic Sensor" \
                                            }, \
                                            {   "name": "Gamma", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12, \
                                                "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":48 }, \
                                                "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":10, "A_rollMax":15, "B_rollMin":-15, "B_rollMax":-10}, \
                                                "mode": [{"@id":0, "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}}, \
                                                        {"@id":"roll_pos", "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": 25}}, \
                                                        { "@id":"roll_neg", "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle": -25}}  \
                                                        ], \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@id": "bs3", "@type":"Basic Sensor" \
                                            } \
                                            ], \
                            "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0}, \
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 0, "raan": 35, "aop": 145, "ta": -25} \
                                            } \
                            }'

# 1 instruments with multiple modes
spc5_json = '{"name": "PlanetX", \
                            "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5, \
                                            "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"} \
                                            }, \
                                "instrument": [ \
                                            {   "fieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":0.1, "angleWidth":10 }, \
                                                "sceneFieldOfViewGeometry": {"shape": "RECTANGULAR", "angleHeight":5, "angleWidth":10 }, \
                                                "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                                "mode": [{"@id":0, "maneuver":{"maneuverType": "single_Roll_Only", "A_rollMin":10, "A_rollMax":15}}, \
                                                        {"@id":1, "maneuver":{"maneuverType": "single_Roll_Only", "A_rollMin":-15, "A_rollMax":-10}}, \
                                                        { "@id":2, "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":10, "A_rollMax":15, "B_rollMin":-15, "B_rollMax":-10}}  \
                                                        ], \
                                                "numberDetectorRows":5, "numberDetectorCols":10, "@id": "sen1", "@type":"Basic Sensor" \
                                            } \
                                            ], \
                            "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":3, "day":18, "hour":12, "minute":10, "second":0}, \
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7078.137, "ecc": 0.001, "inc": 98, "raan": 35, "aop": 145, "ta": -225} \
                                            } \
                            }'