""" The below script calculated specular coverage of CYGNSS satellite(s) over the CONUS.
    The CONUS is represented by a grid used by the USGS for conveying fire-danger information.

    Skyfield package is used to convert the TLEs to ECI coords at a specified epoch.
"""
import os, shutil
import propcov

from orbitpy.coveragecalculator import SpecularCoverage
from orbitpy.util import Spacecraft, OrbitState, SpacecraftBus, GroundStation
from orbitpy.propagator import PropagatorFactory
from orbitpy.grid import Grid
from orbitpy.eclipsefinder import EclipseFinder
from orbitpy.contactfinder import ContactFinder

from instrupy import Instrument

from skyfield.api import EarthSatellite, load, wgs84
from skyfield.framelib import itrs

import time

start_time = time.time()

############################################################################################
#                               Configuration
############################################################################################
# Set mission epoch (GREGORIAN UT1) and duration. Make sure the epoch is around the TLE epochs.
# The TLE epochs are close to and before the below date. 
year = 2020
month = 8
day = 1
hour = 0
minute = 0
second = 0

duration = 1 # days
step_size = 1 # propagation step size in seconds

# set grid
covGridFilePath = os.path.dirname(os.path.realpath(__file__)) + '/Grid_WLFP_Day_1_Aug_1_2020.csv' # path to the file containing the grid-data
grid = Grid.from_dict({"@type": "customGRID", "covGridFilePath": covGridFilePath, "@id": "usgsFD"})

# set ground stations
gs1 = GroundStation.from_dict({"@id":"HI", "name": "hawaii", "latitude": 19, "longitude": -155.65, "altitude": 0.367 })
gs2 = GroundStation.from_dict({"@id":"CHI", "name": "chile", "latitude": -33.13, "longitude": -70.67, "altitude": 0.7234 })
gs3 = GroundStation.from_dict({"@id":"AUS", "name": "australia", "latitude": -29.08, "longitude": 115.58, "altitude": 0.250 })

# set the diameter of the specular location (to be used for grid-based coverage)
specular_pnt_dia = 25 # km (Size of the area of influence around the specular point)
# cygnss instrument
# https://www.eoportal.org/satellite-missions/cygnss#mission-capabilities Says the swath is 1480km
cyg_instru = Instrument.from_dict({"@type":"Basic Sensor", "@id":"CygSen", \
                                "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}, \
                                "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":107.35 } \
                                })
cyg_bus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}})

# Create new working directory to store output
dir_path = os.path.dirname(os.path.realpath(__file__))
out_dir = os.path.join(dir_path, 'results')
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

############################################################################################
#                      Load TLEs and make Skyfield Satellite objects 
############################################################################################
# TLEs close to and before the simulation period of Aug 2020.

# To get latest TLE by Celestrak use the URL: celestrak.com/cgi-bin/TLE.pl?CATNR=40052
# Alternatively the entire list of GPS, Galelio, CYGNSS can be obtained from the urls: 
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=galileo&FORMAT=tle
#   *   https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle
# Obtain the TLEs at the same time.

gps_sats = load.tle_file(dir_path+'/GPS.txt')
galileo_sats = load.tle_file(dir_path+'/Galelio.txt')
#beidou_sats = load.tle_file(dir_path+'/Beidou.txt')

gnss_sats = gps_sats + galileo_sats #+ beidou_sats

#print(gnss_sats)
cygnss_sats = load.tle_file(dir_path+'/CYGNSS.txt')
#cygnss_sats = [cygnss_sats[1]] # select only one of the cgynss satellites as test
#print(cygnss_sats)

############################################################################################
#        Make propcov Spacecraft objectsand initialize file paths for storing results.
############################################################################################

# Get the satellite states at a common start date/time of simulation.
ts = load.timescale()
eph = ts.ut1(year, month, day, hour, minute, second) # mission epoch (Ut1)
print("\n Mission epoch in UTC is: ", eph.utc_jpl())

spc_gnss = [] # list of GNSS propcov.Spacecraft objects
gnss_state_fl = [] # list of GNSS propagation state data files

for sat in gnss_sats:
    print(sat)
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
    

spc_cygnss = [] # list of CYGNSS propcov.Spacecraft objects
cyg_state_fl = [] # list of CYGNSS propagation state data files
cyg_eclipse_fl = [] # list of CYGNSS eclipse data files
cyg_gs1_contact_fl = [] # List of CYGNSS contact files with Ground Station 1
cyg_gs2_contact_fl = [] # List of CYGNSS contact files with Ground Station 2
cyg_gs3_contact_fl = [] # List of CYGNSS contact files with Ground Station 3
out_file_specular = [] # list of coverage (specular points) files
out_file_grid_access = [] # list of coverage (grid) files
for sat in cygnss_sats:
    print(sat)
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
    # set the eclispe output file path
    cyg_eclipse_fl.append("/CYG" + str(sat.model.satnum) + "_eclipse.csv") # directory is specified later
    # set the ground station contact output file path
    cyg_gs1_contact_fl.append("/CYG" + str(sat.model.satnum) + "_gs1_contact.csv") # directory is specified later
    cyg_gs2_contact_fl.append("/CYG" + str(sat.model.satnum) + "_gs2_contact.csv") # directory is specified later
    cyg_gs3_contact_fl.append("/CYG" + str(sat.model.satnum) + "_gs3_contact.csv") # directory is specified later
    # set coverage output file path
    out_file_specular.append(out_dir + "/CYG" + str(sat.model.satnum) + "_specular_acc.csv")    
    out_file_grid_access.append(out_dir + "/CYG" + str(sat.model.satnum) + "_grid_acc.csv")
    
# ############################################################################################
#           Carry out Specular Coverage, eclpise & ground-station contact finders. 
#           Use the J2 propagator for the GNSS and CYGNSS satellite orbit propagation. 
# #############################################################################################
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

    # run the eclipse calculator
    x = EclipseFinder.execute(spc_cygnss[idx], out_dir, cyg_state_fl[idx], cyg_eclipse_fl[idx], EclipseFinder.OutType.INTERVAL)

    # run the ground station contact finder
    ContactFinder.execute(spc_cygnss[idx], gs1, out_dir, cyg_state_fl[idx], None, cyg_gs1_contact_fl[idx], ContactFinder.OutType.INTERVAL, 0)
    ContactFinder.execute(spc_cygnss[idx], gs2, out_dir, cyg_state_fl[idx], None, cyg_gs2_contact_fl[idx], ContactFinder.OutType.INTERVAL, 0)
    ContactFinder.execute(spc_cygnss[idx], gs3, out_dir, cyg_state_fl[idx], None, cyg_gs3_contact_fl[idx], ContactFinder.OutType.INTERVAL, 0)

    # run the coverage calculator
    spec_cov = SpecularCoverage(rx_spc=spc_cygnss[idx], rx_state_file=cyg_state_fl[idx],
                                tx_spc=spc_gnss, tx_state_file=gnss_state_fl,
                                grid=grid)
    spec_cov.execute(instru_id=None, mode_id=None, out_file_specular=out_file_specular[idx], specular_region_dia=specular_pnt_dia, out_file_grid_access=out_file_grid_access[idx], mid_access_only=True) # Only the mid-access times are retained.
    print(idx, " Execution time: ", time.time() - start_time, "seconds")

end_time = time.time()
print("Total execution time: ", end_time - start_time, "seconds")