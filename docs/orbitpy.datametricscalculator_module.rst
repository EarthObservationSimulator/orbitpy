``orbitpy.datametricscalculator`` --- Data Metrics Calculator Module
======================================================================

Description
^^^^^^^^^^^^^

This module provides classes and functions to handle observation data-metric calculations by invoking the :code:`instrupy` package. The module may be thought
of as a wrapper which passes in the relevant OrbitPy results (time of observation, target location, satellite-position) as inputs (along with the instrument object)
to the :class:`instrupy.base.Instrument.calc_data_metrics` function of the InstruPy module. 

An object of the class ``DataMetricsCalculator`` is be initialized for a particular spacecraft by passing the corresponding ``Spacecraft`` object and the filepath of the file
containing the spacecraft's propagated states.
The results of the coverage calculation (performed using any one of the coverage-calculators provided in the :class:`orbitpy.coveragecalculator` module) 
is also necessary for the data-metrics calculation. The access file locations, and the identifiers of the
instrument, mode corresponding to the coverage calculations is collected in the ``namedtuple`` object ``AccessFileInfo``. A list of ``AccessFileInfo`` objects
are passed as an input during the initialization of the ``DataMetricsCalculator`` object.


``DataMetricsCalculator.execute`` function
............................................
The ``execute`` function can be invoked on an ``DataMetricsCalculator`` object to calculate the data-metrics corresponding to each access. The
instrument, mode identifiers are to be provided so that the corresponding access-file can be selected for processing. 
The satellite state data is extracted from the satellite state file corresponding 
to the access-time of an access event. The target location at the access-time is available in the access data file. A ``DataMetricsOutputInfo`` object
containing meta-data about the results of the calculation is returned upon the successful execution of the ``execute`` function.

.. _datametrics_file_format:

Output data file format
-------------------------
The format of the output data file is as follows:

*  The first row contains the coverage calculation type.
*  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
*  The third row contains the time-step size in seconds. 
*  The fourth row contains the duration (in days) for which the data-metrics calculation is done.
*  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

Description of the csv data is given below:

.. csv-table:: Observation data metrics description
   :header: Column, Data type, Units, Description
   :widths: 10,10,10,30

   time index, int, , Access time-index.
   GP index, int, , Grid-point index. 
   pnt-opt index, int, , Pointing options index.
   lat [deg], float, degrees, Latitude corresponding to the GP index/ pnt-opt index.
   lon [deg], float, degrees, Longitude in corresponding to the GP index/ pnt-opt index.

Other columns containing the data-metrics specific to the instrument type are present. Refer to the docs of the corresponding instrument type (in ``instrupy`` package)
for description of the evaluated data-metrics.

Examples
^^^^^^^^^

1. In the below code snippet a spacecraft with two instruments with ids *bs1* and *bs2* is initialized. Grid based coverage calculations are first carried out
   for *bs1*. A datametrics calculator object is initialized with the spacecraft object, state file and the access-file info corresponding to *bs1*. The 
   data-metrics calculator is executed to give the results in the file *bs1_datametrics.csv*.

   The coverage calculations for *bs2* is then carried out and the corresponding access-file info is added to the data-metrics calculator object. The 
   data-metrics calculator is executed to give the results in the file *bs2_datametrics.csv*.
   
   .. code-block:: python

         from orbitpy.util import OrbitState, Spacecraft, SpacecraftBus
         from orbitpy.propagator import J2AnalyticalPropagator
         from orbitpy.coveragecalculator import GridCoverage
         from orbitpy.grid import Grid
         from instrupy.base import Instrument
         from orbitpy.datametricscalculator import DataMetricsCalculator, AccessFileInfo
         import os

         out_dir = os.path.dirname(os.path.realpath(__file__))

         # initialize J2 analytical propagator with 2 secs propagation step-size
         j2_prop = J2AnalyticalPropagator.from_dict({"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':2} )

         # initialize orbit (initial state of the satellite)
         orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                           "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6378+500, "ecc": 0.001, "inc": 0, "raan": 20, "aop": 0, "ta": 120}
                           })
         bus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}})
         instru1 = Instrument.from_json({"@id":"bs1","@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":30}, 
                                       "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}})
         instru2 = Instrument.from_json({"@id":"bs2","@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":25}, 
                                       "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "SIDE_LOOK", "sideLookAngle":25}})
         # spacecraft with 1 instrument
         sc = Spacecraft(orbitState=orbit, spacecraftBus=bus, instrument=[instru1, instru2])

         state_cart_file = os.path.dirname(os.path.realpath(__file__)) + '/cart_state.csv'

         # execute the propagator for duration of 0.1 days 
         j2_prop.execute(sc, None, state_cart_file, None, duration=0.1) 

         # make the Grid object
         grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})

         # set output file path
         out_file_access = out_dir + '/access_bs1.csv'

         # execute coverage calculations for "bs1" and subsequently datametrics calculations
         cov_cal = GridCoverage(grid=grid, spacecraft=sc, state_cart_file=state_cart_file)
         cov_cal.execute(instru_id="bs1", mode_id=None, use_field_of_regard=False, out_file_access=out_file_access, filter_mid_acc=False)

         acf = AccessFileInfo("bs1", None, out_file_access)
         dm_calc = DataMetricsCalculator(sc, state_cart_file, acf)

         out_file_dm = out_dir + '/bs1_datametrics.csv'
         dm_calc.execute(out_datametrics_fl=out_file_dm, instru_id='bs1')

         # execute coverage calculations for "bs2" and subsequently datametrics calculations
         out_file_access = out_dir + '/access_bs2.csv'
         cov_cal.execute(instru_id="bs2", mode_id=None, use_field_of_regard=False, out_file_access=out_file_access, filter_mid_acc=False)

         # add the (new) access file information
         dm_calc.add_access_file_info(AccessFileInfo("bs2", None, out_file_access)) 

         out_file_dm = out_dir + '/bs2_datametrics.csv'
         dm_calc.execute(out_datametrics_fl=out_file_dm, instru_id='bs2')

         bs1_datametrics.csv
         --------------------
         Datametrics file based on GRID COVERAGE
         Epoch [JDUT1] is 2458265.0
         Step size [s] is 2.0
         Mission Duration [Days] is 0.1
         time index,GP index,pnt-opt index,lat [deg],lon [deg],observation range [km],look angle [deg],incidence angle [deg],solar zenith [deg]
         0,4303,,0.0,76.0,503.3,0.14,0.15,77.65
         1,4303,,0.0,76.0,503.5,1.37,1.47,77.66
         2,4303,,0.0,76.0,504.0,2.87,3.09,77.67
         ...

         bs2_datametrics.csv
         --------------------
         Datametrics file based on GRID COVERAGE
         Epoch [JDUT1] is 2458265.0
         Step size [s] is 2.0
         Mission Duration [Days] is 0.1
         time index,GP index,pnt-opt index,lat [deg],lon [deg],observation range [km],look angle [deg],incidence angle [deg],solar zenith [deg]
         0,3943,,2.0,76.0,553.9,23.7,25.7,76.92
         1,3943,,2.0,76.0,554.0,23.73,25.73,76.93
         2,3943,,2.0,76.0,554.5,23.83,25.84,76.93
         ...


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.datametricscalculator.DataMetricsCalculator
   orbitpy.datametricscalculator.DataMetricsOutputInfo

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.datametricscalculator.AccessFileInfo