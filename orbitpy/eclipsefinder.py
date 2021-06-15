""" 
.. module:: eclipsefinder

:synopsis: *Module to find eclipse times, i.e. the times at which the spacecraft does not have an line-of-sight
            to the Sun.* 

"""

import numpy as np
import copy
import pandas as pd
import csv
from collections import namedtuple

from instrupy.util import Entity, EnumEntity, Constants, MathUtilityFunctions, GeoUtilityFunctions
import orbitpy.util
from orbitpy.util import Spacecraft, GroundStation

class EclipseFinder(Entity):
    
    class OutType(EnumEntity):
        """ Indicates the type of output data to be saved. 'INTERVAL' indicates that the eclipse time-intervals are stored, 
            while 'DETAIL' stores the eclipse (true or false) at each time-step of mission.  
        """
        INTERVAL = 'INTERVAL'
        DETAIL = 'DETAIL'

    @staticmethod
    def execute(spacecraft, out_dir, state_cart_fl, out_filename=None, out_type=OutType.INTERVAL):
        """ Find the eclipse times of a spacecraft. The eclipsed times correspond to the times when the line-of-sight does *NOT* exist between 
            the spacecraft and Sun.

        The results are available in two different formats *INTERVAL* or *DETAIL* (either of which can be specified in the input argument ``out_type``).

        1. *INTERVAL*: The first line of the file indicates the spacecraft identifier. The second line contains the epoch in Julian Date UT1. The 
            third line contains the step-size in seconds. The later lines contain the interval data in csv format with the following column headers:

            .. csv-table:: Contact file INTERVAL data format
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    start index, int, , Eclipse start time-index.
                    stop index, int, , Eclipse stop time-index.

        2. *DETAIL*: The first line of the file indicates the spacecraft identifier. The second line contains the epoch in Julian Date UT1. The 
            third line contains the step-size in seconds. The later lines contain the interval data in csv format with the following column headers:

            .. csv-table:: Eclipse file INTERVAL data format
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    time index, int, , Time-index.
                    eclipse, bool, , 'T' indicating True or F indicating False.

        :param spacecraft: Spacecraft object.
        :paramtype spacecraft: :class:`orbitpy.util.Spacecraft`

        :param out_dir: Path to directory where the file with results is to be stored.
        :paramtype out_dir: str

        :param state_cart_fl: File name with path of the (input) file in which the orbit states (of the input spacecraft) in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
                              Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
        :paramtype state_cart_fl: str

        :param out_filename: Name of output file in when the results are written. If not specified, the output filename is: *eclipse.csv*
        :paramtype out_filename: str or None

        :param out_type: Indicates the type of output data to be saved. Default is OutType.INTERVAL.
        :paramtype out_type: :class:`orbitpy.eclipsefinder.EclipseFinder.OutType`

        :return: Output info.
        :rtype: :class:`orbitpy.eclipsefinder.EclipseFinderOutputInfo`

        """
        state_df = pd.read_csv(state_cart_fl, skiprows=4)
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(state_cart_fl)

        time_indx = list(state_df['time index'])
        numTimeSteps = len(time_indx)
        A_pos = state_df
        A_x_km = list(state_df['x [km]'])
        A_y_km = list(state_df['y [km]'])
        A_z_km = list(state_df['z [km]'])

        # get the coordinates of the Sun in the ECI frame at the different times of the mission.
        B_x_km = [None] * numTimeSteps
        B_y_km = [None] * numTimeSteps
        B_z_km = [None] * numTimeSteps
        for idx, value in enumerate(time_indx):
            time_JDUT1 = epoch_JDUT1 + value*step_size*(1.0/86400.0) 
            coords_eci = GeoUtilityFunctions.SunVector_ECIeq(time_JDUT1)
            B_x_km[idx] = coords_eci[0]
            B_y_km[idx] = coords_eci[1]
            B_z_km[idx] = coords_eci[2]   
        
        # construct output filepath
        if out_filename:
            out_filepath = out_dir + '/' + out_filename
        else:
            out_filepath = out_dir + '/' + 'eclipse.csv'

        # create and initialize output file
        with open(out_filepath, 'w') as out:
            out.write('Eclipse times for Spacecraft with id {}\n'.format(spacecraft._id))
            out.write('Epoch [JDUT1] is {}\n'.format(epoch_JDUT1))
            out.write('Step size [s] is {}\n'.format(step_size))

        # Loop over entire mission duration        
        eclipse_log = [None] * numTimeSteps
        for idx, value in enumerate(time_indx):

            A_pos = np.array([A_x_km[idx], A_y_km[idx], A_z_km[idx]]).astype(float)
            B_pos = np.array([B_x_km[idx], B_y_km[idx], B_z_km[idx]]).astype(float)
            
            los = GeoUtilityFunctions.checkLOSavailability(A_pos, B_pos, Constants.radiusOfEarthInKM)

            eclipse_log[idx] = not los # if los, no eclipse

        if out_type == EclipseFinder.OutType.DETAIL:
            # Write DETAIL output file
            data = pd.DataFrame(list(zip(time_indx, eclipse_log)), columns=['time index', 'eclipse'])
            data.to_csv(out_filepath, mode='a', index=False)
        
        elif out_type == EclipseFinder.OutType.INTERVAL:    
            # Post process to create intervals
            interval_boundary = [] # TODO: Having variable-sized list could slow down computation in case of large number of intervals
            flag = eclipse_log[0]
            for indx in range(1,numTimeSteps):
                if flag!=eclipse_log[indx]:
                    interval_boundary.append(time_indx[indx])
                    flag = eclipse_log[indx]

            if eclipse_log[0] is True: # Means the mission starts off with the satellite seeing each other
                if(len(interval_boundary) == 0):
                    interval_boundary.append(time_indx[numTimeSteps-1]) # There is LOS for complete mission duration
                interval_boundary = [0] + interval_boundary  # append start of LOS, which is start of mission
                
            # interval_boundary should be even, else add the end of mission time to the interval boundary
            if(len(interval_boundary)%2 != 0):
                interval_boundary.append(time_indx[numTimeSteps-1])

            # write results           
            with open(out_filepath, 'a', newline='') as csvfile:
                fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                fwriter.writerow(['start index', 'end index'])
                indx = 0
                while indx < len(interval_boundary):
                    fwriter.writerow([interval_boundary[indx], interval_boundary[indx+1]])
                    indx = indx + 2    

        else:
            raise RuntimeError("Unknown specification of the contact finder output data format.") 

        
        
        return EclipseFinderOutputInfo.from_dict({"@type": "EclipseFinderOutputInfo",
                                                "spacecraftId": spacecraft._id,
                                                "stateCartFile": state_cart_fl,
                                                "eclipseFile": out_filepath,
                                                "outType": out_type.value,
                                                "startDate": epoch_JDUT1,
                                                "duration": duration,
                                                "@id": None})
             
class EclipseFinderOutputInfo(Entity):
    """ Class to hold information about the results of the eclipse-finder. An object of this class is returned upon the execution
        of the eclipse finder.
    
    :ivar spacecraftId: Spacecraft identifier.
    :vartype spacecraftId: str or int

    :ivar stateCartFile: File (filename with path) where the spacecraft time-series state data is saved.
    :vartype stateCartFile: str

    :ivar eclipseFile: File (filename with path) where the eclipse data are saved.
    :vartype eclipseFile: str

    :param out_type: Indicates the type of output data to be saved.
    :paramtype out_type: :class:`orbitpy.eclipsefinder.EclipseFinder.OutType`

    :ivar startDate: Time start for eclipse-finder calculations in Julian Date UT1.
    :vartype startDate: float

    :ivar duration: Time duration in days for which the eclipse-finder calculations were carried out.
    :vartype duration: float

    :ivar _id: Unique identifier.
    :vartype _id: str or int

    """
    def __init__(self, spacecraftId=None, stateCartFile=None, 
                 eclipseFile=None, outType=None, startDate=None, duration=None, _id=None):
        self.spacecraftId = spacecraftId if spacecraftId is not None else None
        self.stateCartFile = str(stateCartFile) if stateCartFile is not None else None
        self.eclipseFile = str(eclipseFile) if eclipseFile is not None else None
        self.outType = EclipseFinder.OutType.get(outType) if outType is not None else None
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None

        super(EclipseFinderOutputInfo, self).__init__(_id, "EclipseFinderOutputInfo")
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``EclipseFinderOutputInfo`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the EclipseFinderOutputInfo attributes.
        :paramtype d: dict

        :return: EclipseFinderOutputInfo object.
        :rtype: :class:`orbitpy.eclipsefinder.EclipseFinderOutputInfo`

        """
        out_type_str = d.get('outType', None)
        
        return EclipseFinderOutputInfo( spacecraftId = d.get('spacecraftId', None),
                                        stateCartFile = d.get('stateCartFile', None),
                                        eclipseFile = d.get('eclipseFile', None),
                                        outType =  EclipseFinder.OutType.get(out_type_str) if out_type_str is not None else None,
                                        startDate = d.get('startDate', None),
                                        duration = d.get('duration', None),
                                        _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the EclipseFinderOutputInfo object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: EclipseFinderOutputInfo object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "EclipseFinderOutputInfo",
                     "spacecraftId": self.spacecraftId,
                     "stateCartFile": self.stateCartFile,
                     "eclipseFile": self.eclipseFile,
                     "outType": self.outType.value,
                     "startDate": self.startDate,
                     "duration": self.duration,
                     "@id": self._id})

    def __repr__(self):
        return "EclipseFinderOutputInfo.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes.Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.spacecraftId==other.spacecraftId) and (self.stateCartFile==other.stateCartFile) and \
                   (self.eclipseFile==other.eclipseFile) and  (self.outType==other.outType) and \
                   (self.startDate==other.startDate) and (self.duration==other.duration) 
                
        else:
            return NotImplemented