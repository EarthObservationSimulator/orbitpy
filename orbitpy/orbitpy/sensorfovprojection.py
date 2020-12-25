import numpy as np
import os
import subprocess
import json
import shutil
import glob
import warnings
import logging
logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

_date = 2451179.50000143
_state_eci = "0,7000.0,0,-10.0,0,0"
_satOrien = "1,2,3,0,0,0"
_senOrien = "1,2,3,0,0,0"
angleWidth = 60
angleHeight = 60
widthDetectors = 3
heightDetectors = 1
outFilePath = "../senFovProj.json"

try:
    print("start calcs")
    result = subprocess.run([
                os.path.join(dir_path, '..', 'oci', 'bin', 'sensor_fov_projector'),
                str(_date), str(_state_eci), str(_satOrien), str(_senOrien), 
                str(angleWidth), str(angleHeight), str(widthDetectors), str(heightDetectors), str(outFilePath)
                ], check= True)
except:
    raise RuntimeError('Error executing "sensor_fov_projection" OC script')