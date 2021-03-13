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
        return GridCoverage(grid = Grid.from_dict(d.get('grid_filepath', None)), 
                            _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the J2AnalyticalPropagator object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: J2AnalyticalPropagator object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "J2 Analytical Propagator",
                     "stepSize": self.stepSize,
                     "@id": self._id})

    def __repr__(self):
        return "J2AnalyticalPropagator.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.stepSize == other.stepSize)
                
        else:
            return NotImplemented

    def execute(self, spacecraft, start_date=None, out_file_cart=None, out_file_kep=None, duration=1):
        """ Execute orbit propagation of the input spacecraft and write to a csv data-file.

        :param spacecraft: Spacecraft whose orbit is to be propagated.
        :paramtype spacecraft: :class:`orbitpy.util.Spacecraft`

        :param out_file_cart: File name with path of the file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are written.
        :paramtype out_file_cart: str

        :param out_file_kep: File name with path of the file in which the orbit states in KEPLERIAN_EARTH_CENTERED_INERTIAL are written.
        :paramtype out_file_kep: str

        :param start_date: Time start for propagation. If None, the date at which the spacecraft orbit-state is referenced shall be used as the start date.
        :paramtype start_date: :class:`orbitpy.propcov.AbsoluteDate`

        :param duration: Time duration propagation in days.  Default is 1 day.
        :paramtype duration: float

        :return: 0 if success. The results are stored in a csv data-file at the indicated file-path.
        :rtype: int

        """
        # form the propcov.Spacecraft object
        earth = propcov.Earth()
