""" 
.. module:: intersatellitecomm

:synopsis: *Module to handle computation of inter-satellite communications periods.*

"""
import os
import shutil
import pandas as pd
import csv
import numpy as np
from .util import Constants, MathUtilityFunctions

class InterSatelliteComm:
   """ Class to handle computation of inter-satellite communication periods.
       The class takes as input, a directory path containing satellite states 
       present in separate files. As output, it produces periods of contact
       between any two satellites (in separate files for each possible pair 
       of satellites). 
   """
   def __init__(self, user_dir, state_dir, comm_dir, opaque_atmos_height_km):
      self.user_dir = user_dir
      self.state_dir = state_dir
      self.comm_dir = comm_dir
      self.opaque_atmos_height_km = opaque_atmos_height_km
      

   def compute_all_contacts(self):
      try:
         _path, _dirs, filenames = next(os.walk(self.state_dir))
      except StopIteration:
         pass

      number_of_files = len(filenames)


      for indx1 in range(0,number_of_files):

         sat1_filename = filenames[indx1]
         sat1 = pd.read_csv(self.state_dir+sat1_filename, skiprows=5, header=None, delimiter=r",")
         sat1 = sat1[:-1]
         time_s = sat1.iloc[:,0]

         sat1_x_km = sat1.iloc[:,1]
         sat1_y_km = sat1.iloc[:,2]
         sat1_z_km = sat1.iloc[:,3]
         
         for indx2 in range(indx1+1,number_of_files):
               
               sat2_filename = filenames[indx2]

               with open(self.state_dir+sat1_filename) as fd:
                  reader = csv.reader(fd)
                  epoch = [row for idx, row in enumerate(reader) if idx == 1]
                  epoch = str(epoch)[3:-3]

               sat2 = pd.read_csv(self.state_dir+sat2_filename, skiprows=5, header=None, delimiter=r",")
               sat2 = sat2[:-1]               

               sat2_x_km = sat2.iloc[:,1]
               sat2_y_km = sat2.iloc[:,2]
               sat2_z_km = sat2.iloc[:,3]

               # Loop over entire mission duration
               numTimeSteps = len(time_s)
               access_log = []
               range_log = []
               for indx in range(0,numTimeSteps):
                  # Get satellite coordinates in ECI coordinate frame
                  sat1_position = np.array([sat1_x_km[indx], sat1_y_km[indx], sat1_z_km[indx]]).astype(float)
                  sat2_position = np.array([sat2_x_km[indx], sat2_y_km[indx], sat2_z_km[indx]]).astype(float)

                  access_log.append(MathUtilityFunctions.checkLOSavailability(sat1_position, sat2_position, Constants.radiusOfEarthInKM + self.opaque_atmos_height_km))

                  sat12_km = sat2_position - sat1_position
                  r_sat12_km = np.sqrt(np.dot(sat12_km, sat12_km))
                  range_log.append(r_sat12_km)
                  
               # Post process to create intervals
               interval_boundary = []
               flag = access_log[0]
               for indx in range(1,numTimeSteps):
                  if flag!=access_log[indx]:
                     interval_boundary.append(time_s[indx])
                     flag = access_log[indx]

               if access_log[0] is True: # Means the mission startes off with the satellite seeing each other
                  if(len(interval_boundary) == 0):
                     interval_boundary.append(time_s[numTimeSteps-1]) # There is LOS for complete mission duration
                  interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
                  
               # interval_boundary should be even, else add the end of mission time to the interval boundary
               if(len(interval_boundary)%2 != 0):
                  interval_boundary.append(time_s[numTimeSteps-1])
      
               # Write detailed output file
               output_detailed_filename = sat1_filename+"_to_"+sat2_filename+"_detailed.csv"
               f = open(self.comm_dir + output_detailed_filename, "w")
               f.write(epoch)
               f.write("\n")
               f.close()
               with open(self.comm_dir + output_detailed_filename, 'a', newline='') as csvfile:
                  fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                  fwriter.writerow(['Time[s]', 'AccessOrNoAccess', 'Range[km]'])
                  indx = 0
                  for indx in range(0,len(time_s)):
                     fwriter.writerow([time_s[indx], access_log[indx], range_log[indx]])
                     

               output_concise_filename = sat1_filename+"_to_"+sat2_filename+"_concise.csv"
               # Concise file        
               f = open(self.comm_dir + output_concise_filename, "w")
               f.write(epoch)
               f.write("\n")
               f.close()
               with open(self.comm_dir + output_concise_filename, 'a', newline='') as csvfile:
                  fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                  fwriter.writerow(['AccessFrom[s]', 'AccessTo[s]'])
                  indx = 0
                  while indx < len(interval_boundary):
                     fwriter.writerow([interval_boundary[indx], interval_boundary[indx+1]])
                     indx = indx + 2

class GroundStationComm:
   """ Class to handle computation of contact periods between 
       satellites and ground stations. 
   """
   def __init__(self, user_dir = None, state_dir = None, gndstn_dir = None, gnd_stn_fl = None):
      self.user_dir = user_dir
      self.state_dir = state_dir
      self.gndstn_dir = str(gndstn_dir)        
      try:
         try:
            self.gnd_stn_specs = pd.read_csv(gnd_stn_fl, header=0, delimiter=r",")
         except:
            print('Error in reading ground-station(s) specifications file.')
            raise  
      except:
         raise Exception("Error in processing (initialization) of ground station contacts.")
         

   def compute_all_contacts(self):
      """ Compute contact intervals between all satellites and all the ground stations
      """ 

      try:
         _path, _dirs, satfilenames = next(os.walk(self.state_dir))
      except StopIteration:
         pass

      # Iterate over all satellites
      for indx1 in range(0,len(satfilenames)):

         sat_filename = satfilenames[indx1]
         sat = pd.read_csv(self.state_dir+sat_filename, skiprows=5, header=None, delimiter=r",")
         sat = sat[:-1]

         time_s = sat.iloc[:,0]
         sat_x_km = sat.iloc[:,1]
         sat_y_km = sat.iloc[:,2]
         sat_z_km = sat.iloc[:,3]

         with open(self.state_dir+sat_filename) as fd:
                  reader = csv.reader(fd)
                  epoch = [row for idx, row in enumerate(reader) if idx == 1]
                  epoch = str(epoch)[3:-3]
         _epoch = float(str(epoch).split()[2])
         
         # Iterate over all ground stations
         for indx2 in range(0,self.gnd_stn_specs.shape[0]):
               
               gnd_stn_i = int(self.gnd_stn_specs.iloc[indx2]['index'])
               gnd_stn_lat = float(self.gnd_stn_specs.iloc[indx2]['lat[deg]'])
               gnd_stn_lon = float(self.gnd_stn_specs.iloc[indx2]['lon[deg]'])
               gnd_stn_alt = float(self.gnd_stn_specs.iloc[indx2]['alt[km]'])
               gnd_stn_minelv = float(self.gnd_stn_specs.iloc[indx2]['minElevation[deg]'])

                # Loop over entire mission duration
               numTimeSteps = len(time_s)
               access_log = []
               range_log = []
               elv_log = []
               for indx in range(0,numTimeSteps):

                  # Get satellite coordinates in ECI frame
                  sat_position = np.array([sat_x_km[indx], sat_y_km[indx], sat_z_km[indx]]).astype(float)
                  
                  # Get ground station coordinates in ECI frame
                  time_JDUT1 = _epoch + time_s[indx]*(1.0/(24*60*60))
                  gnd_stn_coords_eci = MathUtilityFunctions.geo2eci([gnd_stn_lat, gnd_stn_lon, gnd_stn_alt], time_JDUT1)

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
                     if(elv_angle > np.deg2rad(gnd_stn_minelv)):
                        access_log.append(True)
                     else:
                        access_log.append(False) 
                  else:
                     access_log.append(False)             
               
               # Post process to create intervals
               interval_boundary = []
               flag = access_log[0]
               for indx in range(1,numTimeSteps):
                  if flag!=access_log[indx]:
                     interval_boundary.append(time_s[indx])
                     flag = access_log[indx]

               if access_log[0] is True: # Means the mission startes off with the satellite seeing the ground station
                  if(len(interval_boundary) == 0):
                     interval_boundary.append(time_s[numTimeSteps-1]) # There is LOS for complete mission duration
                  interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
                  
               # interval_boundary should be even, else add the end of mission time to the interval boundary
               if(len(interval_boundary)%2 != 0):
                  interval_boundary.append(time_s[numTimeSteps-1])
      
               # Write detailed output file
               output_detailed_filename = sat_filename+"_to_gndSt"+str(gnd_stn_i)+"_detailed.csv"
               f = open(self.gndstn_dir + output_detailed_filename, "w")
               f.write(epoch)
               f.write("\n")
               f.close()
               with open(self.gndstn_dir + output_detailed_filename, 'a', newline='') as csvfile:
                  fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                  fwriter.writerow(['Time[s]', 'AccessOrNoAccess', 'Range[km]','Elevation[deg]'])
                  indx = 0
                  for indx in range(0,len(time_s)):
                     fwriter.writerow([time_s[indx], access_log[indx], range_log[indx], elv_log[indx]])
                     

               output_concise_filename = sat_filename+"_to_gndSt"+str(gnd_stn_i)+"_concise.csv"
               # Concise file        
               f = open(self.gndstn_dir + output_concise_filename, "w")
               f.write(epoch)
               f.write("\n")
               f.close()
               with open(self.gndstn_dir + output_concise_filename, 'a', newline='') as csvfile:
                  fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                  fwriter.writerow(['AccessFrom[s]', 'AccessTo[s]'])
                  indx = 0
                  while indx < len(interval_boundary):
                     fwriter.writerow([interval_boundary[indx], interval_boundary[indx+1]])
                     indx = indx + 2





