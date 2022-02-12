import os, shutil
import time
import json

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.coveragecalculator import PointingOptionsWithGridCoverage
from datametricscalculator import DataMetricsCalculator, AccessFileInfo
from orbitpy.grid import Grid
import orbitpy

start_time = time.process_time()    

wdir = os.path.dirname(os.path.realpath(__file__)) + "/../examples/nos_oceans_landsat_seahawk_1/"

# define mission epoch
mission_epoch_dict = {"@type":"GREGORIAN_UTC", "year":2018, "month":7, "day":1, "hour":0, "minute":0, "second":0}
mission_epoch = OrbitState.date_from_dict(mission_epoch_dict)
mission_epoch_JDUt1 = mission_epoch.GetJulianDate()

# define duration
duration = 31*5

# load assets
with open(wdir +'/assets.json', 'r') as asset_specs:
  assets = json.load(asset_specs)

spacecraft = []
for _asset in assets:
    spacecraft.append(Spacecraft.from_dict(_asset))

# define grid
gridRes = orbitpy.grid.compute_grid_res(spacecraft, 0.25)
grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":42, "latLower":35, "lonUpper":-70, "lonLower":-80, "gridRes": gridRes})
grid.write_to_file(wdir + 'grid.csv' )

# define propagator
#time_step = orbitpy.propagator.compute_time_step(spacecraft, 0.25)
time_step = 5
propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": time_step})

# run coverage and datametrics calculations for each asset
for spc in spacecraft:
    
    spc_dir = wdir + str(spc._id)

    if os.path.exists(spc_dir):
        shutil.rmtree(spc_dir)
    os.makedirs(spc_dir)

    spc_state_cart_file = spc_dir + '/state_cartesian.csv'
    spc_state_kep_file = spc_dir + '/state_keplerian.csv'

    propagator.execute(spc, mission_epoch, spc_state_cart_file, spc_state_kep_file, duration)

    for instru_idx, instru in enumerate(spc.instrument):
        for mode_idx, mode in enumerate(instru.mode):

            acc_fl = spc_dir + '/access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
            cov_calc = PointingOptionsWithGridCoverage(grid=grid, spacecraft=spc, state_cart_file=spc_state_cart_file)
            cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl, filter_mid_acc=True)

            dm_file = spc_dir + '/datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
            dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=spc_state_cart_file, access_file_info=AccessFileInfo(instru._id, mode._id, acc_fl))                 
            dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._id, mode_id=mode._id)

print('time taken: {}s'.format(time.process_time() - start_time))