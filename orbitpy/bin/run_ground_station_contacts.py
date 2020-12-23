import argparse
import os
import shutil
import sys
import csv
import glob
from orbitpy import preprocess, orbitpropcov, communications, obsdatametrics, util
import time

def main(user_dir, gnd_stn_fl):
    """ This script invokes the relevant classes and functions from the :code:`orbitpy` package to execute
    a mission. It takes as argument the path to the user directory where it expects a :code:`MissionSpecs.json`
    user configuration file, a CSV formatted file with ground station information and an optional coverage grid file.    
    """
    sat_dirs =  glob.glob(user_dir+'sat*/')
    # Compute satellite-to-ground-station contacts
    print(".......Computing satellite-to-ground-station contact periods.......")
    t1 = time.process_time() 
    gnd_stn_comm = communications.GroundStationComm(sat_dirs, gnd_stn_fl)
    gnd_stn_comm.compute_all_contacts()
    t2 = time.process_time()   
    print(".......DONE.......time taken (s): ", t2-t1)

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
        description='Find Ground Station Contacts'
    )
    parser.add_argument(
        'user_dir',        
        action=readable_dir,
        help="Directory with the satellite folders (containing the state files)."
    )
    parser.add_argument(
        'gnd_stn_fl',        
        help="Ground-stations data file."
    )
    args = parser.parse_args()
    main(args.user_dir,args.gnd_stn_fl)
