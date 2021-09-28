""" 
.. module:: grid

:synopsis: *Module to handle grid (array of geo-coordinates) related operations.*

.. todo:: Revise the module to a factory pattern implementation. 

"""
import numpy as np
import pandas as pd
from collections import namedtuple
import uuid

import propcov
from instrupy.util import Entity, EnumEntity, Constants
import orbitpy.util
from orbitpy.util import OutputInfoUtility

GridPoint = namedtuple("GridPoint", ["latitude", "longitude"])
"""Function returns a namedtuple class to store grid-points as (in general this shall be a list) latitudes and longitudes in degrees.

"""

class Grid(Entity):
    """ Class to handle grid related operations. 

    :ivar point_group: A ``propcov`` object of the instance ``propcov.PointGroup``, used to store and handle 
                       the grid locations (latitudes and longitudes in degrees). The grid-points are referred by indices starting from 0.
                       E.g. Grid-point 0 refers to the first grid-point in the point_group object (which can be obtained 
                       using the ``GetLatLon(.)``, ``GetPointPositionVector(.)`` function.).
    :vartype point_group: :class:`propcov.PointGroup`

    :ivar num_points: Total number of grid points.
    :vartype num_points: int

    :ivar filepath: Path to file (with filename) where the grid-point locations are stored. See :class:`orbitpy.grid.Grid.from_customgrid_dict`
                    for description of the file-format. The instance variable is ``None`` if no file is present.
    :vartype filepath: str or None

    :ivar _id: Unique identifier of the grid. Could be used to indicate a region identifier, where the set of grid-points represent a region.
    :vartype _id: str/ int

    """

    def __init__(self, point_group=None, filepath=None, _id=None):

        self.point_group = point_group if point_group is not None and isinstance(point_group, propcov.PointGroup) else None
        self.num_points = self.point_group.GetNumPoints()
        self.filepath = str(filepath) if filepath is not None else None
        super(Grid, self).__init__(_id, "Grid")

    class Type(EnumEntity):
        """Enumeration of recognized grid types."""
        CUSTOMGRID = "CUSTOMGRID",
        AUTOGRID = "AUTOGRID"

    @staticmethod
    def from_dict(d):
        """ Parses an Grid object from a normalized JSON dictionary.
        
        :param d: Dictionary with the Grid specifications.

                Following keys are to be specified.
                
                * "@type": (str) Grid type. Possible values are "autoGrid" or "customGrid". Depending on the value, other key/value pairs manifest, as described
                                 in the functions ``from_autogrid(d)`` and ``from_custom_grid(d)``.

        :paramtype d: dict

        :return: ``Grid`` object.
        :rtype: :class:`orbitpy.grid.Grid`

        """ 
        grid_type = Grid.Type.get(d['@type']) 
        if grid_type == Grid.Type.AUTOGRID:
            return Grid.from_autogrid_dict(d)
        elif grid_type == Grid.Type.CUSTOMGRID:
            return Grid.from_customgrid_dict(d)
        else:
            raise Exception("Please specify a valid grid type.")

    def to_dict(self):
        """ Translate the Grid object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
            The grid data is stored in a file whose path is to supplied as an argument.
        
            :return: ``Grid`` object as python dictionary
            :rtype: dict

        """
        return {"@type": "CUSTOMGRID", "covGridFilePath": self.filepath, "@id": self._id}

    @staticmethod
    def from_autogrid_dict(d):
        """ Parses an ``Grid`` object from dictionary with ``autoGrid`` specifications (i.e. "@type":"autoGrid"). 

        Following keys are to be specified:

                * "latUpper": (float) Upper latitude in degrees. Default value is 90 deg.
                * "latLower": (float) Lower latitude in degrees. Default value is -90 deg.
                * "lonUpper": (float) Upper longitude in degrees. Default value is 180 deg.
                * "lonLower": (float) Lower longitude in degrees. Default value is -180 deg.
                * "gridRes": (float)  Grid resolution in degrees. Default value is 1 deg.
                * "@id" : (str or int) Unique grid-identifier. If absent a random id is assigned.

        *Specify latitude bounds in the range of -90 deg to +90 deg. Specify longitude bounds in the range of -180 deg to +180 deg.*
        
        Example:

        .. code-block:: javascript
        
            {
                "@type": "autoGrid",
                "@id":1,
                "latUpper":20,
                "latLower":15,
                "lonUpper":45,
                "lonLower":0,
                "gridRes": 0.5               
            }

        :return: Grid object
        :rtype: :class:`orbitpy.grid.Grid`

        """
        latUp = np.deg2rad(d.get("latUpper", 90))
        latLow = np.deg2rad(d.get("latLower", -90))
        lonUp = np.deg2rad(d.get("lonUpper", 180))
        lonLow = np.deg2rad(d.get("lonLower", -180))
        angleBetweenPoints = np.deg2rad(d.get("gridRes", 1))

        point_group = propcov.PointGroup()
        point_group.SetLatLonBounds(latUp=latUp, latLow=latLow, lonUp=lonUp, lonLow=lonLow)
        point_group.AddHelicalPointsByAngle(angleBetweenPoints=angleBetweenPoints)
        return Grid( point_group=point_group,
                     _id = d.get('@id', uuid.uuid4())
                    )
        
    @staticmethod
    def from_customgrid_dict(d):
        """  Parses an ``Grid`` object from dictionary with ``customGrid`` specifications (i.e. "@type":"customGrid"). 

        Following keys are to be specified:

                * "covGridFilePath": (str) Filepath to the file containing the grid points.
                * "@id" : (str or int) Unique grid-identifier. If absent a random id is assigned.

        Example:

        .. code-block:: javascript
        
            {
                "@type": "customGrid",
                "@id":101,
                "covGridFilePath": "C:\workspace\covGridUSA.csv"
            }

        The datafile needs to be of CSV format as indicated in the example below. *lat[deg]* is the latitude
        in degrees, and *lon[deg]* is the longitude in degrees. The grid-points are referred by indices starting from 0.

        .. csv-table:: Example of the coverage grid data file.
            :header: lat [deg], lon [deg]
            :widths: 10,10
        
            9.9,20
            9.9,20.1015
            9.9,20.203
            -49.1,21.9856
            -49.1,22.1383
            -49.1,22.291
            -49.1,22.4438
            -49.1,22.5965
            -49.1,22.7493
            -49.1,22.902

        .. warning:: Please specify latitudes in the range of -90 deg to +90 deg and longitudes in the range of -180 deg to +180 deg. Do *NOT* 
                  specify the longitudes in range of 0 deg to 360 deg.
        
        :return: Grid object
        :rtype: :class:`orbitpy.grid.Grid`

        """
        data = pd.read_csv(d['covGridFilePath'])
        data = data.multiply(np.pi/180) # convert angles to radians
        point_group = propcov.PointGroup()
        point_group.AddUserDefinedPoints(data['lat [deg]'].tolist(),data['lon [deg]'].tolist())
        return Grid( point_group = point_group,
                     filepath = d['covGridFilePath'],
                     _id = d.get('@id', str(uuid.uuid4()))
                    )

    def write_to_file(self, filepath):
        """ Write the grid points (coordinates) to a csv file.

        :param filepath: File path (with filename) of the output file. The format of the data written in the file is the same format of an 
                         input custom grid data file as described in the function ``from_custom_grid``.
        :paramtype filepath: str

        :returns: Output grid info.
        :rtype: :class:`orbitpy.grid.GridOutputInfo`

        """
        grid_points = self.get_lat_lon()
        df = pd.DataFrame(list(zip(grid_points.latitude, grid_points.longitude)), columns =['lat [deg]','lon [deg]'])
        df.to_csv(filepath, index=False)
        self.filepath = filepath # update the instance variable
        return GridOutputInfo.from_dict({'gridId': self._id,
                                         'gridFile': self.filepath,
                                         '_id': None}    
                                        )

    def get_lat_lon(self):
        """ Get all the grid points (coordinates).

        :return: Grid points (latitudes and longitudes in degrees).
        :rtype: namedtuple, (list, list), float

        """
        [lat, lon] = self.point_group.GetLatLonVectors()
        # convert to degrees and round to two decimal places
        lat= np.rad2deg(np.array(lat)).round(decimals=3)
        lon= np.rad2deg(np.array(lon)).round(decimals=3)   

        return GridPoint(latitude=list(lat), longitude=list(lon))
    
    def get_lat_lon_from_index(self, indexes):
        """ Get the grid points (coordinates) corresponding to the input (list of) point-indices.
        
        :param indexes: List of indices.
        :paramtype indexes: list, int

        :return: Grid points (latitudes and longitudes in degrees) corresponding to the input indices.
        :rtype: namedtuple, (list, list), float

        """
        # if only one index specified
        if isinstance(indexes, int):
            (lat, lon) = self.point_group.GetLatAndLon(indexes)
            return GridPoint(latitude=np.rad2deg(lat).round(decimals=3), longitude=np.rad2deg(lon).round(decimals=3))
        elif isinstance(indexes, list):
            if len(indexes)==1:
                (lat, lon) = self.point_group.GetLatAndLon(indexes[0])
                return GridPoint(latitude=np.rad2deg(lat).round(decimals=3), longitude=np.rad2deg(lon).round(decimals=3))

        (_lat, _lon) = self.get_lat_lon()
        # filter
        lat = [_lat[x] for x in indexes]
        lon = [_lon[x] for x in indexes]        

        return GridPoint(latitude=lat, longitude=lon)

def compute_grid_res(spacecraft, grid_res_fac):
    """ Compute grid resolution to be used for coverage grid generation. See SMAD 3rd ed Pg 113. Fig 8-13.

    The grid resolution is to be set such that at any given arbitrary time, the sensor footprint from its (scene) field-of-**view** captures atleast one grid-point
    when the satellite is somewhere well within the interior of a region. This can be achieved by setting the grid resolution (spacing between
    the grid points) to be less than the minimum footprint dimension. A grid resolution factor :code:`grid_res_fac` is defined 
    (with default value 0.9) and the grid resolution is computed as (:code:`grid_res_fac` . minimum footprint angular dimension).
    For example, in case of rectangular sensor with FOV: 5 deg x 15 deg at an altitude of 500km, the minimum footprint angular dimension 
    is the Earth centric angle subtended by the 5 deg side = 0.3922 deg. This gives the grid resolution as 0.3530 deg.

    :param spacecraft: List of spacecrafts in the mission.
    :paramtype spacecraft: list, :class:`orbitpy:util.Spacecraft`

    :param grid_res_fac: Factor which decides the resolution of the generated grid.
    :paramtype grid_res_fac: float  

    :return: Grid resolution in degrees.
    :rtype: float  

    .. note:: The field-of-**view** is used here, and not the field-of-**regard**. The scene-field-of-view is used if different from the field-of-view. 
              The scene-field-of-view is typically larger than the instrument field-of-view to allow for coarser grid-resolution.

    """
    RE = Constants.radiusOfEarthInKM        

    params = orbitpy.util.helper_extract_spacecraft_params(spacecraft) # obtain list of tuples of relevant spacecraft parameters
    # find the minimum required grid resolution over all satellites
    min_grid_res_deg = 1e1000 # some large number
    for p in params:

        sma = p.sma # orbit semi-major axis
        fov = None
        if p.scfov_height is not None:
            fov = min(p.scfov_height, p.scfov_width) # note that scene field of view is considered not field of regard
        if fov is None:
            # no instruments specified, hence no scene field-of-view to consider, hence consider the entire horizon angle as field-of-view
            f = RE/sma
            fov = np.rad2deg(2*np.arcsin(f))

        # calculate horizon angle
        sinRho = RE/sma            
        horizon_angle = np.rad2deg(2*np.arcsin(sinRho))
        if(fov > horizon_angle):
            fov = horizon_angle # use the horizon angle if the instrument fov is larger than the horizon angle

        hfov_deg = 0.5*fov
        
        # below snippet is needed because sometimes when for_at = horizon angle, it leads to x slightly greater then 1 due to floating-point errors.
        x = np.sin(np.deg2rad(hfov_deg))/sinRho
        if abs(np.sin(np.deg2rad(hfov_deg)) - sinRho) < 1e-7:
            x = 1
        elev_deg = np.rad2deg(np.arccos(x))

        lambda_deg = 90 - hfov_deg - elev_deg # half-earth centric angle 
        eca_deg = lambda_deg*2 # total earth centric angle
        grid_res_deg = eca_deg*grid_res_fac 
        if(grid_res_deg < min_grid_res_deg):
            min_grid_res_deg = grid_res_deg

    return min_grid_res_deg

class GridOutputInfo(Entity):
    """ Class to hold information about the grid-data (geo-coordinates).
    
    :ivar gridId: Grid identifier.
    :vartype gridId: str or int

    :ivar gridFile: File (filename with path) where the grid data is saved.
    :vartype gridFile: str

    :ivar _id: Unique identifier of the ``GridOutputInfo`` instance.
    :vartype _id: str or int

    """
    def __init__(self, gridId=None, gridFile=None, _id=None):
        self.gridId = gridId if gridId is not None else None
        self.gridFile = str(gridFile) if gridFile is not None else None

        super(GridOutputInfo, self).__init__(_id, OutputInfoUtility.OutputInfoType.GridOutputInfo.value)
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``GridOutputInfo`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the GridOutputInfo attributes.

        Following keys are to be specified:

                * "gridId": (str or int) Grid identifier.
                * "gridFile": (str)  File (filename with path) where the grid data is saved.
                * "@id" : (str or int) Unique identifier. Default is None.

        :paramtype d: dict

        :return: GridOutputInfo object.
        :rtype: :class:`orbitpy.grid.GridOutputInfo`

        """
        return GridOutputInfo( gridId = d.get('gridId', None),
                               gridFile = d.get('gridFile', None),
                               _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the GridOutputInfo object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: GridOutputInfo object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": OutputInfoUtility.OutputInfoType.GridOutputInfo.value,
                     "gridId": self.gridId,
                     "gridFile": self.gridFile,
                     "@id": self._id})

    def __repr__(self):
        return "GridOutputInfo.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.gridId==other.gridId) and (self.gridFile==other.gridFile)
                
        else:
            return NotImplemented
    
    def check_loose_equality(self, other):
        """ Check for equality with another ``GridOutputInfo`` object considering only some instance variables.

            :param other: The other ``GridOutputInfo`` object with which the comparision shall be done.
            :paramtype other: :class:`orbitpy.grid.GridOutputInfo`

        """
        if(isinstance(self, other.__class__)):
            return (self.gridId==other.gridId)
                
        else:
            return False