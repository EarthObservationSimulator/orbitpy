""" 
.. module:: orbitpropcov

:synopsis: *Module to produce overall mission related information.*

.. note::  - The pointing of the satellite is fixed to be Nadir-pointing.

   - Lat must be in the range -pi/2 to pi/2, while lon must be in the range -pi to pi

"""

import numpy as np
import os
import subprocess
from .util import PropagationCoverageParameters

class OrbitPropCov:
    """ Class to handle propagation and coverage of a satellite
    
    :ivar sat_id: Mission epoch in Gregorian UTC format
    :vartype sat_id: int
    
    :ivar covGridFn: Coverage grid filename (output file)
    :vartype _type: str
    """
    def __init__(self, prop_cov_param = PropagationCoverageParameters()):
        self.sat_id = prop_cov_param.sat_id
        self.epoch = prop_cov_param.epoch
        self.sma = prop_cov_param.sma
        self.ecc = prop_cov_param.ecc
        self.inc = prop_cov_param.inc
        self.raan = prop_cov_param.raan
        self.aop = prop_cov_param.aop
        self.ta = prop_cov_param.ta
        self.duration = prop_cov_param.duration
        self.cov_grid_fl = prop_cov_param.cov_grid_fl
        self.sen_type = prop_cov_param.sen_type
        self.sen_orien = prop_cov_param.sen_orien
        self.sen_clock = prop_cov_param.sen_clock
        self.sen_cone = prop_cov_param.sen_cone
        self.step_size = prop_cov_param.step_size
        self.sat_state_fl = prop_cov_param.sat_state_fl
        self.sat_acc_fl = prop_cov_param.sat_acc_fl

    def run(self): 

        # get path to *this* file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            result = subprocess.run([
            os.path.join(dir_path, '..', 'oci', 'bin', 'orbitpropcov'),
            str(self.epoch), str(self.sma), str(self.ecc), str(self.inc), str(self.raan), str(self.aop), str(self.ta), str(self.duration), 
            str(self.cov_grid_fl), str(self.sen_type), str(self.sen_orien), str(self.sen_clock), str(self.sen_cone), str(self.step_size), 
            str(self.sat_state_fl), str(self.sat_acc_fl)
            ], check= True)
        except:
            raise RuntimeError('Error executing "orbitpropcov" OC script')

