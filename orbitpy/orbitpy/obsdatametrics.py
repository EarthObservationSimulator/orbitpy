""" 
.. module:: obsdatametrics

:synopsis: *Module to produce observational data metrics by invoking the instrupy package.*

"""
import os
import csv
import pandas as pd
import glob
from instrupy.public_library import Instrument    


class ObsDataMetrics(): 
    """ Class to handle computation of observational data metrics by invoking the :code:`instrupy` package.

        :ivar sat_dirs: List of all satellite directories
        :vartype sat_dirs: list, str

        :ivar cov_grid_fl: Filepath with name to the coverage grid data
        :vartype cov_grid_fl: str

        :ivar instru_specs: List of instrument specifications
        :vartype instru_specs: list, dict

    """
    def __init__(self, sat_dirs = None, cov_grid_fl = None, instru_specs = dict()):
      self.sat_dirs = sat_dirs
      self.cov_grid_fl = cov_grid_fl
      self.instru_specs = instru_specs

    def compute_all_obs_dmetrics(self):
        """ Iterate over all satellite directories and compute the observational data metrics. A 
            seperate data-file containing the observational metrics is produced per payload. Currently 
            hardcoded to process only one payload.
        """
        instru = Instrument.from_json(self.instru_specs[0]) # hardcoded to 1 instrument     
        # process each access file separately
        for _dir in self.sat_dirs:           
            
            sat_state_fl = os.path.join(_dir, 'state')
            accessInfo_fl = glob.glob(_dir+'*_access')[0] # hardcoded to 1 instrument          
            obsMetrics_fl = os.path.join(_dir, 'pay1_obsMetrics') # hardcoded to 1 instrument  
            ObsDataMetrics.compute_obs_data_metrics(instru, self.cov_grid_fl, sat_state_fl, accessInfo_fl,
                                        obsMetrics_fl)

    @staticmethod
    def compute_obs_data_metrics(instru, POI_filepath, SatelliteState_filepath, AccessInfo_filepath, Result_filepath): 
        ''' Generate typical data metrics for a set of instrument, satellite states, access data. 
            Iterate over all access times in the access data file. The time column of the satellite-state data file and the
            access data file must be referenced to the same epoch and produced at the same time-step size.
            This function iteratively calls :code:`calc_typ_data_metrics` of the instrument over all access events 
            available in the input file.

            :param POI_filepath: Filepath to CSV file containing lat/lon co-ordinates of points of interest along with index.

                                 First row contains the following header elements, and the following rows contain the data corresponding to these headers.
                                 
                                 Description of the header elements:
                            
                                 * :code:`gpi`, Index of the point-of-interest.
                                 * :code:`lat[deg]`, :code:`lon[deg]`, latitude, longitude of the point-of-interest.  

                                 .. note:: Make sure the header titles are as specified above, and the delimiters are commas.

            :paramtype POI_filepath: str

             
            :param SatelliteState_filepath: Filepath to CSV file containing data satellite states at fixed time-step.
                    First four rows convey general information. The second row conveys the Epoch in Julian Days UT1. The third row contains the step size in seconds.
                    The fifth row  contains the following header elements, and the following rows contain the data corresponding to these headers.

                    Description of the header elements:
                    
                    * :code:`TimeIndex`,  Time Index, where time (seconds) = TImeIndex * step size 
                    * :code:`X[km]`, :code:`Y[km]` :code:`Z[km]`, cartesian spatial coordinates of satellite in Earth Centered Inertial frame with equatorial plane.
                    * :code:`VX[km/s]`, :code:`VY[km/s]`, :code:`VZ[km/s]`, velocity of spacecraft in Earth Centered Inertial frame with equatorial plane.

            :paramtype SatelliteState_filepath: str

            :param AccessInfo_filepath: Filepath to CSV file containing data of access events and their time-intervals.
                               First three rows convey general information. The second row conveys the Epoch in Julian Days UT1. The third row contains the step size in seconds.
                               The fifth row  contains the following header elements, and the following rows contain the data corresponding to these headers.

                               Description of the header elements:
                                
                               * :code:`TimeIndex`,  Time Index, where time (seconds) = TimeIndex * step size 
                               * :code:`GP0, GP1, GP2, ....` Columns specific to each ground-point.

            :paramtype AccessInfo_filepath: str

            :param Result_filepath: Filepath to CSV file in which the results are written. First row contains the epoch in Julian Day UT1. The second row contains the step size in seconds.
                                The third row contains the column header elements. Description of the header elements:
                                
                               * :code:`observationTimeIndex`,  The time index at which the observation is made.  
                               * :code:`gpi` indicating index of ground-point.
                               * + other header elements containing data-metrics specific to the instrument type

                               .. note:: this is an **output** file of the function
            
            :paramtype Result_filepath: str

        '''
        epoch_JDUT1 = pd.read_csv(AccessInfo_filepath, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])

        step_size = pd.read_csv(AccessInfo_filepath, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])
                
        poi_info_df = pd.read_csv(POI_filepath)
        poi_info_df = poi_info_df.set_index('gpi')

        # Read the access file
        access_info_df = pd.read_csv(AccessInfo_filepath,skiprows = [0,1,2,3]) # read the access times (corresponding to the DSM in which the instrument was used)
        access_info_df = access_info_df.set_index('TimeIndex')

        # Read the satellite state file
        sat_state_df = pd.read_csv(SatelliteState_filepath,skiprows = [0,1,2,3]) 
        sat_state_df = sat_state_df.set_index('TimeIndex')
        sat_state_df = sat_state_df.loc[access_info_df.index] # retain states at only those times in which there are accesses

        # copy second and third row from the original access file
        with open(AccessInfo_filepath, 'r') as f:
            next(f)
            head = [next(f) for x in [1,2]] 

        # erase any old file and create new one
        with open(Result_filepath,'w') as f:
            for r in head:
                f.write(str(r))         

        with open(Result_filepath,'a+', newline='') as f:
            w = csv.writer(f)

            # Iterate over all valid logged access events
            acc_indx = list(access_info_df[access_info_df.notnull()].stack().index) # list of valid access [time, POI]

            idx = 0
            for indx in acc_indx:

                time_i = float(indx[0])
                poi_indx = int(indx[1][2:])

                TargetCoords = dict()                
                TargetCoords["Lat [deg]"] = poi_info_df.loc[poi_indx]["lat[deg]"]
                TargetCoords["Lon [deg]"] = poi_info_df.loc[poi_indx]["lon[deg]"]

                SpacecraftOrbitState = dict()
                SpacecraftOrbitState["Time[JDUT1]"] = epoch_JDUT1 + time_i*step_size*1.0/86400.0 
                SpacecraftOrbitState["x[km]"] = sat_state_df.loc[time_i]["X[km]"] 
                SpacecraftOrbitState["y[km]"] = sat_state_df.loc[time_i]["Y[km]"] 
                SpacecraftOrbitState["z[km]"] = sat_state_df.loc[time_i]["Z[km]"] 
                SpacecraftOrbitState["vx[km/s]"] = sat_state_df.loc[time_i]["VX[km/s]"] 
                SpacecraftOrbitState["vy[km/s]"] = sat_state_df.loc[time_i]["VY[km/s]"] 
                SpacecraftOrbitState["vz[km/s]"] = sat_state_df.loc[time_i]["VZ[km/s]"] 

                obsv_metrics = instru.calc_typ_data_metrics(SpacecraftOrbitState, TargetCoords) # calculate the data metrics specific to the instrument type
                _v = dict({'observationTimeIndex':time_i, 'gpi': poi_indx}, **obsv_metrics)
                if idx==0: #1st iteration
                    w.writerow(_v.keys())    
                w.writerow(_v.values())
                idx = idx + 1
                #print(obsv_metrics)
