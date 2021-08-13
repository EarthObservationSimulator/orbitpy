``orbit.grid`` --- Grid Module
================================

Description
^^^^^^^^^^^^^

Module to handle grid (array of geo-coordinates) related operations. The ``Grid`` class of this module can be used to either generate set of 
grid points given latitude/ longitude bounds or load a custom set of grid points. 

The module also offers computation of an appropriate grid-resolution for list of satellites and an user-set *grid-resolution factor* 
by using the ``compute_grid_res(.)`` function. The grid resolution is to be set such that at any given arbitrary time, the sensor footprint 
from its (scene) field-of-**view** captures atleast one grid-point when the satellite is somewhere well within the interior of a region. 
This can be achieved by setting the grid resolution (spacing between the grid points) to be less than the minimum footprint dimension. 
A grid resolution factor :code:`grid_res_fac` is defined (with default value 0.9) and the grid resolution is computed as 
(:code:`grid_res_fac` . minimum footprint angular dimension).
For example, in case of rectangular sensor with FOV: 5 deg x 15 deg at an altitude of 500km, the minimum footprint angular dimension 
is the Earth centric angle subtended by the 5 deg side = 0.3922 deg. This gives the grid resolution as 0.3530 deg.

.. figure:: grid_res_illus.png
   :scale: 75 %
   :align: center

   Illustration of relationship between grid resolution and sensor footprint.

.. note:: The field-of-**view** is used here, and not the field-of-**regard**. The scene-field-of-view is used if different from the field-of-view. 
          The scene-field-of-view is typically larger than the instrument field-of-view to allow for coarser grid-resolution (and hence faster coverage computation).

.. warning:: Please specify latitudes in the range of -90 deg to +90 deg and longitudes in the range of -180 deg to +180 deg while loading points
            from a data file. Do *NOT* specify the longitudes in range of 0 deg to 360 deg.

.. todo:: Describe the grid pattern of the auto generated grid points.

Examples
^^^^^^^^^

1. Generating a autogrid of a region with the latitude bounds of 15 deg to 20 deg and longitude bounds of 45 deg to 80 deg and grid-resolution 
   (i.e. spacing between the grid-points) of 1 deg.

   .. code-block:: python

         from orbitpy.grid import Grid
         regionA = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
         print(regionA.num_points) # access total number of generated points
         print(regionA.get_lat_lon_from_index([0,2,10])) # access the lat, lon coordinates of grid-points 0, 2, 10. Note that the indx starts from 0.
         print(regionA.get_lat_lon) # get all the generated grid-points

         >> 169
         >> GridPoint(latitude=[20.0, 20.0, 20.0], longitude=[45.0, 47.13, 55.651])
         >> GridPoint(latitude=[20.0, 20.0, 20.0,... 16.0, 16.0], longitude=[45.0, 46.065, 47.13, 48.195,...77.254, 78.295, 79.335])
                  
2. Load points from a data-file (customgrid). Note that the latitudes have to be in the range of -90 deg to +90 deg and longitudes 
   have to be in the range of -180 deg to +180 deg.
   
   .. code-block:: python

         gridDataIn.csv
         ---------------
         lat [deg],lon [deg]
         50,-110
         50,-106.044
         50,-102.088
         50,-98.1319
   
         from orbitpy.grid import Grid
         import os

         covGridFilePath = os.path.dirname(os.path.realpath(__file__)) + '/gridDataIn.csv' # path to the file containing the grid-data
         regionB = Grid.from_customgrid_dict({"@type": "customGRID", "covGridFilePath": covGridFilePath, "@id": 5})
         print(regionB.num_points) # access total number of generated points
         print(regionB.get_lat_lon_from_index([0,2,10])) # access the lat, lon coordinates of grid-points 0, 2, 10

         >> 4
         >> GridPoint(latitude=[50.0, 50.0], longitude=[-110, -102.088])

3. Writing data to a file. Note the ``GridOutputInfo`` object which is returned. This object stores metadata about the grid data 
   (such as location of output file, grid-id, etc).
   
   .. code-block:: python
         
         from orbitpy.grid import Grid
         import os

         out_file = os.path.dirname(os.path.realpath(__file__)) + '/gridDataOut.csv'
         o = Grid.from_autogrid_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})
         out_info = o.write_to_file(out_file)
         print(out_info)

         >> GridOutputInfo.from_dict({'@type': 'GridOutputInfo', 'gridId': 1, 'gridFile': '/mnt/hgfs/Workspace/orbits/gridDataOut.csv', '@id': None})

         gridDataOut.csv
         ----------------
         lat [deg],lon [deg]
         20.0,45.0
         20.0,46.065
         20.0,47.13
         ...

4. Computing grid resolution for a set of 2 satellites with 1 and 2 instruments respectively. The altitude of both the satellites and the FOV of all 
   the instruments impact the footprint-size and hence the grid-resolution. Output is in degrees.

   .. code-block:: python
         
         import orbitpy.grid 
         from orbitpy.util import OrbitState, Spacecraft
         from instrupy import Instrument

         RE = 6378.137 # radius of Earth in kilometers
         instru1 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 20}}')
         instru2 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 5}}')
         instru3 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 15}}')

         orbit1 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+700, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
         orbit2 = OrbitState.from_dict({"date":{"dateType":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+710, "ecc": 0.001, "inc": 30, "raan": 0, "aop": 0, "ta": 0}})

         sats = [Spacecraft(orbitState=orbit1, instrument=[instru1]), # list of 2 satellites with 1 and 2 instruments respectively
                 Spacecraft(orbitState=orbit2, instrument=[instru2, instru3])]
         x = orbitpy.grid.compute_grid_res(sats, 1) # custom grid resolution factor is chosen as 0.9
         print(x)

         >> 0.5013032847651403


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.grid.Grid
   orbitpy.grid.GridOutputInfo

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.grid.GridPoint
   orbitpy.grid.compute_grid_res
