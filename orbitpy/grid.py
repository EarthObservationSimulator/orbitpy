""" 
.. module:: grid

:synopsis: *Module to handle grid (array of geo-coordinates) related operations.*

"""
import numpy as np
import pandas as pd

import propcov
from instrupy.util import Entity, EnumEntity, Constants
import orbitpy.util

class Grid(Entity):
    """ Class to handle grid related operations. 

    Note that there is an implicit relationship that the entries at the same index of the respective lists
    correspond to one another. E.g. the coords of pointIndex[5] = (lon[5], lat[5]).

    :ivar gpi: List of indices of the grid points. The entries should be unique. 
    :vartype gpi: list, int

    :ivar lon: Longitude coordinates in degrees.
    :vartype lon: list, float

    :ivar lat: Latitude coordinates in degrees.
    :vartype lat: list, float

    :ivar _id: Unique identifier of the grid. Could be used to indicate a region identifier, where the set of grid-points represent a region.
    :vartype _id: str

    """

    def __init__(self, gpi=None, lon=None, lat=None, _id=None):
        if gpi is not None:
            if isinstance(gpi, list):
                self.gpi = [float(x) for x in gpi]
            else: # single element
                self.gpi = [int(gpi)] # make into list
        if lon is not None:
            if isinstance(lon, list):
                self.lon = [float(x) for x in lon]
            else: # single element
                self.lon = [float(lon)] # make into list
        if lat is not None:
            if isinstance(lat, list):
                self.lat = [float(x) for x in lat]
            else: # single element
                self.lat = [float(lat)] # make into list
        super(Grid, self).__init__(_id, "Grid")

    class Type(EnumEntity):
        """Enumeration of recognized coverage-grid types."""
        CUSTOMGRID = "CUSTOMGRID",
        AUTOGRID = "AUTOGRID"

    @staticmethod
    def from_dict(d):
        """ Parses an Grid object from a normalized JSON dictionary.
        
        :param d: Dictionary with the Grid specifications.

                Following keys are to be specified.
                
                * "@type": (str) Grid type. Possible values are "autoGrid" or "customGrid". Depending on the value, other key/value pairs manifest, as described
                                 in the functions ``from_autogrid(d)`` and ``from_custom_grid(d)``.
                * "@id": (str) Unique identifier of the grid. Could be used to indicate a region identifier, where the set of grid-points 
                          represent a region. Default: A random string.

        :paramtype d: dict

        :return: Grid object.
        :rtype: :class:`orbitpy.grid.Grid`

        """ 
        grid_type = Grid.Type.get(d['@type']) 
        if grid_type == Grid.Type.AUTOGRID:
            return Grid.from_autogrid_dict(d)
        elif grid_type == Grid.Type.CUSTOMGRID:
            return Grid.from_custom_grid(d)
        else:
            raise Exception("Please specify a valid grid type.")

    @staticmethod
    def from_autogrid_dict(d):
        """ Parses an ``Grid`` object from dictionary with ``autoGrid`` specifications (i.e. "@type":"autoGrid"). 

        Following keys are to be specified:

                *  "latUpper": (float) Upper latitude in degrees. Default value is 90 deg.
                *  "latLower": (float) Lower latitude in degrees. Default value is -90 deg.
                *  "lonUpper": (float) Upper longitude in degrees. Default value is 180 deg.
                *  "lonLower": (float) Lower longitude in degrees. Default value is -180 deg.
                *  "gridRes": (float)  Grid resolution in degrees. Default value is 1 deg.

        Specify latitude bounds in the range of -90 deg to +90 deg. Specify longitude bounds in the range of -180 deg to +180 deg. 
        
        Example:

        .. code-block:: javascript
        
            {
                "@type": "autoGrid",
                "@id":1,
                "latUpper":20,
                "latLower":15,
                "lonUpper":360,
                "lonLower":0,
                "gridRes": 0.5               
            }

        """
        latUp = np.deg2rad(d.get("latUpper", 90))
        latLow = np.deg2rad(d.get("latLower", -90))
        lonUp = np.deg2rad(d.get("lonUpper", 180))
        lonLow = np.deg2rad(d.get("lonLower", -180))
        angleBetweenPoints = np.deg2rad(d.get("gridRes", 1))

        point_group = propcov.PointGroup()
        point_group.SetLatLonBounds(latUp=latUp, latLow=latLow, lonUp=lonUp, lonLow=lonLow)
        point_group.AddHelicalPointsByAngle(angleBetweenPoints=angleBetweenPoints)
        return Grid( gpi=data['gpi'].tolist(),
                     lat=data['lat [deg]'].tolist(),
                     lon=data['lon [deg]'].tolist(),
                     _id = d.get('@id', None)
                    )
        

    @staticmethod
    def from_custom_grid(d):
        """  Parses an ``Grid`` object from dictionary with ``customGrid`` specifications (i.e. "@type":"customGrid"). 

        Following keys are to be specified:

                *  "covGridFilePath": (str) Filepath to the file containing the grid points.

        Example:

        .. code-block:: javascript
        
            {
                "@type": "customGrid",
                "@id":101,
                "covGridFilePath": "C:\workspace\covGridUSA.csv"
            }

        The datafile needs to be of CSV format as indicated in the example below. *gpi* is the grid point index, *lat[deg]* is the latitude
        in degrees, and *lon[deg]* is the longitude in degrees. **gpi must start from 0 and increment by 1 as shown in the example.**

        .. csv-table:: Example of the coverage grid data file.
        :header: gpi,lat[deg],lon[deg]
        :widths: 10,10,10
        
            0,9.9,20
            1,9.9,20.1015
            2,9.9,20.203
            3,-49.1,21.9856
            4,-49.1,22.1383
            5,-49.1,22.291
            6,-49.1,22.4438
            7,-49.1,22.5965
            8,-49.1,22.7493
            9,-49.1,22.902

        .. note:: Please specify latitudes in the range of -90 deg to +90 deg and longitudes in the range of -180 deg to +180 deg. Do *NOT* 
                  specify the longitudes in range of 0 deg to 360 deg.
        """
        data = pd.read_csv(d['covGridFilePath'])
        return Grid( gpi=data['gpi'].tolist(),
                     lat=data['lat [deg]'].tolist(),
                     lon=data['lon [deg]'].tolist(),
                     _id = d.get('@id', None)
                    )

    def write_to_file(self, filepath):
        """ Write the grid points (coordinates) to a csv file.

        :param filepath: File path (with filename) of the output file. The format of the data written in the file is the same format of an 
                         input custom grid data file as described in the function ``from_custom_grid``.
        :paramtype filepath: str

        """
        df = pd.DataFrame(list(zip(self.gpi, self.lat, self.lon)), 
               columns =['gpi', 'lat [deg]','lon [deg]'])
        df.to_csv(filepath)


def compute_grid_res(spacecraft, grid_res_fac=0.9):
    """ Compute grid resolution to be used for coverage grid generation. See SMAD 3rd ed Pg 113. Fig 8-13.

    The grid resolution is set such that at any given arbitrary time, the sensor footprint from its field-of-**view** captures atleast one grid-point
    when the satellite is somewhere well within the interior of a region. This can be achieved by setting the grid resolution (spacing between
    the grid points) to be less than the minimum footprint dimension. A grid resolution factor :code:`grid_res_fac` is defined 
    (with default value 0.9) and the grid resolution is computed as (:code:`grid_res_fac` . minimum footprint angular dimension).
    For example, in case of rectangular sensor with FOV: 5 deg x 15 deg at an altitude of 500km, the minimum footprint angular dimension 
    is the Earth centric angle subtended by the 5 deg side = 0.3922 deg. This gives the grid resolution as 0.3530 deg.

    .. figure:: grid_res_illus.png
        :scale: 75 %
        :align: center

        Illustration of relationship between grid resolution and sensor footprint.

    .. note:: Note that the grid-resolution is calculated from the FOV.

    :param spacecraft: List of spacecrafts in the mission.
    :paramtype spacecraft: list, :class:`orbitpy:util.Spacecraft`

    :param grid_res_fac: Factor which decides the resolution of the generated grid. Default value is 0.9.
    :paramtype grid_res_fac: float  

    :return: Grid resolution in degrees.
    :rtype: float  

    .. note:: The field-of-**view** is used here, and not the field-of-**regard**.

    """
    RE = Constants.radiusOfEarthInKM        

    params = orbitpy.util.helper_extract_spacecraft_params(spacecraft) # obtain list of tuples of relevant spacecraft parameters

    # find the minimum required grid resolution over all satellites
    min_grid_res_deg = 1e1000 # some large number
    for p in params:

        sma = p.sma # orbit semi-major axis
        fov = min(p.fov_height, p.fov_width) # note that field of view is considered not field of regard
        if fov is None:
            # no instruments specified, hence no field-of-view to consider, hence consider the entire horizon angle as field-of-view
            f = RE/sma
            fov = np.rad2deg(2*np.arcsin(f))

        # calculate maximum horizon angle
        sinRho = RE/sma            
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