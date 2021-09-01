""" 
.. module:: coveragecalculator

:synopsis: *Module providing classes and functions to handle coverage related calculations.*

.. todo:: Revise to include coverage calculations of spacecrafts without sensors.

"""
import numpy as np
from collections import namedtuple
import csv
import pandas as pd

import propcov
from instrupy.util import Entity
from orbitpy.grid import Grid
import orbitpy.util
from orbitpy.util import Spacecraft
from instrupy.util import ReferenceFrame, SphericalGeometry

DAYS_PER_SEC = 1.1574074074074074074074074074074e-5

class CoverageCalculatorFactory:
    """ Factory class which allows to register and invoke the appropriate coverage calculator class. 
    
    The following classes are registered in the factory:
    
    * :class:`GridCoverage` 
    * :class:`PointingOptionsCoverage`
    * :class:`PointingOptionsWithGridCoverage`
     
    Additional user-defined coverage calculator classes can be registered as shown below: 

    Usage: 
    
    .. code-block:: python
        
        factory = orbitpy.CoverageCalculatorFactory()
        factory.register_coverage_calculator('Custom Coverage Finder', CoverageFinder) # CoverageFinder is the user class
        cov_calc = factory.get_coverage_calculator('CoverageFinder')

    :ivar _creators: Dictionary mapping coverage type label to the appropriate coverage calculator class. 
    :vartype _creators: dict

    """
    def __init__(self):
        self._creators = {}
        self.register_coverage_calculator('GRID COVERAGE', GridCoverage)
        self.register_coverage_calculator('POINTING OPTIONS COVERAGE', PointingOptionsCoverage)
        self.register_coverage_calculator('POINTING OPTIONS WITH GRID COVERAGE', PointingOptionsWithGridCoverage)

    def register_coverage_calculator(self, _type, creator):
        """ Function to register coverage calculators.

        :var _type: Coverage calculator type (label).
        :vartype _type: str

        :var creator: Coverage calculator class.
        :vartype creator: Coverage calculator class.

        """
        self._creators[_type] = creator

    def get_coverage_calculator(self, specs):
        """ Function to get the appropriate coverage calculator instance.

        :var specs: Coverage calculator specifications which also contains a valid coverage calculator
                    type in the "@type" dict key. The coverage calculator type is valid if it has been
                    registered with the ``CoverageCalculatorFactory`` instance.
        :vartype _type: dict

        :return: The appropriate coverage calculator object initialized to the input specifications.
        :rtype: :class:`orbitpy.coveragecalculator.GridCoverage` or :class:`orbitpy.coveragecalculator.PointingOptionsCoverage` or :class:`orbitpy.coveragecalculator.PointingOptionsWithGridCoverage` or custom coverage calculator class.
                
        """
        _type = specs.get("@type", None)
        if _type is None:
            raise KeyError('Coverage Calculator type key/value pair not found in specifications dictionary.')

        creator = self._creators.get(_type)
        if not creator:
            raise ValueError(_type)
        return creator.from_dict(specs)

def helper_extract_coverage_parameters_of_spacecraft(spc):
    """ Helper function to extract tuples of (instrument_id, mode_id, scene-field-of-view, field-of-regard, pointing_option(s)).
        Only these parameters of a spacecraft are relevant to coverage calculations.
    
    :param spc: (Single) spacecraft of which coverage parameters are to be extracted.
    :paramtype spc: :class:`orbitpy.util.Spacecraft`

    :return: Tuples with instrument-id, mode-id, scene-field-of-view, field-of-regard and pointing_option(s).
    :rtype: list, namedtuple, (str or int, str or int, :class:`instrupy.util.ViewGeometry`, <list,:class:`instrupy.util.ViewGeometry`>, <list,:class:`instrupy.util.Orientation`>)

    .. note::  The field-of-regard parameter and pointing_option parameter are lists in the tuple. 

    """
    _p = namedtuple("spc_cov_params", ["instru_id", "mode_id", "scene_field_of_view", "field_of_regard", "pointing_option"])
    params = []

    if spc.instrument is not None:
        for instru in spc.instrument: # iterate over each instrument
            instru_id = instru.get_id()

            for mode_id in instru.get_mode_id(): # iterate over each mode in the instrument

                scene_field_of_view  = instru.get_scene_field_of_view(mode_id)
                field_of_regard  = instru.get_field_of_regard(mode_id) 
                pointing_option = instru.get_pointing_option(mode_id)

                if field_of_regard is None or []: # if FOR is None, use sceneFOV for FOR
                    field_of_regard = [instru.get_scene_field_of_view(mode_id)]
                
                params.append(_p(instru_id, mode_id, scene_field_of_view, field_of_regard, pointing_option))
                    
    return params

def find_in_cov_params_list(cov_param_list, instru_id=None, mode_id=None):
    """ For an input instrument-id, mode-id, find the corresponding coverage-parameter in an input list of coverage-parameters 
        (list of tuples of (instru_id, mode_id, field-of-view, field-of-regard, pointing_option)). 

    :param cov_param_list: List of tuples of (instrument id, mode id, field-of-view, field-of-regard, pointing_option).
    :paramtype cov_param_list: list, namedtuple, (str or int, str or int, :class:`instrupy.util.ViewGeometry`, <list, :class:`instrupy.util.ViewGeometry`>, <list,:class:`instrupy.util.Orientation`>)

    :param instru_id: Instrument identifier. If ``None``, the first tuple in the list of coverage parameters is returned.
    :paramtype instru_id: str (or) int

    :param mode_id: Mode identifier. If ``None``, the first tuple in the list of coverage parameters with the matching instru_id is returned.
    :paramtype mode_id: str (or) int

    :return: (Single) Tuple of (instrument id, mode id, field-of-view, field-of-regard, pointing-option(s)), such that the instrument-id and 
             the mode-id match the input identifiers (instru_id, mode_id).
    :rtype: namedtuple, (str or int, str or int, :class:`instrupy.util.ViewGeometry`, <list, :class:`instrupy.util.ViewGeometry`> , <list,:class:`instrupy.util.Orientation`> )

    """ 
    if cov_param_list is not None and cov_param_list != []:
        if instru_id is None:
            return (cov_param_list[0])
        idx = 0
        for a,b,c,d,e in cov_param_list:
            if a == instru_id and mode_id is None:
                return cov_param_list[idx]
            elif a == instru_id and b == mode_id:
                return cov_param_list[idx]
            idx = idx + 1
            
        raise Exception('Entry corresponding to the input instrument-id and mode-id was not found.')
    else:
        raise Exception('cov_param_list input argument is empty.')

def filter_mid_interval_access(inp_acc_df=None, inp_acc_fl=None, out_acc_fl=None):
        """ Extract the access times at middle of access intervals. The input can be a path to a file or a dataframe. 

        This function can be used for "correction" of access files for purely side-looking instruments with narrow along-track FOV as described below:

        In case of purely side-looking instruments with narrow-FOV (eg: SARs executing Stripmap operation mode), the access to a grid-point takes place
        when the grid-point is seen with no squint angle and the access is almost instantaneous (i.e. access duration is very small). 
        The coverage calculations is carried out with the corresponding instrument scene-field-of-view or field-of-regard (built using the scene-filed-of-view) 
        (see :code:`instrupy` package documentation). 
        If the instrument FOV is to be used for coverage calculations, a *very very* small time step-size would need to be used which to impractically long computation time.

        The access files list rows of access-time, ground-points, and thus independent access opportunities for the instrument
        when the scene-field-of-view / field-of-regard is used for coverage calculations. 
        If the generated access files from the these coverage calculations of a purely side-looking, narrow along-track FOV instrument is
        interpreted in the same manner, it would be erroneous.

        Thus the generated access files are then *corrected* to show access only at approximately (to the nearest propagation time-step) 
        the middle of the access interval. 
        This should be coupled with the required scene-scan-duration (from scene-field-of-view) to get complete information about the access. 

        .. warning:: The correction method is to be used only when the instrument access-duration (determined from the instrument FOV) is smaller 
                     than the propagation time step (determined from the sceneFOV). 

        :ivar inp_acc_df: Dataframe with the access data which needs to be filtered. The rows correspond to pairs of 
                          access time and corresponding ground-point index. The columns are to be named as: ``time index``, ``GP index``, ``lat [deg]``, ``lon [deg]``.
                          If ``None``, the ``inp_acc_fl`` input argument must be specified.
        :vartype inp_acc_df: pd.DataFrame or None

        :ivar inp_acc_fl: Input access file (filepath with filename). Refer to the ``execute`` method in the ``GridCoverage`` class
                          for description of the file format. If ``None``, the ``inp_acc_df`` input argument must be specified.
        :vartype inp_acc_fl: str or None

        :ivar out_acc_fl: Output access file (filepath with filename). The format is the same as that of the input access file. If ``None`` the file is not written.
        :vartype out_acc_fl: str or None

        :returns: Dataframe with the resultant access data.
        :rtype: pd.DataFrame

        """
        if inp_acc_fl: # If input file is specified, the data is taken from it. 
            df = pd.read_csv(inp_acc_fl, skiprows=4)            
        else:
            df = inp_acc_df

        max_num_acc = len(df.index)
        data_indx = 0
        data = np.zeros((max_num_acc,len(df.columns))) # make a data structure with maximum possible size  

        if 'pnt-opt index' in df: # pointing-options with grid coverage access file
            
            for popt, df_per_popt in df.groupby('pnt-opt index'): # iterate over each pointing-option

                # iterate over all the groups (ground-point indices)                
                for name, group in df_per_popt.groupby('GP index'):
                    x = (group['time index'].shift(periods=1) - group['time index']) < -1
                    _intv = np.where(x == True)[0]            
                    interval_indices = [0] # add the very first interval start index
                    interval_indices.extend(_intv)
                    interval_indices.extend((_intv - 1).tolist())
                    interval_indices.append(len(group)-1) # add the very last interval end index
                    interval_indices.sort()
                    mid_points = [(a + b) / 2 for a, b in zip(interval_indices[::2], interval_indices[1::2])]
                    mid_points = [int(np.round(x)) for x in mid_points]
                    _data = group.iloc[mid_points].to_numpy()
                    m = _data.shape[0]
                    data[data_indx:data_indx+m,:] = _data
                    data_indx = data_indx + m
            
            data = data[0:data_indx] # remove unnecessary rows
        
            out_df = pd.DataFrame(data = data, columns = ['time index', 'pnt-opt index', 'GP index',  'lat [deg]', 'lon [deg]'])
            out_df = out_df.astype({"time index": int, 'pnt-opt index': int, "GP index": int, "lat [deg]": float, "lon [deg]": float})

        else: # grid coverage access file

            # iterate over all the groups (ground-point indices)            
            for name, group in df.groupby('GP index'):
                x = (group['time index'].shift(periods=1) - group['time index']) < -1
                _intv = np.where(x == True)[0]            
                interval_indices = [0] # add the very first interval start index
                interval_indices.extend(_intv)
                interval_indices.extend((_intv - 1).tolist())
                interval_indices.append(len(group)-1) # add the very last interval end index
                interval_indices.sort()
                mid_points = [(a + b) / 2 for a, b in zip(interval_indices[::2], interval_indices[1::2])]
                mid_points = [int(np.round(x)) for x in mid_points]
                _data = group.iloc[mid_points].to_numpy()
                m = _data.shape[0]
                data[data_indx:data_indx+m,:] = _data
                data_indx = data_indx + m

            data = data[0:data_indx] # remove unnecessary rows
        
            out_df = pd.DataFrame(data = data, columns = ['time index', 'GP index', 'lat [deg]', 'lon [deg]'])
            out_df = out_df.astype({"time index": int, "GP index": int, "lat [deg]": float, "lon [deg]": float})
        
        out_df.sort_values(by=['time index'], inplace=True)
        out_df = out_df.reset_index(drop=True)
        
        if out_acc_fl:
            head = []
            if inp_acc_fl:
                with open(inp_acc_fl, 'r') as f1:
                    head = [next(f1) for x in range(4)] # copy first four header lines from the original access file                  

            with open(out_acc_fl, 'w') as f2:
                if head:
                    for k in range(0,len(head)):
                        f2.write(str(head[k]))
                out_df.to_csv(f2, index=False, header=True, line_terminator='\n')

        return out_df

class GridCoverage(Entity):
    """A coverage calculator class which handles coverage calculation for a spacecraft over a grid. Each ``GridCoverage`` object is specific to 
        a particular grid and spacecraft.

    :ivar grid: Locations (longitudes, latitudes) (represented by a :class:`orbitpy.util.grid` object) over which coverage calculation is to be performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar spacecraft: Spacecraft for which the coverage calculation is performed.
    :vartype spacecraft: :class:`orbitpy.util.Spacecraft`

    :ivar state_cart_file: File name with path of the (input) file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
    :vartype state_cart_file: str

    :ivar cov_params: List of coverage parameters corresponding to all the instruments, modes per instrument in the spacecraft.
                        Refer to the :class:`orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft` function.
    :vartype cov_params: list, namedtuple

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, spacecraft=None, state_cart_file=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        self.spacecraft = spacecraft if spacecraft is not None and isinstance(spacecraft, Spacecraft) else None
        self.state_cart_file = str(state_cart_file) if state_cart_file is not None else None
        # Extract the coverage related parameters
        self.cov_params = helper_extract_coverage_parameters_of_spacecraft(self.spacecraft) if self.spacecraft is not None else None

        super(GridCoverage, self).__init__(_id, "GRID COVERAGE")

    @staticmethod
    def from_dict(d):
        """ Parses an ``GridCoverage`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the GRID COVERAGE specifications.

                Following keys are to be specified.
                
                * "grid":                  (dict) Refer to :class:`orbitpy.grid.Grid.from_dict`
                * "spacecraft":            (dict) Refer to :class:`orbitpy.util.Spacecraft.from_dict`
                * "cartesianStateFilePath": (str) File path (with file name) to the file with the propgated spacecraft states. The states must be in 
                                             CARTESIAN_EARTH_CENTERED_INERTIAL. Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the data format.
                * "@id":                    (str or int) Unique identifier of the coverage calculator object.

        :paramtype d: dict

        :return: ``GridCoverage`` object.
        :rtype: :class:`orbitpy.coveragecalculator.GridCoverage`

        """
        grid_dict = d.get('grid', None)
        spc_dict = d.get('spacecraft', None)
        return GridCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                            spacecraft = Spacecraft.from_dict(spc_dict) if spc_dict else None, 
                            state_cart_file = d.get('cartesianStateFilePath', None),
                            _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the GridCoverage object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``GridCoverage`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "GRID COVERAGE",
                     "grid": self.grid.to_dict(),
                     "spacecraft": self.to_dict(),
                     "cartesianStateFilePath": self.state_cart_file,
                     "@id": self._id})

    def __repr__(self):
        return "GridCoverage.from_dict({})".format(self.to_dict())

    def execute(self, instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=None, filter_mid_acc=False):
        """ Perform orbit coverage calculation for a specific instrument and mode of the instrument in the object instance. Coverage is calculated for the period over which the 
            input spacecraft propagated states are available. The time-resolution of the coverage calculation is the 
            same as the time resolution at which the spacecraft states are available. Note that the sceneFOV of an instrument (which may be the same as the instrument FOV)
            is used for coverage calculations unless it has been specified to use the field-of-regard.

        :param instru_id: Instrument identifier (must be present in the input spacecraft). If ``None``, the first instrument in the spacecraft's list of instruments is considered.
        :paramtype instru_id: str (or) int

        :param mode_id: Mode identifier (corresponding to the input instrument (id)). If ``None``, the first mode of the instrument is considered.
        :paramtype mode_id: str (or) int

        :param use_field_of_regard: This is a boolean flag to specify if the the field-of-regard is to be considered for the coverage calculations. 
                                    Default value is ``False`` (i.e. the scene-field-of-view will be considered in the coverage calculations).
        :paramtype use_field_of_regard: bool

        :param out_file_access: File name with path of the file in which the access data is written. If ``None`` the file is not written.
                
                The file format is as follows:

                *  The first row contains the coverage calculation type.
                *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
                *  The third row contains the time-step size in seconds. 
                *  The fourth row contains the duration (in days) for which coverage calculation is executed.
                *  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

                Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

                Description of the coverage data is given below:

                .. csv-table:: Coverage data description
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    time index, int, , Access time-index.
                    GP index, int, , Grid-point index.
                    lat [deg], float, degrees, Latitude corresponding to the GP index.
                    lon [deg], float, degrees, Longitude corresponding to the GP index.

        :paramtype out_file_access: str

        :param filter_mid_acc: Flag to indicate if the coverage data is to be processed to indicate only the access at the middle of an (continuous) access-interval. 
                                Default value is ``False``.
        :paramtype filter_mid_acc: bool

        :return: Coverage output info.
        :rtype: :class:`orbitpy.coveragecalculator.CoverageOutputInfo`

        """
        ###### read in the propagated states and auxillary information ######               
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(self.state_cart_file)
        states_df = pd.read_csv(self.state_cart_file, skiprows=4)

        ###### Prepare output file in which results shall be written ######
        if out_file_access:
            access_file = open(out_file_access, 'w', newline='')
            access_writer = csv.writer(access_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            access_writer.writerow(["GRID COVERAGE"])
            access_writer.writerow(["Epoch [JDUT1] is {}".format(epoch_JDUT1)])
            access_writer.writerow(["Step size [s] is {}".format(step_size)])
            access_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            access_writer.writerow(['time index','GP index', 'lat [deg]', 'lon [deg]'])
        
        ###### find the FOV/ FOR corresponding to the input sensor-id, mode-id  ######
        cov_param= find_in_cov_params_list(self.cov_params, instru_id, mode_id)
        #print("cov_param ", cov_param)
        # the input instru_id, mode_id may be None, so get the sensor, mode ids.
        instru_id = cov_param.instru_id
        mode_id = cov_param.mode_id

        if use_field_of_regard is True:
            view_geom = cov_param.field_of_regard # a list
        else:
            view_geom = [cov_param.scene_field_of_view] # make into list 
            
        
        #print("view_geom ", view_geom)
        ###### iterate and calculate coverage seperately for each view_geom element. TODO: Streamline this behavior ######
        for __view_geom in view_geom:
            
            ###### form the propcov.Spacecraft object ######
            attitude = propcov.NadirPointingAttitude()
            interp = propcov.LagrangeInterpolator()

            spc = propcov.Spacecraft(self.spacecraft.orbitState.date, self.spacecraft.orbitState.state, attitude, interp, 0, 0, 0, 1, 2, 3)
            # orient the spacecraft-bus
            spc_orien = self.spacecraft.spacecraftBus.orientation
            if spc_orien.ref_frame == ReferenceFrame.NADIR_POINTING:            
                spc.SetBodyNadirOffsetAngles(angle1=spc_orien.euler_angle1, angle2=spc_orien.euler_angle2, angle3=spc_orien.euler_angle3, # input angles are in degrees
                                            seq1=spc_orien.euler_seq1, seq2=spc_orien.euler_seq2, seq3=spc_orien.euler_seq3)            
            else:
                raise NotImplementedError # only NADIR_POINTING reference frame is supported.           

            ###### build the sensor object ######
            sen_sph_geom = __view_geom.sph_geom
            if(sen_sph_geom.shape == SphericalGeometry.Shape.CIRCULAR):
                sensor= propcov.ConicalSensor(halfAngle = 0.5*np.deg2rad(sen_sph_geom.diameter)) # input angle in radians
            elif(sen_sph_geom.shape == SphericalGeometry.Shape.RECTANGULAR or sen_sph_geom.shape == SphericalGeometry.Shape.CUSTOM):
                sensor = propcov.CustomSensor( coneAngleVecIn    =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.cone_angle_vec   )   )   ),  # input angle in radians  
                                               clockAngleVecIn   =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.clock_angle_vec  )   )   )   
                                             )         
            else:
                raise Exception("please input valid sensor spherical geometry shape.")

            sen_orien = __view_geom.orien
            if (sen_orien.ref_frame == ReferenceFrame.SC_BODY_FIXED) or (sen_orien.ref_frame == ReferenceFrame.NADIR_POINTING and spc_orien.ref_frame == ReferenceFrame.NADIR_POINTING): # The second condition is equivalent of orienting sensor w.r.t spacecraft body if the spacecraft body is aligned to nadir-frame
                sensor.SetSensorBodyOffsetAngles(angle1=sen_orien.euler_angle1, angle2=sen_orien.euler_angle2, angle3=sen_orien.euler_angle3, # input angles are in degrees
                                                 seq1=sen_orien.euler_seq1, seq2=sen_orien.euler_seq2, seq3=sen_orien.euler_seq3)
            else:
                raise NotImplementedError
            
            ###### attach the sensor ######
            spc.AddSensor(sensor)
            ###### make propcov coverage checker object ######
            cov_checker = propcov.CoverageChecker(self.grid.point_group, spc)
            ###### iterate over the propagated states ######
            date = propcov.AbsoluteDate()
            for idx, state in states_df.iterrows():
                time_index = int(state['time index'])
                jd_date = epoch_JDUT1 + time_index*step_size*DAYS_PER_SEC
                date.SetJulianDate(jd_date)
                
                cart_state = [state['x [km]'], state['y [km]'], state['z [km]'], state['vx [km/s]'], state['vy [km/s]'], state['vz [km/s]']]
                spc.SetOrbitStateCartesian(date, propcov.Rvector6(cart_state))
                
                # compute coverage
                points = cov_checker.CheckPointCoverage() # list of indices of the GPs accessed shall be returned
                if len(points)>0: #If no ground-points are accessed at this time, skip writing the row altogether.
                    for pnt in points:
                        coords = self.grid.get_lat_lon_from_index(pnt)
                        access_writer.writerow([time_index, pnt, coords.latitude, coords.longitude])

        ##### Close file #####                
        if access_file:
            access_file.close()

        ##### filter mid-interval access data if necessary #####
        if filter_mid_acc is True:
            filter_mid_interval_access(inp_acc_fl=out_file_access, out_acc_fl=out_file_access)        
        
        return CoverageOutputInfo.from_dict({"@type": "CoverageOutputInfo",
                                                "coverageType": "GRID COVERAGE",
                                                "spacecraftId": self.spacecraft._id,
                                                "instruId": instru_id,
                                                "modeId": mode_id,
                                                "usedFieldOfRegard": use_field_of_regard,
                                                "filterMidIntervalAccess": filter_mid_acc,
                                                "gridId": self.grid._id,
                                                "stateCartFile": self.state_cart_file,
                                                "accessFile": out_file_access,
                                                "startDate": epoch_JDUT1,
                                                "duration": duration,
                                                "@id": None})
            
class PointingOptionsCoverage(Entity):
    """A coverage calculator which handles coverage calculation for an instrument (on a spacecraft) with a set of pointing-options.
       A pointing-option refers to orientation of the instrument in the NADIR_POINTING frame. The set of pointing-options 
       represent all the possible orientations of the instrument due to maneuverability of the instrument and/or satellite-bus.
       The ground-locations for each pointing-option, at each propagation time-step is calculated as the coverage result.      

    :ivar spacecraft: Spacecraft for which the coverage calculation is performed. The pointing options are included in the instrument definitions of the spacecraft. 
    :vartype spacecraft: :class:`orbitpy.util.Spacecraft`

    :ivar state_cart_file: File name with path of the (input) file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
                           Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
    :vartype state_cart_file: str

    :ivar cov_params: List of coverage parameters corresponding to all the instruments, modes per instrument in the spacecraft.
                        Refer to the :class:`orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft` function.
    :vartype cov_params: list, namedtuple

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, spacecraft=None, state_cart_file=None, _id=None):
        self.spacecraft = spacecraft if spacecraft is not None and isinstance(spacecraft, Spacecraft) else None
        self.state_cart_file = str(state_cart_file) if state_cart_file is not None else None
        # Extract the coverage related parameters
        self.cov_params = helper_extract_coverage_parameters_of_spacecraft(self.spacecraft) if self.spacecraft is not None else None

        super(PointingOptionsCoverage, self).__init__(_id, "POINTING OPTIONS COVERAGE")

    @staticmethod
    def from_dict(d):
        """ Parses an ``PointingOptionsCoverage`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the GridCoverage specifications.

                Following keys are to be specified.
                
                * "spacecraft":             (dict) Refer to :class:`orbitpy.util.Spacecraft.from_dict`
                * "cartesianStateFilePath": (str) File path (with file name) to the file with the propgated spacecraft states. The states must be in 
                                             CARTESIAN_EARTH_CENTERED_INERTIAL. Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the data format.
                * "@id":                    (str or int) Unique identifier of the coverage calculator object.

        :paramtype d: dict

        :return: ``PointingOptionsCoverage`` object.
        :rtype: :class:`orbitpy.coveragecalculator.PointingOptionsCoverage`

        """
        spc_dict = d.get('spacecraft', None)
        return PointingOptionsCoverage(spacecraft = Spacecraft.from_dict(spc_dict) if spc_dict else None, 
                                       state_cart_file = d.get('cartesianStateFilePath', None),
                                            _id  = d.get('@id', None))

    
    def to_dict(self):
        """ Translate the PointingOptionsCoverage object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``PointingOptionsCoverage`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "POINTING OPTIONS COVERAGE",
                     "spacecraft": self.to_dict,
                     "cartesianStateFilePath": self.state_cart_file,
                     "@id": self._id})

    def __repr__(self):
        return "PointingOptionsCoverage.from_dict({})".format(self.to_dict())

    @staticmethod
    def intersect_vector_sphere(r, o, vec_direc):
        """  Find intersection of an input vector with a sphere. The origin of the reference-frame (in which the input vector is expressed)
             is assumed to be at the center of the sphere.
             https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection  
        
        :param r: Radius of sphere.
        :paramtype r: float

        :param o: Cartesian coordinates of the start position of the vector.
        :paramtype o: list, float

        :param vec_direc: Direction of the vector.
        :paramtype vec_direc: list, float

        :return: Cartesian coordinates of the intersection point if valid intersection, else ``False`` to indicate no intersection.
        :rtype: list, float

        """
        o = np.array(o)
        vec_direc = np.array(vec_direc)
        # normalize direction vector        
        norm = np.linalg.norm(vec_direc)
        if(norm == 0):
            raise Exception("Encountered division by zero in vector normalization function.")
        l = vec_direc/norm 

        under_root = np.dot(l, o)**2 - (np.dot(o,o)-np.dot(r,r))
        if under_root > 0:
            d1 = -1*np.dot(l, o) - np.sqrt(under_root)
            d2 = -1*np.dot(l, o) + np.sqrt(under_root)
            if np.abs(d1) < np.abs(d2): # find the point closest to the sphere wrt the vector origin
                intersect_point = o + np.dot(l,d1)
            else:
                intersect_point = o + np.dot(l,d2)
            
        elif under_root == 0:
            d = -1*np.dot(l,o)
            intersect_point = o + np.dot(l,d)
        else:
            return False
        
        return intersect_point.tolist()

    def execute(self, instru_id=None, mode_id=None, out_file_access=None):
        """ Perform coverage calculation for a specific instrument and mode. Coverage is calculated for the period over which the 
            input spacecraft propagated states are available. The time-resolution of the coverage calculation is the 
            same as the time resolution at which the spacecraft states are available.

        :param instru_id: Sensor identifier (corresponding to the input spacecraft). If ``None``, the first sensor in the spacecraft list of sensors is considered.
        :paramtype instru_id: str (or) int

        :param mode_id: Mode identifier (corresponding to the input sensor (id) and spacecraft). If ``None``, the first mode of the corresponding input sensor of the spacecraft is considered.
        :paramtype mode_id: str (or) int        

        :param out_file_access: File name with path of the file in which the access data is written. If ``None`` the file is not written.
                
                The format of the output data file is as follows:

                *  The first row contains the coverage calculation type.
                *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
                *  The third row contains the time-step size in seconds. 
                *  The fourth row contains the duration (in days) for which coverage calculation is executed.
                *  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

                Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

                Description of the coverage data is given below:

                .. csv-table:: Coverage data description
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    time index, int, , Access time-index.
                    pnt-opt index, int, , "Pointing options index. The indexing starts from 0, where 0 is the first pointing-option in the list of instrument pointing-options."
                    lat [deg], float, degrees, Latitude of accessed ground-location.
                    lon [deg], float, degrees, Longitude of accessed ground-location.
        
        :paramtype out_file_access: str

        :return: Coverage output info.
        :rtype: :class:`orbitpy.coveragecalculator.CoverageOutputInfo`

        """
        ###### read in the propagated states and auxillary information ######               
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(self.state_cart_file)
        states_df = pd.read_csv(self.state_cart_file, skiprows=4)

        earth = propcov.Earth()

        ###### Prepare output file in which results shall be written ######
        if out_file_access:
            access_file = open(out_file_access, 'w', newline='')
            access_writer = csv.writer(access_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            access_writer.writerow(["POINTING OPTIONS COVERAGE"])
            access_writer.writerow(["Epoch [JDUT1] is {}".format(epoch_JDUT1)])
            access_writer.writerow(["Step size [s] is {}".format(step_size)])
            access_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            access_writer.writerow(['time index', 'pnt-opt index', 'lat [deg]', 'lon [deg]'])
        
        ###### find the pointing-options corresponding to the input sensor-id, mode-id  ######
        cov_param = find_in_cov_params_list(self.cov_params, instru_id, mode_id)
        pointing_option = cov_param.pointing_option
        if pointing_option is None:
            print("No pointing options specified for the particular sensor, mode. Exiting PointingOptionsCoverage.")
            return
        # the input instru_id, mode_id may be None, so get the sensor, mode ids.
        instru_id = cov_param.instru_id
        mode_id = cov_param.mode_id
        ###### iterate over the propagated states ######
        date = propcov.AbsoluteDate()
        for idx, state in states_df.iterrows():
            time_index = int(state['time index'])
            jd_date = epoch_JDUT1 + time_index*step_size*DAYS_PER_SEC
            date.SetJulianDate(jd_date)
            
            cart_state = [state['x [km]'], state['y [km]'], state['z [km]'], state['vx [km/s]'], state['vy [km/s]'], state['vz [km/s]']]
            orbit_state = propcov.OrbitState.fromCartesianState(propcov.Rvector6(cart_state))
            
            # iterate over all pointing options
            if pointing_option:
                for pnt_opt_idx, pnt_opt in enumerate(pointing_option): # note that the pointing-option is indexed from 0 onwards
                    ###### form the propcov.Spacecraft object ######
                    attitude = propcov.NadirPointingAttitude()
                    interp = propcov.LagrangeInterpolator()

                    spc = propcov.Spacecraft(date, orbit_state, attitude, interp, 0, 0, 0, 1, 2, 3)

                    # orient the spacecraft-bus according to the pointing-option. Assumed that the instrument-pointing axis is aligned to the spacecraft-bus z-axis.
                    if pnt_opt.ref_frame == ReferenceFrame.NADIR_POINTING:            
                        spc.SetBodyNadirOffsetAngles(angle1=pnt_opt.euler_angle1, angle2=pnt_opt.euler_angle2, angle3=pnt_opt.euler_angle3, # input angles are in degrees
                                                    seq1=pnt_opt.euler_seq1, seq2=pnt_opt.euler_seq2, seq3=pnt_opt.euler_seq3)            
                    else:
                        raise NotImplementedError # only NADIR_POINTING reference frame is supported.
                    
                    rot_N2B = spc.GetNadirToBodyMatrix()
                    earth_fixed_state = earth.GetBodyFixedState(propcov.Rvector6(cart_state), jd_date)
                    rot_EF2N = spc.GetBodyFixedToReference(earth_fixed_state) # Earth fixed to Nadir
                    rot_EF2B = rot_N2B * rot_EF2N
                    # find the direction of the pointing axis (z-axis of the satellite body) in the Earth-Fixed frame                
                    pnt_axis = [rot_EF2B.GetElement(2,0), rot_EF2B.GetElement(2,1), rot_EF2B.GetElement(2,2)] # Equivalelent to pnt_axis = R_EF2B.Transpose() * Rvector3(0,0,1)
                    earth_fixed_state = earth_fixed_state.GetRealArray()
                    earth_fixed_pos = [earth_fixed_state[0], earth_fixed_state[1], earth_fixed_state[2]]

                    intersect_point = PointingOptionsCoverage.intersect_vector_sphere(earth.GetRadius(), earth_fixed_pos, pnt_axis)

                    if intersect_point is not False:
                        geo_coords = earth.Convert(propcov.Rvector3(intersect_point), "Cartesian", "Spherical").GetRealArray()
                        access_writer.writerow([time_index, pnt_opt_idx, np.round(np.rad2deg(geo_coords[0]),3), np.round(np.rad2deg(geo_coords[1]),3)])

        ##### Close file #####                
        if access_file:
            access_file.close()
        
        return CoverageOutputInfo.from_dict({"@type": "CoverageOutputInfo",
                                                "coverageType": "POINTING OPTIONS COVERAGE",
                                                "spacecraftId": self.spacecraft._id,
                                                "instruId": instru_id,
                                                "modeId": mode_id,
                                                "usedFieldOfRegard": None,
                                                "filterMidIntervalAccess": None,
                                                "gridId": None,
                                                "stateCartFile": self.state_cart_file,
                                                "accessFile": out_file_access,
                                                "startDate": epoch_JDUT1,
                                                "duration": duration,
                                                "@id": None})

class PointingOptionsWithGridCoverage(Entity):
    """A coverage calculator which handles coverage calculation for a spacecraft over a grid for a set of pointing-options (of an instrument (on a spacecraft)).   
        A pointing-option refers to orientation of the instrument in the NADIR_POINTING frame. Set of pointing-options 
        represent all the possible orientations of the instrument due to maneuverability of the instrument and/or satellite-bus.
        Access opportunities (set of access-time, grid-point) is calculated seperately for each pointing-option at each propagation time-step.
        Each coverage object is specific to a particular grid and spacecraft. 

    :ivar grid: Locations (longitudes, latitudes) over which coverage calculation is to be performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar spacecraft: Spacecraft for which the coverage calculation is performed.
    :vartype spacecraft: :class:`orbitpy.util.Spacecraft`

    :ivar state_cart_file: File name with path of the (input) file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
                           Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the file data format.
    :vartype state_cart_file: str

    :ivar cov_params: List of coverage parameters corresponding to all the instruments, modes per instrument in the spacecraft.
                        Refer to the :class:`orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft` function.
    :vartype cov_params: list, namedtuple

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, spacecraft=None, state_cart_file=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        self.spacecraft = spacecraft if spacecraft is not None and isinstance(spacecraft, Spacecraft) else None
        self.state_cart_file = str(state_cart_file) if state_cart_file is not None else None
        # Extract the coverage related parameters
        self.cov_params = helper_extract_coverage_parameters_of_spacecraft(self.spacecraft) if self.spacecraft is not None else None

        super(PointingOptionsWithGridCoverage, self).__init__(_id, "POINTING OPTIONS WITH GRID COVERAGE")

    @staticmethod
    def from_dict(d):
        """ Parses an ``PointingOptionsWithGridCoverage`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the PointingOptionsWithGridCoverage specifications.

                Following keys are to be specified.
                
                * "grid":                  (dict) Refer to :class:`orbitpy.grid.Grid.from_dict`
                * "spacecraft":            (dict) Refer to :class:`orbitpy.util.Spacecraft.from_dict`
                * "cartesianStateFilePath": (str) File path (with file name) to the file with the propgated spacecraft states. The states must be in 
                                             CARTESIAN_EARTH_CENTERED_INERTIAL. Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the data format.
                * "@id":                    (str or int) Unique identifier of the coverage calculator object.

        :paramtype d: dict

        :return: ``PointingOptionsWithGridCoverage`` object.
        :rtype: :class:`orbitpy.coveragecalculator.PointingOptionsWithGridCoverage`

        """
        grid_dict = d.get('grid', None)
        spc_dict = d.get('spacecraft', None)
        return PointingOptionsWithGridCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                                               spacecraft = Spacecraft.from_dict(spc_dict) if spc_dict else None, 
                                               state_cart_file = d.get('cartesianStateFilePath', None),
                                               _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the GridCoverage object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``PointingOptionsWithGridCoverage`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "POINTING OPTIONS WITH GRID COVERAGE",
                     "grid": self.grid.to_dict,
                     "spacecraft": self.to_dict,
                     "cartesianStateFilePath": self.state_cart_file,
                     "@id": self._id})

    def __repr__(self):
        return "PointingOptionsWithGridCoverage.from_dict({})".format(self.to_dict())

    def execute(self, instru_id=None, mode_id=None, out_file_access=None, filter_mid_acc=False):
        """ Perform orbit coverage calculation for a specific instrument and mode. 
            The scene-field-of-view of the instrument is considered (no scope to use field-of-regard) in the coverage calculation. 
            Coverage is calculated for the period over which the input spacecraft propagated states are available. 
            The time-resolution of the coverage calculation is the same as the time resolution at which the spacecraft states are available.
            The access-times, grid-points are calculated seperately for each pointing-option.
            Note that the sceneFOV of an instrument (which may be the same as the instrument FOV) is used for coverage calculations.

        :param instru_id: Sensor identifier (corresponding to the input spacecraft). If ``None``, the first sensor in the spacecraft list of sensors is considered.
        :paramtype instru_id: str (or) int

        :param mode_id: Mode identifier (corresponding to the input sensor (id) and spacecraft). If ``None``, the first mode of the corresponding input sensor of the spacecraft is considered.
        :paramtype mode_id: str (or) int

        :param out_file_access: File name with path of the file in which the access data is written. If ``None`` the file is not written.
                
                The format of the output data file is as follows:

                *  The first row contains the coverage calculation type.
                *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
                *  The third row contains the time-step size in seconds. 
                *  The fourth row contains the duration (in days) for which coverage calculation is executed.
                *  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

                Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

                Description of the coverage data is given below:

                .. csv-table:: Coverage data description
                    :header: Column, Data type, Units, Description
                    :widths: 10,10,10,30

                    time index, int, , Access time-index.
                    pnt-opt index, int, , "Pointing options index. The indexing starts from 0, where 0 is the first pointing-option in the list of instrument pointing-options."
                    GP index, int, , Grid-point index.
                    lat [deg], float, degrees, Latitude corresponding to the GP index.
                    lon [deg], float, degrees, Longitude corresponding to the GP index.
        
        :paramtype out_file_access: str

        :param filter_mid_acc: Flag to indicate if the coverage data is to be processed to indicate only the access at the middle of an (continuous) access-interval. 
                                Default value is ``False``.
        :paramtype filter_mid_acc: bool

        :return: Coverage output info.
        :rtype: :class:`orbitpy.coveragecalculator.CoverageOutputInfo`

        """
        ###### read in the propagated states and auxillary information ######               
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(self.state_cart_file)
        states_df = pd.read_csv(self.state_cart_file, skiprows=4)

        ###### Prepare output file in which results shall be written ######
        if out_file_access:
            access_file = open(out_file_access, 'w', newline='')
            access_writer = csv.writer(access_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            access_writer.writerow(["POINTING OPTIONS WITH GRID COVERAGE"])
            access_writer.writerow(["Epoch [JDUT1] is {}".format(epoch_JDUT1)])
            access_writer.writerow(["Step size [s] is {}".format(step_size)])
            access_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            access_writer.writerow(['time index','pnt-opt index', 'GP index', 'lat [deg]', 'lon [deg]'])
        
        ###### find the coverage-parameters of the input sensor-id, mode-id  ######
        cov_param= find_in_cov_params_list(self.cov_params, instru_id, mode_id)
        
        # the input instru_id, mode_id may be None, so get the sensor, mode ids.
        instru_id = cov_param.instru_id
        mode_id = cov_param.mode_id

        sen_sph_geom = cov_param.scene_field_of_view.sph_geom # only the spherical geometry of the sensor is required. the orientation is ignored, since the pointing-option gives the orientation of the pointing-axis in the NADIR_POINTING frame.
        pointing_option = cov_param.pointing_option
        if pointing_option is None:
            print("No pointing options specified for the particular sensor, mode. Exiting PointingOptionsWithGridCoverage.")
            return

        ###### iterate and calculate coverage seperately for each pointing-option.
        for pnt_opt_idx, pnt_opt in enumerate(pointing_option):
            
            ###### form the propcov.Spacecraft object ######
            attitude = propcov.NadirPointingAttitude()
            interp = propcov.LagrangeInterpolator()
            spc = propcov.Spacecraft(self.spacecraft.orbitState.date, self.spacecraft.orbitState.state, attitude, interp, 0, 0, 0, 1, 2, 3) # align spacecraft to NADIR_POINTING frame
          
            ###### build the sensor object ######
            if(sen_sph_geom.shape == SphericalGeometry.Shape.CIRCULAR):
                sensor= propcov.ConicalSensor(halfAngle = 0.5*np.deg2rad(sen_sph_geom.diameter)) # input angle in radians
            elif(sen_sph_geom.shape == SphericalGeometry.Shape.RECTANGULAR or sen_sph_geom.shape == SphericalGeometry.Shape.CUSTOM):
                sensor = propcov.CustomSensor( coneAngleVecIn    =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.cone_angle_vec   )   )   ),  # input angle in radians  
                                               clockAngleVecIn   =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.clock_angle_vec  )   )   )   
                                             )         
            else:
                raise Exception("please input valid sensor spherical geometry shape.")
            # orient sensor according to the pointing-option
            if (pnt_opt.ref_frame == ReferenceFrame.NADIR_POINTING): 
                sensor.SetSensorBodyOffsetAngles(angle1=pnt_opt.euler_angle1, angle2=pnt_opt.euler_angle2, angle3=pnt_opt.euler_angle3, # input angles are in degrees
                                                   seq1=pnt_opt.euler_seq1, seq2=pnt_opt.euler_seq2, seq3=pnt_opt.euler_seq3)
            else:
                raise NotImplementedError
            
            ###### attach the sensor ######
            spc.AddSensor(sensor)
            ###### make propcov coverage checker object ######
            cov_checker = propcov.CoverageChecker(self.grid.point_group, spc)
            ###### iterate over the propagated states ######
            date = propcov.AbsoluteDate()
            for idx, state in states_df.iterrows():
                time_index = int(state['time index'])
                jd_date = epoch_JDUT1 + time_index*step_size*DAYS_PER_SEC
                date.SetJulianDate(jd_date)
                
                cart_state = [state['x [km]'], state['y [km]'], state['z [km]'], state['vx [km/s]'], state['vy [km/s]'], state['vz [km/s]']]
                spc.SetOrbitStateCartesian(date, propcov.Rvector6(cart_state))
                
                # compute coverage
                points = cov_checker.CheckPointCoverage() # list of indices of the GPs accessed shall be returned
                if len(points)>0: #If no ground-points are accessed at this time, skip writing the row altogether.
                    for pnt in points:
                        coords = self.grid.get_lat_lon_from_index(pnt)
                        access_writer.writerow([time_index, pnt_opt_idx, pnt, coords.latitude, coords.longitude])

        ##### Close file #####                
        if access_file:
            access_file.close()

        ##### filter mid-interval access data if necessary #####
        if filter_mid_acc is True:
            #inp_acc_df = pd.read_csv(out_file_access, skiprows = 4)
            filter_mid_interval_access(inp_acc_fl=out_file_access, out_acc_fl=out_file_access)

        return CoverageOutputInfo.from_dict({"@type": "CoverageOutputInfo",
                                                "coverageType": "POINTING OPTIONS WITH GRID COVERAGE",
                                                "spacecraftId": self.spacecraft._id,
                                                "instruId": instru_id,
                                                "modeId": mode_id,
                                                "usedFieldOfRegard": None,
                                                "filterMidIntervalAccess": filter_mid_acc,
                                                "gridId": self.grid._id,
                                                "stateCartFile": self.state_cart_file,
                                                "accessFile": out_file_access,
                                                "startDate": epoch_JDUT1,
                                                "duration": duration,
                                                "@id": None})

class CoverageOutputInfo(Entity):
    """ Class to hold information about the results of the coverage calculation. An object of this class is returned upon the execution
        of the coverage calculator.
    
    :ivar coverageType: Type of coverage calculator which produced the results.
    :vartype coverageType: str

    :ivar spacecraftId: Spacecraft identifier.
    :vartype spacecraftId: str or int

    :param instruId: Sensor identifier.
    :paramtype instruId: str (or) int

    :param modeId: Mode identifier.
    :paramtype modeId: str (or) int 

    :param usedFieldOfRegard: Boolean flag which indicates if the field-of-regard was used in the coverage calculations. 
                              If not relevant the value is ``None``. 
    :paramtype usedFieldOfRegard: bool (or) None

    :param filterMidIntervalAccess: Flag to indicate if the coverage data is to be processed to indicate only the access at the middle of an (continuous) access-interval. 
                                       If not relevant (such as in the case of pointing-options coverage) the value is ``None``. 
    :paramtype filterMidIntervalAccess: bool (or) None

    :param gridId: Grid identifier. 
    :paramtype gridId: str (or) int 

    :ivar stateCartFile: State file (filename with path) where the time-series of the cartesian states of the spacecraft are saved.
    :vartype stateCartFile: str

    :ivar accessFile: File (filename with path) where the access data is saved.
    :vartype accessFile: str

    :ivar startDate: Time start for coverage calculation in Julian Date UT1.
    :vartype startDate: float

    :ivar duration: Time duration over which coverage was calculated in days.
    :vartype duration: float

    :ivar _id: Unique identifier.
    :vartype _id: str or int

    """
    def __init__(self, coverageType=None, spacecraftId=None, instruId=None, modeId=None, usedFieldOfRegard=None, filterMidIntervalAccess=None, 
                 gridId=None,  stateCartFile=None, accessFile=None, startDate=None, duration=None, _id=None):
        self.coverageType = coverageType if coverageType is not None else None
        self.spacecraftId = spacecraftId if spacecraftId is not None else None
        self.instruId = instruId if instruId is not None else None
        self.modeId = modeId if modeId is not None else None
        self.gridId = gridId if gridId is not None else None 
        self.usedFieldOfRegard = usedFieldOfRegard if usedFieldOfRegard is not None else None
        self.filterMidIntervalAccess = bool(filterMidIntervalAccess) if filterMidIntervalAccess is not None else None
        self.stateCartFile = str(stateCartFile) if stateCartFile is not None else None
        self.accessFile = str(accessFile) if accessFile is not None else None
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None

        super(CoverageOutputInfo, self).__init__(_id, "CoverageOutputInfo")
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``CoverageOutputInfo`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the CoverageOutputInfo attributes.
        :paramtype d: dict

        :return: ``CoverageOutputInfo`` object.
        :rtype: :class:`orbitpy.coveragecalculator.CoverageOutputInfo`

        """
        return CoverageOutputInfo( coverageType = d.get('coverageType', None),
                                   spacecraftId = d.get('spacecraftId', None),
                                   instruId = d.get('instruId', None),
                                   modeId = d.get('modeId', None),
                                   usedFieldOfRegard = d.get('usedFieldOfRegard', None),
                                   filterMidIntervalAccess = d.get('filterMidIntervalAccess', None),
                                   gridId = d.get('gridId', None),
                                   stateCartFile = d.get('stateCartFile', None),
                                   accessFile = d.get('accessFile', None),
                                   startDate = d.get('startDate', None),
                                   duration = d.get('duration', None),
                                   _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the CoverageOutputInfo object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``CoverageOutputInfo`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "CoverageOutputInfo",
                     "coverageType": self.coverageType,
                     "spacecraftId": self.spacecraftId,
                     "instruId": self.instruId,
                     "modeId": self.modeId,
                     "usedFieldOfRegard": self.usedFieldOfRegard,
                     "filterMidIntervalAccess": self.filterMidIntervalAccess,
                     "gridId": self.gridId,
                     "stateCartFile": self.stateCartFile,
                     "accessFile": self.accessFile,
                     "startDate": self.startDate,
                     "duration": self.duration,
                     "@id": self._id})

    def __repr__(self):
        return "CoverageOutputInfo.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different.
        if(isinstance(self, other.__class__)):
            return (self.coverageType==other.coverageType) and (self.spacecraftId==other.spacecraftId) and (self.instruId==other.instruId) and (self.modeId==other.modeId) and \
                   (self.usedFieldOfRegard==other.usedFieldOfRegard) and (self.filterMidIntervalAccess == other.filterMidIntervalAccess) and (self.gridId==other.gridId) and  (self.stateCartFile==other.stateCartFile) and (self.accessFile==other.accessFile) and \
                    (self.startDate==other.startDate) and (self.duration==other.duration) 
                
        else:
            return NotImplemented