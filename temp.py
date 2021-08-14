import orbitpy.grid 
from orbitpy.util import OrbitState, Spacecraft
from instrupy import Instrument

RE = 6378.137 # radius of Earth in kilometers
instru1 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 20}}')
instru2 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 5}, "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":10, "A_rollMax":15, "B_rollMin":-15, "B_rollMax":-10}}')
instru3 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 15}}')

orbit1 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+700, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
orbit2 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+510, "ecc": 0.001, "inc": 30, "raan": 0, "aop": 0, "ta": 0}})

sats = [Spacecraft(orbitState=orbit1, instrument=[instru1]), # list of 2 satellites with 1 and 2 instruments respectively
        Spacecraft(orbitState=orbit2, instrument=[instru2, instru3])]
x = orbitpy.grid.compute_grid_res(sats, 0.9) # custom grid resolution factor is chosen as 0.9
0.36007964028136996

