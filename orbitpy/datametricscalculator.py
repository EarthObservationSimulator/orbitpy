""" 
.. module:: datametricscalculator

:synopsis: *Module providing classes and functions to handle observation data-metric calculations by invoking the :code:`instrupy` package.*

"""
from collections import namedtuple
import csv
import pandas as pd


from instrupy.util import Entity
import orbitpy.util
from orbitpy.util import Spacecraft

AccessFileInfo = namedtuple("AccessFileInfo", ["instru_id", "mode_id", "access_filepath"])
""" Function returns a namedtuple class to store the parameters (``instru_id``, ``mode_id``, ``access_filepath``).
    The ``instru_id`` and ``mode_id`` specify the instrument-mode and the ``access_filepath`` specifies the 
    location of the corresponding access-data (i.e. the times and locations of access by the instrument-mode).
"""
class DataMetricsCalculator(Entity): 
    """ Class to handle computation of observational data metrics by invoking the :code:`instrupy` package.

    :ivar spacecraft: Spacecraft for which the coverage calculation is to be performed.
    :vartype spacecraft: :class:`orbitpy.util.Spacecraft`

    :ivar state_cart_file: File name with path of the (input) file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are available. 
                           Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
    :vartype state_cart_file: str

    :ivar access_file_info: List of namedtuples (sensor-id, mode-id, access-file path (with name)). 
                            
                            The namedtuple object has the name as ``AccessFileInfo`` and fields as ``instru_id``, ``mode_id`` and ``access_filepath``.
                            The access-file indicated in each tuple corresponds to the sensor-id and mode-id of the tuple. 
                            The list maybe incomplete, i.e. the access-data of *all* the possible instruments, modes of the spacecraft
                            may not be available. Use the ``add_access_file_info(.)`` function to add a new tuple to the list as they become available.
                            
                            Refer to the :class:`orbitpy.coveragecalculator` module for the format of the access-files. 
                            Note that different coverage-calculators have different access-file formats.
    :vartype access_file_info: list, :class:`orbitpy.datametricscalculator.AccessFileInfo`

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, spacecraft=None, state_cart_file=None, access_file_info=None, _id=None):
        self.spacecraft = spacecraft if spacecraft is not None and isinstance(spacecraft, Spacecraft) else None
        self.state_cart_file = str(state_cart_file) if state_cart_file is not None else None
        self.access_file_info = [] # empty list        
        if isinstance(access_file_info, list):
             if all(isinstance(x, AccessFileInfo) for x in access_file_info):
                self.access_file_info = access_file_info
        elif(isinstance(access_file_info, AccessFileInfo)): # make into list if not list
            self.access_file_info = [access_file_info]

        super(DataMetricsCalculator, self).__init__(_id, "Data Metrics Calculator")

    def add_access_file_info(self, acc_info):
        """ Add access-info of a specific instrument, mode.
        # TODO: Checks to see if the sensor-id, mode-id is exists for the spacecraft. Check for uniqueness before adding.

        :param acc_info: Namedtuple indicating path of access data file for a particular instrument, mode.
        :paramtype: :class:`orbitpy.datametricscalculator.AccessFileInfo`

        :return: None
        :rtype: None

        """
        if(isinstance(acc_info, AccessFileInfo)):
            self.access_file_info.append(acc_info)
        else:
            raise Exception("Please input the namedtuple object AccessFileInfo defined in the datametricscalculator module.")
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``DataMetricsCalculator`` object from a normalized JSON dictionary.
        
        .. todo:: Add feature to test that the specified accessFileInfo parameters (instruId and modeId) are valid (i.e. the instrument is available in the spacecraft).
        
        :param d: Dictionary with the ``DataMetricsCalculator`` specifications.

                Following keys are to be specified.
                
                * "spacecraft":             (dict) Refer to :class:`orbitpy.util.Spacecraft.from_dict`
                * "cartesianStateFilePath": (str) File path (with file name) to the file with the propgated spacecraft states. The states must be in CARTESIAN_EARTH_CENTERED_INERTIAL.
                                            Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the data format.
                * "accessFileInfo":         (list, dict). List of dictionaries, where each dictionary contains the following keys: (1) instruId (str or int), (2) modeId (str or int)
                                            and (3) accessFilePath (str). 
                * "@id":                    (str or int) Unique identifier of the datametrics calculator object.

        :paramtype d: dict

        :return: ``DataMetricsCalculator`` object.
        :rtype: :class:`orbitpy.datametricscalculator.DataMetricsCalculator`

        """
        spc_dict = d.get('spacecraft', None)
        afi_dict = d.get('accessFileInfo', None)
        afi = []
        if isinstance(afi_dict, list): # list of dictionaries
            for x in afi_dict:
                afi.append(AccessFileInfo(instru_id=x.get('instruId', None), mode_id=x.get('modeId', None), access_filepath=x.get('accessFilePath', None)))
        elif isinstance(afi_dict, dict): # single dictionary
            afi = [AccessFileInfo(instru_id=afi_dict.get('instruId', None), mode_id=afi_dict.get('modeId', None), access_filepath=afi_dict.get('accessFilePath', None))]
        else:
            afi = None
        return DataMetricsCalculator(spacecraft = Spacecraft.from_dict(spc_dict) if spc_dict else None, 
                                     state_cart_file = d.get('cartesianStateFilePath', None),
                                     access_file_info = afi,
                                     _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the ``DataMetricsCalculator`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``DataMetricsCalculator`` object as python dictionary
        :rtype: dict
        
        """
        access_file_info_dict = None
        for afi in self.access_file_info:
            access_file_info_dict.append({"instruId": afi.instru_id, "modeId": afi.mode_id, "accessFilePath": afi.access_filepath})
        return dict({"@type": "Data Metrics Calculator",
                     "spacecraft": self.to_dict,
                     "accessFileInfo" : access_file_info_dict,
                     "cartesianStateFilePath": self.state_cart_file,
                     "@id": self._id})

    def search_access_file_info(self, instru_id=None, mode_id=None):
        """ Search the list of namedtuples (of the instance ``access_file_info`` attribute) and find tuple with matching sensor-id and mode-id.

        :param instru_id: Instrument identifier. If ``None``, the first tuple in the list of the instance ``access_file_info`` attribute is returned.
        :paramtype instru_id: str (or) int

        :param mode_id: Mode identifier. If ``None``, the first tuple in the list of the instance ``access_file_info`` attribute with the matching instru_id is returned.
        :paramtype mode_id: str (or) int

        :return: (Single) Tuple of (instrument id, mode id, access filepath), such that the instrument-id and 
                 the mode-id match the input identifiers (instru_id, mode_id).
        :rtype: namedtuple, (str or int, str or int, str ) 

        """
        if self.access_file_info is not None and self.access_file_info != []:
            if instru_id is None:
                return (self.access_file_info[0])
            idx = 0
            for a,b,c in self.access_file_info:
                if a == instru_id and mode_id is None:
                    return self.access_file_info[idx]
                elif a == instru_id and b == mode_id:
                    return self.access_file_info[idx]
                idx = idx + 1
            raise Exception('Entry corresponding to the input instrument-id and mode-id was not found.')
        else:
            raise Exception('Access file info (i.e. the instance access_file_info attribute) is empty.')

    def execute(self, out_datametrics_fl, instru_id=None, mode_id=None):
        """ Execute data-metrics calculation for the specified instrument, mode in the spacecraft.
            This function iterates over the access file corresponding to the specified instrument, mode and calculates the data-metrics 
            for each access. The satellite state data is extracted from the satellite state file (CARTESIAN_EARTH_CENTERED_INERTIAL) corresponding 
            to the access-time of an access event. The target location at the access-time is available in the access data file.
        
        :param out_datametrics_fl: Filepath (with name) of the output file in which the datametrics is to be written.

                The format of the output data file is as follows:

                *  The first row contains the coverage calculation type.
                *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
                *  The third row contains the time-step size in seconds. 
                *  The fourth row contains the duration (in days) for which the data-metrics calculation is done.
                *  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

                Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

                Description of the csv data is given below:

                .. csv-table:: Observation data metrics description
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    time index, int, , Access time-index.
                    GP index, int, , Grid-point index. 
                    pnt-opt index, int, , Pointing options index.
                    lat [deg], float, degrees, Latitude corresponding to the GP index/ pnt-opt index.
                    lon [deg], float, degrees, Longitude corresponding to the GP index/ pnt-opt index.

                Other columns containing the data-metrics specific to the instrument type are present. Refer to the docs of the corresponding instrument type (in ``instrupy`` package)
                for description of the evaluated data-metrics.

        :paramtype out_datametrics_fl: str

        :param instru_id: Instrument identifier. If ``None``, the first tuple in the list of the instance ``access_file_info`` attribute is considered.
        :paramtype instru_id: str (or) int

        :param mode_id: Mode identifier. If ``None``, the first tuple in the list of the instance ``access_file_info`` attribute is considered.
        :paramtype mode_id: str (or) int

        :return: Output info.
        :rtype: :class:`orbitpy.datametricscalculator.DataMetricsOutputInfo`
        
        """
        # get instrument corresponding to the input id
        instru = self.spacecraft.get_instrument(instru_id)

        # read in the satellite states (CARTESIAN_EARTH_CENTERED_INERTIAL) and auxillary info
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(self.state_cart_file)
        sat_state_df = pd.read_csv(self.state_cart_file, skiprows=4)
        sat_state_df = sat_state_df.set_index('time index')

        # get the access file corresponding to the specified instrument, mode
        (x, y, acc_filepath) = self.search_access_file_info(instru_id, mode_id)
        access_info_df = pd.read_csv(acc_filepath, skiprows = [0,1,2,3]) # read the access times 
        # the input instru_id, mode_id may be None, so get the sensor, mode ids.
        instru_id = x
        mode_id = y
        
        # copy info rows from the original access file
        with open(acc_filepath, 'r') as f:
            head = [next(f) for x in [0,1,2,3]] 

        # erase any old file and create new one
        with open(out_datametrics_fl,'w') as f:
            for idx, r in enumerate(head):
                if idx==0:
                    f.write("Datametrics file based on " + str(r))    
                else:
                    f.write(str(r))             
        
        with open(out_datametrics_fl,'a+', newline='') as f:
            w = csv.writer(f)

            # Iterate over all logged access events
            header_written_flag = False
            idx = 0
            for idx in range(0,len(access_info_df)):       

                time_i = int(access_info_df.loc[idx]["time index"])   

                if "GP index" in access_info_df.columns:
                    gp_i = int(access_info_df.loc[idx]["GP index"]) if pd.notna(access_info_df.loc[idx]["GP index"]) else None   
                else:
                    gp_i = None

                if "pnt-opt index" in access_info_df.columns:
                    pnt_opt_i = int(access_info_df.loc[idx]["pnt-opt index"]) if pd.notna(access_info_df.loc[idx]["pnt-opt index"]) else None 
                else:
                    pnt_opt_i = None
                
                # find the target coordinates. 
                target_coords = dict()
                target_coords["lat [deg]"] = float(access_info_df.loc[idx]["lat [deg]"])
                target_coords["lon [deg]"] = float(access_info_df.loc[idx]["lon [deg]"])   

                # TODO: TEMPORARY 
                #if not (target_coords["lat [deg]"] > 35 and target_coords["lat [deg]"] < 45 and target_coords["lon [deg]"] > 280 and target_coords["lon [deg]"] < 290):
                #   continue           
                # END TEMPORARY
                
                sc_orbit_state = dict()
                sc_orbit_state["time [JDUT1]"] = epoch_JDUT1 + time_i*step_size*1.0/86400.0 
                sc_orbit_state["x [km]"] = sat_state_df.loc[time_i]["x [km]"] 
                sc_orbit_state["y [km]"] = sat_state_df.loc[time_i]["y [km]"] 
                sc_orbit_state["z [km]"] = sat_state_df.loc[time_i]["z [km]"] 
                sc_orbit_state["vx [km/s]"] = sat_state_df.loc[time_i]["vx [km/s]"] 
                sc_orbit_state["vy [km/s]"] = sat_state_df.loc[time_i]["vy [km/s]"] 
                sc_orbit_state["vz [km/s]"] = sat_state_df.loc[time_i]["vz [km/s]"] 

                obsv_metrics = instru.calc_data_metrics(mode_id=mode_id, sc_orbit_state=sc_orbit_state, target_coords=target_coords) # calculate the data metrics specific to the instrument type
                _v = dict({'time index':time_i, 'GP index': gp_i, 'pnt-opt index': pnt_opt_i, 'lat [deg]':target_coords["lat [deg]"], 'lon [deg]':target_coords["lon [deg]"]}, **obsv_metrics)
                
                if header_written_flag is False:
                    w.writerow(_v.keys())    
                    header_written_flag = True
                w.writerow(_v.values())
                idx = idx + 1
        
        return DataMetricsOutputInfo.from_dict({"@type": "DataMetricsOutputInfo",
                                                "spacecraftId": self.spacecraft._id,
                                                "instruId": instru_id,
                                                "modeId": mode_id,
                                                "accessFile": acc_filepath,
                                                "dataMetricsFile": out_datametrics_fl,
                                                "startDate": epoch_JDUT1,
                                                "duration": duration,
                                                "@id": None})

class DataMetricsOutputInfo(Entity):
    """ Class to hold information about the results of the data-metrics calculation. An object of this class is returned upon the execution
        of the data metrics calculator.
    
    :ivar spacecraftId: Spacecraft identifier.
    :vartype spacecraftId: str or int

    :param instruId: Sensor identifier.
    :paramtype instruId: str (or) int

    :param modeId: Mode identifier.
    :paramtype modeId: str (or) int 

    :ivar accessFile: File (filename with path) where the access data is saved.
    :vartype accessFile: str

    :ivar dataMetricsFile: File (filename with path) where the data-metrics data is saved.
    :vartype dataMetricsFile: str

    :ivar startDate: Time start for the data-metrics calculation in Julian Date UT1.
    :vartype startDate: float

    :ivar duration: Time duration over which data-metrics was calculated in days.
    :vartype duration: float

    :ivar _id: Unique identifier.
    :vartype _id: str or int

    """
    def __init__(self, spacecraftId=None, instruId=None, modeId=None,
                 accessFile=None, dataMetricsFile=None,  startDate=None, duration=None, _id=None):
        self.spacecraftId = spacecraftId if spacecraftId is not None else None
        self.instruId = instruId if instruId is not None else None
        self.modeId = modeId if modeId is not None else None
        self.accessFile = str(accessFile) if accessFile is not None else None
        self.dataMetricsFile = str(dataMetricsFile) if dataMetricsFile is not None else None
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None

        super(DataMetricsOutputInfo, self).__init__(_id, "DataMetricsOutputInfo")
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``DataMetricsOutputInfo`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the ``DataMetricsOutputInfo`` attributes.
        :paramtype d: dict

        :return: ``DataMetricsOutputInfo`` object.
        :rtype: :class:`orbitpy.datametricscalculator.DataMetricsOutputInfo`

        """
        return DataMetricsOutputInfo( spacecraftId = d.get('spacecraftId', None),
                                      instruId = d.get('instruId', None),
                                      modeId = d.get('modeId', None),
                                      accessFile = d.get('accessFile', None),
                                      dataMetricsFile = d.get('dataMetricsFile', None),
                                      startDate = d.get('startDate', None),
                                      duration = d.get('duration', None),
                                      _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the ``DataMetricsOutputInfo`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``DataMetricsOutputInfo`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "DataMetricsOutputInfo",
                     "spacecraftId": self.spacecraftId,
                     "instruId": self.instruId,
                     "modeId": self.modeId,
                     "accessFile": self.accessFile,
                     "dataMetricsFile": self.dataMetricsFile,
                     "startDate": self.startDate,
                     "duration": self.duration,
                     "@id": self._id})

    def __repr__(self):
        return "DataMetricsOutputInfo.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different.
        if(isinstance(self, other.__class__)):
            return (self.spacecraftId==other.spacecraftId) and (self.instruId==other.instruId) and (self.modeId==other.modeId) and \
                   (self.accessFile==other.accessFile) and  (self.dataMetricsFile==other.dataMetricsFile) and \
                   (self.startDate==other.startDate) and (self.duration==other.duration) 
                
        else:
            return NotImplemented
