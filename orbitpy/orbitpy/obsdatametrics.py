""" 
.. module:: obsdatametrics

:synopsis: *Module to produce observational data metrics by invoking the :code:`instrupy` package.*

"""
import os
import csv
import pandas as pd
import glob
from instrupy.public_library import Instrument    

class ObsDataMetrics(): 
    """ Class to handle computation of observational data metrics by invoking the :code:`instrupy` package.

        :ivar sats: List of Satellites
        :vartype sats: list, :class:`orbitpy.util.Satellite`

    """
    def __init__(self, sats = None):

        self.sats = sats

    def compute_all_obs_metrics(self):

        for _sat in self.sats:           
            sat_state_fl = os.path.join(_sat.dir_pth, 'state')
            for _instru in _sat.instru: # iterate through list of instruments
                for _ssid in _instru._ssen_id: # iterate through list of subsensors ids
                    accessInfo_fl = os.path.join(_sat.dir_pth, str(_ssid)+"_access")
                    obsMetrics_fl = os.path.join(_sat.dir_pth, str(_ssid) +'_obsMetrics')
                    ObsDataMetrics.compute_obs_data_metrics(_instru, _ssid, sat_state_fl, accessInfo_fl,
                                                obsMetrics_fl)

    @staticmethod
    def compute_obs_data_metrics(instru, ssid, state_fl, access_fl, datametrics_fl): 
        ''' Generate typical data metrics for a set of instrument, satellite states, access data. 
            Iterate over all access times in the access data file. The time column of the satellite-state data file and the
            access data file must be referenced to the same epoch and produced at the same time-step size.
            This function iteratively calls :code:`calc_typ_data_metrics` of the :code:`instrupy` over all access events 
            available in the input file. The ouput is a datafile containing the observation metrics.
            
            :param instru: Instrument object for which the data-metrics are to be calculated.
            :paramtype instru: :class:`instrupy.public_library.Instrument`

            :param ssid: Subsensor id
            :paramtype ssid: str

            :param state_fl: Filepath to CSV file containing data of satellite states at fixed time-step.
                    First four rows convey general information. The second row conveys the Epoch in Julian Days UT1. The third row contains the step size in seconds.
                    The fifth row contains the following header elements, and the following rows contain the data corresponding to these headers.

                    Description of the header elements:
                    
                    * :code:`TimeIndex`, Time Index, where time (seconds) = TimeIndex * step size 
                    * :code:`X[km]`, :code:`Y[km]` :code:`Z[km]`, cartesian spatial coordinates of satellite in Earth Centered Inertial frame with equatorial plane.
                    * :code:`VX[km/s]`, :code:`VY[km/s]`, :code:`VZ[km/s]`, velocity of spacecraft in Earth Centered Inertial frame with equatorial plane.

            :paramtype state_fl: str

            :param access_fl: Filepath to CSV file containing data of access events and their time-intervals. A *1* in a cell entry correponds to valid (potential in case of FOR having been
                              used for access calculations) access.
                              First four rows convey general information. The second row conveys the Epoch in Julian Days UT1. The third row contains the step size in seconds.
                              The fifth row  contains the following header elements, and the following rows contain the data corresponding to these headers.

                              Description of the header elements:
                               
                              * :code:`TimeIndex`,  Time Index, where time (seconds) = TimeIndex * step size 
                              * :code:`GP0, GP1, GP2, ....` Columns specific to each ground-point.

            :paramtype access_fl: str

            :param datametrics_fl: Filepath to CSV file in which the results are written. First row contains the epoch in Julian Day UT1. The second row contains the step size in seconds.
                                The third row contains the column header elements. Description of the header elements:
                                
                               * :code:`observationTimeIndex`,  The time index at which the observation is made, where time (seconds) = observationTimeIndex * step size
                               * :code:`gpi` indicating index of ground-point.
                               * + other header elements containing data-metrics specific to the instrument type

                               .. note:: this is an **output** file of the function
            
            :paramtype datametrics_fl: str

            :param covgrid_fl: Filepath to CSV file containing lat/lon co-ordinates of points of interest along with index.

                        First row contains the following header elements, and the following rows contain the data corresponding to these headers.
                        
                        Description of the header elements:
                
                        * :code:`regi`, Index of the region to which the grid-point belongs.
                        * :code:`gpi`, Index of the point-of-interest. 
                        * :code:`lat[deg]`, :code:`lon[deg]`, latitude, longitude (in degrees) of the point-of-interest.  

            :paramtype covgrid_fl: str

            :returns: None

        '''
        epoch_JDUT1 = pd.read_csv(access_fl, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[2])

        step_size = pd.read_csv(access_fl, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        step_size = float(step_size[0][0].split()[4])

        # Read the access file
        access_info_df = pd.read_csv(access_fl,skiprows = [0,1,2,3]) # read the access times       

        # Read the satellite state file
        sat_state_df = pd.read_csv(state_fl,skiprows = [0,1,2,3]) 
        sat_state_df = sat_state_df.set_index('TimeIndex')

        # copy info rows from the original access file
        with open(access_fl, 'r') as f:
            head = [next(f) for x in [0,1,2]] 

        # erase any old file and create new one
        with open(datametrics_fl,'w') as f:
            for r in head:
                f.write(str(r))         

        with open(datametrics_fl,'a+', newline='') as f:
            w = csv.writer(f)

            # Iterate over all logged access events
            idx = 0
            for idx in range(0,len(access_info_df)):       

                time_i = int(access_info_df.loc[idx]["accessTimeIndex"])   

                regi = int(access_info_df.loc[idx]["regi"]) if pd.notna(access_info_df.loc[idx]["regi"]) else None             
                gpi = int(access_info_df.loc[idx]["gpi"]) if pd.notna(access_info_df.loc[idx]["gpi"]) else None   
                pOpti = int(access_info_df.loc[idx]["pntopti"]) if pd.notna(access_info_df.loc[idx]["pntopti"]) else None 
                
                TargetCoords = dict()   
                TargetCoords["Lat [deg]"] = float(access_info_df.loc[idx]["lat[deg]"])
                TargetCoords["Lon [deg]"] = float(access_info_df.loc[idx]["lon[deg]"])             

                SpacecraftOrbitState = dict()
                SpacecraftOrbitState["Time[JDUT1]"] = epoch_JDUT1 + time_i*step_size*1.0/86400.0 
                SpacecraftOrbitState["x[km]"] = sat_state_df.loc[time_i]["X[km]"] 
                SpacecraftOrbitState["y[km]"] = sat_state_df.loc[time_i]["Y[km]"] 
                SpacecraftOrbitState["z[km]"] = sat_state_df.loc[time_i]["Z[km]"] 
                SpacecraftOrbitState["vx[km/s]"] = sat_state_df.loc[time_i]["VX[km/s]"] 
                SpacecraftOrbitState["vy[km/s]"] = sat_state_df.loc[time_i]["VY[km/s]"] 
                SpacecraftOrbitState["vz[km/s]"] = sat_state_df.loc[time_i]["VZ[km/s]"] 

                obsv_metrics = instru.calc_typ_data_metrics(SpacecraftOrbitState, TargetCoords, ssid) # calculate the data metrics specific to the instrument type
                _v = dict({'observationTimeIndex':time_i, 'regi': regi, 'gpi': gpi, 'lat[deg]':TargetCoords["Lat [deg]"], 'lon[deg]':TargetCoords["Lon [deg]"], 'pntopti': pOpti }, **obsv_metrics)
                if idx==0: #1st iteration
                    w.writerow(_v.keys())    
                w.writerow(_v.values())
                idx = idx + 1