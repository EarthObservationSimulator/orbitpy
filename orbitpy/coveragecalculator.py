""" 
.. module:: coveragecalculator

:synopsis: *Module providing classes and functions to handle coverage related calculations.*

"""
import numpy as np
from collections import namedtuple
import csv
import pandas as pd

import propcov
from instrupy.util import Entity, Constants
from orbitpy.grid import Grid
import orbitpy.util
from orbitpy.util import Spacecraft
from instrupy.util import ViewGeometry, Orientation, ReferenceFrame, SphericalGeometry

DAYS_PER_SEC = 1.1574074074074074074074074074074e-5

class CoverageCalculatorFactory:
    """ Factory class which allows to register and invoke the appropriate coverage calculator class. 
    
    The following classes are registered in the factory:
    
    * :class:`GridCoverage` 
    * :class:`PointingOptionCoverage`
    * :class:`GridWithPointingOptionCoverage`
     
    Additional user-defined coverage calculator classes can be registered as shown below: 

    Usage: 
    
    .. code-block:: python
        
        factory = orbitpy.CoverageCalculatorFactory()
        factory.register_coverage_calculator('Custom Coverage Finder', CoverageFinder)
        cov_calc1 = factory.get_coverage_calculator('CoverageFinder')

    :ivar _creators: Dictionary mapping coverage type label to the appropriate coverage calculator class. 
    :vartype _creators: dict

    """
    def __init__(self):
        self._creators = {}
        self.register_coverage_calculator('Grid Coverage', GridCoverage)
        self.register_coverage_calculator('Pointing Options Coverage', PointingOptionsCoverage)
        self.register_coverage_calculator('Pointing Options With Grid Coverage', PointingOptionsWithGridCoverage)

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
                    type in the "@type" dict key. The propagator type is valid if it has been
                    registered with the ``CoverageCalculatorFactory`` instance.
        :vartype _type: dict
        
        """
        _type = specs.get("@type", None)
        if _type is None:
            raise KeyError('Coverage Calculator type key/value pair not found in specifications dictionary.')

        creator = self._creators.get(_type)
        if not creator:
            raise ValueError(_type)
        return creator.from_dict(specs)

def helper_extract_coverage_parameters_of_spacecraft(spc):
    """ Helper function to extract tuples of (sensor_id, mode_id, field-of-view, field-of-regard).
        Only these parameters of a spacecraft are relevant to coverage calculations.
    
    :param spc: (Single) spacecraft of which coverage parameters are to be extracted.
    :paramtype spc: :class:`orbitpy.util.Spacecraft`

    :return: Tuples with instrument-id, mode-id, field-of-view, field-of-regard.
    :rtype: list, namedtuple, (str or int, str or int, :class:`instrupy.util.ViewGeometry`, <list,:class:`instrupy.util.ViewGeometry`>)

    .. note::  The field-of-regard parameter is a list in the tuple. 

    """
    _p = namedtuple("spc_cov_params", ["instru_id", "mode_id", "field_of_view", "field_of_regard"])
    params = []

    if spc.instrument is not None:
        for instru in spc.instrument: # iterate over each instrument
            instru_id = instru.get_id()

            for mode_id in instru.get_mode_id():# iterate over each mode in the instrument

                field_of_view  = instru.get_field_of_view(mode_id)
                field_of_regard  = instru.get_field_of_regard(mode_id) 

                if field_of_regard is None or []: # if FOR is None, use FOV for FOR
                    field_of_regard = [instru.get_field_of_view(mode_id)]
                
                params.append(_p(instru_id, mode_id, field_of_view, field_of_regard))
                    
    return params

def find_in_cov_params_list(cov_param_list, sensor_id=None, mode_id=None):
    """ For an input instrument-id, mode-id, find the corresponding FOV, FOR in an input list of coverage-parameters 
        (list of tuples of (sensor_id, mode_id, field-of-view, field-of-regard)). 

    :param cov_param_list: List of tuples of (instrument id, mode id, field-of-view, field-of-regard).
    :paramtype cov_param_list: list, namedtuple, <str or int, str or int, :class:`instrupy.util.ViewGeometry`, :class:`instrupy.util.ViewGeometry`>

    :param sensor_id: Instrument identifier. If ``None``, the first tuple in the list of coverage parameters is considered.
    :paramtype sensor_id: str (or) int

    :param mode_id: Mode identifier. If ``None``, the first tuple in the list of coverage parameters is considered.
    :paramtype mode_id: str (or) int

    :return: (Single) Tuples of (instrument id, mode id, field-of-view, field-of-regard), such that the instrument-id and 
             the mode-id match the (corresponding) input identifiers.
    :rtype: namedtuple, <str or int, str or int, :class:`instrupy.util.ViewGeometry`, :class:`instrupy.util.ViewGeometry`>

    """ 
    if cov_param_list is not None and cov_param_list != []:
        if sensor_id is None:
            return (cov_param_list[0])
        for a,b,c,d in cov_param_list:
            if a == sensor_id and mode_id is None:
                return (a,b,c,d)
            elif a == sensor_id and b == mode_id:
                return (a,b,c,d)
            
        raise Exception('Entry corresponding to the input instrument-id and mode-id was not found.')
    else:
        return None

class GridCoverage(Entity):
    """A coverage calculator which handles coverage calculation for a spacecraft over a grid. Each coverage object is specific to 
        a particular grid and spacecraft.  

    :ivar grid: Array of locations (longitudes, latitudes) over which coverage calculation is performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar spacecraft: Spacecraft for which the coverage calculation is performed.
    :vartype spacecraft: :class:`orbitpy.util.Spacecraft`

    :ivar state_cart_file: File name with path of the (input) file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are available.
    :vartype state_cart_file: str

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, spacecraft=None, state_cart_file=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        self.spacecraft = spacecraft if spacecraft is not None and isinstance(spacecraft, Spacecraft) else None
        self.state_cart_file = str(state_cart_file) if state_cart_file is not None else None
        # Extract the coverage related parameters
        self.cov_params = helper_extract_coverage_parameters_of_spacecraft(self.spacecraft) if self.spacecraft is not None else None

        super(GridCoverage, self).__init__(_id, "Grid Coverage")

    @staticmethod
    def from_dict(d):
        """ Parses an GridCoverage object from a normalized JSON dictionary.
        
        :param d: Dictionary with the GridCoverage specifications.

                Following keys are to be specified.
                
                * "grid":                  (dict) Refer to :class:`orbitpy.grid.Grid.from_dict`
                * "spacecraft":            (dict) Refer to :class:`orbitpy.util.Spacecraft.from_dict`
                * "cartesianStateFilePath": (str) File path (with file name) to the file with the propgated spacecraft states. The states must be in 
                                             CARTESIAN_EARTH_CENTERED_INERTIAL. Refer to :class:`orbitpy.propagator.J2AnalyticalPropagator.execute` for description of the data format.
                * "@id":                    (str or int) Unique identifier of the coverage calculator object.

        :paramtype d: dict

        :return: GridCoverage object.
        :rtype: :class:`orbitpy.coveragecalculator.GridCoverage`

        """
        grid_dict = d.get('grid', None)
        spc_dict = d.get('spacecraft', None)
        return GridCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                            spacecraft = Spacecraft.from_dict(spc_dict) if spc_dict else None, 
                            state_cart_file = d.get('cartesianStateFilePath', None),
                            _id  = d.get('@id', None))

    
    def execute(self, sensor_id=None, mode_id=None, use_field_of_regard=False, out_file_access=None):
        """ Perform orbit coverage calculation for a specific instrument and mode. Coverage is calculated for the period over which the 
            input spacecraft propagated states are available. The time-resolution of the coverage calculation is the 
            same as the time resolution at which the spacecraft states are available. The complete-access output corresponds 
            to the data with **all** the access-times over (all) the grid of ground-points. The mid-access data 
            file corresponds to the access-time only **at the middle of an access-interval** over (all) the grid
            of ground-points.        

        :param sensor_id: Sensor identifier (corresponding to the input spacecraft). If ``None``, the first sensor in the spacecraft list of sensors is considered.
        :paramtype sensor_id: str (or) int

        :param mode_id: Mode identifier (corresponding to the input sensor (id) and spacecraft). If ``None``, the first mode of the corresponding input sensor of the spacecraft is considered.
        :paramtype mode_id: str (or) int

        :param use_field_of_regard: This is a boolean flag to specify if the field-of-view is to be considered or the field-of-regard is to be considered for the coverage calculations. 
                                    Default value is ``False`` (i.e. the field-of-view is to be considered in the coverage calculations).
        :paramtype use_field_of_regard: bool

        :param out_file_access: File name with path of the file in which the access data is written. If ``None`` the file is not written.
        :paramtype out_file_access: str

        :return: 0 if success. The results are stored in a csv data-file at the indicated file-path.
        :rtype: int

        """
        ###### read in the propagated states and auxillary information ######               
        (epoch_JDUT1, step_size, duration) = orbitpy.util.extract_auxillary_info_from_state_file(self.state_cart_file)
        states_df = pd.read_csv(self.state_cart_file, skiprows=4)

        ###### Prepare output file in which results shall be written ######
        if out_file_access:
            access_file = open(out_file_access, 'w', newline='')
            access_writer = csv.writer(access_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            access_writer.writerow(["Complete access data file."])
            access_writer.writerow(["Epoch [JDUT1] is {}".format(epoch_JDUT1)])
            access_writer.writerow(["Step size [s] is {}".format(step_size)])
            access_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            access_writer.writerow(['time index','GP index'])

        ###### form the propcov.Spacecraft object ######
        attitude = propcov.NadirPointingAttitude()
        interp = propcov.LagrangeInterpolator()

        spc = propcov.Spacecraft(self.spacecraft.orbitState.date, self.spacecraft.orbitState.state, attitude, interp, 0, 0, 0, 1, 2, 3)
        # orient the spacecraft
        spc_orien = self.spacecraft.spacecraftBus.orientation
        if spc_orien.ref_frame == ReferenceFrame.NADIR_POINTING:            
            spc.SetBodyNadirOffsetAngles(angle1=spc_orien.euler_angle1, angle2=spc_orien.euler_angle2, angle3=spc_orien.euler_angle3, # input angles are in degrees
                                         seq1=spc_orien.euler_seq1, seq2=spc_orien.euler_seq2, seq3=spc_orien.euler_seq3)            
        else:
            raise NotImplementedError # only NADIR_POINTING reference frame is supported.
        ###### find the FOV/ FOR corresponding to the input sensor-id, mode-id  ######
        cov_param= find_in_cov_params_list(self.cov_params, sensor_id, mode_id)
        if use_field_of_regard is True:
            sensor_view_geom = cov_param.field_of_regard # a list
        else:
            sensor_view_geom = [cov_param.field_of_view] # make into list 
        
        ###### iterate and calculate coverage seperately for each sensor_view_geom element. TODO: Streamline this behavior ######
        
        # initialize variables to be used in the loop
        date = propcov.AbsoluteDate()

        for sen_view_geom in sensor_view_geom:
            
            ###### build the sensor object ######
            sen_sph_geom = sen_view_geom.sph_geom
            if(sen_sph_geom.shape == SphericalGeometry.Shape.CIRCULAR):
                sensor= propcov.ConicalSensor(halfAngle = 0.5*np.deg2rad(sen_sph_geom.diameter)) # input angle in radians
            elif(sen_sph_geom.shape == SphericalGeometry.Shape.RECTANGULAR or sen_sph_geom.shape == SphericalGeometry.Shape.CUSTOM):
                sensor = propcov.CustomSensor( coneAngleVecIn   =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.cone_angle_vec   )   )   ),  # input angle in radians  
                                              clockAngleVecIn   =   propcov.Rvector(  np.deg2rad( np.array( sen_sph_geom.clock_angle_vec  )   )   )   
                                             )         
            else:
                raise Exception("please input valid sensor spherical geometry shape.")

            sen_orien = sen_view_geom.orien
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
            #states_df.reset_index()
            for idx, state in states_df.iterrows():
                time_index = int(state['time index'])
                _date = epoch_JDUT1 + time_index*step_size*DAYS_PER_SEC
                date.SetJulianDate(_date)
                
                cart_state = [state['x [km]'], state['y [km]'], state['z [km]'], state['vx [km/s]'], state['vy [km/s]'], state['vz [km/s]']]
                spc.SetOrbitStateCartesian(date, propcov.Rvector6(cart_state))
                
                # compute coverage
                points = cov_checker.CheckPointCoverage() # list of indices of the GPs accessed shall be returned
                if len(points)>0: #If no ground-points are accessed at this time, skip writing the row altogether.
                    for pnt in points:
                        access_writer.writerow([time_index, pnt])

        ##### Close files #####                
        if access_file:
            access_file.close()

        return 0
            
class PointingOptionsCoverage(Entity):
    """A coverage calculator which calculates coverage over a grid.

    The instance variable(s) correspond to the coverage calculator setting(s). 

    :ivar grid: Array of locations (longitudes, latitudes) over which coverage calculation is performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        super(PointingOptionsCoverage, self).__init__(_id, "Pointing Options Coverage")

    @staticmethod
    def from_dict(d):
        grid_dict = d.get('grid', None)
        return PointingOptionsCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                            _id  = d.get('@id', None))


class PointingOptionsWithGridCoverage(Entity):
    """A coverage calculator which calculates coverage over a grid.

    The instance variable(s) correspond to the coverage calculator setting(s). 

    :ivar grid: Array of locations (longitudes, latitudes) over which coverage calculation is performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        super(PointingOptionsWithGridCoverage, self).__init__(_id, "Pointing Options With Grid Coverage")

    @staticmethod
    def from_dict(d):
        grid_dict = d.get('grid', None)
        return PointingOptionsWithGridCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                            _id  = d.get('@id', None))