""" Below script simulates Landsat8, SeaHawk1 and SeaHawk2 (hypothetical) satellites.
    The Landsat8 and SeaHawk1 orbital specs are present in the `landsat8.xml` and `seahawk1.xml` files respectively, obtained from NORAD database.
    SeaHawk2 is an hypothetical satellite placed at 180 deg TA offset from SeaHawk1, in a similar constellation configuration as Sentinel 1A,1B.

    The specifications of the spacecraft and their instruments are loaded from the `assets.json` file. In case of Landsat8, the OLI
    and TIRS instruments are modeled. For SeaHawk1,2 , HawkEye is modelled. (Only 1 spectral band is modeled in all the instruments). 
    Landsat8 has no maneuverability, while the SeaHawks are modeled with five modes, with each mode having a different pointing option.
    
    The pointing options of SeaHawk span from -45.2 deg to +45.2 deg. Note that the pointing options are structured so that there is no
    overlap or gap between the swaths. The region of interest is specified by lat/lon bounds (lat: 35N to 42N, lon: 70W to 80W).
    (The reason for including the pointing-options in separate modes was to have results for each of the pointing-options in separate files.
     The same results can be obtained by including all the pointing-options under a single mode.)
    
    Since the instruments have a narrow FOV in the along-track direction, and if these FOV were considered, 
    the coverage calculations would need to done with very small propagation step-size. Hence a sceneFOV is defined which has a larger 
    along-track dimension (cross-track dimension is same as the instrument FOV). The sceneFOV (= FOR in this case) is considered for coverage calculations.
    The middle of the registered access events calculated from the sceneFOV are filtered through by setting the ``mid_access_only`` flag to ``True``.

    Note that the orbital elements of the spacecraft are at different date/time from the mission start date. The spacecrafts are first
    propagated to the mission start date and then the propagation is done at the (propagation) step-size. The (propagation) step-size 
    is specified to be 5 seconds, while in case of grid, the grid-resolution is calculated for a grid-resolution factor of 0.25. 
    
    References
    ------------

    [1] TIRS, OLI modeling: https://github.com/EarthObservationSimulator/instrupy/blob/master/examples/passive_scanner_model/Landsat_8_TIRS_and_OLI.pdf
    [2] HawkEye modeling: Presentations available in  https://uncw.edu/socon/hawkeye.html

    Execute
    --------
    Execute the script from the main repo directory using the command: `python examples/landsat_seahawk_1/landsat_seahawk_1.py`
    
    Output
    ---------

    Following are the files after script execution (mission duration = 2days).

    .. code:: bash

        │   assets.json (input: spacecraft/instrument specifications)
        │   grid.csv (output: lat/lon of grid-points)
        │   landsat8.xml (Landsat-8 NORAD orbit elements)
        │   nos_oceans_landsat_seahawk_1.py
        │   seahawk1.xml (SeaHawk-1 NORAD orbit elements)
        │
        ├───landsat
        │       access_instru0_mode0.csv (coverage data for TIRS)
        │       access_instru1_mode0.csv (coverage data for OLI)
        │       datametrics_instru0_mode0.csv (datametrics for TIRS)
        │       datametrics_instru1_mode0.csv (datametrics for OLI)
        │       state_cartesian.csv (Cartesian ECI orbit data)
        │       state_keplerian.csv (Keplerian ECI orbit data)
        │
        ├───seahawk1
        │       access_instru0_mode0.csv (coverage data for HawkEye, pointing = 0 deg roll)
        │       access_instru0_mode1.csv (pointing = +22.6 deg roll)
        │       access_instru0_mode2.csv (pointing = +45.2 deg roll)
        │       access_instru0_mode3.csv (pointing = -22.6 deg roll)
        │       access_instru0_mode4.csv (pointing = -45.2 deg roll)
        │       datametrics_instru0_mode0.csv (datametrics for HawkEye, pointing = 0 deg roll)
        │       datametrics_instru0_mode1.csv (pointing = +22.6 deg roll)
        │       datametrics_instru0_mode2.csv (pointing = +45.2 deg roll)
        │       datametrics_instru0_mode3.csv (pointing = -22.6 deg roll)
        │       datametrics_instru0_mode4.csv (pointing = -45.2 deg roll)
        │       state_cartesian.csv
        │       state_keplerian.csv
        │
        └───seahawk2
                access_instru0_mode0.csv
                access_instru0_mode1.csv
                access_instru0_mode2.csv
                access_instru0_mode3.csv
                access_instru0_mode4.csv
                datametrics_instru0_mode0.csv
                datametrics_instru0_mode1.csv
                datametrics_instru0_mode2.csv
                datametrics_instru0_mode3.csv
                datametrics_instru0_mode4.csv
                state_cartesian.csv
                state_keplerian.csv

"""
import os, shutil
import time
import json

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import J2AnalyticalPropagator
from orbitpy.coveragecalculator import PointingOptionsWithGridCoverage
from orbitpy.datametricscalculator import DataMetricsCalculator, AccessFileInfo
from orbitpy.grid import Grid
import orbitpy

start_time = time.process_time()    

wdir = os.path.dirname(os.path.realpath(__file__)) + "/"

# define mission epoch
mission_epoch_dict = {"@type":"GREGORIAN_UTC", "year":2018, "month":7, "day":1, "hour":0, "minute":0, "second":0}
mission_epoch = OrbitState.date_from_dict(mission_epoch_dict)
mission_epoch_JDUt1 = mission_epoch.GetJulianDate()

# define duration [days]
duration = 2

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
#step_size = orbitpy.propagator.compute_step_size(spacecraft, 0.25) # compute appropriate step-size for a propgation time-resolution factor of 0.25.
step_size = 5
propagator = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": step_size})

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
            cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl, mid_access_only=True)

            dm_file = spc_dir + '/datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
            dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=spc_state_cart_file, access_file_info=AccessFileInfo(instru._id, mode._id, acc_fl))                 
            dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._id, mode_id=mode._id)

print('time taken: {}s'.format(time.process_time() - start_time))