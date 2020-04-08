""" 
.. module:: orbitpropcov

:synopsis: *Module to produce overall mission related information.*

.. note::  - The pointing of the satellite is fixed to be Nadir-pointing.

   - Lat must be in the range -pi/2 to pi/2, while lon must be in the range -pi to pi

"""

import numpy as np
import copy
import os
import shutil
import subprocess
import pandas as pd
from .util import PropagationCoverageParameters
from instrupy.public_library import Instrument
class OrbitPropCov:
    """ Class to handle propagation and coverage of a satellite
    
    :ivar sat_id: Mission epoch in Gregorian UTC format
    :vartype sat_id: int
    
    :ivar covGridFn: Coverage grid filename (output file)
    :vartype _type: str

    """
    def __init__(self, prop_cov_param = PropagationCoverageParameters()):
        self.params = copy.deepcopy(prop_cov_param)


    def run(self): 

        # get path to *this* file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            result = subprocess.run([
                        os.path.join(dir_path, '..', 'oci', 'bin', 'orbitpropcov'),
                        str(self.params.epoch), str(self.params.sma), str(self.params.ecc), str(self.params.inc), 
                        str(self.params.raan), str(self.params.aop), str(self.params.ta), str(self.params.duration), 
                        str(self.params.cov_grid_fl), str(self.params.sen_fov_geom.value), str(self.params.sen_orien), 
                        str(self.params.sen_clock), str(self.params.sen_cone), str(self.params.yaw180_flag), 
                        str(self.params.step_size), str(self.params.sat_state_fl), str(self.params.sat_acc_fl)
                        ], check= True)
        except:
            raise RuntimeError('Error executing "orbitpropcov" OC script')

    @staticmethod
    def correct_access_files(access_dir, step_size):
        """ When the instrument takes observations at purely side-looking geometry (no quint),
            post-process the access files to indicate access at middle of access-interval. 
            The middle of access-interval is approximately the time at which the instrument shall
            be at side-looking geometry to the target ground-point.
        """              
        # rename access_dir
        old_access_dir = access_dir[0:-1]+'old/'
        if os.path.exists(old_access_dir):
                    shutil.rmtree(old_access_dir)        
        os.rename(access_dir, old_access_dir) 
        # make empty access_dir to store the corrected access data
        new_access_dir = access_dir
        os.makedirs(new_access_dir)

        try:
            _path, _dirs, _OldAccessInfo_files = next(os.walk(old_access_dir))
        except StopIteration:
            pass

        for OldAccessInfo_file in _OldAccessInfo_files:

            old_accessInfo_fl = os.path.join(old_access_dir, OldAccessInfo_file)
            new_accessInfo_fl = os.path.join(new_access_dir, OldAccessInfo_file)

            df = pd.read_csv(old_accessInfo_fl, skiprows = 4)
            df = df.set_index('Time[s]')
            dfnew =  pd.DataFrame(np.nan, index=df.index, columns=df.columns)
            # iterate over all the columns (ground-points)
            for gpi in range(0, df.shape[1]):
                # Select column by index position using iloc[]
                gp_acc = df.iloc[: , gpi]
                gp_acc = gp_acc.dropna()
                # search for consequitive (in time) access, and replace by access 
                # at (approximately) the middel of the access period
                mid_access = []
                if(gp_acc.index.size>0): 
                    acc_evt = []                 
                    t0 = gp_acc.index[0]
                    acc_evt.append(t0)
                    for j in range(1,len(gp_acc.index)):
                        if(gp_acc.index[j] == t0 + step_size):
                            # same access event                            
                            t0 = gp_acc.index[j]
                            acc_evt.append(t0)
                        else:
                            # new access event
                            mid_access.append(acc_evt[int(0.5*len(acc_evt))])
                            acc_evt = []
                            t0 = gp_acc.index[j]
                            acc_evt.append(t0)
                    # append the mid access time of the final access event
                    mid_access.append(acc_evt[int(0.5*len(acc_evt))])
                    
                    for j in range(0,len(mid_access)):
                        dfnew.loc[mid_access[j]][gpi] = 1


            with open(old_accessInfo_fl, 'r') as f1:
                head = [next(f1) for x in range(4)] # copy first four header lines from the original access file
            
                with open(new_accessInfo_fl, 'w') as f2:
                    for r in head:
                        f2.write(str(r))

            with open(new_accessInfo_fl, 'a') as f2:
                dfnew.to_csv(f2, header=True)


                



          

