import argparse
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, util
from instrupy.public_library import Instrument     

def main(user_dir):
    """
        example usage: python bin/run_mission.py examples/example1/
    """
  
    # Read in mssion specifications from user config file, coverage grid file (optional) 
    # and the ground stations specifications file in the user directory.
    usf = user_dir + 'MissionSpecs.json'
    with open(usf, 'r') as orbit_specs_file:
            miss_specs = util.FileUtilityFunctions.from_json(orbit_specs_file)  
    
    DEBUG = 0
    if DEBUG:
        state_dir = user_dir + 'state/'
        access_dir = user_dir + 'access/'
        comm_dir = user_dir + 'comm/'
        gndstn_dir = user_dir + 'gndstn/'
        cov_grid_fl = user_dir + 'covGrid'
        gnd_stn_fl = user_dir + str(miss_specs['groundStations']['gndStnFn'])

    else:
        # Preprocess
        pi = preprocess.PreProcess(miss_specs, user_dir) # generates grid if-needed, calculates propagation 
                                                        # and coverage parameters, enumerates orbits, etc.
        prop_cov_param = pi.generate_prop_cov_param()   

        # Run orbit propagation and coverage for each of the satellties (orbits) in the constellation
        for orb_indx in range(0,len(prop_cov_param)):
            pcp = prop_cov_param[orb_indx]
            opc = orbitpropcov.OrbitPropCov(pcp)
            print(".......Running Orbit Propagation and Coverage for satellite.......", pcp.sat_id)
            opc.run()        
            print(".......Done.......")

        state_dir = pi.state_dir
        access_dir = pi.access_dir    
        comm_dir = pi.comm_dir
        gndstn_dir = pi.gndstn_dir
        gnd_stn_fl = pi.gnd_stn_fl
        cov_grid_fl = pi.cov_grid_fl

        # correct access files for purely side-looking instruments if necessary
        if(pi.instru.purely_side_look):
            print(".......Correcting access files......")
            orbitpropcov.OrbitPropCov.correct_access_files(access_dir, pi.time_step)
            print(".......Done.......")

        # Compute satellite-to-satellite contacts
        print(".......Computing satellite-to-satellite contact periods.......")
        opaque_atmos_height_km = 30
        inter_sat_comm = communications.InterSatelliteComm(user_dir, state_dir, comm_dir, opaque_atmos_height_km)
        inter_sat_comm.compute_all_contacts()    
        print(".......Done.......")

        # Compute satellite-to-ground-station contacts
        print(".......Computing satellite-to-ground-station contact periods.......")
        gnd_stn_comm = communications.GroundStationComm(user_dir, state_dir, gndstn_dir, gnd_stn_fl)
        gnd_stn_comm.compute_all_contacts()
        print(".......Done.......")

    
    # Compute observational data-metrics
    print("Computing observational data metrics") 

    obsmetrics_dir = user_dir + 'obsMetrics/'
    if os.path.exists(obsmetrics_dir):
        shutil.rmtree(obsmetrics_dir)
    os.makedirs(obsmetrics_dir)

    try:
        _path, _dirs, _AccessInfo_files = next(os.walk(access_dir))
    except StopIteration:
        pass

    instru_specs = miss_specs['instrument']

    indx = 0
    level0dataMetrics_filepath = []
     # process each access file separately
    for AccessInfo_file in _AccessInfo_files:

        x = Instrument.from_json(instru_specs)

        accessInfo_fl = os.path.join(access_dir, AccessInfo_file)

        # Extract the satellite index as written in the Access filename. 
        temp_AccessInfo_filepath = accessInfo_fl.split(os.path.sep)
        temp_last_index = len(temp_AccessInfo_filepath) - 1
        satIndx = temp_AccessInfo_filepath[temp_last_index].split('_')[0]
        sat_state_filename = str(satIndx)
        sat_state_fl = os.path.join(state_dir, sat_state_filename)

        obsmetrics_filename = str(satIndx) + '_level0_data_metrics.csv'
        level0dataMetrics_filepath.append(os.path.join(obsmetrics_dir, obsmetrics_filename))
        x.dshield_generate_level0_data_metrics(cov_grid_fl, sat_state_fl, accessInfo_fl,
                                       level0dataMetrics_filepath[indx])
        indx = indx + 1
    




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

