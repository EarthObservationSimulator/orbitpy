import os, shutil
import numpy as np
import pandas as pd
import csv
import time

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.coveragecalculator import GridCoverage
from orbitpy.grid import Grid


"""
Find SMAP coverage over the mission-interval. Approximate sensor-FOV geometry specification for SMAP.

The path to the working directory and the grid file needs to be provided.

Epoch: 2020-03-01 12:00:00, Intervals 6hrs, 12hrs, 18hrs, 24hrs.

Use in EXCEL: =SUM(IF(FREQUENCY(B6:B10, B6:B10)>0,1)) to count # unique GPs in an access interval

"""

start_time = time.process_time()    

# Provide the path to the grid file ('covGrid.csv') appropriately.
wdir = os.path.dirname(os.path.realpath(__file__)) + "/../../../wdir/orbitpy_smap/"
grid = Grid.from_dict({"@type": "customGrid", "covGridFilePath": wdir+"covGrid.csv"})


epoch_dict = {"@type":"GREGORIAN_UT1", "year":2020, "month":1, "day":1, "hour":12, "minute":0, "second":0}
epoch = OrbitState.date_from_dict(epoch_dict)
epoch_JDUt1 = epoch.GetJulianDate()

sat = Spacecraft.from_dict({"spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                                            },
                             "orbitState": {"date": {"@type":"GREGORIAN_UT1", "year":2019, "month":12, "day":31, "hour":18, "minute":32, "second":15.461952},
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7060.468, "ecc": 0.00016890, "inc": 98.1228, "raan": 9.7929, "aop": 109.2526, "ta": 250.8855}
                                        },
                             "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"},
                                            "fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight":5, "angleWidth": 70.871565275094700 },
                                            "@id":"smap", "name": "SMAP", "@type":"Basic Sensor"}
                                    })


propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1})

sat_dir = wdir + '/smap/'

if os.path.exists(sat_dir):
    shutil.rmtree(sat_dir)
os.makedirs(sat_dir)

for k in range(0,4):

    print('processing at {} hrs'.format(k*6))

    duration = 0.25
    sim_start_date = OrbitState.date_from_dict({"@type":"JULIAN_DATE_UT1", "jd": epoch_JDUt1 + k*duration})


    state_cart_file = sat_dir + 'state_cartesian_' + str(6*k) + 'hrs.csv'
    state_kep_file = sat_dir + 'state_keplerian_' + str(6*k) + 'hrs.csv'

    out_info = []
    
    print("start propagation")
    x = propagator.execute(sat, sim_start_date, state_cart_file, state_kep_file, duration)
    out_info.append(x)     
    print('finished propagation, time until now: {}s'.format(time.process_time() - start_time))
    
    print("start coverage")
    acc_fl = sat_dir + 'access_instru_sar_' + str(6*k) + 'hrs.csv'
    cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
    x = cov_calc.execute(instru_id='smap', mode_id=None, use_field_of_regard=False, out_file_access=acc_fl, mid_access_only=True)
    out_info.append(x)     
    print('finished coverage, time until now: {}s'.format(time.process_time() - start_time))
