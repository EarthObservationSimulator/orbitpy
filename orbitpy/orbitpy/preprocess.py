""" 
.. module:: preprocess

:synopsis: *Module to handle pre-processing of user inputs.*

.. note::  - Any input latitudes must be in the range -pi/2 to pi/2, while longitudes must be in the range -pi to pi.

"""
import numpy as np
import os
import subprocess
import json
import shutil
import glob
import warnings
from .util import *
from instrupy.public_library import Instrument
import instrupy

class ConstellationType(EnumEntity):
    """Enumeration of recognized constellation types"""
    CUSTOM = "CUSTOM",
    WALKERDELTA = "WALKERDELTA"
class GridType(EnumEntity):
    """Enumeration of recognized coverage-grid types"""
    CUSTOM = "CUSTOMGRID",
    AUTOGRID = "AUTOGRID"
class FOVGeometry(EnumEntity):
    """Enumeration of recognized instrument sensor geometries."""
    CONICAL = "CONICAL",
    RECTANGULAR = "RECTANGULAR",
    CUSTOM = "CUSTOM"

class PntOptsRefFrame(EnumEntity):
    """Enumeration of recognized reference frames used in specification of the pointing."""
    NADIRREFFRAME = "NADIRREFFRAME"

class OrbitParameters():
    """ Data structure to hold parameters defining the orbit of a satellite in the constellation. An orbit is 
        assumed to be unique for a satellite.

    .. note:: Epoch is defined to be common for all the orbits in the mission and is hence defined separately.
    
    :ivar @_id: Unique identifier of the orbit (satellite)
    :vartype @_id: str

    :ivar sma: Semi-major axis in kilometers
    :vartype sma: float

    :ivar ecc: Eccentricity (:math:0<=ecc<1)
    :vartype ecc: float

    :ivar inc: Inclination in degrees
    :vartype inc: float

    :ivar raan: Right Ascension of Ascending Node in degrees
    :vartype raan: float

    :ivar aop: Argument of Perigee in degrees
    :vartype aop: float

    :ivar ta: True Anomaly in degrees
    :vartype ta: float
    
    """
    def __init__(self, _id = None, sma = None, ecc = None, inc = None, raan = None, aop = None, ta = None):
        self._id = str(_id) if _id is not None else None
        self.sma = float(sma) if sma is not None else None
        self.ecc = float(ecc) if ecc is not None else None
        self.inc = float(inc) if inc is not None else None
        self.raan = float(raan) if raan is not None else None
        self.aop = float(aop) if aop is not None else None
        self.ta = float(ta) if ta is not None else None

class InstrumentCoverageParameters():
    """ Data structure to hold instrument coverage related parameters.

    :ivar fov_geom: Geometry of the field-of-view
    :vartype fov_geom: :class:`FOVGeometry`

    :ivar fov_cone: List of cone angles in degrees
    :vartype fov_cone: list, float

    :ivar fov_clock: List of clock angles in degrees
    :vartype fov_clock: list, float

    :ivar fov_at: Along-track FOV in degrees
    :vartype fov_at: float

    :ivar fov_ct: Cross-track FOV in degrees
    :vartype fov_ct: float

    :ivar orien_eu_seq1: Euler sequence 1
    :vartype orien_eu_seq1: int

    :ivar orien_eu_seq2: Euler sequence 2
    :vartype orien_eu_seq2: int

    :ivar orien_eu_seq3: Euler sequence 3
    :vartype orien_eu_seq3: int

    :ivar orien_eu_ang1: Euler angle 1 in degrees
    :vartype orien_eu_ang1: float

    :ivar orien_eu_ang2: Euler angle 2 in degrees
    :vartype orien_eu_ang2: float

    :ivar orien_eu_ang3: Euler angle 3 in degrees
    :vartype orien_eu_ang3: float

    :ivar purely_side_look: Flag to specify if instrument operates in a strictly side-looking viewing geometry.
    :vartype purely_side_look: bool

    :ivar yaw180_flag: Flag applies in case of field-of-regard. If true, it signifies that the field-of-regard includes the field-of-view of payload rotated along nadir by 180 deg. 
    :vartype yaw180_flag: bool
    
    """
    def __init__(self, fov_geom = None, fov_cone = None, fov_clock = None, fov_at = None, fov_ct = None, 
                 orien_eu_seq1 = None, orien_eu_seq2 = None, orien_eu_seq3 = None, 
                 orien_eu_ang1 = None, orien_eu_ang2 = None, orien_eu_ang3 = None,
                 purely_side_look = None, yaw180_flag = None):
        
 
        self.fov_geom = FOVGeometry.get(fov_geom) if fov_geom is not None else None
        self.fov_cone = [float(i) for i in fov_cone] if fov_cone is not None else None
        self.fov_clock = [float(i) for i in fov_clock] if fov_clock is not None else None # clock can be "None" if Conical Sensor
        if(self.fov_clock is None):
            if(self.fov_geom=='CONICAL'):
                self.fov_clock = [0]
            else:
                pass
                #raise RuntimeError("Missing clock angles from instrument coverage specifications for non-conical sensor fov.")
        self.fov_at = float(fov_at) if fov_at is not None else None
        self.fov_ct = float(fov_ct) if fov_ct is not None else None
        self.orien_eu_seq1 = int(orien_eu_seq1) if orien_eu_seq1 is not None else None
        self.orien_eu_seq2 = int(orien_eu_seq2) if orien_eu_seq2 is not None else None
        self.orien_eu_seq3 = int(orien_eu_seq3) if orien_eu_seq3 is not None else None
        self.orien_eu_ang1 = float(orien_eu_ang1) if orien_eu_ang1 is not None else None
        self.orien_eu_ang2 = float(orien_eu_ang2) if orien_eu_ang2 is not None else None
        self.orien_eu_ang3 = float(orien_eu_ang3) if orien_eu_ang3 is not None else None
        self.purely_side_look = bool(purely_side_look) if purely_side_look is not None else None
        self.yaw180_flag = bool(yaw180_flag) if yaw180_flag is not None else None


    def get_as_string(self, param):
        """ Get the necessary instrument coverage specifications in string format so it can be directly passed
            as arguments to the :code:`orbitpropcov` program.
        """
        if(param == 'Geometry'):
            return self.fov_geom.name
        elif(param == 'Clock'):
            clock = [str(i) for i in self.fov_clock] 
            clock = ','.join(clock) 
            return clock
        elif(param == 'Cone'):
            cone = [str(i) for i in self.fov_cone] 
            cone = ','.join(cone) 
            return cone 
        elif(param == 'Orientation'):
            orien = str(self.orien_eu_seq1) + ',' + str(self.orien_eu_seq2) + ',' + str(self.orien_eu_seq3) + ',' + \
                   str(self.orien_eu_ang1) + ',' + str(self.orien_eu_ang2) + ',' + str(self.orien_eu_ang3)
            return orien
        elif(param == 'yaw180_flag'):
            return str(int(self.yaw180_flag))
        else:
            raise RuntimeError("Unknown parameter")    
class Satellite():
    """ Data structure holding attributes of a Satellite.
    
    :ivar orbit: Orbital parameters of the satellite. 
    :vartype orbit: :class:`orbitpy.preprocess.OrbitParameters` 

    :ivar ics_fov: Instrument coverage parameters relating to the field-of-view.
    :vartype ics_fov: :class:`orbitpy.preprocess.InstrumentCoverageParameters` 

    :ivar ics_for: Instrument coverage parameters relating to the field-of-regard.
    :vartype ics_for: :class:`orbitpy.preprocess.InstrumentCoverageParameters` 

    """
    def __init__(self, orbit = None, ics_fov =None, ics_for = None):

        self.orbit = orbit if orbit is not None else None
        self.ics_fov = ics_fov if ics_fov is not None else None
        self.ics_for = ics_for if ics_for is not None else None

class PreProcess(): 
    """ Class to handle pre-processing of user inputs.
    
    :ivar epoch: Mission epoch in Gregorian UTC format (Year, Mointh, Day, hour, minute, second). eg: "2018,1,15,12,0,0.12".
    :vartype epoch: str
    
    :ivar user_dir: User directory path. The output directories, files are stored under the user directory.
    :vartype user_dir: str

    :ivar comm_dir: Directory path to where intersatellite comm results are stored.
    :vartype comm_dir: str

    :ivar duration: Mission duration in days
    :vartype duration: float

    :ivar sats: List of satellites in the mission
    :vartype sats: list, :class:`orbitpy.preprocess.Satellites`

    :ivar time_step: Time step in seconds to be used in orbit propagation and coverage calculations. Also the time step
                     of the output satellite states.
    :vartype time_step: float

    :ivar grid_res: Grid resolution in degrees.
    :vartype grid_res: float

    :ivar cov_grid_fl: Filepath of the file containing the coverage grid info.
    :vartype cov_grid_fl: str

    ivar gnd_stn_fl: Filepath of the file containing the ground station info.
    :vartype gnd_stn_fl: str
    
    """
    def __init__(self, specs=dict(), user_dir=None):
        """ Initialization function with preprocessing tasks included.

            :param specs: Dictionary of the mission specifications.
            :paramtype specs: dict

            :param user_dir: User directory path from which files are read, written.
            :paramtype user_dir: string

            .. note:: Refer to :ref:`User JSON Input Description` for complete desciption of the fields in the specifications
                      dictionary. 

        """
        self.user_dir = str(user_dir)       
       
        # delete any existing satellite directories and files within it.
        sat_dirs =  glob.glob(user_dir+'sat*/')
        for indx in range(0,len(sat_dirs)):
            if os.path.exists(sat_dirs[indx]):
                shutil.rmtree(sat_dirs[indx])
        # delete and create empty inter-satellite comm directory
        self.comm_dir = self.user_dir + 'comm/'
        if os.path.exists(self.comm_dir):
            shutil.rmtree(self.comm_dir)
        os.makedirs(self.comm_dir) 

        self.epoch = str(specs['epoch'])

        self.duration = float(specs['duration'])

        self.sats = PreProcess.enumerate_satellites(specs['constellation'], specs["instrument"])

        # set time resolution factor based on default value or user input value
        if "settings" in specs and 'customTimeResFactor' in specs['settings']:
            time_res_f = specs['settings']['customTimeResFactor']
            print('Custom time resolution factor of ' + str(time_res_f) + ' being used.')
        else:
            time_res_f = OrbitPyDefaults.time_res_fac
            print('Default time resolution factor of ' + str(time_res_f) + ' being used.')

        _time_step = PreProcess.compute_time_step(self.sats, time_res_f)
        if "settings" in specs and 'customTimeStep' in specs['settings']:                    
            self.time_step = float(specs['settings']['customTimeStep'])
            if(_time_step < self.time_step ):
                warnings.warn("Custom time-step coarser than computed time-step.")
                print("Custom time-step [s]: ", self.time_step)
                print("Computed time-step [s]: ", _time_step)
        else:
            self.time_step = _time_step        
        print("Time step in seconds is: ", self.time_step)

        if("grid" in specs):
            self.cov_calc_app = CoverageCalculationsApproach.GRIDPNTS
            print("Grid-point approach being used for coverage calculations.")

            # set grid resolution factor based on default value or user input value
            if "settings" in specs and 'customGridResFactor' in specs['settings']:
                grid_res_f = specs['settings']['customGridResFactor']
                print('Custom grid resolution factor of ' + str(grid_res_f) + ' being used.')
            else:
                grid_res_f = OrbitPyDefaults.grid_res_fac
                print('Default grid resolution factor of ' + str(grid_res_f) + ' being used.')
            
            _grid_res = PreProcess.compute_grid_res(self.sats, grid_res_f) 
            if "settings" in specs and 'customGridRes' in specs['settings']:
                self.grid_res = float(specs['settings']['customGridRes'])
                if(_grid_res < self.grid_res):
                    warnings.warn("Custom grid-resolution is coarser than computed grid resolution.")
                    print("Custom grid resolution [deg]: ", self.grid_res)
                    print("Computed grid resolution [deg]: ", _grid_res) 
            else:
                self.grid_res = _grid_res
            print("Grid resolution in degrees is: ", self.grid_res)

            self.cov_grid_fl = PreProcess.process_cov_grid(self.user_dir, specs['grid'], self.grid_res)
            self.pnt_opts_fl = None

        elif("pointingOptions" in specs):
            self.cov_calc_app = CoverageCalculationsApproach.PNTOPTS
            print("Pointing-Options approach being used for coverage calculations.")

            self.cov_grid_fl = None
            self.pnt_opts_fl = PreProcess.process_pointing_options(user_dir, specs['pointingOptions'])

        else:
            raise Exception("Please specify either 'grid' or 'pointingOptions' JSON fields.")


        self.gnd_stn_fl = self.user_dir + str(specs['groundStations']['gndStnFn'])
            

    @staticmethod
    def get_FOV_FOR(sensor):
        """ Obtain field-of-view (FOV), field-of-regard (FOR) for a given instrument.
        
        :param sensor: Instrument object from the `instrupy` package.
        :paramtype: :class:`instrupy.public_library.Instrument`

        :returns: FOV and FOR related parameters
        :rtype: list, :class:`InstrumentCoverageParameters`
        
        """       
        _ics = FileUtilityFunctions.from_json(sensor.get_coverage_specs())
        ics_fldofview = InstrumentCoverageParameters(_ics["fieldOfView"]["geometry"], 
                                            _ics["fieldOfView"]["coneAnglesVector"], _ics["fieldOfView"]["clockAnglesVector"],
                                            _ics["fieldOfView"]["AlongTrackFov"], _ics["fieldOfView"]["CrossTrackFov"],
                                            _ics["Orientation"]["eulerSeq1"], _ics["Orientation"]["eulerSeq2"], _ics["Orientation"]["eulerSeq3"],
                                            _ics["Orientation"]["eulerAngle1"], _ics["Orientation"]["eulerAngle2"], _ics["Orientation"]["eulerAngle3"],
                                            _ics["purely_side_look"], _ics["fieldOfView"]["yaw180_flag"]
                                            )           
        ics_fldofreg = InstrumentCoverageParameters(_ics["fieldOfRegard"]["geometry"], 
                                            _ics["fieldOfRegard"]["coneAnglesVector"], _ics["fieldOfRegard"]["clockAnglesVector"],
                                            _ics["fieldOfRegard"]["AlongTrackFov"], _ics["fieldOfRegard"]["CrossTrackFov"],
                                            _ics["Orientation"]["eulerSeq1"], _ics["Orientation"]["eulerSeq2"], _ics["Orientation"]["eulerSeq3"],
                                            _ics["Orientation"]["eulerAngle1"], _ics["Orientation"]["eulerAngle2"], _ics["Orientation"]["eulerAngle3"],
                                            _ics["purely_side_look"], _ics["fieldOfRegard"]["yaw180_flag"]
                                            )           
        print("fieldOfRegard is: ", _ics["fieldOfRegard"])
        print("Orientation:", _ics["Orientation"])
        print("purely_side_look:", _ics["purely_side_look"])
        return [ics_fldofview, ics_fldofreg]

    @staticmethod
    def enumerate_orbits(constel=dict()):
        """ Enumerate all the orbits (corresponding to unique satellites) in the constellation.
        
            :param constel: Constellation specifications
            :paramtype constel: dict

            :returns: Orbits (parameters) in the constellation 
            :rtype: list, :class:`orbitpy.preprocess.OrbitParameters`        
        """       
        constel_type = ConstellationType.get(constel['@type'])        
        
        if(constel_type is None):
            raise RuntimeError("Invalid constellation type.")

        elif(constel_type == 'CUSTOM'):
            # read in the list of orbits
            if isinstance(constel['orbits'], list):
                if (len(constel['orbits']) >= 1):
                    orbits = PreProcess.custom_orbits(constel['orbits'])
                else:
                    raise RuntimeError("Please specify atleast one orbit.")
            else:
                raise RuntimeError('Please specify orbits as a list (within "[]").')

        elif(constel_type == 'WALKERDELTA'):
            orbits = PreProcess.walker_orbits(constel)
        
        else:
            raise RuntimeError("Unknown constellation type.")   

        return orbits

    @staticmethod
    def custom_orbits(data):
        """ Make a list of orbits. Convert form list of dictionaries to list of :class:`orbitpy.preprocess.OrbitParameters`.

        :param data: List of dictionaries containing the orbit ID and Keplerian parameters. A common epoch is separately 
                     considered for all orbits.
        :paramtype data: list, dict

        :returns: List of orbits in the constellation
        :rtype: list, :class:`orbitpy.preprocess.OrbitParameters` 
        
        """
        num_of_orbs = len(data)
        orbits = []
        for orb_i in range(0,num_of_orbs):
            _orb = data[orb_i]
            orbits.append(OrbitParameters(_orb['@id'], _orb['sma'], _orb['ecc'], _orb['inc'],
                                          _orb['raan'], _orb['aop'], _orb['ta']))                   
        return orbits


    @staticmethod
    def walker_orbits(data):
        """ Process the Walker Delta constellation parameters to generate list of orbits containing their respective Keplerian elements.

        :param data: Dictionary containing the Walker Delta constellation specifications.

                     Dictionary keys are: 
                                
                        * :code:`numberSatellites` (:class:`int`) Number of satellites 
                        * :code:`numberPlanes` (:class:`int`): Number of orbital planes
                        * :code:`relativeSpacing` (:class:`int`): Factor controlling the spacing between the satellites in different planes 
                        * :code:`alt` (:class:`float`): Altitude in kilometers
                        * :code:`ecc`(:class:`float`): Eccentricity
                        * :code:`inc` (:class:`float`): Inclination in degrees
                        * :code:`aop` (:class:`float`): Argument of perigee in degrees
        :paramtype: dict

        :returns: List of orbits in the constellation
        :rtype: list, :class:`orbitpy.preprocess.OrbitParameters` 

        """        
        num_sats = int(data['numberSatellites'])
        num_planes = int(data['numberPlanes'])
        rel_spc = int(data['relativeSpacing'])
        sma = Constants.radiusOfEarthInKM + float(data['alt'])
        ecc = float(data['ecc'])
        inc = float(data['inc'])
        aop = float(data['aop'])

        num_sats_pp = num_sats/num_planes
        if(not num_sats_pp.is_integer()):
            raise RuntimeError("Ratio of number of satellites to number of planes must be an integer.")
        else:
            num_sats_pp = int(num_sats_pp)

        print(".......Generating Walker Delta orbital Keplerian elements.......")
        print("orb_id, sma, ecc, inc, raan, aop, ta")
        orbits = []
        for pl_i in range(0,num_planes):
            raan = pl_i * 360.0/num_planes
            ta_ref = pl_i * rel_spc * 360.0/num_sats
            for sat_i in range(0,num_sats_pp):
                orb_id = str(pl_i+1) + str(sat_i+1)
                ta = (ta_ref + sat_i * 360.0/num_sats_pp)%360
                orbits.append(OrbitParameters(orb_id, sma, ecc, inc,
                                          raan, aop, ta)) 
                print(orb_id,sma,ecc, inc,raan, aop, ta)
        print(".......Done.......")
        return orbits

    @staticmethod
    def enumerate_satellites(orb_specs = dict(), instru_specs = dict()):
        """ Enumerate list of satellites in a mission from the user-given specifications.

        :param orb_specs: Specifications of the orbits of the satellites in form of a constellation. :class:`orbitpy.preprocess.ConstellationType` lists the allowed constellation types.
        :paramtype orb_specs: dict

        :param instru_specs: Specifications of the instrument carried by all the satellites. 
        :paramtype instru_specs: dict

        :returns: List of satellites in the mission
        :rtype: list, :class:`orbitpy.preprocess.Satellite`

        """
        orbits = PreProcess.enumerate_orbits(orb_specs)

        o = Instrument.from_json(instru_specs[0])
        [ics_fov, ics_for] =  PreProcess.get_FOV_FOR(o)

        sats = []
        for orb_indx in range(0,len(orbits)): 
            # Common instrument in all satellites.
            sats.append(Satellite(orbits[orb_indx], ics_fov, ics_for))
        
        return sats


    def generate_prop_cov_param(self):
        ''' Generate propagation and coverage parameters from the class instance variables. 

        :returns: List of propagation and coverage parameters with each element of the list corresponding to a satellite in the constellation.
        :rtype: list, :class:`orbitpy.util.PropagationCoverageParameters`

        '''              
        # For each orbit, create and separate PropagationCoverageParameters object and append to a list.
        prop_cov_param = []
        for sat_indx in range(0,len(self.sats)):  

            orb = self.sats[sat_indx].orbit
            x =  self.sats[sat_indx].ics_for 
            y =  self.sats[sat_indx].ics_fov 
            sat_dir = self.user_dir + 'sat' + str(orb._id) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)                  
            sat_state_fl = sat_dir + 'state'
            sat_acc_fl = sat_dir +'pay1_access' # hardcoded to 1 instrument
            pcp = PropagationCoverageParameters(sat_id=orb._id, epoch=self.epoch, sma=orb.sma, ecc=orb.ecc, inc=orb.inc, 
                     raan=orb.raan, aop=orb.aop, ta=orb.ta, duration=self.duration, cov_grid_fl=self.cov_grid_fl, 
                     sen_fov_geom=x.get_as_string('Geometry'), sen_orien=x.get_as_string('Orientation'), sen_clock=x.get_as_string('Clock'), 
                     sen_cone=x.get_as_string('Cone'), purely_sidelook = y.purely_side_look, yaw180_flag = x.get_as_string('yaw180_flag'), step_size=self.time_step, 
                     sat_state_fl = sat_state_fl, sat_acc_fl = sat_acc_fl, popts_fl= self.pnt_opts_fl, cov_calcs_app= self.cov_calc_app)

            prop_cov_param.append(pcp)
            
        return prop_cov_param

    @staticmethod
    def process_pointing_options(user_dir, pnt_opts):
        """ Process coverage grid and return the filepath containing the grid info. See :class:`orbitpy.GridType` for allowed grid types.

        :param user_dir: Path to the user directory where the coverage grid file exists or is to be created.
        :paramtype user_dir: str

        :param pnt_opts: Dictionary containing the filename with pointing options (must be inside the user directory) and other relevant information.
        :paramtype pnt_opts: dict

        :returns: Filepath to the file containing the pointing options info.
        :rtype: str

        """                   
        ref_frame = PntOptsRefFrame.get(pnt_opts['referenceFrame'])     
        popts_fl = user_dir + pnt_opts["pntOptsFn"] # pointing options file path  

        return popts_fl

    @staticmethod
    def process_cov_grid(user_dir, grid, grid_res):
        """ Process coverage grid and return the filepath containing the grid info. See :class:`orbitpy.GridType` for allowed grid types.

        :param user_dir: Path to the user directory where the coverage grid file exists or is to be created.
        :paramtype user_dir: str

        :param grid: Dictionary containing the specifications of the grid to be generated or the filename with existing grid data (must be inside the user directory).
        :paramtype grid: dict

        :param grid_res: grid resolution in degrees
        :paramtype grid_res: float

        :returns: Filepath to the file containing the coverage grid info.
        :rtype: str

        """                   
        grid_type = GridType.get(grid['@type'])     
        if grid_type == "AUTOGRID":
            print(".......Generating grid.......")
            # get path to *this* file
            dir_path = os.path.dirname(os.path.realpath(__file__))
            prc_args = [os.path.join(dir_path, '..', 'oci', 'bin', 'genCovGrid')] # path to program which generates the grid.

            # Generate grid based on user input lat, lon bounds
            cov_grid_fl = user_dir + "covGrid" # coverage grid file path        
            prc_args.append(cov_grid_fl)
            regions = grid["regions"]            
            # process the dictionary entries of (possibly) multiple regions into strings
            # Format: 'region_id, lat_upper, lat_lower, lon_upper, lon_lower, grid_res' 
            for reg_indx in range(0,len(regions)):
                _reg = regions[reg_indx]
                prc_args.append(str(_reg["@id"])+','+str(_reg["latUpper"])+','+str(_reg["latLower"])+
                                ','+str(_reg["lonUpper"])+','+str(_reg["lonLower"])+','+str(grid_res) # same grid resolution for all regions
                                )
            result = subprocess.run(prc_args, check= True)
            print(".......Done.......")
        
        elif grid_type == "CUSTOMGRID":
            print("Custom grid file to be used.")
            cov_grid_fl = user_dir + grid["covGridFn"] # coverage grid file path  

        else:
            raise RuntimeError('Error in processing grid. Unknown option, only "autoGrid" \
                                and "customGrid" options are supported.')

        return cov_grid_fl

    @staticmethod
    def compute_time_step(sats, time_res_fac):
        """ Compute time step to be used for orbit propagation based on the orbits and the sensor field-of-regard.
        
        :param sats: List of sats in the mission
        :paramtype sats: list,:class:`orbitpy:preprocess.Satellites`

        :param time_res_fac: Factor which decides the time resolution of orbit propagation
        :paramtype time_res_fac: float    

        :return: Time step in seconds
        :rtype: float      
        
        .. note:: The field-of-**regard** is used here, and not the field-of-**view**.

        """
        RE = Constants.radiusOfEarthInKM
        GMe = Constants.GMe
        
        # find the minimum require time-step over all the satellites
        min_t_step = 1e1000 # some large number
        for indx in range(0,len(sats)):

            sma = sats[indx].orbit.sma 
            fov_at = sats[indx].ics_for.fov_at # use FOR, and not FOV
            f = RE/sma
            # calculate maximum horizon angle
            max_horizon_angle = np.rad2deg(2*np.arcsin(f))
            if(fov_at > max_horizon_angle):
                fov_at = max_horizon_angle # use the maximum horizon angle if the instrument fov is larger than the maximum horizon angle
            satVel = np.sqrt(GMe/sma)
            satGVel = f * satVel
            sinRho = RE/sma
            hfov_deg = fov_at/2
            elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfov_deg))/sinRho))
            lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
            eca_deg = lambda_deg*2 # total earth centric angle
            AT_FP_len = RE * np.deg2rad(eca_deg)                
            t_AT_FP = AT_FP_len / satGVel # find time taken by satellite to go over the along-track length
            tstep = time_res_fac * t_AT_FP
            if(tstep < min_t_step):
                min_t_step = tstep  

        return min_t_step

    @staticmethod
    def compute_grid_res(sats, grid_res_fac):
        """ Compute grid resolution to be used for coverage grid generation. See SMAD 3rd ed Pg 113. Fig 8-13.

        :param sats: List of sats in the mission
        :paramtype sats: list, :class:`orbitpy:preprocess.Satellites`

        :param grid_res_fac: Factor which decides the resolution of the generated grid
        :paramtype grid_res_fac: float  

        :return: Grid resolution in degrees.
        :rtype: float  

        .. note:: The field-of-**view** is used here, and not the field-of-**regard**.

        """
        RE = Constants.radiusOfEarthInKM        
        # find the minimum required grid resolution over all satellites
        min_grid_res_deg = 1e1000 # some large number
        for indx in range(0,len(sats)):
            fov = min(sats[indx].ics_fov.fov_at, sats[indx].ics_fov.fov_ct) # (use FOV and not FOR)

            sinRho = RE/sats[indx].orbit.sma
            # calculate maximum horizon angle
            max_horizon_angle = np.rad2deg(2*np.arcsin(sinRho))
            if(fov > max_horizon_angle):
                fov = max_horizon_angle # use the maximum horizon angle if the instrument fov is larger than the maximum horizon angle

            hfov_deg = 0.5*fov
            elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfov_deg))/sinRho))
            lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
            eca_deg = lambda_deg*2 # total earth centric angle
            grid_res_deg = eca_deg*grid_res_fac 
            if(grid_res_deg < min_grid_res_deg):
                min_grid_res_deg = grid_res_deg

        return min_grid_res_deg


