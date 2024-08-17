import os, shutil

from orbitpy.coveragecalculator import NewGridCoverage
from orbitpy.grid import Grid
from orbitpy.util import Spacecraft
from orbitpy.propagator import PropagatorFactory

RE = 6378.137 # radius of Earth in kilometers

dir_path = os.path.dirname(os.path.realpath(__file__))
out_dir = os.path.join(dir_path, 'results_new')
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

# make propagator
factory = PropagatorFactory()
step_size = 1
j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": step_size})


duration = 0.1
spacecraftBus_dict = {"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}
grid = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 1})

orbit_dict = {"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                               "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, 
                                        "ecc": 0.001, "inc": 0, "raan": 20, 
                                        "aop": 0, "ta": 120}
                               }

instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":20.0}, 
                                    "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 10, "angleWidth": 20 }, 
                                    "@id":"bs1", "@type":"Basic Sensor"}
# instrument_dict = {"orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":15}, 
#                                    "fieldOfViewGeometry": {"shape": "rectangular", "angleHeight": 15, "angleWidth": 25 }, 
#                                    "@id":"bs1", "@type":"Basic Sensor"}
sat = Spacecraft.from_dict({"orbitState":orbit_dict, "instrument":instrument_dict, "spacecraftBus":spacecraftBus_dict})
state_cart_file = out_dir+'/test_cov_cart_states.csv'
# execute propagator
j2_prop.execute(spacecraft=sat, out_file_cart=state_cart_file, duration=duration)   
# set output file path
out_file_access = out_dir+'/access.csv'

# make and run the coverage calculator
cov = NewGridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)

cov.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access)