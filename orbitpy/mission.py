""" 
.. module:: mission

:synopsis: *Module to handle mission initialization and execution.*

"""
import json
import os, shutil
import numpy as np
import math
import uuid
from collections import namedtuple
import pandas as pd

from instrupy.util import Entity
from instrupy import Instrument
import propcov

import orbitpy.util
from .util import Spacecraft, GroundStation, SpacecraftBus
from .constellation import ConstellationFactory
import orbitpy.propagator
import orbitpy.grid
from .propagator import PropagatorFactory
from .coveragecalculator import CoverageCalculatorFactory, CoverageType, GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
from datametricscalculator import DataMetricsCalculator
from .contactfinder import ContactFinder
from .grid import Grid

class Settings(Entity):
    """ Data container of the mission settings.

    :ivar outDir: Output directory path.
    :vartype outDir: str 

    :ivar coverageType: Type of coverage calculation. 
    :vartype coverageType: :class:`orbitpy.coveragecalculator.CoverageType` or None

    :ivar propTimeResFactor: Factor which influences the propagation step-size calculation. See :class:`orbitpy.propagator.compute_time_step`.
    :vartype propTimeResFactor: float

    :ivar gridResFactor: Factor which influences the grid-resolution of an auto-generated grid. See :class:`orbitpy.grid.compute_grid_res`. 
    :vartype gridResFactor: float

    """
    def __init__(self, outDir=None, coverageType=None, propTimeResFactor=None, gridResFactor=None, _id=None):
        self.outDir = str(outDir) if outDir is not None else None
        self.coverageType = coverageType if coverageType is not None and isinstance(coverageType, CoverageType) else None
        self.propTimeResFactor = float(propTimeResFactor) if propTimeResFactor is not None else None
        self.gridResFactor = float(gridResFactor) if gridResFactor is not None else None

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

        :paramtype d: dict

        :return: Settings object.
        :rtype: :class:`orbitpy.mission.Settings`

        """
        
        try: 
            coverageType = CoverageType.get(d.get('coverageType', None))
        except:
            coverageType = None

        return Settings( outDir= d.get('outDir', os.path.dirname(os.path.realpath(__file__))), # current directory as default
                         coverageType = coverageType,
                         propTimeResFactor = d.get('propTimeResFactor', 0.25), # default value is 0.25
                         gridResFactor = d.get('gridResFactor', 0.9) # default value is 0.9
                        )                        
        
    def to_dict(self):
        """ Translate the Settings object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: Settings object as python dictionary.
        :rtype: dict
        
        """
        return dict({"@type": "Settings",
                     "outDir": self.outDir,
                     "coverageType": self.coverageType.value if self.coverageType is not None else None,
                     "propTimeResFactor": self.propTimeResFactor,                     
                     "gridResFactor": self.gridResFactor,
                     "@id": self._id})

    def __repr__(self):
        return "Settings.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes.Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.outDir==other.outDir) and (self.coverageType==other.coverageType) \
                    and (self.propTimeResFactor==other.propTimeResFactor) and (self.gridResFactor==other.gridResFactor)                    
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

    :ivar grid: Grid object to be used in case of coverage calculations.
    :vartype grid: :class:`orbitpy.grid.Grid` or None

    :ivar groundStation: List of ground-stations in the mission.
    :vartype groundStation: list, :class:`orbitpy.util.GroundStation` or None

    :ivar settings: Mission settings. Refer to the ``Settings.from_dict(.)`` method for the default values.
    :vartype settings: :class:`orbitpy.mission.settings`

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, startDate=None, duration=None, spacecraft=None, propagator=None,
                 grid=None, groundStation=None, settings=None, _id=None):
        self.startDate = startDate if startDate is not None and isinstance(startDate, propcov.AbsoluteDate) else None
        self.duration = float(duration) if duration is not None else None
        self.spacecraft = orbitpy.util.initialize_object_list(spacecraft, Spacecraft)
        self.propagator = propagator if propagator is not None else None
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        self.groundStation = orbitpy.util.initialize_object_list(groundStation, GroundStation)
        self.settings = settings if isinstance(settings, Settings) else None

        super(Mission, self).__init__(_id, "Mission")
        
 
    @staticmethod
    def from_dict(d):
        """Parses an Mission object from a normalized JSON dictionary.
        
        :param d: Dictionary with the mission specifications.
        :paramtype d: dict

        :return: Mission object.
        :rtype: :class:`orbitpy.mission.Mission`

        """
        startDate = propcov.AbsoluteDate()
        startDate.SetJulianDate(d.get('startDate', 2459270.5)) # 25 Feb 2021 0:0:0 default startDate

        # parse settings
        settings_dict: = d.get('settings', {})
        settings = Settings.from_dict(settings_dict)

        # parse spacecraft(s) 
        custom_spc_dict = d.get("spacecraft", None)
        constel_dict = d.get("constellation", None)
        if custom_spc_dict is not None:
            spacecraft = orbitpy.util.dictionary_list_to_object_list(custom_spc_dict, Spacecraft)
        elif constel_dict is not None:
            factory = PropagatorFactory()        
            constel = factory.get_propagator(constel_dict)
            orbits = constel.from_dict(constel_dict).generate_orbits()
            # one common spacecraft-bus specifications can be expected to be defined for all the satellites in the constellation
            spc_bus_dict = d.get("spacecraftBus", None)
            spc_bus = SpacecraftBus.from_dict(spc_bus_dict) if spc_bus_dict is not None else None
            # list of instrument specifications could be present, in which case all the instruments in the list are distributed to all the 
            # spacecraft in the constellation.
            instru_dict = d.get("instrument", None)
            instru_list = orbitpy.util.dictionary_list_to_object_list(instru_dict, Instrument) # list of instruments
            spacecraft = []
            for orb in orbits:
                spacecraft.append(Spacecraft(orbitState=orb, spacecraftBus=spc_bus, instrument=instru_list))

        # parse propagator
        factory = PropagatorFactory()
        # Compute step-size
        time_step = orbitpy.propagator.compute_time_step(spacecraft, settings.propTimeResFactor)
        prop_dict = d.get('propagator', {'@type': 'J2 ANALYTICAL PROPAGATOR', 'stepSize': time_step}) # default to J2 Analytical propagator and time-step as calculated before 
        propagator = factory.get_propagator(prop_dict)

        # parse grid        
        grid_dict = d.get('grid', None)
        if grid_dict:
            if ((grid_dict.get('@type', None)=='autogrid') and (grid_dict.get('gridRes', None) is None)):
                # calculate grid resolution factor
                gridRes = orbitpy.grid.compute_grid_res(spacecraft, settings.gridResFactor)
                grid_dict['gridRes'] = gridRes

            grid = Grid.from_dict(grid_dict)
        else:
            grid = None        

        # parse ground-station(s) 
        groundStation = orbitpy.util.dictionary_list_to_object_list(d.get("groundStation", None), GroundStation)
        return Mission(startDate = startDate, # 25 Feb 2021 0:0:0 default startDate
                       duration = d.get('duration', 1), # 1 day default
                       spacecraft = spacecraft,
                       propagator = propagator,                       
                       grid = grid,
                       groundStation = groundStation,
                       settings = settings,
                       _id = d.get('@id', None)
                      ) 
    
    def to_dict(self):
        """ Translate the Mission object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: Mission object as python dictionary.
        :rtype: dict
        
        """
        return dict({"@type": "Mission",
                     "startDate": self.startDate,
                     "duration": self.duration,                     
                     "spacecraft": orbitpy.util.object_list_to_dictionary_list(self.spacecraft),
                     "propagator": self.propagator.to_dict(),
                     "coverageType": self.coverageType.value,
                     "grid": self.grid.to_dict,                     
                     "groundStation": orbitpy.util.object_list_to_dictionary_list(self.groundStation),
                     "settings": self.settings.to_dict(),
                     "@id": self._id})

    def __repr__(self):
        return "Mission.from_dict({})".format(self.to_dict())

    def execute(self):
        """ Execute a mission where all the spacecrafts are propagated, (field-of-regard) coverage calculated for all spacecraft-instrument-modes, 
            ground-station contact-periods computed between all spacecraft-ground-station pairs and intersatellite contact-periods
            computed for all possible spacecraft pairs.

        :return: Mission output info as an heterogenous list of output info objects from propagation, coverage and contact calculations.
        :rtype: list, :class:`orbitpy.propagate.PropagatorOutputInfo`, :class:`orbitpy.coveragecalculator.CoverageOutputInfo`, :class:`orbitpy.contactfinder.ContactFinderOutputInfo`

        """           

        out_info = [] # list to accululate info objects of the various objects        

        # execute orbit propagation for all satellites in the mission
        for spc_idx, spc in enumerate(self.spacecraft):
            
            # make satellite directory
            sat_dir = self.outDir + '/sat' + str(spc_idx) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)

            state_cart_file = sat_dir + 'state_cartesian.csv'
            state_kep_file = sat_dir + 'state_keplerian.csv'
            x = self.propagator.execute(spc, self.startDate, state_cart_file, state_kep_file, self.duration)
            out_info.append(x)

            # loop over all the instruments and modes (per instrument) and calculate the corresponding coverage, data-metrics
            if spc.instrument:
                for instru_idx, instru in enumerate(spc.instrument):

                    for mode_idx, mode in enumerate(instru.mode):

                        acc_fl = sat_dir + 'access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
                        
                        if self.coverageType == CoverageType.GRID_COVERAGE:
                            cov_calc = GridCoverage(grid=self.grid, spacecraft=spc, state_cart_file=state_cart_file)
                            x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, use_field_of_regard=True, out_file_access=acc_fl)
                            out_info.append(x)                       

                        elif self.coverageType == CoverageType.POINTING_OPTIONS_COVERAGE:
                            cov_calc = PointingOptionsCoverage(spacecraft=spc, state_cart_file=state_cart_file)
                            x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl)
                            out_info.append(x) 

                        elif self.coverageType == CoverageType.POINTING_OPTIONS_WITH_GRID_COVERAGE:
                            cov_calc = PointingOptionsWithGridCoverage(grid=self.grid, spacecraft=spc, state_cart_file=state_cart_file)
                            x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, out_file_access=acc_fl)
                            out_info.append(x)
                        
                        dm_file = sat_dir + 'datametrics_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'

                        dm_calc = DataMetricsCalculator(spacecraft=spc, state_cart_file=state_cart_file, access_file_info=acc_fl)
            
                        x = dm_calc.execute(out_datametrics_fl=dm_file, instru_id=instru._idx, mode_id=mode._id)
                        out_info.append(x)
        
            # loop over all the ground-stations and calculate contacts
            if self.groundStation:
                for gnd_stn_idx, gnd_stn in enumerate(self.groundStation):
                    
                    out_gnd_stn_file = sat_dir+'gndStn'+str(gnd_stn_idx)+'.csv'
                    x = ContactFinder.execute(spc, gnd_stn, sat_dir, state_cart_file, None, out_gnd_stn_file, ContactFinder.OutType.INTERVAL, 0)
                    out_info.append(x)

        # Calculate inter-satellite contacts
        intersat_comm_dir = self.outDir + '/comm/'
        if os.path.exists(intersat_comm_dir):
            shutil.rmtree(intersat_comm_dir)
        os.makedirs(intersat_comm_dir)

        for spc1_idx in range(0, len(self.spacecraft)):
            spc1 = self.spacecraft[spc1_idx]
            spc1_state_cart_file = self.outDir + 'sat' + str(spc1_idx) + '/state_cartesian.csv'
            
            # loop over the rest of the spacecrafts in the list (i.e. from the current spacecraft to the last spacecraft in the list)
            for spc2_idx in range(spc1_idx+1, len(self.spacecraft)):
                
                spc2_state_cart_file = self.outDir + 'sat' + str(spc1_idx) + '/state_cartesian.csv'
                
                spc2 = self.spacecraft[spc2_idx]
                out_intersat_filename = 'sat'+str(spc_idx)+'_to_sat'+str(spc2_idx)+'.csv'
                x = ContactFinder.execute(spc1, spc2, intersat_comm_dir, spc1_state_cart_file, spc2_state_cart_file, out_intersat_filename, ContactFinder.OutType.INTERVAL, 0)
                out_info.append(x)
    
        return out_info
                    

                    






        