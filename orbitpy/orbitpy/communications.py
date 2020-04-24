""" 
.. module:: intersatellitecomm

:synopsis: *Module to handle computation of inter-satellite communications periods.*

"""
import os
import shutil
import pandas as pd
import csv
import numpy as np
from orbitpy.util import Constants, MathUtilityFunctions
class InterSatelliteComm:
   """ Class to handle computation of inter-satellite communication periods.

       :ivar sat_state_fls: Satellite state filepaths with names
       :vartype sat_state_fls: list, str

       :ivar comm_dir: Inter-satellite Comm directory path
       :vartype comm_dir: str

       :ivar opaque_atmos_height_km: Height of opaque atmosphere to be considered below which communication cannot 
                                     take place
       :vartype opaque_atmos_height_km: float

   """
   def __init__(self, sat_state_fls, comm_dir, opaque_atmos_height_km):
      self.sat_state_fls = sat_state_fls
      self.comm_dir = comm_dir
      self.opaque_atmos_height_km = opaque_atmos_height_km     
   
   def compute_all_contacts(self):
      """ Iterate over all possible satellite pairs, and compute their contact times. Accepts list of satellite state
      files in the instance variable :code:`sat_state_fls` as input. 
      
      The format of the data in each of the state files is as follows:
      The first four lines contain auxillary information. The second line contains the mission epoch.
      The third line contains the step size in seconds.
      The fifth line contains comma seperated coulmn headers as follows:
      :code:`TimeIndex,X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]`. 
      However the headers are ignored and the data is read according to the position of the columns. 
      
      The states of all the satellites must be synced to the same time-series.
      """
      number_of_files = len(self.sat_state_fls)

      for indx1 in range(0,number_of_files):

         sat1_fl = self.sat_state_fls[indx1]
         sat1 = pd.read_csv(sat1_fl, skiprows=5, header=None, delimiter=r",")
         sat1 = sat1[:-1]
         time_s = list(sat1.iloc[:,0])

         sat1_x_km = list(sat1.iloc[:,1])
         sat1_y_km = list(sat1.iloc[:,2])
         sat1_z_km = list(sat1.iloc[:,3])
         
         for indx2 in range(indx1+1,number_of_files):
               
               sat2_fl = self.sat_state_fls[indx2]

               with open(sat1_fl) as fd:
                  reader = csv.reader(fd)
                  epoch = [row for idx, row in enumerate(reader) if idx == 1]
                  epoch = str(epoch)[3:-3]

               sat2 = pd.read_csv(sat2_fl, skiprows=5, header=None, delimiter=r",")
               sat2 = sat2[:-1]               

               sat2_x_km = list(sat2.iloc[:,1])
               sat2_y_km = list(sat2.iloc[:,2])
               sat2_z_km = list(sat2.iloc[:,3])
               
               # prepare output files
               output_detailed_fl = self.comm_dir + sat1_fl.split('/')[-2]+"_to_"+sat2_fl.split('/')[-2]+"_detailed"
               f = open(output_detailed_fl, "w")
               f.write(epoch)
               f.write("\n")
               f.close()

               output_concise_fl = self.comm_dir + sat1_fl.split('/')[-2]+"_to_"+sat2_fl.split('/')[-2]+"_concise"       
               f = open(output_concise_fl, "w")
               f.write(epoch)
               f.write("\n")
               f.close()

               InterSatelliteComm.compute_satA_to_satB_contact(time_s, sat1_x_km, sat1_y_km, sat1_z_km, sat2_x_km, sat2_y_km, sat2_z_km, 
                                                  output_concise_fl, output_detailed_fl, self.opaque_atmos_height_km)
   
   @staticmethod
   def compute_satA_to_satB_contact(time_indx, satA_x_km, satA_y_km, satA_z_km, satB_x_km, satB_y_km, satB_z_km,
                                       output_concise_fl, output_detailed_fl, opaque_atmos_height_km):
      """ Compute contact times between two given satellites over a time series. The results are written onto data files,
      one containing contact info per time step along with range information, and the other file containing contact intervals. 

      :param time_indx: Time index series
      :paramtype time_indx: list, float

      :param satA_x_km: Satellite A X position series in kilometers
      :paramtype satA_x_km: list, float

      :param satA_y_km: Satellite A Y position series in kilometers
      :paramtype satA_y_km: list, float

      :param satA_z_km: Satellite A Z position series in kilometers
      :paramtype satA_z_km: list, float

      :param satB_x_km: Satellite B X position series in kilometers
      :paramtype satB_x_km: list, float

      :param satB_y_km: Satellite B Y position series in kilometers
      :paramtype satB_y_km: list, float

      :param satB_z_km: Satellite B Z position series in kilometers
      :paramtype satB_z_km: list, float

      :param output_concise_fl: Filepath with name to write contact intervals
      :paramtype output_concise_fl: str

      :param output_detailed_fl: Filepath with name to write contact data with range information
      :paramtype output_detailed_fl: str

      :param opaque_atmos_height_km: Height of atmosphere below which line-of-sight communication cannot take place
      :paramtype opaque_atmos_height_km: float

      :returns: None

      """
      # Loop over entire mission duration
      numTimeSteps = len(time_indx)
      access_log = []
      range_log = []
      for indx in range(0,numTimeSteps):

         satA_pos = np.array([satA_x_km[indx], satA_y_km[indx], satA_z_km[indx]]).astype(float)
         satB_pos = np.array([satB_x_km[indx], satB_y_km[indx], satB_z_km[indx]]).astype(float)

         access_log.append(MathUtilityFunctions.checkLOSavailability(satA_pos, satB_pos, Constants.radiusOfEarthInKM + opaque_atmos_height_km))

         satAB_km = satB_pos - satA_pos
         r_satAB_km = np.sqrt(np.dot(satAB_km, satAB_km))
         range_log.append(r_satAB_km)
         
      # Post process to create intervals
      interval_boundary = []
      flag = access_log[0]
      for indx in range(1,numTimeSteps):
         if flag!=access_log[indx]:
            interval_boundary.append(time_indx[indx])
            flag = access_log[indx]

      if access_log[0] is True: # Means the mission startes off with the satellite seeing each other
         if(len(interval_boundary) == 0):
            interval_boundary.append(time_indx[numTimeSteps-1]) # There is LOS for complete mission duration
         interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
         
      # interval_boundary should be even, else add the end of mission time to the interval boundary
      if(len(interval_boundary)%2 != 0):
         interval_boundary.append(time_indx[numTimeSteps-1])

      # Write detailed output file
      with open(output_detailed_fl, 'a', newline='') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
         fwriter.writerow(['Time[s]', 'AccessOrNoAccess', 'Range[km]'])
         indx = 0
         for indx in range(0,len(time_indx)):
            fwriter.writerow([time_indx[indx], access_log[indx], range_log[indx]])     
      
      with open(output_concise_fl, 'a', newline='') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
         fwriter.writerow(['AccessFrom[s]', 'AccessTo[s]'])
         indx = 0
         while indx < len(interval_boundary):
            fwriter.writerow([interval_boundary[indx], interval_boundary[indx+1]])
            indx = indx + 2

               

class GroundStationComm:
   """ Class to handle computation of contact periods between satellites and ground stations. 

   The ground station specifications is read of an input file (whose path is given as input during instantiation 
   of the class object). The entry in the files is as in CSV format with the first row having the following headers:
   :code:`index,name,lat[deg],lon[deg],alt[km],minElevation[deg]`. The rest of the rows contain the corresponding 
   information for each ground-station in the mission. The names of the headers is to be striclty as indicated.

   :ivar sat_dirs: List of all satellite directories
   :vartype sat_dirs: list, str

   :ivar gnd_stn_specs: Dataframe containing data of all the ground-stations.
   :vartype gnd_stn_specs: :class:`pandas.DataFrame`

   """
   def __init__(self, sat_dirs = None, gnd_stn_fl = None):
      self.sat_dirs = sat_dirs
      try:
         try:
            self.gnd_stn_specs = pd.read_csv(gnd_stn_fl, header=0, delimiter=r",")
         except:
            print('Error in reading ground-station(s) specifications file.')
            raise  
      except:
         raise Exception("Error in processing (initialization) of ground station contacts.")
         

   def compute_all_contacts(self):
      """ Iterate over all possible satellites and ground-stations, and compute their contact times. Accepts list of satellite state
      files in the instance variable :code:`sat_state_fls` as input. 
      
      The format of the data in each of the state files is as follows:
      The first four lines contain auxillary information. The second line contains the mission epoch. 
      The third line contains the step size in seconds.
      The fifth line contains comma seperated coulmn headers as follows:
      :code:`TimeIndex,X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]`. 
      However the headers are ignored and the data is read according to the position of the columns. 

      The ground-station coordinates and minimum elelvation requirements is read off the instance variable :code:`gnd_stn_specs`.
      """
      # Iterate over all satellites
      for indx1 in range(0,len(self.sat_dirs)):

         sat_fl = self.sat_dirs[indx1] + 'state'
         with open(sat_fl) as fd:
                  reader = csv.reader(fd)
                  epoch = [row for idx, row in enumerate(reader) if idx == 1]
                  epoch = str(epoch)[3:-3]
         __epoch = float(str(epoch).split()[2])

         with open(sat_fl) as fd:
                  reader = csv.reader(fd)
                  step_size = [row for idx, row in enumerate(reader) if idx == 2]
                  step_size = str(step_size)[3:-3]
         __step_size = float(str(step_size).split()[4])
         
         sat = pd.read_csv(sat_fl, skiprows=5, header=None, delimiter=r",")
         sat = sat[:-1]

         time_indx = sat.iloc[:,0]
         sat_x_km = sat.iloc[:,1]
         sat_y_km = sat.iloc[:,2]
         sat_z_km = sat.iloc[:,3]
                 
         # Iterate over all ground stations
         for indx2 in range(0,self.gnd_stn_specs.shape[0]):
               
               gnd_stn_i = int(self.gnd_stn_specs.iloc[indx2]['index'])
               gnd_stn_lat = float(self.gnd_stn_specs.iloc[indx2]['lat[deg]'])
               gnd_stn_lon = float(self.gnd_stn_specs.iloc[indx2]['lon[deg]'])
               gnd_stn_alt = float(self.gnd_stn_specs.iloc[indx2]['alt[km]'])
               ground_stn_coords = [gnd_stn_lat, gnd_stn_lon, gnd_stn_alt]
               gnd_stn_minelv_deg = float(self.gnd_stn_specs.iloc[indx2]['minElevation[deg]'])

               # prepare output files
               output_detailed_fl = self.sat_dirs[indx1] + "gndStn"+str(gnd_stn_i)+"_contact_detailed"
               f = open(output_detailed_fl, "w")
               f.write(epoch)
               f.write("\n")
               f.write(step_size)
               f.write("\n")
               f.close()

               output_concise_fl = self.sat_dirs[indx1] + "gndStn"+str(gnd_stn_i)+"_contact_concise"
               f = open(output_concise_fl, "w")
               f.write(epoch)
               f.write("\n")
               f.write(step_size)
               f.write("\n")
               f.close()

               GroundStationComm.compute_sat_to_GS_contact(__epoch, __step_size, time_indx, sat_x_km, sat_y_km, sat_z_km, ground_stn_coords,
                                 output_concise_fl, output_detailed_fl, gnd_stn_minelv_deg)

              

   @staticmethod
   def compute_sat_to_GS_contact(epoch, step_size, time_indx, sat_x_km, sat_y_km, sat_z_km, ground_stn_coords,
                                 output_concise_fl, output_detailed_fl, gnd_stn_minelv_deg):
      """ Compute contact times between two given satellites over a time series. The results are written onto data files,
      one containing contact info per time step along with range information, and the other file containing contact intervals. 

      :param epoch: Epoch in Julian Day UT1
      :paramtype epoch: float

      :param step_size: Step size in seconds
      :paramtype step_size: float

      :param time_indx: Time index series in seconds
      :paramtype time_indx: list, int

      :param sat_x_km: Satellite X position series in kilometers
      :paramtype satA_x_km: list, float

      :param sat_y_km: Satellite Y position series in kilometers
      :paramtype satA_y_km: list, float

      :param sat_z_km: Satellite Z position series in kilometers
      :paramtype satA_z_km: list, float

      :param ground_stn_coords: Ground station latitude, longitude (in degrees) and altitude in kilometers
      :paramtype ground_stn_coords: list, float

      :param output_concise_fl: Filepath with name to write contact intervals
      :paramtype output_concise_fl: str

      :param output_detailed_fl: Filepath with name to write contact data with elevation information
      :paramtype output_detailed_fl: str

      :param gnd_stn_minelv_deg: Minimum elevation angle beyond which communication can take place with the ground-station
      :paramtype gnd_stn_minelv_deg: float

      :returns: None

      """
      # Loop over entire mission duration
      numTimeSteps = len(time_indx)
      access_log = []
      range_log = []
      elv_log = []
      for k in range(0,numTimeSteps):

         # Get satellite coordinates in ECI frame
         sat_position = np.array([sat_x_km[k], sat_y_km[k], sat_z_km[k]]).astype(float)
         
         time_s = time_indx[k] * step_size
         # Get ground station coordinates in ECI frame
         time_JDUT1 = epoch + time_s*(1.0/(24*60*60))
         gnd_stn_coords_eci = MathUtilityFunctions.geo2eci(ground_stn_coords, time_JDUT1)

         los = MathUtilityFunctions.checkLOSavailability(sat_position, gnd_stn_coords_eci, Constants.radiusOfEarthInKM)
         gndst_to_sat = sat_position - gnd_stn_coords_eci
         r_gndst_to_sat = np.linalg.norm(gndst_to_sat)
         unit_gndst_to_sat = MathUtilityFunctions.normalize(gndst_to_sat)
         unit_gndst = MathUtilityFunctions.normalize(gnd_stn_coords_eci)
         elv_angle = np.pi/2 - np.arccos(np.dot(unit_gndst, unit_gndst_to_sat))
         range_log.append(r_gndst_to_sat)
         elv_log.append(np.rad2deg(elv_angle))
         if(los):
            # Satellite is in line-of-sight of the ground station
            # Check if the satellite fulfills the elevation condition                     
            if(elv_angle > np.deg2rad(gnd_stn_minelv_deg)):
               access_log.append(True)
            else:
               access_log.append(False) 
         else:
            access_log.append(False)             
      
      # Post process to create intervals
      interval_boundary = []
      flag = access_log[0]
      for k in range(1,numTimeSteps):
         if flag!=access_log[k]:
            interval_boundary.append(time_indx[k])
            flag = access_log[k]

      if access_log[0] is True: # Means the mission startes off with the satellite seeing the ground station
         if(len(interval_boundary) == 0):
            interval_boundary.append(time_indx[numTimeSteps-1]) # There is LOS for complete mission duration
         interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
         
      # interval_boundary should be even, else add the end of mission time to the interval boundary
      if(len(interval_boundary)%2 != 0):
         interval_boundary.append(time_indx[numTimeSteps-1])

      # Write detailed output file     
      with open(output_detailed_fl, 'a', newline='') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
         fwriter.writerow(['TimeIndex', 'AccessOrNoAccess', 'Range[km]','Elevation[deg]'])
         k = 0
         for k in range(0,numTimeSteps):
            fwriter.writerow([time_indx[k], access_log[k], range_log[k], elv_log[k]])
   
      # Write concise output file
      with open(output_concise_fl, 'a', newline='') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
         fwriter.writerow(['AccessFromIndex', 'AccessToIndex'])
         k = 0
         while k < len(interval_boundary):
            fwriter.writerow([interval_boundary[k], interval_boundary[k+1]])
            k = k + 2




