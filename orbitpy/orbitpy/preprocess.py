""" 
.. module:: preprocess

:synopsis: *Module to handle pre-processing of user inputs.*

.. note::  - Lat must be in the range -pi/2 to pi/2, while lon must be in the range -pi to pi

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
    """Enumeration of recognized constellation types"""
    CUSTOM = "CUSTOMGRID",
    AUTOGRID = "AUTOGRID"
class FOVGeometry(EnumEntity):
    """Enumeration of recognized instrument sensor geometries."""
    CONICAL = "CONICAL",
    RECTANGULAR = "RECTANGULAR",
    CUSTOM = "CUSTOM"
class OrbitParameters():
    """ Data structure to hold parameters defining the orbit of a satellite in the constellation. An orbit is 
        assumed to be unique for a satellite.

    .. note:: Epoch is defined to be common for all the orbits in the mission and is hence defined separately.
    
    :ivar @_id: Unique identifier of the orbit (satellite)
    :vartype @_id: str

    :ivar sma: Semi-major axis in kilometers
    :vartype sma: float

    :ivar ecc: Eccentricity
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
    def __init__(self, _id=None, sma=None, ecc=None, inc=None, raan=None, aop=None, ta=None):
        try:
            self._id = str(_id)
            self.sma = float(sma)
            self.ecc = float(ecc)
            self.inc = float(inc)
            self.raan = float(raan)
            self.aop = float(aop)
            self.ta = float(ta)
        except:
            raise Exception("Error in initialization of OrbitParameters object.")
class InstrumentCoverageParameters():
    """ Data structure to hold instrument coverage related parameters. For a more detailed description of the representation
    of the FOV in terms of clock, cone angles and the orientation in terms of Euler sequences, angles, please refer to the
    Appendix.

    .. todo:: Make description in another section.

    :ivar fov_geom: Geometry of the field of view
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

    :ivar yaw180_flag: Flag applies in case of field-of-regard. If true ,it signifies that the field-of-regard includes the field-of-view of payload rotated along yaw axis by 180 deg. 
    :vartype yaw180_flag: bool
    
    """
    def __init__(self, fov_geom=None, fov_cone=None, fov_clock=None, fov_at = None, fov_ct = None, 
                 orien_eu_seq1=None, orien_eu_seq2=None, orien_eu_seq3=None, 
                 orien_eu_ang1=None, orien_eu_ang2=None, orien_eu_ang3=None,
                 purely_side_look = bool(), yaw180_flag = bool()):
        
        try:
            self.fov_geom = FOVGeometry.get(fov_geom)
            self.fov_cone = [float(i) for i in fov_cone]
            self.fov_clock = [float(i) for i in fov_clock] if fov_clock is not None else None # clock can be "None" if Conical Sensor
            if(self.fov_clock is None):
                if(self.fov_geom=='CONICAL'):
                    self.fov_clock = [0]
                else:
                    print("Missing clock angles from instrument coverage specifications for non-conical sensor fov.")
                    raise Exception()
            self.fov_at = float(fov_at)
            self.fov_ct = float(fov_ct)
            self.orien_eu_seq1 = int(orien_eu_seq1)
            self.orien_eu_seq2 = int(orien_eu_seq2)
            self.orien_eu_seq3 = int(orien_eu_seq3)
            self.orien_eu_ang1 = float(orien_eu_ang1)
            self.orien_eu_ang2 = float(orien_eu_ang2)
            self.orien_eu_ang3 = float(orien_eu_ang3)
            self.purely_side_look = bool(purely_side_look)
            self.yaw180_flag = bool(yaw180_flag)
        except:
            raise Exception("Error in initilization of InstrumentCoverageParameters object.")

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
            raise Exception("Unknown parameter")    
class Satellite():

    """ Data structure holding attributes of a Satellite.
    
    :ivar orbit: Orbital parameters of the satellite. 
    :vartype orbit: :class:`orbitpy.preprocess.OrbitParameters` 

    :ivar ics_fov: Instrument coverage parameters relating to the field-of-view
    :vartype ics_fov: :class:`orbitpy.preprocess.InstrumentCoverageParameters` 

    :ivar ics_for: Instrument coverage parameters relating to the field-of-regard
    :vartype ics_for: :class:`orbitpy.preprocess.InstrumentCoverageParameters` 

    """
    def __init__(self, orbit, ics_fov, ics_for):

        self.orbit = orbit
        self.ics_fov = ics_fov
        self.ics_for = ics_for

class PreProcess(): 
    """ Class to handle pre-processing of user inputs.
    
    :ivar epoch: Mission epoch in Gregorian UTC format
    :vartype epoch: str
    
    :ivar user_dir: User directory path
    :vartype user_dir: str

    :ivar comm_dir: Directory path to where comm results are written.
    :vartype comm_dir: str

    :ivar duration: Mission duration in days
    :vartype duration: float

    :ivar sats: List of satellites in the mission
    :vartype sats: list, :class:`orbitpy.preprocess.Satellites`

    :ivar time_step: Time step in seconds to be used in orbit propagation and coverage calculations. Also the time step
                     of the output satellite states.
    :vartype time_step: float

    :ivar grid_res: Grid resolution 
    :vartype grid_res: float

    :ivar cov_grid_fl: Filepath (including filename) of the file containing the coverage grid info.
    :vartype cov_grid_fl: str

    ivar gnd_stn_fl: Filepath (including filename) of the file containing the ground station info.
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
        
        try:

            try:
                self.user_dir = str(user_dir)
            except ValueError:
                print('Invalid user_dir')
                raise            
            try:                
                # delete any existing satellite directories
                sat_dirs =  glob.glob(user_dir+'sat*/')
                for indx in range(0,len(sat_dirs)):
                   if os.path.exists(sat_dirs[indx]):
                        shutil.rmtree(sat_dirs[indx])
                # delete and create empty comm directory
                self.comm_dir = self.user_dir + 'comm/'
                if os.path.exists(self.comm_dir):
                   shutil.rmtree(self.comm_dir)
                os.makedirs(self.comm_dir) 

            except:
                print('Error in removing and/or creating state, access, comm and gndstn directories.')
                raise
            try:
                self.epoch = str(specs['epoch'])
            except ValueError:
                print('Valid epoch, please')
                raise
            try:
                self.duration = float(specs['duration'])
            except ValueError:
                print('Valid duration, please')
                raise
            try:
                self.sats = PreProcess.enumerate_satellites(specs['constellation'], specs["instrument"])
            except:
                print('Error in enumerating satellites')
                raise            
            try:
                _time_step = PreProcess.compute_time_step(self.sats, OrbitPyDefaults.time_res_fac)
                if "settings" in specs and 'customTimeStep' in specs['settings']:                    
                    self.time_step = float(specs['settings']['customTimeStep'])
                    if(_time_step < self.time_step ):
                        warnings.warn("Custom time-step coarser than computed time-step")
                        print("Custom time-step [s]: ", self.time_step)
                        print("Computed time-step [s]: ", _time_step)
                else:
                    self.time_step = _time_step
            except:
                print('Error in processing time step')
                raise            
            try:
                _grid_res = PreProcess.compute_grid_res(self.sats, OrbitPyDefaults.grid_res_fac) 
                if "settings" in specs and 'customGridRes' in specs['settings']:
                    self.grid_res = float(specs['settings']['customGridRes'])
                    if(_grid_res < self.grid_res):
                       warnings.warn("Custom grid-resolution is coarser than computed grid resolution.")
                       print("Custom grid resolution [deg]: ", self.grid_res)
                       print("Computed grid resolution [deg]: ", _grid_res) 
                else:
                    self.grid_res = _grid_res
            except:
                print('Error in processing grid resolution')
                raise
            try:
                self.cov_grid_fl = PreProcess.process_cov_grid(self.user_dir, specs['grid'], self.grid_res)
            except:
                print('Error in processessing coverage grid')
                raise    
            try:
                self.gnd_stn_fl = self.user_dir + str(specs['groundStations']['gndStnFn'])
            except ValueError:
                print('Invalid ground station file name')
                raise              
        except:
            raise Exception("Error in processing user JSON input file.")


    @staticmethod
    def process_FOV_FOR(o):
        """ Compute field-of-view (FOV), field-of-regard (FOR) for a given instrument and manuverability.
        
        :param o: Instrument object from the `instrupy` package.
        :paramtype: :class:`instrupy.public_library.Instrument`

        :returns: FOV and FOR related parameters
        :rtype: list, :class:`InstrumentCoverageParameters`
        
        """
        try:
            _ics = FileUtilityFunctions.from_json(o.get_coverage_specs())
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

        except:
            raise Exception("Error in obtaining instrument coverage specifications. Perhaps required dict field missing.")       
        
        return [ics_fldofview, ics_fldofreg]




    @staticmethod
    def enumerate_orbits(constel=dict()):
        """ Enumerate all the orbits (corresponding to unique satellites) in the constellation.
        
            :param constel: Constellation specifications (Custom or Walker Delta)
            :paramtype constel: dict

            :returns: Orbits (parameters) in the constellation 
            :rtype: list, :class:`orbitpy.preprocess.OrbitParameters`        
        """       
        constel_type = ConstellationType.get(constel['@type'])        
        
        if(constel_type is None):
            raise Exception("Invalid constellation type.")

        elif(constel_type == 'CUSTOM'):
            # read in the list of orbits
             if isinstance(constel['orbits'], list) and len(constel['orbits']) >= 1:
                 orbits = PreProcess.custom_orbits(constel['orbits'])

        elif(constel_type == 'WALKERDELTA'):
            orbits = PreProcess.walker_orbits(constel)
        
        else:
            raise Exception(("Unknown error in PreProcess.enumerate_orbits"))        


        return orbits

    @staticmethod
    def custom_orbits(data):
        """ Make a list of orbits. Convert form list of dictonaries to list of :class:`orbitpy.preprocess.OrbitParameters`.

        :param data: List of dictionaries containing the orbit Keplerian parameters, orbit ID. A common epoch is separately 
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
        """ Process the Walker Delta constellation parameters to generate list of orbits containing their 
        respective Keplerian elements.

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
        
        try:
            num_sats = int(data['numberSatellites'])
            num_planes = int(data['numberPlanes'])
            rel_spc = int(data['relativeSpacing'])
            sma = Constants.radiusOfEarthInKM + data['alt']
            ecc = float(data['ecc'])
            inc = float(data['inc'])
            aop = float(data['aop'])
        except:
            print("Error in parsing Walker Delta constellation specs. Perhaps missing entry?")
            raise

        num_sats_pp = num_sats/num_planes
        if(not num_sats_pp.is_integer()):
            print("Ratio of number of satellites to number of planes must be an integer.")
            raise Exception()
        else:
            num_sats_pp = int(num_sats_pp)

        orbits = []
        for pl_i in range(0,num_planes):
            raan = pl_i * 360.0/num_planes
            ta_ref = pl_i * rel_spc * 360.0/num_sats
            for sat_i in range(0,num_sats_pp):
                orb_id = str(pl_i) + str(sat_i)
                ta = (ta_ref + sat_i * 360.0/num_sats_pp)%360
                orbits.append(OrbitParameters(orb_id, sma, ecc, inc,
                                          raan, aop, ta)) 
                print(orb_id, sma, ecc, inc, raan, aop, ta)

        return orbits

    @staticmethod
    def enumerate_satellites(orb_specs = dict(), instru_specs = dict()):
        """ Enumerate list of satellites in a mission from the user-given specifications.

        :param orb_specs: Specifications of the orbits of the satellites in form of a constellation. :class:`orbitpy.preprocess.ConstellationType` lists the allowed constellation types.
        :paramtype orb_specs: dict

        :param instru_specs: Specifications of the instrument carried by all the satellites. 
        :paramtype instru_specs: dict

        :returns: List of Satellites in the mission
        :rtype: list, :class:`orbitpy.preprocess.Satellite`

        """
        try:
            orbits = PreProcess.enumerate_orbits(orb_specs)
        except:
            print('Error in enumerating orbits')
            raise
        try:
            o = Instrument.from_json(instru_specs[0])
            [ics_fov, ics_for] =  PreProcess.process_FOV_FOR(o)
        except:
            print('Error in obtaining instrument specifications')
            raise 

        sats = []
        for orb_indx in range(0,len(orbits)): 
            sats.append(Satellite(orbits[orb_indx], ics_fov, ics_for))
        
        return sats


    def generate_prop_cov_param(self):
        ''' Generate propagation and coverage parameters from the class instance variables. 

        :returns: List of propagation and coverage parameters with each element of the list corresponding to an orbit in the constellation.
        :rtype: list, :class:`orbitpy.util.PropagationCoverageParameters`

        '''              
        # For each orbit, create and separate PropagationCoverageParameters object and append to a list.
        prop_cov_param = []
        for sat_indx in range(0,len(self.sats)):  

            orb = self.sats[sat_indx].orbit
            x =  self.sats[sat_indx].ics_for 
            sat_dir = self.user_dir + 'sat' + str(orb._id) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)                  
            sat_state_fl = sat_dir + 'state'
            sat_acc_fl = sat_dir +'pay1_access' # hardcoded to 1 instrument
            pcp = PropagationCoverageParameters(sat_id=orb._id, epoch=self.epoch, sma=orb.sma, ecc=orb.ecc, inc=orb.inc, 
                     raan=orb.raan, aop=orb.aop, ta=orb.ta, duration=self.duration, cov_grid_fl=self.cov_grid_fl, 
                     sen_fov_geom=x.get_as_string('Geometry'), sen_orien=x.get_as_string('Orientation'), sen_clock=x.get_as_string('Clock'), 
                     sen_cone=x.get_as_string('Cone'), yaw180_flag = x.get_as_string('yaw180_flag'), step_size=self.time_step, 
                     sat_state_fl = sat_state_fl, sat_acc_fl = sat_acc_fl)

            prop_cov_param.append(pcp)
            
        return prop_cov_param

    @staticmethod
    def process_cov_grid(user_dir, grid, grid_res):
        """ Process coverage grid (auto or custom) and return the filepath with filename containing the grid info.

        :param user_dir: Path to the user directory where the coverage grid file exists or is to be created.
        :paramtype user_dir: str

        :param grid: Dictionary containing the specifications of the grid to be generated or the filename with existing grid data (must be inside the user directory).
        :paramtype grid: dict

        :param grid_res: grid resolution
        :paramtype grid_res: float

        :returns: Filepath (with filename)
        :rtype: str

        """               
        # get path to *this* file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        prc_args = [os.path.join(dir_path, '..', 'oci', 'bin', 'genCovGrid')]
        
        grid_type = GridType.get(grid['@type'])     
        if grid_type == "AUTOGRID":
            # Generate grid based on user input lat, lon bounds
            cov_grid_fl = user_dir + "covGrid" # coverage grid file path        
            prc_args.append(cov_grid_fl)

            try:
                regions = grid["regions"]            
                # process the dictionary entries of (possibly) multiple regions into strings
                # Format: 'region_id, lat_upper, lat_lower, lon_upper, lon_lower, grid_res' 
                for reg_indx in range(0,len(regions)):
                    _reg = regions[reg_indx]
                    prc_args.append(str(_reg["@id"])+','+str(_reg["latUpper"])+','+str(_reg["latLower"])+
                                    ','+str(_reg["lonUpper"])+','+str(_reg["lonLower"])+','+str(grid_res)
                                    )
            except:
                print('Error in processing regions within the "autoGrid" option') 
                raise

            try:
                result = subprocess.run(prc_args, check= True)
            except:
                print('Error executing "genCovGrid" OC script')
                raise
        
        elif grid_type == "CUSTOMGRID":
            try:
                cov_grid_fl = user_dir + grid["covGridFn"] # coverage grid file path  
            except:
                print('Error in processing "customGrid" option. Make sure "covGridFn" is specified.')
                raise

        else:
            raise RuntimeError('Error in processing grid. Unknown option, only "autoGrid" \
                                and "customGrid" options are supported.')

        return cov_grid_fl

    @staticmethod
    def compute_time_step(sats, time_res_fac):
        """ Compute time step to be used for orbit propagation based on the orbits and the sensor field-of-view.
        
        :param sats: List of sats in the mission
        :paramtype sats: list,:class:`orbitpy:preprocess.Satellites`

        :param time_res_fac: Factor which decides the time resolution of orbit propagation
        :paramtype time_res_fac: float        
        
        """
        RE = Constants.radiusOfEarthInKM
        GMe = Constants.GMe
        
        # find the minimum require time-step over all the satellites
        min_t_step = 1e1000 # some large number
        for indx in range(0,len(sats)):

            sma = sats[indx].orbit.sma 
            fov_at = sats[indx].ics_fov.fov_at
            alt = sma - RE # minimum latitude in km
            f = RE/(RE+alt)
            satVel = np.sqrt(GMe/(RE+alt))
            satGVel = f * satVel
            sinRho = RE/(RE+alt)
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
        :paramtype sats: list,:class:`orbitpy:preprocess.Satellites`

        :param grid_res_fac: Factor which decides the resolution of the generated grid
        :paramtype grid_res_fac: float  

        :return: Minimum required grid resolution in degrees.
        :rtype: float  

        """
        RE = Constants.radiusOfEarthInKM        
        # find the minimum required grid resolution
        min_grid_res_deg = 1e1000 # some large number
        for indx in range(0,len(sats)):
            alt = sats[indx].orbit.sma - RE # altitude
            fov_ct = sats[indx].ics_fov.fov_ct # instrument cross-track fov in degrees
            sinRho = RE/(RE+alt)
            hfov_deg = 0.5*fov_ct
            elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfov_deg))/sinRho))
            lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
            eca_deg = lambda_deg*2 # total earth centric angle
            grid_res_deg = eca_deg*grid_res_fac 
            if(grid_res_deg < min_grid_res_deg):
                min_grid_res_deg = grid_res_deg

        return min_grid_res_deg

    ''' delete
    @staticmethod
    def process_instru_cov_specs(o = None):

        try:
            ics = FileUtilityFunctions.from_json(o.get_coverage_specs())
            m = InstrumentCoverageParameters(ics["fieldOfView"]["geometry"], 
                                            ics["fieldOfView"]["coneAnglesVector"], ics["fieldOfView"]["clockAnglesVector"],
                                            ics["fieldOfView"]["AlongTrackFov"], ics["fieldOfView"]["CrossTrackFov"],
                                            ics["Orientation"]["eulerSeq1"], ics["Orientation"]["eulerSeq2"], ics["Orientation"]["eulerSeq3"],
                                            ics["Orientation"]["eulerAngle1"], ics["Orientation"]["eulerAngle2"], ics["Orientation"]["eulerAngle3"],
                                            ics["purely_side_look"]
                                            )
        except:
            print("Error in obtaining instrument coverage specifications. Perhaps required dict field missing.")
            raise       

        # Return the instrument converage specifications in format required for 
        # calling the orbitpropcov (C++) script.
        sen_type = m.fov_geom.name
        sen_orien = str(m.orien_eu_seq1) + ',' + str(m.orien_eu_seq2) + ',' + str(m.orien_eu_seq3) + ',' + \
                    str(m.orien_eu_ang1) + ',' + str(m.orien_eu_ang2) + ',' + str(m.orien_eu_ang3)       
        sen_clock = [str(i) for i in m.fov_clock]        
        sen_clock = ','.join(sen_clock)        
        sen_cone = [str(i) for i in m.fov_cone]        
        sen_cone = ','.join(sen_cone)        

        return [m, sen_type, sen_orien, sen_clock, sen_cone]
    '''

