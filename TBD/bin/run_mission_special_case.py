import argparse
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
import time
import pandas as pd 
import numpy as np

def assign_pointing_bins(obsmetrics_fp, swath_width, spc_acc_fp):    

    spc_df = pd.read_csv(obsmetrics_fp, skiprows=[0,1,2], usecols=['observationTimeIndex','regi', 'gpi', 'Look angle [deg]'])

    x = spc_df['Look angle [deg]'].values

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
    else:
        swath_bins = swath50km_pnt_bins

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
                spc_df.to_csv(f2, index=False, header=True, line_terminator='\n') 

def main(user_dir):
    ''' This module is executes mission with sidelooking instruments modeled as Basic Sensor type. 
        It also appends an additional column of "pointing-options" in the access files. 
        This corresponding to the pointing (within the input Field-Of-Regard) at which the access 
        over a ground-point shall occur.
    '''
    start_time = time.process_time()
    # Read in mssion specifications from user config file, coverage grid file (optional) 
    # and the ground stations specifications file in the user directory.
    usf = user_dir + 'MissionSpecs.json'
    with open(usf, 'r') as orbit_specs_file:
            miss_specs = util.FileUtilityFunctions.from_json(orbit_specs_file)      

    # Preprocess
    print(".......Preprocessing user config file.......")
    pi = preprocess.PreProcess(miss_specs, user_dir) # generates grid if-needed, calculates propagation 
                                                    # and coverage parameters, enumerates orbits, etc.
    prop_cov_param = pi.generate_prop_cov_param()   
    print(".......Done.......")

    # Run orbit propagation and coverage for each of the satellties (orbits) in the constellation
    for orb_indx in range(0,len(prop_cov_param)):
        pcp = prop_cov_param[orb_indx]
        pcp.purely_sidelook = True # SPECIAL case in which the sensor (modeled as Basic Sensor) is sidelooking
        opc = orbitpropcov.OrbitPropCov(pcp)
        print(".......Running Orbit Propagation and Coverage for satellite.......", pcp.sat_id)
        opc.run()        
        print(".......Done.......")

    comm_dir = pi.comm_dir
    gnd_stn_fl = pi.gnd_stn_fl

    sat_dirs =  glob.glob(user_dir+'sat*/')
    sat_state_fls =  glob.glob(user_dir+'sat*/state')
    
    # Compute satellite-to-satellite contacts
    print(".......Computing satellite-to-satellite contact periods.......")
    t1 = time.process_time()    
    opaque_atmos_height_km = 30
    inter_sat_comm = communications.InterSatelliteComm(sat_state_fls, comm_dir, opaque_atmos_height_km)
    inter_sat_comm.compute_all_contacts() 
    t2 = time.process_time()       
    print(".......DONE.......time taken (s): ", t2-t1)

    # Compute satellite-to-ground-station contacts    
    t1 = time.process_time() 
    if gnd_stn_fl is None:
        print("No ground-stations specified, skip computation of graound-station contacts.")
    else:
        print(".......Computing satellite-to-ground-station contact periods.......")
        gnd_stn_comm = communications.GroundStationComm(sat_dirs, gnd_stn_fl)
        gnd_stn_comm.compute_all_contacts()
        t2 = time.process_time()   
        print(".......DONE.......time taken (s): ", t2-t1)
    
    # Compute observational data-metrics
    print(".......Computing observational data metrics.......")
    t1 = time.process_time()
     
    if "instrument" in miss_specs:
        instru_specs = miss_specs['instrument']
    elif "satellite" in miss_specs:
        instru_specs = []
        for sat in miss_specs["satellite"]:
            instru_specs.extend(sat["instrument"])

    obs = obsdatametrics.ObsDataMetrics(pi.sats)
    obs.compute_all_obs_metrics()      
    t2 = time.process_time()      
    print(".......DONE.......time taken (s): ", t2-t1)

    #assign_pointing_bins(obsmetrics_fp, swath_width, spc_acc_fp)    
    
    end_time = time.process_time()
    print("Total time taken (s):", end_time - start_time)
    



class readable_dir(argparse.Action):
    """Defines a custom argparse Action to identify a readable directory."""
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError(
                '{0} is not a valid path'.format(prospective_dir)
            )
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(
                '{0} is not a readable dir'.format(prospective_dir)
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run Mission'
    )
    parser.add_argument(
        'user_dir',
        action=readable_dir,
        help="Directory with user config JSON file, and also to write the results."
    )
    args = parser.parse_args()
    main(args.user_dir)

