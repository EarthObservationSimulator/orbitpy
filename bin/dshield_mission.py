import os, shutil
import numpy as np
import pandas as pd
import csv
import time

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.coveragecalculator import GridCoverage
from datametricscalculator import DataMetricsCalculator, AccessFileInfo
from orbitpy.eclipsefinder import EclipseFinder
from orbitpy.grid import Grid

"""
2020-03-01 12:00:00
3 satellites in 1 plane, both L+P (spaced by 120 degrees of true anomaly):
502.5 km altitude
89 degree inclination

(both circular orbits)

"""
# pointing options (roll-angles) as given by Emmanuel. Note that the options are to be indexed by 1.
pnt_opts = [-60.419,-59.993,-59.545,-59.073,-58.577,-58.055,-57.505,-56.925,-56.315,-55.671,-54.992,-54.276,-53.52,-52.722,-51.879,-50.988,-50.047,
            -49.052,-47.999,-46.886,-45.709,-44.463,-43.145,-41.751,-40.277,-38.718,-37.072,-35.334,-33.502,-31.573,-29.544,29.544,31.573,33.502,35.334,37.072,
            38.718,40.277,41.751,43.145,44.463,45.709,46.886,47.999,49.052,50.047,50.988,51.879,52.722,53.52,54.276,54.992,55.671,56.315,56.925,57.505,58.055,
            58.577,59.073,59.545,59.993,60.419]

def bins_from_pointing_options(pnt_opts, swath_width, altitude):
    """ Parse bins from pointing options for given swath-width, satellite altitude. Each bin gives the range of look-angles from the satellite
        that the sensor FOV shall span (for a specific pointing-option).
    
    :param pnt_opts: List of pointing options (look angles to the middle of the swath).
    :paramtype pnt_opts: list, float

    :param swath_width: Swath width in kilometers.
    :paramtype swath_width: float

    :param altitude: Altitude of the satellite in kilometers.
    :paramtype altitude: float

    :returns: List of lists, with each fundamental list specifying the range of look-angles (hence bin).
    :rtype: list, list, float

    """
    pass

def assign_pointing_bins(obsmetrics_fp, swath_width, spc_acc_fp):    

    spc_df = pd.read_csv(obsmetrics_fp, skiprows=[0,1,2,3], usecols=['time index', 'GP index', 'look angle [deg]'])

    x = spc_df['look angle [deg]'].values

    swath25km_pnt_bins = np.array([[-60.714,-60.298],
                                [-60.298,-59.86],
                                [-59.86,-59.4],
                                [-59.4,-58.915],
                                [-58.915,-58.405],
                                [-58.405,-57.868],
                                [-57.868,-57.303],
                                [-57.303,-56.707],
                                [-56.707,-56.078],
                                [-56.078,-55.416],
                                [-55.416,-54.718],
                                [-54.718,-53.98],
                                [-53.98,-53.202],
                                [-53.202,-52.38],
                                [-52.38,-51.512],
                                [-51.512,-50.595],
                                [-50.595,-49.625],
                                [-49.625,-48.6],
                                [-48.6,-47.515],
                                [-47.515,-46.368],
                                [-46.368,-45.154],
                                [-45.154,-43.87],
                                [-43.87,-42.512],
                                [-42.512,-41.075],
                                [-41.075,-39.556],
                                [-39.556,-37.951],
                                [-37.951,-36.256],
                                [-36.256,-34.468],
                                [-34.468,-32.584],
                                [-32.584,-30.602],
                                [-30.602,-28.519],
                                [28.519,30.602],
                                [30.602,32.584],
                                [32.584,34.468],
                                [34.468,36.256],
                                [36.256,37.951],
                                [37.951,39.556],
                                [39.556,41.075],
                                [41.075,42.512],
                                [42.512,43.87],
                                [43.87,45.154],
                                [45.154,46.368],
                                [46.368,47.515],
                                [47.515,48.6],
                                [48.6,49.625],
                                [49.625,50.595],
                                [50.595,51.512],
                                [51.512,52.38],
                                [52.38,53.202],
                                [53.202,53.98],
                                [53.98,54.718],
                                [54.718,55.416],
                                [55.416,56.078],
                                [56.078,56.707],
                                [56.707,57.303],
                                [57.303,57.868],
                                [57.868,58.405],
                                [58.405,58.915],
                                [58.915,59.4],
                                [59.4,59.86],
                                [59.86,60.298],
                                [60.298,60.714]])

    swath50km_pnt_bins = np.array([[-60.82935,-59.993],
                                    [-60.419,-59.545],
                                    [-59.993,-59.073],
                                    [-59.545,-58.577],
                                    [-59.073,-58.055],
                                    [-58.577,-57.505],
                                    [-58.055,-56.925],
                                    [-57.505,-56.315],
                                    [-56.925,-55.671],
                                    [-56.315,-54.992],
                                    [-55.671,-54.276],
                                    [-54.992,-53.52],
                                    [-54.276,-52.722],
                                    [-53.52,-51.879],
                                    [-52.722,-50.988],
                                    [-51.879,-50.047],
                                    [-50.988,-49.052],
                                    [-50.047,-47.999],
                                    [-49.052,-46.886],
                                    [-47.999,-45.709],
                                    [-46.886,-44.463],
                                    [-45.709,-43.145],
                                    [-44.463,-41.751],
                                    [-43.145,-40.277],
                                    [-41.751,-38.718],
                                    [-40.277,-37.072],
                                    [-38.718,-35.334],
                                    [-37.072,-33.502],
                                    [-35.334,-31.573],
                                    [-33.502,-29.544],
                                    [-31.573,-27.41],
                                    [27.41,31.573],
                                    [29.544,33.502],
                                    [31.573,35.334],
                                    [33.502,37.072],
                                    [35.334,38.718],
                                    [37.072,40.277],
                                    [38.718,41.751],
                                    [40.277,43.145],
                                    [41.751,44.463],
                                    [43.145,45.709],
                                    [44.463,46.886],
                                    [45.709,47.999],
                                    [46.886,49.052],
                                    [47.999,50.047],
                                    [49.052,50.988],
                                    [50.047,51.879],
                                    [50.988,52.722],
                                    [51.879,53.52],
                                    [52.722,54.276],
                                    [53.52,54.992],
                                    [54.276,55.671],
                                    [54.992,56.315],
                                    [55.671,56.925],
                                    [56.315,57.505],
                                    [56.925,58.055],
                                    [57.505,58.577],
                                    [58.055,59.073],
                                    [58.577,59.545],
                                    [59.073,59.993],
                                    [59.545,60.419],
                                    [59.993,60.82935]]
                                    )

    if swath_width == 25:
        swath_bins = swath25km_pnt_bins
    elif swath_width == 50:
        swath_bins = swath50km_pnt_bins
    else:
        raise RuntimeError('Unsupported swath width.')

    pnt_opt = []
    for indx in range(0, len(x)):
        # evaluate the pointing option(s) corresponding to the bin
        _po = []
        for k in range(0,len(swath_bins)):        
            if swath_bins[k][0] < x[indx] <= swath_bins[k][1]:
                _po.append(k+1) # (k+1) because pointing options index begins from 1
        pnt_opt.append(_po)

    
    spc_df =  pd.concat([spc_df, pd.DataFrame({'pOpts': pnt_opt})], axis=1) 
    spc_df = spc_df.loc[spc_df['pOpts'].apply(len)>0] 

    with open(spc_acc_fp, 'w') as f2:
                spc_df.to_csv(f2, index=False, header=True, line_terminator='\n', sep="\t", quoting=csv.QUOTE_NONE, quotechar="", escapechar="") # , quoting=csv.QUOTE_NONE, quotechar="",  escapechar="\\"
    
############################ Start mission simulation ############################

start_time = time.process_time()    

wdir = os.path.dirname(os.path.realpath(__file__)) + "/../examples/20210909_500kmSARConstellation/"

epoch_dict = {"dateType":"GREGORIAN_UTC", "year":2020, "month":1, "day":1, "hour":12, "minute":0, "second":0}
epoch = OrbitState.date_from_dict(epoch_dict)
epoch_JDUt1 = epoch.GetJulianDate()

sat = Spacecraft.from_dict({"spacecraftBus":{"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                                            },
                             "orbitState": {"date": epoch_dict,
                                            "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.1369999999997162, "ecc": 0.0, "inc": 89, "raan": 0, "aop": 0, "ta": 120}
                                        },
                             "instrument": { "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":45},
                                            "fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight":5, "angleWidth": 10 },
                                            "maneuver":{"maneuverType": "Double_Roll_Only", "A_rollMin":30, "A_rollMax":60, "B_rollMin":-60, "B_rollMax":-30},
                                            "@id":"sar", "name": "L-band SAR", "@type":"Basic Sensor"}
                                    })

grid = Grid.from_dict({"@type": "customGrid", "covGridFilePath": wdir+"covGrid.csv"})

propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1})


instru_id = sat.instrument[0]._id
mode_id = sat.instrument[0].mode[0]._id

sat_dir = wdir + '/sat2/'

if os.path.exists(sat_dir):
    shutil.rmtree(sat_dir)
os.makedirs(sat_dir)

for k in range(0,4):

    print('processing at {} hrs'.format(k*6))

    duration = 0.25
    sim_start_date = OrbitState.date_from_dict({"dateType":"JULIAN_DATE_UT1", "jd": epoch_JDUt1 + k*duration})


    state_cart_file = sat_dir + 'state_cartesian_' + str(6*k) + 'hrs.csv'
    state_kep_file = sat_dir + 'state_keplerian_' + str(6*k) + 'hrs.csv'

    out_info = []
    
    print("start propagation")
    x = propagator.execute(sat, sim_start_date, state_cart_file, state_kep_file, duration)
    out_info.append(x)     
    print('finished propagation, time until now: {}s'.format(time.process_time() - start_time))
    
    
    print("start eclipse finder")
    eclipse_filename = 'eclipse_' + str(6*k) + 'hrs.csv'
    x = EclipseFinder.execute(sat, sat_dir, state_cart_file, eclipse_filename, EclipseFinder.OutType.INTERVAL)
    out_info.append(x) 
    print('finished eclipse finder, time until now: {}s'.format(time.process_time() - start_time))

    
    print("start coverage")
    acc_fl = sat_dir + 'access_instru_sar_' + str(6*k) + 'hrs.csv'
    cov_calc = GridCoverage(grid=grid, spacecraft=sat, state_cart_file=state_cart_file)
    x = cov_calc.execute(instru_id=instru_id, mode_id=mode_id, use_field_of_regard=True, out_file_access=acc_fl, filter_mid_acc=True)
    out_info.append(x)     
    print('finished coverage, time until now: {}s'.format(time.process_time() - start_time))

    print("start datametrics")
    dm_file = sat_dir + 'datametrics_instru_sar_' + str(6*k) + 'hrs.csv'
    dm_calc = DataMetricsCalculator(spacecraft=sat, state_cart_file=state_cart_file, access_file_info=AccessFileInfo(instru_id, mode_id, acc_fl))                    
    x = dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru_id, mode_id=mode_id)
    out_info.append(x)
    print('finished datametrics, time until now: {}s'.format(time.process_time() - start_time))

    print("start binning.")
    # assign pointing bins
    lsar_acc_fp = sat_dir + 'lsar_dshield_result_' + str(6*k) + 'hrs.csv'
    psar_acc_fp = sat_dir + 'psar_dshield_result_' + str(6*k) + 'hrs.csv'

    assign_pointing_bins(dm_file, 25, lsar_acc_fp) 
    assign_pointing_bins(dm_file, 50, psar_acc_fp) 
    print('stop binning, time until now: {}s'.format(time.process_time() - start_time))
    


