""" 
.. module:: orbitpropcov_popts

:synopsis: *Module to run the propagation and coverage calculations given pointing options.*

"""

import numpy as np
import copy
import os
import shutil
import subprocess
import pandas as pd
from .util import PropagationCoverageParameters
from instrupy.public_library import Instrument
class OrbitPropCov_POpts:
    """ Class to handle propagation and coverage calculations with the pointing options approach.
    
    :ivar prop_cov_param: Propagation and coverage parameters
    :vartype prop_cov_param: :class:`orbitpy.util.PropagationCoverageParameters`

    """
    def __init__(self, prop_cov_param = PropagationCoverageParameters()):
        self.params = copy.deepcopy(prop_cov_param)


    def run(self): 
        """ Function which invokes the :code:`orbitpropcov` program to propagate and compute coverage of a satellite
        over a given mission duration.
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.params.epoch = '2017, 1, 15, 22, 30, 20.111'
        self.params.sma = 6378+700
        self.params.ecc = 0
        self.params.inc = 98
        self.params.raan = 0
        self.params.aop = 0
        self.params.ta = 0
        self.params.duration = 0.25
        self.params.popts_fl = 'examples/example6/pOpts'
        self.params.step_size = 5
        self.params.sat_state_fl = 'examples/example6/state'
        self.params.sat_acc_fl = 'examples/example6/access'
        try:
            result = subprocess.run([
                        os.path.join(dir_path, '..', 'oci', 'bin', 'orbitpropcov_popts'),
                        str(self.params.epoch), str(self.params.sma), str(self.params.ecc), str(self.params.inc), 
                        str(self.params.raan), str(self.params.aop), str(self.params.ta), str(self.params.duration), 
                        str(self.params.popts_fl), 
                        str(self.params.step_size), str(self.params.sat_state_fl), str(self.params.sat_acc_fl)
                        ], check= True)
        except:
            raise RuntimeError('Error executing "orbitpropcov" OC script')

