import argparse
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
 

def main(user_dir):
    """ This script invokes the relevant classes and functions from the :code:`orbitpy` package to execute
    a mission. It takes as argument the path to the user directory where it expects a :code:`MissionSpecs.json`
    user configuration file, a CSV formatted file with ground station information and an optional coverage grid file.    

    The following steps are carried out upon execution of this script:
        1. Read in the user configuration file.
        2. Preprocess: Delete existing output directories and create new empty directories, compute field-of-regard,
           decide propagation time step and grid resolution,  generate coverage grid if needed, compute orbits.
        3. Run orbit propagation and coverage for each of the satellites in the mission sequentially by invoking the :code:`orbitpropcov` program.
        4. "Corrrection" of access files if purely side looking instrument.
        5. Computation of inter-satellite contact periods.
        6. Computation of ground-station contacts.
        7. Invoke :code:`instrupy` and compute of observational data metrics. 
        
    Example usage: :code:`python bin/run_mission.py examples/example1/`

    Directory structure (input files are starred):

    .. code-block:: bash

        example1/
            ├── comm/
            ├── sat11/
            ├── sat12/
            ├── covGrid
            ├── groundStations*
            ├── MissionSpecs.json*


    """
    # Read in mssion specifications from user config file, coverage grid file (optional) 
    # and the ground stations specifications file in the user directory.
    usf = user_dir + 'MissionSpecs.json'
    with open(usf, 'r') as orbit_specs_file:
            miss_specs = util.FileUtilityFunctions.from_json(orbit_specs_file)  
    
    DEBUG = 0
    if DEBUG:
        comm_dir = user_dir + 'comm/'
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

        comm_dir = pi.comm_dir
        gnd_stn_fl = pi.gnd_stn_fl
        cov_grid_fl = pi.cov_grid_fl

        sat_dirs =  glob.glob(user_dir+'sat*/')
        sat_state_fls =  glob.glob(user_dir+'sat*/state')
        sat_access_fls =  glob.glob(user_dir+'sat*/*_access')

        # Correct access files for purely side-looking instruments if necessary        
        if(pi.sats[0].ics_fov.purely_side_look):            
            print(".......Correcting access files......")
            orbitpropcov.OrbitPropCov.correct_access_files(sat_access_fls, pi.time_step)
            print(".......Done.......")

        # Compute satellite-to-satellite contacts
        print(".......Computing satellite-to-satellite contact periods.......")
        
        opaque_atmos_height_km = 30
        inter_sat_comm = communications.InterSatelliteComm(sat_state_fls, comm_dir, opaque_atmos_height_km)
        inter_sat_comm.compute_all_contacts()    
        print(".......Done.......")

        # Compute satellite-to-ground-station contacts
        print(".......Computing satellite-to-ground-station contact periods.......")
        gnd_stn_comm = communications.GroundStationComm(sat_dirs, gnd_stn_fl)
        gnd_stn_comm.compute_all_contacts()
        print(".......Done.......")

    
        # Compute observational data-metrics
        print(".......Computing observational data metrics.......") 

        instru_specs = miss_specs['instrument']
        obs = obsdatametrics.ObsDataMetrics(sat_dirs, cov_grid_fl, instru_specs)
        obs.compute_all_obs_dmetrics()      
        
        print(".......DONE.......")




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

