""" Script illustrating obtaining the most recent available satellite orbit data from SpaceTrack.org 
    close to a given target date. Note that the data is available at a latency from the time of 
    measurement of the satellite state.

Initialize SpaceTrackAPI instance with credentials from a JSON file in the following format: 
{
    "username": "xxxx",
    "password":  "xxxx"
}

"""

from orbitpy.util import SpaceTrackAPI
import os

file_dir = os.path.dirname(__file__)

# Initialize SpaceTrackAPI instance with credentials from a JSON file 
space_track_api = SpaceTrackAPI(os.path.join(file_dir, 'credentials.json'))

# Login to Space-Track.org
space_track_api.login()

# Specify the 'norad_id' of the satellite you want to retrieve data for
#norad_id = "41886"  # Example: CYGNSS CYGFM06
norad_id = "31698" # Example TerraSARX

# Specify the target date and time to find the closest OMM (format: YYYY-MM-DDTHH:MM:SS)
target_datetime = "2024-04-09T01:00:00"

# Retrieve the closest OMM for the specified satellite closest to the target date and time
space_track_api.get_closest_omm(norad_id, target_datetime)

# Logout
space_track_api.logout()