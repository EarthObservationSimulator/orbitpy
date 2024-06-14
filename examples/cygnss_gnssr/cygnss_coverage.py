import os, shutil
import pandas as pd
import propcov

from orbitpy.coveragecalculator import SpecularCoverage
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus
from orbitpy.propagator import PropagatorFactory
from orbitpy.grid import Grid

from instrupy import Instrument

from skyfield.api import load

######## User Configuration ########
# Set mission epoch (GREGORIAN UT1) and duration. Make sure the epoch is around the TLE epochs.
year = 2022
month = 12
day = 5
hour = 12
minute = 0
second = 0

duration = 0.25 # days
step_size = 30 # propagation step size in seconds

# set grid
grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":35, "latLower":33, "lonUpper":-76, "lonLower":-78, "gridRes": 0.1})
# set the diameter of the specular location (to be used for grid-based coverage)
specular_pnt_dia = 50 # km
# cygnss instrument
# https://www.eoportal.org/satellite-missions/cygnss#mission-capabilities Says the swath is 1480km
cyg_instru = Instrument.from_dict({"@type":"Basic Sensor", "@id":"CygSen", \
                                "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":107.35 } \
                                })
cyg_bus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}})

# Create new working directory to store output
dir_path = os.path.dirname(os.path.realpath(__file__))
out_dir = os.path.join(dir_path, 'temp')
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

######## Load TLEs and make Skyfield Satellite objects ########

# To get latest TLE by Celestrak use the URL: celestrak.com/cgi-bin/TLE.pl?CATNR=40052
# Alternatively the entire list of GPS, Galelio, CYGNSS can be obtained from the urls: 
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=galileo&FORMAT=tle
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle
# Obtain the TLEs at the same time.

gps_sats = load.tle_file(dir_path+'/GPS.txt')
galileo_sats = load.tle_file(dir_path+'/Galelio.txt')
beidou_sats = load.tle_file(dir_path+'/Beidou.txt')

gnss_sats = gps_sats + galileo_sats + beidou_sats
#print(gnss_sats)
cygnss_sats = load.tle_file(dir_path+'/CYGNSS.txt')
#print(cygnss_sats)

######## Make propcov Spacecraft objects ########

# Get the satellite states at a common start date/time of simulation.
ts = load.timescale()
eph = ts.ut1(year, month, day, hour, minute, second) # mission epoch (Ut1)
print("\n Mission epoch in UTC is: ", eph.utc_jpl())

spc_gnss = [] # list of GPS Spacecraft objects
gnss_state_fl = [] # list of GPS propagation state data files

for sat in gnss_sats:
    geocentric = sat.at(eph) # in GCRS (ECI) coordinates. GCRS ~ J2000, and is treated as the same in OrbitPy
    pos = geocentric.position.km
    vel = geocentric.velocity.km_per_s

    orbit = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":year, "month":month, "day":day, "hour":hour, "minute":minute, "second":second},
                                       "state":{"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", 
                                                 "x": pos[0], "y": pos[1], "z": pos[2], 
                                                 "vx": vel[0], "vy": vel[1], "vz": vel[2]}
                                       })

    spc_gnss.append(Spacecraft(orbitState=orbit, _id= str(sat.model.satnum)))
    gnss_state_fl.append(out_dir + "/GNSS" + str(sat.model.satnum) + "_state.csv")

    #print(Spacecraft(orbitState=orbit))

spc_cygnss = []
cyg_state_fl = [] # list of CYGNSS propagation state data files
out_file_specular = [] # list of coverage (specular points) files
out_file_grid_access = [] # list of coverage (grid) files
for sat in cygnss_sats:
    geocentric = sat.at(eph) # in GCRS (ECI) coordinates. GCRS ~ J2000, and is treated as the same in OrbitPy
    pos = geocentric.position.km
    vel = geocentric.velocity.km_per_s

    orbit = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":year, "month":month, "day":day, "hour":hour, "minute":minute, "second":second},
                                       "state":{"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", 
                                                 "x": pos[0], "y": pos[1], "z": pos[2], 
                                                 "vx": vel[0], "vy": vel[1], "vz": vel[2]}
                                       })

    spc_cygnss.append(Spacecraft(orbitState=orbit, instrument=cyg_instru, spacecraftBus=cyg_bus))
    cyg_state_fl.append(out_dir + "/CYG" + str(sat.model.satnum) + "_state.csv")
    # set coverage output file path
    out_file_specular.append(out_dir + "/CYG" + str(sat.model.satnum) + "_specular_acc.csv")
    out_file_grid_access.append(out_dir + "/CYG" + str(sat.model.satnum) + "_grid_acc.csv")
    #print(Spacecraft(orbitState=orbit))

######## Carry out Specular Coverage with J2 propagator ########
# make propagator
factory = PropagatorFactory()
j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": step_size})

# execute propagator
start_date = propcov.AbsoluteDate.fromGregorianDate(year, month, day, hour, minute, second)

for idx, spc in enumerate(spc_gnss):
    j2_prop.execute(spacecraft=spc_gnss[idx], start_date=start_date, out_file_cart=gnss_state_fl[idx], duration=duration)
for idx, spc in enumerate(spc_cygnss):
    j2_prop.execute(spacecraft=spc_cygnss[idx], start_date=start_date, out_file_cart=cyg_state_fl[idx], duration=duration)

# iterate over the entire CYGNSS constellation
for idx, spc in enumerate(spc_cygnss):

    # run the coverage calculator
    spec_cov = SpecularCoverage(rx_spc=spc_cygnss[idx], rx_state_file=cyg_state_fl[idx],
                                tx_spc=spc_gnss, tx_state_file=gnss_state_fl,
                                grid=grid)
    spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular[idx], specular_region_dia=specular_pnt_dia, out_file_grid_access=out_file_grid_access[idx]) # the 1st instrument and the 1st mode is selected.

