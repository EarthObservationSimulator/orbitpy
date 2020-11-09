""" 
.. module:: orbitpropcov

:synopsis: *Module to run the propagation and coverage calculations.*

.. note::  - The pointing of the satellite is fixed to be Nadir-pointing.

   - The grid points must have latitudes in the range -pi/2 to pi/2, while longitudes in the range -pi to pi

"""

import numpy as np
import copy
import os
import shutil
import subprocess
import pandas as pd
import csv
import time
import re
from .util import PropagationCoverageParameters, CoverageCalculationsApproach
from instrupy.public_library import Instrument

class OrbitPropCov:
    """ Class to handle propagation and coverage calculations.
    
    :ivar prop_cov_param: Propagation and coverage parameters
    :vartype prop_cov_param: :class:`orbitpy.util.PropagationCoverageParameters`

    """
    def __init__(self, prop_cov_param = PropagationCoverageParameters()):
        self.params = copy.deepcopy(prop_cov_param)


    def run(self): 
        """ Function which invokes the :code:`orbitpropcov` program to propagate and compute coverage of a satellite
        over a given mission duration.
        """
        if(CoverageCalculationsApproach.get(self.params.cov_calcs_app) == CoverageCalculationsApproach.PNTOPTS_WITH_GRIDPNTS):
            opc_grid = OrbitPropCovPoptsWithGrid(self.params)
            opc_grid.run()
        elif(CoverageCalculationsApproach.get(self.params.cov_calcs_app) == CoverageCalculationsApproach.GRIDPNTS):
            opc_grid = OrbitPropCovGrid(self.params)
            opc_grid.run()
        elif(CoverageCalculationsApproach.get(self.params.cov_calcs_app) == CoverageCalculationsApproach.PNTOPTS):
            opc_popts = OrbitPropCovPopts(self.params)
            opc_popts.run()
        else:
            raise RuntimeError("Unrecognized coverage caclulation appproach in 'orbitpropcov' module.")


class OrbitPropCovGrid:
    """ Class to handle propagation and coverage calculations.
    
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
        try:
            if(self.params.do_prop):
                print("start propagation calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'j2_analytical_propagator'),
                            str(self.params.epoch), str(self.params.sma), str(self.params.ecc), str(self.params.inc), 
                            str(self.params.raan), str(self.params.aop), str(self.params.ta), str(self.params.duration), 
                            str(self.params.step_size), str(self.params.sat_state_fl)
                            ], check= True)
        except:
            raise RuntimeError('Error executing "j2_analytical_propagator" OCI script')

        try:    
            if(self.params.do_cov):
                print("start coverage calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'gp_in_fov_cov_calc'),
                            str(self.params.cov_grid_fl), str(self.params.sen_fov_geom), str(self.params.sen_orien), 
                            str(self.params.sen_clock), str(self.params.sen_cone), str(self.params.yaw180_flag), 
                            str(self.params.sat_state_fl), str(self.params.sat_acc_fl + '_') 
                            ], check= True)
        except:
            raise RuntimeError('Error executing "gp_in_fov_cov_calc" OCI script')

        # Correct access files for purely side-looking instruments if necessary        
        if(self.params.purely_sidelook):            
            print(".......Correcting access files......")
            t1 = time.process_time() 
            OrbitPropCovGrid.correct_access_files(self)
            t2 = time.process_time()
            print(".......DONE.......time taken (s): ", t2-t1)
        else:
            print(".......No correction of access files......")

        # reformat access data to common format 
        OrbitPropCovGrid.reformat_access_files(self)

    def reformat_access_files(self):
        """ Reformat the access file data to a common output format used by both the grid-coverage and 
            point-options-coverage approaches.
        """
        covgrid_fl = self.params.cov_grid_fl

        access_fl = self.params.sat_acc_fl  + '_' 
        new_access_fl = self.params.sat_acc_fl 
                
        poi_info_df = pd.read_csv(covgrid_fl, dtype=str)
        types_dict = {'regi': int, 'gpi': int}
        for col, col_type in types_dict.items():
            poi_info_df[col] = poi_info_df[col].astype(col_type)
        poi_info_df = poi_info_df.set_index('gpi')

        # Read the access file
        access_info_df = pd.read_csv(access_fl,skiprows = [0,1,2,3]) # read the access times 
        access_info_df = access_info_df

        # copy headers from the original access file
        with open(access_fl, 'r') as f:
            head = [next(f) for x in [0,1,2,3]] 

        with open(new_access_fl,'w') as f:
            for r in head:
                f.write(str(r)) 

        # Iterate over all valid logged access events
        acc_indx = access_info_df.index # list of valid access [time, POI]
        with open(new_access_fl,'a+', newline='') as f:
            w = csv.writer(f)
           
            _v = dict({'accessTimeIndex':None, 'regi': None, 'gpi': None, 'lat[deg]': None, 'lon[deg]': None, 'pntopti': None})
            w.writerow(_v.keys())
            
            for indx in acc_indx:

                time_i = int(access_info_df.loc[indx][0])
                
                poi_indx = int(access_info_df.loc[indx][1])                

                regi  = int(poi_info_df.loc[poi_indx]["regi"])
                TargetCoords = dict()                
                TargetCoords["lat[deg]"] = poi_info_df.loc[poi_indx]["lat[deg]"]
                TargetCoords["lon[deg]"] = poi_info_df.loc[poi_indx]["lon[deg]"]
                
                _v = dict({'accessTimeIndex':time_i, 'regi': regi, 'gpi': poi_indx, 'lat[deg]': TargetCoords["lat[deg]"], 'lon[deg]': TargetCoords["lon[deg]"], 'pntopti': ''})
                w.writerow(_v.values())

    def correct_access_files(self):
        """ When the instrument takes observations at purely side-looking geometry (no squint),
            post-process the access files to indicate access only at middle of access-interval. 
            The middle of access-interval is approximately the time at which the instrument shall
            be at side-looking geometry to the target ground-point.
            The new access files are written in the same directory (with the same names), while the
            previous access files are renamed as *...._old* under the same directory. 
            The file format is as follows: The first four lines contain general information. The fifth line contains the
            column headers with the following names: :code:`TimeIndex,gpi`. 

            :ivar sat_access_fls: List of access files (paths) which need to be corrected
            :vartype sat_access_fls: list, str

            :returns: None

        """
        acc_fl = self.params.sat_acc_fl  + '_'            
        
        os.rename(acc_fl, acc_fl + '_') 
        old_accessInfo_fl = acc_fl + '_'
        new_accessInfo_fl = acc_fl 

        df = pd.read_csv(old_accessInfo_fl, skiprows = 4)
        df_grp = df.groupby('gpi')
        dfnew =  pd.DataFrame(columns=df.columns)

        # iterate over all the groups (ground-points)
        max_num_acc = len(df.index)
        data = np.zeros((max_num_acc,2), dtype=int)
        k = 0
        data_indx = 0
        for name, group in df_grp:
            x = (group['TimeIndex'].shift(periods=1) - group['TimeIndex']) < -1
            _intv = np.where(x == True)[0]            
            interval_indices = [0] # add the very first interval start index
            interval_indices.extend(_intv)
            interval_indices.extend((_intv - 1).tolist())
            interval_indices.append(len(group)-1) # add the very last interval end index
            interval_indices.sort()
            mid_points = [(a + b) / 2 for a, b in zip(interval_indices[::2], interval_indices[1::2])]
            mid_points = [int(np.floor(x)) for x in mid_points]
            _data = group.iloc[mid_points].to_numpy()
            m = _data.shape[0]
            data[data_indx:data_indx+m,:] = _data
            data_indx = data_indx + m

        data = data[0:data_indx]
        dfnew = pd.DataFrame(data = data, columns = ['TimeIndex', 'gpi']) 
        with open(old_accessInfo_fl, 'r') as f1:
            head = [next(f1) for x in range(4)] # copy first four header lines from the original access file
            with open(new_accessInfo_fl, 'w') as f2:
                for k in range(0,len(head)-1):
                    f2.write(str(head[k]))
                message = " Access listed below corresponds to approximate access instants at the grid-points at a side-look target geometery. The scene scan time should be used along with the below data to get complete access information.\n"
                f2.write(str(head[-1]).rstrip() + message)

        with open(new_accessInfo_fl, 'a') as f2:
            dfnew.to_csv(f2, index=False, header=True, line_terminator='\n')  

class OrbitPropCovPopts:
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
        try:
            if(self.params.do_prop):
                print("start propagation calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'j2_analytical_propagator'),
                            str(self.params.epoch), str(self.params.sma), str(self.params.ecc), str(self.params.inc), 
                            str(self.params.raan), str(self.params.aop), str(self.params.ta), str(self.params.duration), 
                            str(self.params.step_size), str(self.params.sat_state_fl)
                            ], check= True)
        except:
            raise RuntimeError('Error executing "j2_analytical_propagator" OC script')
        try:    
            if(self.params.do_cov):
                print("start coverage calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'pnt_axis_sphere_intsec_cov_calc'),
                            str(self.params.popts_fl), str(self.params.sat_state_fl), 
                            str(self.params.sat_acc_fl + '_') 
                            ], check= True)
        except:
            raise RuntimeError('Error executing "pnt_axis_sphere_intsec_cov_calc" OC script')

        OrbitPropCovPopts.reformat_access_files(self)

    def reformat_access_files(self):
        """ Reformat the access file data to a common output format used by both the grid-coverage and 
            point-options-coverage approaches.
        """
        access_fl = self.params.sat_acc_fl  + '_' 
        new_access_fl = self.params.sat_acc_fl 

        # Read the access file
        access_info_df = pd.read_csv(access_fl,skiprows = [0,1,2,3]) 
        access_info_df = access_info_df.set_index('TimeIndex')

        # copy headers from the original access file
        with open(access_fl, 'r') as f:
            head = [next(f) for x in [0,1,2,3]] 

        with open(new_access_fl,'w') as f:
            for r in head:
                f.write(str(r)) 

        # Iterate over all valid logged access events
        acc_indx = list(access_info_df[access_info_df.notnull()].stack().index) # list of valid access [time, pOpti]

        with open(new_access_fl,'a+', newline='') as f:
            w = csv.writer(f)
           
            _v = dict({'accessTimeIndex':None, 'regi': None, 'gpi': None, 'lat[deg]': None, 'lon[deg]': None, 'pntopti': None})
            w.writerow(_v.keys())
            
            for indx in acc_indx:
                time_i = int(indx[0])
                
                pOpti = int(indx[1][6:])                

                coords = access_info_df.loc[indx]
                [x,y] = coords.split(" ")

                TargetCoords = dict()                

                TargetCoords["lat[deg]"] = re.sub('[(]', '', x)
                TargetCoords["lon[deg]"] = re.sub('[)]', '', y)
                
                _v = dict({'accessTimeIndex':time_i, 'regi': '', 'gpi': '', 'lat[deg]': TargetCoords["lat[deg]"], 'lon[deg]': TargetCoords["lon[deg]"], 'pntopti': pOpti})
                w.writerow(_v.values())

class OrbitPropCovPoptsWithGrid:
    """ Class to handle propagation and coverage calculations.
    
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
        try:
            if(self.params.do_prop):
                print("start propagation calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'j2_analytical_propagator'),
                            str(self.params.epoch), str(self.params.sma), str(self.params.ecc), str(self.params.inc), 
                            str(self.params.raan), str(self.params.aop), str(self.params.ta), str(self.params.duration), 
                            str(self.params.step_size), str(self.params.sat_state_fl)
                            ], check= True)
        except:
            raise RuntimeError('Error executing "j2_analytical_propagator" OC script')
        try:
            if(self.params.do_cov):
                print("start coverage calcs")
                result = subprocess.run([
                            os.path.join(dir_path, '..', 'oci', 'bin', 'pnt_opts_with_gp_in_fov_cov_calc'),
                            str(self.params.cov_grid_fl), str(self.params.popts_fl), str(self.params.sen_fov_geom), 
                            str(self.params.sen_clock), str(self.params.sen_cone),
                            str(self.params.sat_state_fl), str(self.params.sat_acc_fl + '_') 
                            ], check= True)
        except:
            raise RuntimeError('Error executing "pnt_opts_with_gp_in_fov_cov_calc" OC script')

        # Correct access files for purely side-looking instruments if necessary        
        if(self.params.purely_sidelook):            
            print(".......Correcting access files......")
            t1 = time.process_time() 
            OrbitPropCovPoptsWithGrid.correct_access_files(self)
            t2 = time.process_time()
            print(".......DONE.......time taken (s): ", t2-t1)
        else:
            print(".......No correction of access files......")

        # reformat access data to common format 
        OrbitPropCovPoptsWithGrid.reformat_access_files(self)

    def reformat_access_files(self):
        """ Reformat the access file data to a common output format used by both the grid-coverage and 
            point-options-coverage approaches.
        """
        covgrid_fl = self.params.cov_grid_fl

        access_fl = self.params.sat_acc_fl  + '_' 
        new_access_fl = self.params.sat_acc_fl 
                
        poi_info_df = pd.read_csv(covgrid_fl, dtype=str)
        types_dict = {'regi': int, 'gpi': int}
        for col, col_type in types_dict.items():
            poi_info_df[col] = poi_info_df[col].astype(col_type)
        poi_info_df = poi_info_df.set_index('gpi')

        # Read the access file
        access_info_df = pd.read_csv(access_fl,skiprows = [0,1,2,3]) # read the access times 
        access_info_df = access_info_df

        # copy headers from the original access file
        with open(access_fl, 'r') as f:
            head = [next(f) for x in [0,1,2,3]] 

        with open(new_access_fl,'w') as f:
            for r in head:
                f.write(str(r)) 

        # Iterate over all valid logged access events
        acc_indx = access_info_df.index # list of valid access [time, POI]
        with open(new_access_fl,'a+', newline='') as f:
            w = csv.writer(f)
           
            _v = dict({'accessTimeIndex':None, 'regi': None, 'gpi': None, 'lat[deg]': None, 'lon[deg]': None, 'pntopti': None})
            w.writerow(_v.keys())
            
            
            for indx in acc_indx:
                time_i = int(access_info_df.loc[indx][0])
                pntopt_i = int(access_info_df.loc[indx][1])                
                poi_indx = int(access_info_df.loc[indx][2])                

                regi  = int(poi_info_df.loc[poi_indx]["regi"])
                TargetCoords = dict()                
                TargetCoords["lat[deg]"] = poi_info_df.loc[poi_indx]["lat[deg]"]
                TargetCoords["lon[deg]"] = poi_info_df.loc[poi_indx]["lon[deg]"]
                
                _v = dict({'accessTimeIndex':time_i, 'regi': regi, 'gpi': poi_indx, 'lat[deg]': TargetCoords["lat[deg]"], 'lon[deg]': TargetCoords["lon[deg]"], 'pntopti': pntopt_i})
                w.writerow(_v.values())

    def correct_access_files(self):
        """ When the instrument takes observations at purely side-looking geometry (no squint),
            post-process the access files to indicate access only at middle of access-interval. 
            The middle of access-interval is approximately the time at which the instrument shall
            be at side-looking geometry to the target ground-point.
            The new access files are written in the same directory (with the same names), while the
            previous access files are renamed as *...._old* under the same directory. 
            The file format is as follows: The first four lines contain general information. The fifth line contains the
            column headers with the following names: :code:`TimeIndex,gpi`. 

            :ivar sat_access_fls: List of access files (paths) which need to be corrected
            :vartype sat_access_fls: list, str

            :returns: None

        """
        acc_fl = self.params.sat_acc_fl  + '_'            
        
        os.rename(acc_fl, acc_fl + '_') 
        old_accessInfo_fl = acc_fl + '_'
        new_accessInfo_fl = acc_fl 

        df = pd.read_csv(old_accessInfo_fl, skiprows = 4)

        #df = df.set_index(['PntOptIndex'])
        
        d ={}
        for popt, df_per_popt in df.groupby('PntOptIndex'):
                      
            df_grp = df_per_popt.groupby('gpi')
            dfnew =  pd.DataFrame(columns=df_per_popt.columns)
            # iterate over all the gorups (ground-points)
            for name, group in df_grp:
                x = (group['TimeIndex'].shift(periods=1) - group['TimeIndex']) < -1
                _intv = np.where(x == True)[0]            
                interval_indices = [0] # add the very first interval start index
                interval_indices.extend(_intv)
                interval_indices.extend((_intv - 1).tolist())
                interval_indices.append(len(group)-1) # add the very last interval end index
                interval_indices.sort()
                mid_points = [(a + b) / 2 for a, b in zip(interval_indices[::2], interval_indices[1::2])]
                mid_points = [int(np.floor(x)) for x in mid_points]
                dfnew = dfnew.append(group.iloc[mid_points]) # TODO: Replace this time-inefficient append function by preallocated numpy arrays
                dfnew = dfnew.sort_values(by=['TimeIndex'])

            d[popt]=dfnew

        df_final = pd.concat(d)
        df_final = df_final.sort_values(by=['TimeIndex'])
        #df_final.rename_axis(['PntOptIndex', 'TimeIndex'], inplace=True)
        #df_final = df_final.swaplevel(0, 1) # change the order of levels

        with open(old_accessInfo_fl, 'r') as f1:
            head = [next(f1) for x in range(4)] # copy first four header lines from the original access file
        
            with open(new_accessInfo_fl, 'w') as f2:
                for k in range(0,len(head)-1):
                    f2.write(str(head[k]))
                message = " Access listed below corresponds to approximate access instants at the grid-points at a side-look target geometery. The scene scan time should be used along with the below data to get complete access information.\n"
                f2.write(str(head[-1]).rstrip() + message)

        with open(new_accessInfo_fl, 'a') as f2:
            df_final.to_csv(f2, index=False, header=True)  