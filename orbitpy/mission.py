""" 
.. module:: mission

:synopsis: *Module to handle mission initialization and execution.*

"""
import os, shutil
import warnings
from collections import namedtuple

from instrupy.util import Entity
from instrupy.base import Instrument
import propcov

import orbitpy.util
from orbitpy.util import OrbitState
from .util import Spacecraft, GroundStation, SpacecraftBus, InfoType, add_to_list
from .constellation import ConstellationFactory
import orbitpy.propagator
import orbitpy.grid
from orbitpy import util
from .propagator import PropagatorFactory, PropagatorOutputInfo
from .coveragecalculator import GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
from datametricscalculator import DataMetricsCalculator, AccessFileInfo
from .contactfinder import ContactFinder
from .grid import Grid

class Settings(Entity):
    """ Data container of the mission settings.

    :ivar outDir: Output directory path.
    :vartype outDir: str 

    :ivar coverageType: Type of coverage calculation. 
    :vartype coverageType: str or None

    :ivar propTimeResFactor: Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`.
    :vartype propTimeResFactor: float

    :ivar gridResFactor: Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`. 
    :vartype gridResFactor: float

    :ivar opaque_atmos_height: Relevant in-case of inter-satellite communications. Height of atmosphere (in kilometers) below which line-of-sight 
                                    communication between two satellites **cannot** take place. Default value is 0 km.
    :vartype opaque_atmos_height_km: float

    :ivar _id: Unique identifier of the settings object.
    :vartype _id: int/ str

    """
    def __init__(self, outDir=None, coverageType=None, propTimeResFactor=None, gridResFactor=None, opaque_atmos_height=None, _id=None):
        self.outDir = str(outDir) if outDir is not None else None
        self.coverageType = coverageType if coverageType is not None else None
        self.propTimeResFactor = float(propTimeResFactor) if propTimeResFactor is not None else None
        self.gridResFactor = float(gridResFactor) if gridResFactor is not None else None
        self.opaque_atmos_height = float(opaque_atmos_height) if opaque_atmos_height is not None else None

        super(Settings, self).__init__(_id, "Settings")
    
    @staticmethod
    def from_dict(d):
        """ Parses an Settings object from a normalized JSON dictionary.

        :param d: Dictionary with the Settings specifications.
        
        Following dictionary keys are expected:
        
        * outDir: Output directory path. Default is the location of the current directory.
        * coverageType: Type of coverage calculation. Default value is ``None``.
        * propTimeResFactor: Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`. Default value is 0.25.
        * gridResFactor: Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`. Default value is 0.9.
        * opaque_atmos_height: Relevant in-case of inter-satellite communications. Height of atmosphere (in kilometers) below which line-of-sight communication between two satellites **cannot** take place. Default value is 0 km.
        * @id: Unique identifier. Default is ``None``.

        :paramtype d: dict

        :return: Settings object.
        :rtype: :class:`orbitpy.mission.Settings`

        """
        return Settings( outDir= d.get('outDir', os.path.dirname(os.path.realpath(__file__))), # current directory as default
                         coverageType = d.get('coverageType', None),
                         propTimeResFactor = d.get('propTimeResFactor', 0.25), # default value is 0.25
                         gridResFactor = d.get('gridResFactor', 0.9), # default value is 0.9
                         opaque_atmos_height = d.get('opaque_atmos_height', 0), # default value is 0
                         _id = d.get('@id', None)
                        )                        
        
    def to_dict(self):
        """ Translate the ``Settings`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``Settings`` object as python dictionary.
        :rtype: dict
        
        """
        return dict({"@type": "Settings",
                     "outDir": self.outDir,
                     "coverageType": self.coverageType if self.coverageType is not None else None,
                     "propTimeResFactor": self.propTimeResFactor,                     
                     "gridResFactor": self.gridResFactor,
                     "opaque_atmos_height": self.opaque_atmos_height,
                     "@id": self._id})

    def __repr__(self):
        return "Settings.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different.
        if(isinstance(self, other.__class__)):
            return (self.outDir==other.outDir) and (self.coverageType==other.coverageType) \
                    and (self.propTimeResFactor==other.propTimeResFactor) and (self.gridResFactor==other.gridResFactor) \
                        and (self.opaque_atmos_height==other.opaque_atmos_height)                   
        else:
            return NotImplemented

class Mission(Entity):
    """ Class to handle mission initialization and execution.

    Usage: 
    
    .. code-block:: python
        
        mission = orbitpy.Mission.from_json(mission_json_str)
        mission.execute()

    :ivar startDate: Mission epoch in Julian Date UT1.
    :vartype startDate: float

    :ivar duration: Mission duration in days.
    :vartype duration: float    

    :ivar spacecraft: List of spacecraft in the mission.
    :vartype spacecraft: list, :class:`orbitpy.util.Spacecraft`

    :ivar propagator: Orbit propagator.
    :vartype propagator: :class:`orbitpy.propagator.J2AnalyticalPropagator`

    :ivar grid: List of grid objects to be used in case of coverage calculations.
    :vartype grid: list, :class:`orbitpy.grid.Grid` or None

    :ivar groundStation: List of ground-stations in the mission.
    :vartype groundStation: list, :class:`orbitpy.util.GroundStation` or None

    :ivar settings: Mission settings. Refer to the ``Settings.from_dict(.)`` method for the default values.
    :vartype settings: :class:`orbitpy.mission.settings`

    :ivar outputInfo: List of output-info objects produced after execution of a OrbitPy function, e.g. :class:`orbitpy.propagator.PropagatorOutputInfo`, :class:`orbitpy.propagator.ContactFinderOutputInfo`, etc. 
    :vartype outputInfo: list, output-info object

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, epoch=None, duration=None, spacecraft=None, propagator=None,
                 grid=None, groundStation=None, settings=None, outputInfo=None, _id=None):
        self.epoch = epoch if epoch is not None and isinstance(epoch, propcov.AbsoluteDate) else None
        self.duration = float(duration) if duration is not None else None
        self.spacecraft = orbitpy.util.initialize_object_list(spacecraft, Spacecraft)
        self.propagator = propagator if propagator is not None else None
        self.grid = orbitpy.util.initialize_object_list(grid, Grid)
        self.groundStation = orbitpy.util.initialize_object_list(groundStation, GroundStation)
        self.settings = settings if isinstance(settings, Settings) else Settings.from_dict({})
        # Make sure self.outputInfo is a list. Each element of the list could be a different object instance.
        # TODO: check the individual elements of the outputInfo list are of valid class-types. 
        if isinstance(outputInfo, list):
            self.outputInfo = outputInfo
        elif outputInfo is not None:
            self.outputInfo = [outputInfo]
        else:
            self.outputInfo = None

        super(Mission, self).__init__(_id, "Mission")        
 
    @staticmethod
    def from_dict(d):
        """Parses an ``Mission`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the mission specifications.
        :paramtype d: dict

        :return: ``Mission`` object.
        :rtype: :class:`orbitpy.mission.Mission`

        .. note:: *Either* of the ``constellation``, ``instrument`` json objects or the ``spacecraft`` json object should be provided in the mission specifications. Both should not be specified.

        .. note:: The valid key/value pairs in building the mission specifications json/ dict is identical to the key/value pairs expected in the obtaining
                the corresponding OrbitPy objects using the ``from_dict`` or ``from_json`` function. 
        
        .. note:: The propagation time step-size if not specified is calculated from the list of available spacecraft and propagation time-resolution factor. 
                    If no spacecraft, 60s is the assumed step-size.
        
        .. note:: The grid-resolution if not specified is calculated from the list of available spacecraft and grid-resolution factor. 
                    If no spacecraft, 1 deg grid-resolution is assumed.


        """
        date_dict = d.get('epoch') if d.get('epoch') is not None else {"@type":"JULIAN_DATE_UT1", "jd":2459270.5} # 25 Feb 2021 0:0:0 default startDate
        epoch = OrbitState.date_from_dict(date_dict) 

        # parse settings            
        settings_dict = d.get('settings', None) if  d.get('settings', None) is not None else dict()
        settings = Settings.from_dict(settings_dict)

        # parse spacecraft(s) 
        custom_spc_dict = d.get("spacecraft", None)
        constel_dict = d.get("constellation", None)
        if custom_spc_dict is not None:
            spacecraft = orbitpy.util.dictionary_list_to_object_list(custom_spc_dict, Spacecraft)
        elif constel_dict is not None:
            factory = ConstellationFactory()        
            constel = factory.get_constellation_model(constel_dict)
            orbits = constel.from_dict(constel_dict).generate_orbits()
            
            # one common spacecraft-bus specifications can be expected to be defined for all the satellites in the constellation
            spc_bus_dict = d.get("spacecraftBus", None)
            spc_bus = SpacecraftBus.from_dict(spc_bus_dict) if spc_bus_dict is not None else None
            # list of instrument specifications could be present, in which case all the instruments in the list are attached to all the 
            # spacecraft in the constellation.
            instru_dict = d.get("instrument", None)
            if instru_dict:
                instru_list = orbitpy.util.dictionary_list_to_object_list(instru_dict, Instrument) # list of instruments
            else:
                instru_list = None
            spacecraft = []
            for orb in orbits:
                spacecraft.append(Spacecraft(orbitState=orb, spacecraftBus=spc_bus, instrument=instru_list, _id='spc_'+orb._id)) # note the assignment of the spacecraft-id

        # parse propagator
        factory = PropagatorFactory()
        # Compute step-size
        if spacecraft:
            time_step = orbitpy.propagator.compute_time_step(spacecraft, settings.propTimeResFactor)
        else:
            time_step = 60
        # default to J2 Analytical propagator and time-step as calculated before 
        prop_dict = d.get('propagator') if d.get('propagator') is not None else {'@type': 'J2 ANALYTICAL PROPAGATOR', 'stepSize': time_step} 
        if prop_dict.get("stepSize") is None: # i.e. user has not specified step-size
            prop_dict["stepSize"] = time_step # use the autocalculate step-size
        if prop_dict.get("stepSize") > time_step:
            warnings.warn('User given step-size is greater than auto calculated step-size.')
        propagator = factory.get_propagator(prop_dict) 

        # parse grid        
        grid_dict = d.get('grid', None) 
        if grid_dict:
            # make into list of dictionaries if not already list
            if not isinstance(grid_dict, list):
                grid_dict = [grid_dict]
            # iterate through the list of grids
            grid = []
            for gd in grid_dict:
                if ((gd.get('@type', None)=='autogrid') and (gd.get('gridRes', None) is None)):
                    # calculate grid resolution factor
                    if spacecraft:
                        gridRes = orbitpy.grid.compute_grid_res(spacecraft, settings.gridResFactor)
                    else:
                        gridRes = 1 # 1 deg grid-resolution in case of no spacecraft.
                    gd['gridRes'] = gridRes

                grid.append(Grid.from_dict(gd))
        else:
            grid = None        

        # Save auto-grids to files. If custom-grid, then file already exists and is not re-written.
        outputInfo = [] # list of outputInfo objects
        for indx, val in enumerate(grid):
            if grid[indx].filepath is None: # must be an auto-grid configuration, so filepath instance variable is None
                fp = settings.outDir + '/grid_id' + str(grid[indx]._id) # save the file with name according to the unique-id. TODO: check that there is no-conflict with an custom-grid file.
                oi = grid[indx].write_to_file(fp)
                outputInfo.append(oi)

        # parse ground-station(s) 
        groundStation = orbitpy.util.dictionary_list_to_object_list(d.get("groundStation", None), GroundStation)

        # parse any available outputInfo objects. Note that there may be output-info objects from executing the auto-grid function.
        outputInfo_dict = d.get('outputInfo', None)
        if outputInfo_dict:
            # make into list
            if not isinstance(outputInfo_dict, list):
                outputInfo_dict = [outputInfo_dict]
            # iterate over the list
            for oi_d in outputInfo_dict:
                output_info_type = InfoType.get(oi_d.get('@type')) if oi_d.get('@type') else None
                if output_info_type == InfoType.PropagatorOutputInfo:
                    outputInfo.append(PropagatorOutputInfo.from_dict(oi_d)) # append to existing list of output-info objects

        return Mission(epoch = epoch, # 25 Feb 2021 0:0:0 default startDate
                       duration = d.get('duration') if d.get('duration') is not None else 1, # 1 day default
                       spacecraft = spacecraft,
                       propagator = propagator,                       
                       grid = grid,
                       groundStation = groundStation,
                       settings = settings,
                       outputInfo = outputInfo if outputInfo else None, # make into None strictly, it could be [].
                       _id = d.get('@id', None)
                      ) 
    
    def clear(self):
        """ Re-initialize. """
        self.__init__()

    def get_spacecraft_orbit_specs(self):
        """ Get the Keplerian elements of the orbit of the spacecraft(s).

            :return: List of namedtuple objects with the following entries: <spacecraft-id, sma, ecc, inc, raan, aop, ta> 
            :rtype: list, namedtuple

        """ 
        specs = namedtuple("Specs", ["spc_id", "sma", "ecc", "inc", "raan", "aop", "ta"])
        orb_specs = []
        spacecraft = self.spacecraft
        if isinstance(spacecraft, Spacecraft):
            spacecraft = [spacecraft]
        if isinstance(spacecraft, list):
            for spc in spacecraft:
                kep_state = spc.orbitState.get_keplerian_earth_centered_inertial_state()
                orb_specs.append(specs(spc._id, kep_state.sma, kep_state.ecc, kep_state.inc, kep_state.raan, kep_state.aop, kep_state.ta))

        return orb_specs

    def add_instrument_to_spacecraft(self, new_instru, sensor_to_spc):
        """ Add instrument to the given list of spacecrafts.

            :param new_instru: New instrument.
            :paramtype new_instru: :class:`instrupy.base.Instrument`

            :param sensor_to_spc: Unique IDs of spacecrafts to which the instrument is to be attached. 
            :paramtype sensor_to_spc: list

        """
        if isinstance(self.spacecraft, Spacecraft):
            self.spacecraft = [self.spacecraft] # make into list
        if isinstance(self.spacecraft, list):
            # iterate over the list of available spacecrafts
            for spc_indx, spc in enumerate(self.spacecraft):
                if spc._id in sensor_to_spc:
                    # add the sensor to the spacecraft
                    self.spacecraft[spc_indx].add_instrument(new_instru)

    def add_groundstation_from_dict(self, d):
        """ Add one or more ground-stations to the list of ground-stations (instance variable ``groundStation``).

            :param d: Dictionary or list of dictionaries with the ground-station specifications.
            :paramtype d: list, dict or dict

        """
        gndstn_list = util.dictionary_list_to_object_list( d, GroundStation)
        
        if isinstance(self.groundStation, GroundStation):
            self.groundStation = [self.groundStation] # make into list
        if isinstance(self.groundStation, list):
            self.groundStation.extend(gndstn_list) # extend the list
        else:
            self.groundStation = gndstn_list

    def update_epoch_from_dict(self, d):
        """ Update the instance variable ``epoch`` from input dictionary of date specifications.

            :param d: Dictionary with the date specifications.
            :paramtype d: dict

        """
        self.epoch = OrbitState.date_from_dict(d)
    
    def update_propagator_settings(self, prop_dict, propTimeResFactor=None):
        """ Update the propagator settings.

            :param prop_dict: Dictionary with the specifications of the orbit propagator. See the :class:`orbitpy.propagator` module for available propagators and their descriptions.
            :paramtype prop_dict: dict

            :param propTimeResFactor: Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`.
            :paramtype propTimeResFactor: float
        """
        
        self.update_settings(propTimeResFactor=propTimeResFactor) # update settings
        
        # Compute step-size
        if self.spacecraft:
            time_step = orbitpy.propagator.compute_time_step(self.spacecraft, self.settings.propTimeResFactor)
        else:
            time_step = 60
        if prop_dict.get("stepSize") is None: # i.e. user has not specified step-size
            prop_dict["stepSize"] = time_step # use the autocalculate step-size
        if prop_dict.get("stepSize") > time_step:
            warnings.warn('User given step-size is greater than auto calculated step-size.')
        
        # parse propagator
        factory = PropagatorFactory()
        self.propagator = factory.get_propagator(prop_dict)

    def update_coverage_settings_from_dict(self, d):
        """ Update the coverage settings.

            :param d: Dictionary with the coverage settings. Expected key/value pairs are: 

                                        * coverageType: Type of coverage calculation.
                                        * gridResFactor: Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`.

            :paramtype d: dict

        """
        coverageType = d.get('coverageType', None)
        self.update_settings(coverageType=coverageType)

        gridResFactor = d.get('gridResFactor', None)
        self.update_settings(gridResFactor=gridResFactor)
        

    def update_settings(self, outDir=None, coverageType=None, propTimeResFactor=None, gridResFactor=None, opaque_atmos_height=None):
        """ Update settings.

            :param outDir: Output directory path.
            :paramtype outDir: str 

            :param coverageType: Type of coverage calculation. 
            :paramtype coverageType: str or None

            :param propTimeResFactor: Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`.
            :paramtype propTimeResFactor: float

            :param gridResFactor: Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`. 
            :paramtype gridResFactor: float

            :param opaque_atmos_height: Relevant in-case of inter-satellite communications. Height of atmosphere (in kilometers) below which line-of-sight 
                                    communication between two satellites **cannot** take place. Default value is 0 km.
            :paramtype opaque_atmos_height_km: float

        """
        if outDir:
            self.settings.outDir = str(outDir)
        if coverageType:
            self.settings.coverageType = str(coverageType)
        if propTimeResFactor:
            self.settings.propTimeResFactor = float(propTimeResFactor)
        if gridResFactor:
            self.settings.gridResFactor = float(gridResFactor)
        if opaque_atmos_height:
            self.settings.opaque_atmos_height = float(opaque_atmos_height)

    def add_coverage_grid_from_dict(self, grid_dict):
        """ Add coverage grid(s) from the input dictionary. Update the output-info instanace variable.

            :param grid_dict: Dictionary with the grid specifications. Grid can be of type 'autoGrid' or 'customGrid'. 
                                Refer to :class:`orbitpy.grid.Grid.from_autogrid_dict` and :class:`orbitpy.grid.Grid.from_customgrid_dict` for description 
                                of the expected key/value pairs of the dictionary.
            :paramtype grid_dict: dict or list, dict

        """    
        grid = []    
        if grid_dict:
            # make into list of dictionaries if not already list
            if not isinstance(grid_dict, list):
                grid_dict = [grid_dict]
            # iterate through the list of grids            
            for gd in grid_dict:
                grid_type = Grid.Type.get(gd['@type'])
                if ((grid_type==Grid.Type.AUTOGRID) and (gd.get('gridRes', None) is None)):
                    # calculate grid resolution factor
                    if self.spacecraft:
                        gridRes = orbitpy.grid.compute_grid_res(self.spacecraft, self.settings.gridResFactor)
                        print('Auto-calculated grid resolution is %f using a grid-resolution factor of %f.' %(gridRes, self.settings.gridResFactor))
                    else:
                        gridRes = 1 # 1 deg grid-resolution in case of no spacecraft.
                    gd['gridRes'] = gridRes

                grid.append(Grid.from_dict(gd))
        
        # Save auto-grids to files. If custom-grid, then file already exists and is not re-written.
        out_info = []
        for indx, val in enumerate(grid):
            if grid[indx].filepath is None: # must be an auto-grid configuration, so filepath instance variable is None
                fp = self.settings.outDir + '/grid_id' + str(grid[indx]._id) # save the file with name according to the unique-id. TODO: check that there is no-conflict with an custom-grid file.
                oi = grid[indx].write_to_file(fp)
                out_info.append(oi)
        if out_info:
            # add output-info to the instance variable
            self.outputInfo = orbitpy.util.add_to_list(self.outputInfo, out_info)

        if isinstance(self.grid, Grid):
            self.grid = [self.grid] # make into list
        if isinstance(self.grid, list):
            self.grid.extend(grid)
        else:
            self.grid = grid

    def add_spacecraft_from_dict(self, d):
        """ Add one or more spacecrafts to the list of spacecrafts (instance variable ``spacecraft``).

            :param d: Dictionary or list of dictionaries with the spacecraft specifications.
            :paramtype d: list, dict or dict

        """
        sc_list = util.dictionary_list_to_object_list( d, Spacecraft)
        
        if isinstance(self.spacecraft, Spacecraft):
            self.spacecraft = [self.spacecraft] # make into list
        if isinstance(self.spacecraft, list):
            self.spacecraft.extend(sc_list) # extend the list
        else:
            self.spacecraft = sc_list

    def add_constellation_from_dict(self, constel_dict, spc_bus_dict=None, instru_dict=None):
        """ Parse the spacecrafts in the input constellation and add them to the list of spacecrafts (instance variable ``spacecraft``).
            A common spacecraft-bus and instrument(s) can also be specified.
 
            :param constel_dict: Dictionary with the constellation specifications.
            :paramtype constel_dict: dict

            :param spc_bus_dict: Dictionary with the spacecraft-bus specifications.
            :paramtype spc_bus_dict: dict

            :param instru_dict: Dictionary (or list of dictionaries) with the instrument specifications. 
            :paramtype instru_dict: list,dict or dict
        
        """
        factory = ConstellationFactory()        
        constel = factory.get_constellation_model(constel_dict)
        orbits = constel.from_dict(constel_dict).generate_orbits()
        
        # one common spacecraft-bus specifications for all the satellites in the constellation
        spc_bus = SpacecraftBus.from_dict(spc_bus_dict) if spc_bus_dict is not None else None

        # list of instrument specifications could be present, in which case all the instruments in the list are attached to all the 
        # spacecraft in the constellation.
        if instru_dict:
            instru_list = orbitpy.util.dictionary_list_to_object_list(instru_dict, Instrument) # list of instruments
        else:
            instru_list = None
        sc_list = []
        for orb in orbits:
            sc_list.append(Spacecraft(orbitState=orb, spacecraftBus=spc_bus, instrument=instru_list, _id='spc_'+orb._id)) # note the assignment of the spacecraft-id
        
        # Add to existing list of spacecrafts,
        if isinstance(self.spacecraft, Spacecraft):
            self.spacecraft = [self.spacecraft] # make into list
        if isinstance(self.spacecraft, list):
            self.spacecraft.extend(sc_list) # extend the list
        else:
            self.spacecraft = sc_list

    def update_duration(self, duration):
        """ Update the instance variable epoch from input dictionary of date specifications.

            :param d: Dictionary with the date specifications.
            :paramtype d: dict

        """
        self.duration = float(duration)  

    def to_dict(self):
        """ Translate the ``Mission`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``Mission`` object as python dictionary.
        :rtype: dict
        
        """
        outputInfo_dict = None
        if self.outputInfo is not None:
            if not isinstance(self.outputInfo, list):
                self.outputInfo = [self.outputInfo] # make into list
            outputInfo_dict = orbitpy.util.object_list_to_dictionary_list(self.outputInfo)

        return dict({"@type": "Mission",
                     "epoch": orbitpy.util.OrbitState.date_to_dict(self.epoch) if self.epoch is not None else None,
                     "duration": self.duration,                     
                     "spacecraft": orbitpy.util.object_list_to_dictionary_list(self.spacecraft) if self.spacecraft is not None else None,
                     "propagator": self.propagator.to_dict() if self.propagator is not None else None,
                     "grid": orbitpy.util.object_list_to_dictionary_list(self.grid) if self.grid is not None else None,                     
                     "groundStation": orbitpy.util.object_list_to_dictionary_list(self.groundStation) if self.groundStation is not None else None,
                     "outputInfo": outputInfo_dict,
                     "settings": self.settings.to_dict() if self.settings is not None else None,
                     "@id": self._id})

    def __repr__(self):
        return "Mission.from_dict({})".format(self.to_dict())

    def execute(self):
        """ Execute a mission where all the spacecrafts are propagated, (field-of-regard) coverage calculated for all spacecraft-instrument-modes, 
            ground-station contact-periods computed between all spacecraft-ground-station pairs and intersatellite contact-periods
            computed for all possible spacecraft pairs.

            .. note:: In case of *GRID COVERAGE* calculation, the field-of-regard is used (and not the scene-field-of-view). In case of SAR instruments and coverage calculations
                        involving grid (i.e. *GRID COVERAGE* and *POINTING OPTIONS WITH GRID COVERAGE*), only the access at the middle of a continuous access interval is shown
                        (see :ref:`correction_of_access_files`). 

            :return: Mission output info as an heterogenous list of output info objects from propagation, coverage and contact calculations.
            :rtype: list, :class:`orbitpy.propagate.PropagatorOutputInfo`, :class:`orbitpy.coveragecalculator.CoverageOutputInfo`, :class:`orbitpy.contactfinder.ContactFinderOutputInfo`

        """           
        out_info = [] # list to accululate info objects of the various executions        

        # execute orbit propagation for all satellites in the mission
        for spc_idx, spc in enumerate(self.spacecraft):
            
            # make satellite directory
            sat_dir = self.settings.outDir + '/sat' + str(spc_idx) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)

            state_cart_file = sat_dir + 'state_cartesian.csv'
            state_kep_file = sat_dir + 'state_keplerian.csv'
            x = self.propagator.execute(spc, self.epoch, state_cart_file, state_kep_file, self.duration)
            out_info.append(x)

            # loop over all the instruments and modes (per instrument) and calculate the corresponding coverage, data-metrics
            if spc.instrument:
                for instru_idx, instru in enumerate(spc.instrument):

                    for mode_idx, mode in enumerate(instru.mode):                        
                        
                        if self.settings.coverageType == "GRID COVERAGE":
                            if self.grid is None:
                                warnings.warn('Grid not specified, skipping Grid Coverage, Data metrics calculations.')
                                continue
                            # iterate over multiple grids
                            for grid_idx, grid in enumerate(self.grid):
                                grid_fl = self.settings.outDir + 'grid_' + str(grid_idx) + '.csv'
                                x = grid.write_to_file(grid_fl) # TODO inefficient since the same file would be written multiple times, revise
                                out_info.append(x)
                                acc_fl = sat_dir + 'access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '_grid'+ str(grid_idx) + '.csv'
                                cov_calc = GridCoverage(grid=grid, spacecraft=spc, state_cart_file=state_cart_file)
                                # For SAR instruments pick only the time-instants at the middle of access-intervals
                                if instru._type == 'Synthetic Aperture Radar':
                                    filter_mid_acc = True
                                else:
                                    filter_mid_acc = False
                                x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, use_field_of_regard=True, out_file_access=acc_fl)
                                out_info.append(x)     

                                dm_file = sat_dir + 'datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '_grid'+ str(grid_idx) + '.csv'
                                dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=state_cart_file, access_file_info=AccessFileInfo(instru._id, mode._id, acc_fl))                    
                                x = dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._id, mode_id=mode._id)
                                out_info.append(x)                  

                        elif self.settings.coverageType == "POINTING OPTIONS COVERAGE":
                            acc_fl = sat_dir + 'access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
                            cov_calc = PointingOptionsCoverage(spacecraft=spc, state_cart_file=state_cart_file)
                            x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl)
                            out_info.append(x)

                            dm_file = sat_dir + 'datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
                            dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=state_cart_file, access_file_info=AccessFileInfo(instru._id, mode._id, acc_fl))                    
                            x = dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._id, mode_id=mode._id)
                            out_info.append(x) 

                        elif self.settings.coverageType == "POINTING OPTIONS WITH GRID COVERAGE":
                            if self.grid is None:
                                warnings.warn('Grid not specified, skipping Grid Coverage, Data metrics calculations.')
                                continue
                            # iterate over multiple grids
                            for grid_idx, grid in enumerate(self.grid):
                                grid_fl = self.settings.outDir + 'grid_' + str(grid_idx) + '.csv'
                                x = grid.write_to_file(grid_fl)
                                out_info.append(x)
                                acc_fl = sat_dir + 'access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '_grid'+ str(grid_idx) + '.csv'
                                cov_calc = PointingOptionsWithGridCoverage(grid=grid, spacecraft=spc, state_cart_file=state_cart_file)
                                
                                # For SAR instruments pick only the time-instants at the middle of access-intervals
                                if instru._type == 'Synthetic Aperture Radar':
                                    filter_mid_acc = True
                                else:
                                    filter_mid_acc = False
                                x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl, filter_mid_acc=filter_mid_acc)
                                out_info.append(x)
                        
                                dm_file = sat_dir + 'datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '_grid'+ str(grid_idx) + '.csv'
                                dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=state_cart_file, access_file_info=AccessFileInfo(instru._id, mode._id, acc_fl))                    
                                x = dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._id, mode_id=mode._id)
                                out_info.append(x)
        
            # loop over all the ground-stations and calculate contacts
            if self.groundStation:
                for gnd_stn_idx, gnd_stn in enumerate(self.groundStation):
                    
                    out_gnd_stn_file = 'gndStn'+str(gnd_stn_idx)+'_contacts.csv'
                    x = ContactFinder.execute(spc, gnd_stn, sat_dir, state_cart_file, None, out_gnd_stn_file, ContactFinder.OutType.INTERVAL, 0)
                    out_info.append(x)

        # Calculate inter-satellite contacts
        intersat_comm_dir = self.settings.outDir + '/comm/'
        if os.path.exists(intersat_comm_dir):
            shutil.rmtree(intersat_comm_dir)
        os.makedirs(intersat_comm_dir)

        for spc1_idx in range(0, len(self.spacecraft)):
            spc1 = self.spacecraft[spc1_idx]
            spc1_state_cart_file = self.settings.outDir + 'sat' + str(spc1_idx) + '/state_cartesian.csv'
            
            # loop over the rest of the spacecrafts in the list (i.e. from the current spacecraft to the last spacecraft in the list)
            for spc2_idx in range(spc1_idx+1, len(self.spacecraft)):
                
                spc2 = self.spacecraft[spc2_idx]
                spc2_state_cart_file = self.settings.outDir + 'sat' + str(spc2_idx) + '/state_cartesian.csv'
                                
                out_intersat_filename = 'sat'+str(spc1_idx)+'_to_sat'+str(spc2_idx)+'.csv'
                x = ContactFinder.execute(spc1, spc2, intersat_comm_dir, spc1_state_cart_file, spc2_state_cart_file, out_intersat_filename, ContactFinder.OutType.INTERVAL, self.settings.opaque_atmos_height)
                out_info.append(x)
    
        return out_info
    
    def execute_propagation(self):
        """ Execute orbit propagation for all spacecrafts in the mission.
        """
        out_info = [] # list to accululate info objects of the various executions        

        # execute orbit propagation for all satellites in the mission
        for spc_idx, spc in enumerate(self.spacecraft):
            
            # make satellite directory
            sat_dir = self.settings.outDir + '/sat' + str(spc_idx) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)

            state_cart_file = sat_dir + 'state_cartesian.csv'
            state_kep_file = sat_dir + 'state_keplerian.csv'
            x = self.propagator.execute(spc, self.epoch, state_cart_file, state_kep_file, self.duration)
            out_info.append(x)
        
        # add output-info to the instance variable
        self.outputInfo = orbitpy.util.add_to_list(self.outputInfo, out_info)

        return out_info
                    

                    






        