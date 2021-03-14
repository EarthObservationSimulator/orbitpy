""" 
.. module:: coveragecalculator

:synopsis: *Module providing classes and functions to handle coverage related calculations.*

"""
import numpy as np
from collections import namedtuple
import csv

import propcov
from instrupy.util import Entity, Constants
from orbitpy.grid import Grid
import orbitpy.util


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

class GridCoverage(Entity):
    """A coverage calculator which calculates coverage over a grid.

    The instance variable(s) correspond to the coverage calculator setting(s). 

    :ivar grid: Array of locations (longitudes, latitudes) over which coverage calculation is performed.
    :vartype grid: :class:`orbitpy.util.grid`

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, grid=None, _id=None):
        self.grid = grid if grid is not None and isinstance(grid, Grid) else None
        super(GridCoverage, self).__init__(_id, "Grid Coverage")

    @staticmethod
    def from_dict(d):
        grid_dict = d.get('grid', None)
        return GridCoverage(grid = Grid.from_dict(grid_dict) if grid_dict else None, 
                            _id  = d.get('@id', None))

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