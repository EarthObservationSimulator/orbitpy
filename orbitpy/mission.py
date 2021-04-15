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
from .util import Spacecraft, GroundStation
from .propagator import PropagatorFactory, J2AnalyticalPropagator
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

    :ivar grid: Grid object to be used in case of coverage calculations.
    :vartype grid: :class:`orbitpy.grid.Grid` or None

    :ivar groundStation: List of ground-stations in the mission.
    :vartype groundStation: list, :class:`orbitpy.util.GroundStation` or None

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, startDate=None, duration=None, outDir=None, spacecraft=None, propagator=None, coverageType=None, grid=None, groundStation=None, _id=None):
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None
        self.outDir = str(outDir) if outDir is not None else None
        self.spacecraft = orbitpy.util.initialize_object_list(spacecraft, Spacecraft)
        self.propagator = propagator if propagator is not None and isinstance(propagator, J2AnalyticalPropagator) else None
        self.coverageType = coverageType if coverageType is not None and isinstance(coverageType, CoverageType) else None
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
        spacecraft = orbitpy.util.dictionary_list_to_object_list(d.get("Spacecraft", None), Spacecraft)
        # parse propagator
        prop_dict = d.get('propagator', None)
        if prop_dict:
            prop_type = prop_dict.get('@type', 'J2 ANALYTICAL PROPAGATOR')
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
                     "grid": self.grid.to_dict,
                     "groundStation": orbitpy.util.object_list_to_dictionary_list(self.groundStation),
                     "@id": self._id})

    def __repr__(self):
        pass

    def execute(self):
        pass