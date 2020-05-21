.. _output_desc:

Output Description
*******************

Satellite States Data
=========================
The satellite states data is produced by invoking the :class:`orbitpy.orbitpropcov` module. The module is initialized by 
the relevant propagation and coverage parameters which can be produced by the :class:`orbitpy.preprocess` module (which
processes JSON formatted files containing mission specifications). The format of the produced data is a CSV file containing 
the satellite states at the propagated time-steps. 

The first four rows contain general information, with the second row containing the mission epoch in Julian Day UT1. The time
in the state data is referenced to this epoch. The third row contains the time-step size in seconds. 
The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 
Description of the data is given below:

.. csv-table:: State data description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   TimeIndex, int, , Time-index
   X[km], float, kilometers, X component of Satellite position in ECI-equatorial frame
   Y[km], float, kilometers, Y component of Satellite position in ECI-equatorial frame
   Z[km], float, kilometers, Z component of Satellite position in ECI-equatorial frame
   VX[km], float, kilometers, X component of Satellite velocity in ECI-equatorial frame
   VY[km], float, kilometers, Y component of Satellite velocity in ECI-equatorial frame
   VZ[km], float, kilometers, Z component of Satellite velocity in ECI-equatorial frame

Access Data
==============
The format of the access data is similar to the satellite states data and is also produced by the :class:`orbitpy.orbitpropcov` module.
The time data of both the states ad access are synced. One access data file is produced for each satellite payload. The intermediate access
files produced by the :ref:`grid_pnts_cov_calc_app` is different from the intermediate file produced by the :ref:`pnt_opts_cov_calc_app`. 

Grid-point based coverage calculations intermediate access file-format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Excluding the :code:`TimeIndex`
column, the column headers are named as :code:`GP0`, :code:`GP1`, :code:`GP2`, and so on corresponding to the grid-point indices. The grid point
data can be found in the coverage grid data file. Each cell entry corresponds to a True/ False condition for access. If there has been access 
(or if there can be access in the case when the FOR is used for access computation), the cell entry is :code:`1`, else there is no entry. During
times are which there is no access over all the grid-points, the entire row is absent. 

Grid-point based coverage calculations intermediate access file-format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Excluding the :code:`TimeIndex`
column, the column headers are named as :code:`PntOpt0`, :code:`PntOpt1`, :code:`PntOpt2`, and so on corresponding to the pointing-option indices. Each cell entry corresponds to
the latitude and longitude (in degrees) seen by the instrument pointing-axis. 

Common final access file-format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final access file is named as *access*. The data is CSV formatted and includes the following columns: 

.. csv-table:: Observation data metrics description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   accessTimeIndex,int, , Observation time-index
   regi, integer, ,Region index
   gpi, integer, ,Grid-point index
   lat[deg],float, degrees, Geocentrc latitude
   lon[deg],float, degrees, Geocentric Longitude 

.. _intersatt_comm_op:

Intersatellite Contact Data
==================================
The intersatellite contact data is produced by invoking the :class:`orbitpy.communications.InterSatelliteComm` class. The class is 
initialized with a list of the satellite state data files (satellites between which contacts needs to be calculated), a :code:`opaque_atmos_height_km`
parameter and the directory in which the results are to be written. 

Two seperate data files are produced for each satellite pair. One of the data files contains information of the contacts at each propagation time step, 
while the other data file contains the contact intervals. The pair of satellites is indicated in the name of the file, where it is presumed
that the name of the satellite is same as the name of the directory in which the corresponding state data file is present. For example if we have
*/sat12/state*, */sat32/state* as the input state files, the name of the resulting output files are *sat12_sat32_detailed* and *sat12_sat32_concise*.

Description of the data in the *_detailed* file is as follows. The first row contains the epoch. The second row contains the time-step size in seconds. 
The third row contains the column headers with the subsequent rows containing the corresponding data. 

.. csv-table:: Detailed contact description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   TimeIndex, int, , Time-index
   AccessOrNoAccess,bool,, Possible values are :code:`True` or :code:`False` corresponding to access and no-access.
   Range[km], float, kilometers, Distance between the two satellites.

Description of the data in the *_concise* file is as follows. The first row contains the epoch. The second row contains the time-step size in seconds.
The third row contains the column headers with the subsequent rows containing the corresponding data. 

.. csv-table:: Concise contact description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   AccessFromIndex,int,, Access interval start time-index.
   AccessToIndex, int,, Access interval end time-index.

.. _satt2gnd_comm_op:

Ground Stations Contact Data
==============================
The ground stations contact data is produced by invoking the :class:`orbitpy.communications.GroundStationComm` class. The class is initialized
by list of directories in which the satellite states are present. The name of the satellite state data files is presumed to be *state*.
The second initialization parameter is the filepath containing the ground station data (See :ref:`groundStations_json_object`).

The resulting files have a similar format to the intersatellite contact data files. The files are written in the respective satellite directories.
The files are named according to the ground-station index given in the input ground station data file.  For example if we have the ground station 
index as *4*, the name of the resulting files are *gndStn4_contact_detailed* and *gndStn4_contact_concise*.

Description of the data in the *_detailed* file is as follows. The first row contains the epoch. The second row contains the time-step size in seconds. 
The third row contains the column headers with the subsequent rows containing the corresponding data. 

.. csv-table:: Detailed contact description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   TimeIndex, int, seconds, Time-index.
   AccessOrNoAccess,bool,, Possible values are :code:`True` or :code:`False` corresponding to access and no-access.
   Range[km], float, kilometers, Distance between the satellite and the ground station.
   Elevation[deg], float, degrees, Elevation angle at which the satellite is visible from the ground-station.

Description of the data in the *_concise* file is as follows. The first row contains the epoch. The second row contains the time-step size in seconds.
The third row contains the column header with the subsequent rows containing the corresponding data. 

.. csv-table:: Concise contact description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   AccessFromIndex,int,, Access interval start time-index.
   AccessToIndex, int,, Access interval end time-index.
   
Observation Data Metrics 
=========================
The observation data metrics are produced by the :class:`orbitpy.obsdatametrics` module which inturn invokes the :code:`instrupy` package.
The module can be initialized by dictionary containing the instrument specifications, path to the coverage grid file and a list of directories containing the satellite 
state data, access data. The name of the state data file is presumed to be *state* and the name of the access data file is presumed to be of the
format *payI_access*, where *I* is the identifier of the payload to which the access data corresponds. Currently the module is hardcoded to 
work with only one payload with identifier as *1* and hence the name of the access file is *pay1_access*. 

The name of the output file is *pay1_obsMetrics*. The first row of the resulting file contains the mission epoch in Julian Day UT1. 
The second row contains the time-step size in seconds. The third row contains the column headers and the subsequent rows contain the corresponding
data. The description of the first two columns is given below. The rest of the columns contain the data-metrics corresponding to the particular
instrument type (passive-optical, SAR or basic sensor). Description of the data metrics can be found in the :code:`instrupy` documentation.

.. csv-table:: Observation data metrics description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   observationTimeIndex,int, , Observation time-index
   regii, integer, ,Region index
   gpi, integer, ,Grid-point index
   lat[deg],float, degrees, Geocentrc latitude
   lon[deg],float, degrees, Geocentric Longitude 

Coverage Grid Data
====================
Coverage grid data is generated by the :code:`oci/bin/genCovGrid` program. The :class:`orbitpy.Preprocess` class triggers the program 
in the case when the user has specified for generation of grid coordinates via the :code:`@type:autoGrid`  option in the :code:`grid` JSON object
in the user configuration JSON file.

The user can specify bounds on the latitudes and longitudes of a list of regions. If the :code:`customGridRes` parameter is specified in the :code:`settings` JSON
object, a grid of points is generated at the specified grid resolution. If not specified, the grid resolution is automatically determined 
according to the rule described in :ref:`grid_res_determination`. The specified latitude bounds must be in the range -90 deg to + 90 deg 
and the specified longitude bounds must be in the range -180 deg to +180 deg. The produced grid points are indexed from 0 onwards
and can be uniquely identifed by the indices.  A CSV formatted file is produced with columns as described below:

.. csv-table:: Observation data metrics description
   :header: Column, Data type, Units, Description
   :widths: 10,10,5,40

   regi, str,, Unique identifier for region as indicated by the user in the :code:`grid` JSON object.
   gpi, integer,, Grid-point index
   lat[deg], float, degrees, Latitude
   lon[deg], float, degrees, Longitude

.. todo:: Write about pattern of the generated grid-points