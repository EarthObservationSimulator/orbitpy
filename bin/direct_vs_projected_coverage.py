""" In this script the performance of the `DirectSphericalPointInPolygon` (which uses `propcov.DSPIPCustomSensor`) and 
    the `ProjectedSphericalPointInPolygon` (which uses the `propcov.GMATCustomSensor`) coverage methods are compared. 
"""
import time
import os, shutil

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.coveragecalculator import GridCoverage
from orbitpy.grid import Grid



wdir = os.path.dirname(os.path.realpath(__file__)) + "/../examples/direct_vs_projected_coverage/"

epoch_dict = {"@type":"GREGORIAN_UTC", "year":2020, "month":1, "day":1, "hour":12, "minute":0, "second":0}
epoch = OrbitState.date_from_dict(epoch_dict)
epoch_JDUt1 = epoch.GetJulianDate()

sat = Spacecraft.from_dict({"spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                                            },
                             "orbitState": {"date": {"@type":"GREGORIAN_UTC", "year":2019, "month":12, "day":31, "hour":18, "minute":32, "second":15.461952},
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7060.468, "ecc": 0.00016890, "inc": 98.1228, "raan": 9.7929, "aop": 109.2526, "ta": 250.8855}
                                        },
                             "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"},
                                            "fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight":50, "angleWidth": 50},
                                            "@type":"Basic Sensor"}
                                    })

propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1})
duration = 1.0/24*(5.0/60)

sat_dir = wdir + '/sat/'

if os.path.exists(sat_dir):
    shutil.rmtree(sat_dir)
os.makedirs(sat_dir)

# do propagation
sim_start_date = OrbitState.date_from_dict({"@type":"JULIAN_DATE_UT1", "jd": epoch_JDUt1})
state_cart_file = sat_dir + 'state_cartesian.csv'
state_kep_file = sat_dir + 'state_keplerian.csv'

print("start propagation")
propagator.execute(sat, sim_start_date, state_cart_file, state_kep_file, duration)
print('finished propagation')

for k in range(10,11):

    print('grid resolution set to {} deg'.format(1/k))

    grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": 1/k})
    grid.write_to_file(wdir + 'grid_' + str(k) + '.csv')    
    
    print("start DirectSphericalPointInPolygon coverage")
    start_time = time.process_time()  
    acc_fl = sat_dir + 'access_' + str(k) + '.csv'
    cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
    x = cov_calc.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=acc_fl, filter_mid_acc=False, method='DirectSphericalPointInPolygon')
    print('finished DirectSphericalPointInPolygon coverage, time taken: {}s'.format(time.process_time() - start_time))


    print("start ProjectedSphericalPointInPolygon coverage")
    start_time = time.process_time()  
    acc_fl = sat_dir + 'access_' + str(k) + '.csv'
    cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
    x = cov_calc.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=acc_fl, filter_mid_acc=False, method='ProjectedSphericalPointInPolygon')
    print('finished ProjectedSphericalPointInPolygon coverage, time taken: {}s'.format(time.process_time() - start_time))
