import os, json, argparse
from orbitpy.mission import Mission
import time

def main(user_dir):
    """ This script executes a mission according to an input JSON configuration file. 
    It takes as argument the path to the user directory where it expects a :code:`MissionSpecs.json`
    user configuration file, and any auxillary files. The output files are written in the same directory 
    by default.
        
    Example usage: :code:`python bin/run_mission.py examples/mission_1/`

    """
    start_time = time.process_time()
    with open(user_dir +'MissionSpecs.json', 'r') as mission_specs:
        mission_dict = json.load(mission_specs)

    if mission_dict.get("settings", None) is not None:
        mission_dict["settings"]["outDir"] = user_dir # force change of user-dir
    else:
        mission_dict["settings"] = {}
        mission_dict["settings"]["outDir"] = user_dir

    mission = Mission.from_json(mission_dict)   

    print("Start mission.")
    out_info = mission.execute()

    print(out_info)
    print("Time taken to execute in seconds is ", time.process_time() - start_time)

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

