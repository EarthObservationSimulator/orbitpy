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

import orbitpy.util
from .util import Spacecraft, GroundStation, SpacecraftBus
from .constellation import ConstellationFactory
from .propagator import PropagatorFactory
from .coveragecalculator import CoverageCalculatorFactory, CoverageType, GridCoverage, PointingOptionsCoverage, PointingOptionsWithGridCoverage
from datametricscalculator import DataMetricsCalculator
from .contactfinder import ContactFinder
from .grid import Grid

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

    :ivar outDir: Output directory path.
    :vartype outDir: str 

    :ivar spacecraft: List of spacecraft in the mission.
    :vartype spacecraft: list, :class:`orbitpy.util.Spacecraft`

    :ivar propagator: Orbit propagator.
    :vartype propagator: :class:`orbitpy.propagator.J2AnalyticalPropagator`

    :ivar coverageType: Type of coverage calculation. 
    :vartype coverageType: :class:`orbitpy.coveragecalculator.CoverageType` or None

    :ivar fieldOfRegardCoverage: Flag to indicate if coverage calculations is to be done for field-of-regard or field-of-view.
                                 Note that the flag is relevant only in case of `CoverageType.GRIDCOVERAGE`. . Default is None.
    :vartype fieldOfRegardCoverage: bool or None

    :ivar grid: Grid object to be used in case of coverage calculations.
    :vartype grid: :class:`orbitpy.grid.Grid` or None

    :ivar groundStation: List of ground-stations in the mission.
    :vartype groundStation: list, :class:`orbitpy.util.GroundStation` or None

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, startDate=None, duration=None, outDir=None, spacecraft=None, propagator=None, coverageType=None, 
                 fieldOfRegardCoverage=None, grid=None, groundStation=None, _id=None):
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None
        self.outDir = str(outDir) if outDir is not None else None
        self.spacecraft = orbitpy.util.initialize_object_list(spacecraft, Spacecraft)
        self.propagator = propagator if propagator is not None and isinstance(propagator, J2AnalyticalPropagator) else None
        self.coverageType = coverageType if coverageType is not None and isinstance(coverageType, CoverageType) else None
        self.fieldOfRegardCoverage = bool(fieldOfRegardCoverage) if fieldOfRegardCoverage is not None and isinstance(fieldOfRegardCoverage, bool) else None
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        self.groundStation = orbitpy.util.initialize_object_list(groundStation, GroundStation)

        super(Mission, self).__init__(_id, "Mission")
 
    @staticmethod
    def from_dict(d):
        """Parses an Mission object from a normalized JSON dictionary.
        
        :param d: Dictionary with the mission specifications.
        :paramtype d: dict

        :return: Mission object.
        :rtype: :class:`orbitpy.mission.Mission`

        """
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
        prop_dict = d.get('propagator', None)
        if prop_dict:
            prop_type = prop_dict.get('@type', 'J2 ANALYTICAL PROPAGATOR') # default is J2 analytical propagator
            factory = PropagatorFactory()        
            propagator = factory.get_propagator(prop_type)
        else:
            propagator = None
        # parse coverage related objects
        try: 
            coverageType = CoverageType.get(d.get('coverageType', None))
        except:
            coverageType = None
        grid_dict = d.get('grid', None)
        if grid_dict:
            grid = Grid.from_dict(grid_dict)
        # parse ground-station(s) 
        groundStation = orbitpy.util.dictionary_list_to_object_list(d.get("groundStation", None), GroundStation)
        return Mission(startDate = d.get('startDate', 2459270.5), # 25 Feb 2021 0:0:0 default startDate
                       duration = d.get('duration', 1), # 1 day default
                       outDir= d.get('outDir', os.path.dirname(os.path.realpath(__file__))), # current directory as default
                       spacecraft = spacecraft,
                       propagator = propagator,
                       coverageType = coverageType,
                       fieldOfRegardCoverage = d.get('fieldOfRegardCoverage', None),
                       grid = grid,
                       groundStation = groundStation,
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
                     "fieldOfRegardCoverage": self.fieldOfRegardCoverage,
                     "grid": self.grid.to_dict,                     
                     "groundStation": orbitpy.util.object_list_to_dictionary_list(self.groundStation),
                     "@id": self._id})

    def __repr__(self):
        return "Mission.from_dict({})".format(self.to_dict())

    def execute(self):
        """ Execute a mission where all the spacecrafts are propagated, coverage calculated for all spacecraft-instrument-mode, 
            ground-station contact-periods computed between all spacecraft-ground-station pairs and intersatellite contact-periods
            computed for all possible spacecraft pairs.

        :return: Mission output info as an heterogenous list of output info objects from propagation, coverage and contact calculations.
        :rtype: list, :class:`orbitpy.propagate.PropagatorOutputInfo`, :class:`orbitpy.coveragecalculator.CoverageOutputInfo`, :class:`orbitpy.contactfinder.ContactFinderOutputInfo`

        """           

        out_info = [] # list to accululate info objects of the various objects        

        # execute orbit propagation for all satellites in the mission
        for spc_idx, spc in enumerate(self.spacecraft):
            
            # make satellite directory
            sat_dir = self.outDir + '/' + str(spc_idx) + '/'
            if os.path.exists(sat_dir):
                shutil.rmtree(sat_dir)
            os.makedirs(sat_dir)

            state_cart_file = sat_dir + 'state_cartesian.csv'
            state_kep_file = sat_dir + 'state_keplerian.csv'
            x = self.propagator.execute(spc, self.startDate, state_cart_file, state_kep_file, self.duration)
            out_info.append(x)

            # loop over all the instruments and modes (per instrument) and calculate the corresponding coverage, data-metrics
            for instru_idx, instru in enumerate(spc.instrument):

                for mode_idx, mode in enumerate(instru.mode):

                    acc_fl = sat_dir + 'access_instru' + str(instru_idx) + '_mode' + str(mode_idx) + '.csv'
                    
                    if self.coverageType == CoverageType.GRID_COVERAGE:
                        cov_calc = GridCoverage(grid=self.grid, spacecraft=spc, state_cart_file=state_cart_file)
                        x = cov_calc.execute(instru_id=instru._id, mode_id=mode._id, use_field_of_regard=self.fieldOfRegardCoverage, out_file_access=acc_fl)
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
                    

                    






        