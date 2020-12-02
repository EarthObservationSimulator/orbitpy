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
from instrupy.public_library import Instrument, InstrumentCoverageParameters
import instrupy
import logging
logger = logging.getLogger(__name__)

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
    
    def to_dict(self):
        orb_param_dict = {"@id": self._id, "sma": self.sma, "ecc": self.ecc, "inc": self.inc, "raan": self.raan, "aop": self.aop, 
                          "ta": self.ta}
        return orb_param_dict

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

    :ivar pnt_opts_fls: List of dictionaries with filepaths to the file containing the pointing options and corresponding instrument ID tag.
    :vartype pnt_opts_fls: list, dict

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

        if specs.get("constellation", None) is not None and specs.get("instrument", None) is not None:
            self.sats = PreProcess.enumerate_satellites(self.user_dir, orb_specs = specs['constellation'], instru_specs = specs["instrument"], sat_specs = dict())
        elif specs.get("satellite", None) is not None:
            self.sats = PreProcess.enumerate_satellites(self.user_dir, orb_specs = dict(), instru_specs = dict(), sat_specs = specs['satellite'])
        else:
            raise RuntimeError("Please specify either `constellation` and `instrument` JSON objects OR `satellite` JSON object.")

        # set time resolution factor based on default value or user input value
        try:
            time_res_f = specs.get('propagator').get('customTimeResFactor')
        except (AttributeError, KeyError) as e:
            time_res_f = None
        if time_res_f is not None:
            print('Custom time resolution factor of ' + str(time_res_f) + ' being used.')
        else:
            time_res_f = OrbitPyDefaults.time_res_fac
            print('Default time resolution factor of ' + str(time_res_f) + ' being used.')

        __time_step = PreProcess.compute_time_step(self.sats, time_res_f)
        try:
            _time_step = specs.get('propagator').get('customTimeStep')
        except (AttributeError, KeyError) as e:
            _time_step = None
        if _time_step is not None:                    
            self.time_step = float(_time_step)
            if(__time_step < self.time_step ):
                warnings.warn("Custom time-step coarser than computed time-step.")
                print("Custom time-step [s]: ", self.time_step)
                print("Computed time-step [s]: ", __time_step)
        else:
            self.time_step = __time_step
        print("Time step in seconds is: ", self.time_step)

        if(specs.get("grid", None) is not None and specs.get("pointingOptions", None) is not None):
            # Both grid and pointing options specified, calculate coverage for each pointing option over the grid seperately.
            self.cov_calc_app = CoverageCalculationsApproach.PNTOPTS_WITH_GRIDPNTS
            print("Pointing options with grid-points approach being used for coverage calculations.")
        elif(specs.get("grid", None) is not None ):
            self.cov_calc_app = CoverageCalculationsApproach.GRIDPNTS
            print("Grid-point approach being used for coverage calculations.")
        elif(specs.get("pointingOptions", None) is not None):
            self.cov_calc_app = CoverageCalculationsApproach.PNTOPTS
            print("Pointing-Options approach being used for coverage calculations.")
        else:
            self.cov_calc_app = CoverageCalculationsApproach.SKIP

        self.cov_grid_fl = None
        self.pnt_opts_fls = None
        if(self.cov_calc_app == CoverageCalculationsApproach.GRIDPNTS or self.cov_calc_app == CoverageCalculationsApproach.PNTOPTS_WITH_GRIDPNTS):
            # set grid resolution factor based on default value or user input value
            grid_res_f = specs["grid"].get("customGridResFactor")
            if grid_res_f is not None:
                grid_res_f = specs['grid']['customGridResFactor']
                print('Custom grid resolution factor of ' + str(grid_res_f) + ' being used.')
            else:
                grid_res_f = OrbitPyDefaults.grid_res_fac
                print('Default grid resolution factor of ' + str(grid_res_f) + ' being used.')
            
            __grid_res = PreProcess.compute_grid_res(self.sats, grid_res_f) 
            _grid_res = specs["grid"].get('customGridRes')
            if _grid_res is not None:
                self.grid_res = float(_grid_res)
                if(__grid_res < self.grid_res):
                    warnings.warn("Custom grid-resolution is coarser than computed grid resolution.")
                    print("Custom grid resolution [deg]: ", self.grid_res)
                    print("Computed grid resolution [deg]: ", _grid_res) 
            else:
                self.grid_res = __grid_res
            print("Grid resolution in degrees is: ", self.grid_res)

            self.cov_grid_fl = PreProcess.process_cov_grid(self.user_dir, specs['grid'], self.grid_res)
            
        if(self.cov_calc_app == CoverageCalculationsApproach.PNTOPTS or self.cov_calc_app == CoverageCalculationsApproach.PNTOPTS_WITH_GRIDPNTS):           
            self.pnt_opts_fls = PreProcess.process_pointing_options(user_dir, specs['pointingOptions'])

        self.gnd_stn_fl = None
        self.ground_stn_info = None
        if(specs.get("groundStations", None) is not None):
            if('gndStnFileName' in specs['groundStations']):
                self.gnd_stn_fl = self.user_dir + str(specs['groundStations']['gndStnFileName'])        
            elif('gndStnFilePath' in specs['groundStations']):
                self.gnd_stn_fl = str(specs['groundStations']['gndStnFilePath'])    
            elif('stationInfo' in specs['groundStations']):
                stn_info = []
                for stn in specs['groundStations']['stationInfo']:
                    name = stn['name'] if stn['name'] is not None else None
                    alt = float(stn['alt']) if stn['alt'] is not None else float(0)
                    minElevation = float(stn['minElevation'])
                    lat = float(stn['lat'])
                    lon = float(stn['lon'])
                    _stn_info_dict = ({'index': stn['@id'], 'name': str(name), 'lat[deg]':float(lat), 'lon[deg]':float(lon),
                                     'alt[km]': float(alt), 'minElevation[deg]': float(minElevation)})
                    stn_info.append(_stn_info_dict)
                self.ground_stn_info = stn_info
                

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
            if isinstance(constel['orbit'], list):
                if (len(constel['orbit']) >= 1):
                    orbits = PreProcess.custom_orbits(constel['orbit'])
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
                        * :code:`@id` (:class:`float`): (Optional) Constellation Identifier
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

        uid = None
        if('@id' in data):
            uid = str(data['@id'])

        num_sats_pp = num_sats/num_planes
        if(not num_sats_pp.is_integer()):
            raise RuntimeError("Ratio of number of satellites to number of planes must be an integer.")
        else:
            num_sats_pp = int(num_sats_pp)

        print(".......Generating Walker Delta orbital Keplerian elements.......")
        print("orb_id, sma, ecc, inc, raan, aop, ta")
        orbits = []
        for pl_i in range(0,num_planes):
            raan = pl_i * 180.0/num_planes
            ta_ref = pl_i * rel_spc * 360.0/num_sats
            for sat_i in range(0,num_sats_pp):
                if uid is not None:
                    orb_id = uid + str(pl_i+1) + str(sat_i+1)
                else:
                    orb_id = str(pl_i+1) + str(sat_i+1)
                ta = (ta_ref + sat_i * 360.0/num_sats_pp)%360
                orbits.append(OrbitParameters(orb_id, sma, ecc, inc,
                                          raan, aop, ta)) 
                print('{orb_id}, {sma}, {ecc}, {inc}, {raan}, {aop}, {ta}'.format(orb_id=orb_id, sma=sma, ecc=ecc, inc=inc, raan=raan, aop=aop, ta=ta))
        print(".......Done.......")
        return orbits

    @staticmethod
    def enumerate_instruments(data):
        """ Make a list of instrument properties. Convert from list of dictionaries to tuple of list of 
            :class:`orbitpy.preprocess.InstrumentCoverageParameters`.

        :param data: List of dictionaries containing the instrument specifications. 
        :paramtype data: list, dict

        :returns: List of instrument properties
        :rtype: list, :class:`orbitpy.preprocess.InstrumentProperties` 
        
        """            
        instru = []
        for _ins in data:
                instru.append(Instrument.from_dict(_ins))
                
        return instru

    @staticmethod
    def enumerate_satellites(user_dir, orb_specs = dict(), instru_specs = dict(), sat_specs = dict()):
        """ Enumerate list of satellites in a mission from the user-given specifications of :code:`orb_specs` and :code:`instru_specs`
            OR :code:`sat_specs`.

        :param user_dir: Path to the user directory where the satellite dubfolders are to be created.
        :paramtype user_dir: str

        :param orb_specs: Specifications of the orbits of the satellites in form of a constellation. :class:`orbitpy.preprocess.ConstellationType` lists the allowed constellation types.
        :paramtype orb_specs: dict

        :param instru_specs: Specifications of the instrument(s) carried by all the satellites. The instruments are all uniformly distributed to the satellites.
        :paramtype instru_specs: list, dict

        :param sat_specs: Specifications of the satellites (orbits and instruments). Each satellite has an unique identifier same as the orbit identifier (hence no two satellites have the same orbits). 
        :paramtype sat_specs: list, dict

        :returns: List of satellites in the mission
        :rtype: list, :class:`orbitpy.preprocess.Satellite`

        """
        sats = []
        if(sat_specs): 
            # enumerate satellites from the list of satellites provided            
            for _sat in sat_specs:# iterate through each satellite
                _orb = OrbitParameters(_sat["orbit"]['@id'], _sat["orbit"]['sma'], _sat["orbit"]['ecc'], _sat["orbit"]['inc'],
                                       _sat["orbit"]['raan'], _sat["orbit"]['aop'], _sat["orbit"]['ta'])

                if("instrument" in _sat):
                    _instru = PreProcess.enumerate_instruments(_sat["instrument"]) # list of instruments for that satellite
                else:
                    _instru = None

                # Create satellite folder
                sat_dir = user_dir + 'sat' + str(_sat["orbit"]['@id']) + '/'
                if os.path.exists(sat_dir):
                    shutil.rmtree(sat_dir)
                os.makedirs(sat_dir) 

                sats.append(Satellite(_orb, _instru, sat_dir))

        elif(orb_specs):
            orbits = PreProcess.enumerate_orbits(orb_specs)

            if(instru_specs is not None):
                # enumerate instruments (from a list of dictionaries)
                _instru = PreProcess.enumerate_instruments(instru_specs)
            else:
                _instru = None

            for orb_indx in range(0,len(orbits)): 

                # Create satellite folder
                sat_dir = user_dir + 'sat' + str(orbits[orb_indx]._id) + '/'
                if os.path.exists(sat_dir):
                    shutil.rmtree(sat_dir)
                os.makedirs(sat_dir)

                # Common instrument(s) in all satellites.
                sats.append(Satellite(orbits[orb_indx], _instru, sat_dir))
        
        return sats

    def generate_prop_cov_param(self):
        ''' Generate propagation and coverage parameters from the class instance variables. 

        :returns: List of propagation and coverage parameters of all the satellites (seperate set of parameters is generated for
                  instrument of the satellite) in the constellation.
        :rtype: list, list, :class:`orbitpy.util.PropagationCoverageParameters`

        '''              
        # For each orbit and instrument, create and separate PropagationCoverageParameters object and include in a list-of-lists.
        prop_cov_param = []
        for sat_indx in range(0,len(self.sats)):  

            orb = self.sats[sat_indx].orbit
            sat_dir = self.sats[sat_indx].dir_pth                 
            sat_state_fl = sat_dir + 'state'

            instru = self.sats[sat_indx].instru
            if(instru is None or bool(instru) is False or self.cov_calc_app==CoverageCalculationsApproach.SKIP):
                # no instruments specified and/or grid, pointing-options specified, skip coverage calculations
                pcp = PropagationCoverageParameters(sat_id=orb._id, epoch=self.epoch, sma=orb.sma, ecc=orb.ecc, inc=orb.inc, 
                            raan=orb.raan, aop=orb.aop, ta=orb.ta, duration=self.duration, cov_grid_fl=self.cov_grid_fl, 
                            sen_fov_geom=None, sen_orien=None, sen_clock=None, 
                            sen_cone=None, purely_sidelook=None, yaw180_flag=None, step_size=self.time_step, 
                            sat_state_fl = sat_state_fl, sat_acc_fl = None, popts_fl= None, cov_calcs_app= self.cov_calc_app, do_prop = True, do_cov = False)

                prop_cov_param.append(pcp)

            else:
                num_of_instru = len(instru)
                for k in range(0,num_of_instru): # iterate over each instrument

                    ssen_id = instru[k]._ssen_id
                    num_of_ssen = len(ssen_id)

                    for m in range(0,num_of_ssen):# iterate over each subsensor in the instrument

                        [ _y, _x]  = instru[k].get_FOV_FOR_objs(ssen_id[m])
                        if(_x._id):
                            sat_acc_fl = sat_dir + str(_x._id) + '_access'
                        else:
                            raise RuntimeError("Please define instrument, subsensor id.")

                        if(self.cov_calc_app == CoverageCalculationsApproach.PNTOPTS or self.cov_calc_app == CoverageCalculationsApproach.PNTOPTS_WITH_GRIDPNTS): 
                            # if pointing-option coverage calculation find the pointing-option file to be used for this particular instrument. 
                            popts_fl = None
                            for pf in self.pnt_opts_fls:
                                if pf["instrumentID"] == _x._id:
                                    popts_fl = pf["popts_fl"] 
                                    break
                            
                            if not popts_fl:
                                raise RuntimeError("No pointing options specified for instrument with ID " + str(_x.id))
                        elif(self.cov_calc_app == CoverageCalculationsApproach.GRIDPNTS or self.cov_calc_app == CoverageCalculationsApproach.SKIP):
                            popts_fl = None
                        else:
                            raise RuntimeError("Unknown coverage calculation approach.")
                        
                        pcp = PropagationCoverageParameters(sat_id=orb._id, epoch=self.epoch, sma=orb.sma, ecc=orb.ecc, inc=orb.inc, 
                                raan=orb.raan, aop=orb.aop, ta=orb.ta, duration=self.duration, cov_grid_fl=self.cov_grid_fl, 
                                sen_fov_geom=_x.get_as_string('Geometry'), sen_orien=_x.get_as_string('Orientation'), sen_clock= _x.get_as_string('Clock'), 
                                sen_cone=_x.get_as_string('Cone'), purely_sidelook = _y.purely_side_look, yaw180_flag = _x.get_as_string('yaw180_flag'), step_size=self.time_step, 
                                sat_state_fl = sat_state_fl, sat_acc_fl = sat_acc_fl, popts_fl= popts_fl, cov_calcs_app= self.cov_calc_app, do_prop = True, do_cov = True)

                        prop_cov_param.append(pcp)
            
            
        return prop_cov_param

    @staticmethod
    def process_pointing_options(user_dir, pnt_opts):
        """ Process coverage grid and return the filepath containing the grid info. See :class:`orbitpy.GridType` for allowed grid types.

        :param user_dir: Path to the user directory where the coverage grid file exists or is to be created.
        :paramtype user_dir: str

        :param pnt_opts: Dictionary containing list of filenames with pointing options (must be inside the user directory) and other relevant information. 
                         Each entry in the list is tagged with the corresponding instrument ID(s) to which it refers to. Multiple IDs separated by commas are allowed.
                         Only one filename per instrument is allowed. Spaces inside filenames are NOT allowed.
        :paramtype pnt_opts: dict

        :returns: List of dictionaries with filepath to the file containing the pointing options and corresponding instrument ID tag.
        :rtype: list, dict

        """                     
        popts_fls = []
        for x in pnt_opts:
            if x["instrumentID"]: # if instrument ID is empty, the corresponding filename shall be used for all unspecified instruments
                instru_ids = [x.strip() for x in str(x["instrumentID"]).split(',')] 
                for _id in instru_ids:
                    if "pntOptsFileName" in x:
                        _filepath =  user_dir + x["pntOptsFileName"]
                    elif "pntOptsFilePath" in x:
                        _filepath =  x["pntOptsFilePath"]
                    popts_fls.append({"instrumentID": _id, "popts_fl": _filepath})
            else:
                raise RuntimeError("Value of the key 'instrumentID' in the pointing-options specification cannot be left empty.")

        return popts_fls

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
            if("covGridFileName" in grid):
                cov_grid_fl = user_dir + grid["covGridFileName"] # coverage grid file path  
            elif("covGridFilePath" in grid):
                cov_grid_fl = grid["covGridFilePath"]

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
        for j in range(0,len(sats)): # iterate over all satellites
            sma = sats[j].orbit.sma 
            instru = sats[j].instru

            # Find the minimum along-track fov over all the sensors attached to the satellite
            fov_at = 1000 # some large number
            if instru is not None:
                num_of_instru = len(instru)
                _fov_at = 1000 # some large number
                for k in range(0,num_of_instru): # iterate over each instrument

                    ssen_id = instru[k]._ssen_id
                    num_of_ssen = len(ssen_id)

                    for m in range(0,num_of_ssen):# iterate over each subsensor in the instrument

                        [ics_fov, ics_for]  = instru[k].get_FOV_FOR_objs(ssen_id[m])

                        __fov_at = ics_for.fov_at # use FOR, and not FOV

                        if(_fov_at>__fov_at):
                            _fov_at = __fov_at
            else:
                # no instruments specified, hence no FOV/FOR to consider, hence consider the entire horizon angle as FOV
                f = RE/sma
                _fov_at = np.rad2deg(2*np.arcsin(f))

            if fov_at > _fov_at:
                fov_at = _fov_at

            # calculate the minimum time-step corresponding to the 'j'th satellite
            # calculate maximum horizon angle
            f = RE/sma
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
        for j in range(0,len(sats)):

            instru = sats[j].instru
            
            # Find the minimum fov over all the sensors attached to the satellite
            fov = 1000 # some large number
            if instru is not None:
                num_of_instru = len(instru)
                _fov = 1000 # some large number
                for k in range(0,num_of_instru): # iterate over each instrument

                    ssen_id = instru[k]._ssen_id
                    num_of_ssen = len(ssen_id)

                    for m in range(0,num_of_ssen):# iterate over each subsensor in the instrument

                        [ics_fov, ics_for]  = instru[k].get_FOV_FOR_objs(ssen_id[m])

                        __fov = min(ics_fov.fov_at, ics_fov.fov_ct) # (use FOV and not FOR)
                        if(_fov > __fov):
                            _fov = __fov
            else:
                # no instruments specified, hence no FOV/FOR to consider, hence consider the entire horizon angle as FOV
                sinRho = RE/sats[j].orbit.sma
                fov = np.rad2deg(2*np.arcsin(sinRho))

            if fov > _fov:
                fov = _fov

            # calculate the minimum grid-resolution corresponding to the 'j'th satellite
            # calculate maximum horizon angle
            sinRho = RE/sats[j].orbit.sma            
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


