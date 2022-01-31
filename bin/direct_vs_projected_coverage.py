""" In this script the performance of the `DirectSphericalPIP` (which uses `propcov.DSPIPCustomSensor`) and 
    the `ProjectedPIP` (which uses the `propcov.GMATCustomSensor`) coverage methods are compared. 
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
                             "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation":2.5, "yRotation":-7.5, "zRotation":10},
                                            "fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight":50, "angleWidth": 50},
                                            "@type":"Basic Sensor"}
                                    })
'''
sat = Spacecraft.from_dict({"spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                                            },
                             "orbitState": {"date": {"@type":"GREGORIAN_UTC", "year":2019, "month":12, "day":31, "hour":18, "minute":32, "second":15.461952},
                                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7060.468, "ecc": 0.00016890, "inc": 98.1228, "raan": 9.7929, "aop": 109.2526, "ta": 250.8855}
                                        },
                             "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "XYZ", "xRotation":2.5, "yRotation":-7.5, "zRotation":10},
                                            "fieldOfViewGeometry": {"shape": "CUSTOM", "customConeAnglesVector": [25,30,50,35,25], "customClockAnglesVector": [0,90,180,270,0]},
                                            "@type":"Basic Sensor"}
                                    })
'''

duration = [5, 10, 20] # mins
grid_res = [1, 0.5, 0.25, 0.1, 0.05] # deg
#duration = [5] # mins
#grid_res = [0.25] # deg

for d in duration:

    propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1})
    _dur = (1.0/24)*(d/60.0)

    sat_dir = wdir + '/sat/'

    if os.path.exists(sat_dir):
        shutil.rmtree(sat_dir)
    os.makedirs(sat_dir)

    # do propagation
    sim_start_date = OrbitState.date_from_dict({"@type":"JULIAN_DATE_UT1", "jd": epoch_JDUt1})
    state_cart_file = sat_dir + 'state_cartesian_'+ str(d) + 'mins.csv'
    state_kep_file = sat_dir + 'state_keplerian_'+ str(d) + 'mins.csv'

    print("start propagation")
    propagator.execute(sat, sim_start_date, state_cart_file, state_kep_file, _dur)
    print('finished propagation')

    for g in grid_res:

        print('duration set to {} mins'.format(d))
        print('grid resolution set to {} deg'.format(g))

        grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":90, "latLower":-90, "lonUpper":180, "lonLower":-180, "gridRes": g})
        grid.write_to_file(wdir + 'grid_' + str(d) + 'mins_' + str(g) + 'deg.csv')    
        
        print("start DirectSphericalPIP coverage")
        start_time = time.process_time()  
        acc_fl = sat_dir + 'access_' + str(d) + 'mins_' + str(g) + 'deg.csv'
        cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
        x = cov_calc.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=acc_fl, filter_mid_acc=False, method='DirectSphericalPIP')
        print('finished DirectSphericalPIP coverage, time taken: {}s'.format(time.process_time() - start_time))

        print("start ProjectedPIP coverage")
        start_time = time.process_time()  
        acc_fl = sat_dir + 'access_' + str(d) + 'mins_' + str(g) + 'deg.csv'
        cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
        x = cov_calc.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=acc_fl, filter_mid_acc=False, method='ProjectedPIP')
        print('finished ProjectedPIP coverage, time taken: {}s'.format(time.process_time() - start_time))
