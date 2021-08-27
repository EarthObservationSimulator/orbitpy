``orbitpy.coveragecalculator`` --- Coverage Calculator
===========================================================

Description
^^^^^^^^^^^^^

Module providing classes and functions to handle coverage related calculations. Factory method pattern is used for initializing the coverage Calculator 
object (please see :ref:`constellation_module` for details). The module provides for three types of coverage calculations which are described in detail below.
Users may additionally define their own coverage calculator classes adherent to the same interface functions 
(``from_dict(.)``, ``to_dict(.)``, ``execute(.)``, ``__eq__(.)``) as in any of the built in coverage calculator classes.

.. grid_cov_desc::

*GRID COVERAGE* 
----------------

The *GRID COVERAGE* type of coverage calculation involves find the access-times of a spacecraft over a region represented by a grid. Each ``GridCoverage`` object is specific to 
a particular grid and spacecraft. The class instance is initialized using the grid object, spacecraft object and path to a data file containing the satellite propagated orbit-states. 
The format of the input data file of the spacecraft states is the same as the format of the output data file of the 
:class:`orbitpy.propagator` module (see :ref:`propagator_module`). The states must be of the type ``CARTESIAN_EARTH_CENTERED_INERTIAL``.

``GridCoverage.execute`` function
..................................

The coverage calculation can be executed using the ``execute(.)`` function. The instrument and the mode of the instrument (in the spacecraft) can be specified 
by means of their respective identifiers (in the ``instru_id``, ``mode_id`` input arguments). If not specified, the first instrument in the list of spacecraft's instruments, the first mode of the instrument (see the docs of :class:`instrupy.base.Instrument`)
in the list of modes of the instrument shall be selected. 

Coverage is calculated for the period over which the input spacecraft propagated states are available. The time-resolution of the coverage calculation is the same as the time resolution at which the spacecraft states are available.
Note that the sceneFOV of an instrument (which may be the same as the instrument FOV) is used for coverage calculations unless it has been specified to use the field-of-regard (using the ``use_field_of_regard`` input argument).

The ``filter_mid_acc`` input argument can be used to specify if the access times only at the middle of an continuous access-interval. Finally the ``out_file_access`` input argument is 
used to specify the filepath (with filename) at which the results are to be written.
E.g. If the access takes place at time-indices 450, 451, 452, 453, 454, and if the ``filter_mid_acc`` flag is specified to be true, then only the access time-index = 452 is written
in the results.

A ``CoverageOutputInfo`` object containing meta-info about the results is returned at the end of execution of the function.

Output data file format
.........................

The output of executing the coverage calculator is a csv data file containing the access data.

*  The first row contains the coverage calculation type.
*  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
*  The third row contains the time-step size in seconds. 
*  The fourth row contains the mission duration in days.
*  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

Description of the coverage data is given below:

.. csv-table:: Coverage data description
      :header: Column, Data type, Units, Description
      :widths: 10,10,10,30

      time index, int, , Access time-index.
      GP index, integer, , Grid-point index.
      lat [deg], float, degrees, Latitude corresponding to the GP index.
      lon [deg], float, degrees, Longitude corresponding to the GP index.

.. pointing_opt_cov_desc::

*POINTING OPTIONS COVERAGE*
----------------------------

This type of coverage calculations is possible for an instrument (on a spacecraft) with a set of pointing-options.
A pointing-option refers to orientation of the instrument in the NADIR_POINTING frame. The set of pointing-options 
represent all the possible orientations of the instrument due to maneuverability of the instrument and/or satellite-bus.
The ground-locations for each pointing-option, at each propagation time-step is calculated as the coverage result.

The class instance is initialized using the spacecraft object and path to a data file containing the satellite propagated orbit-states. 
The format of the input data file of the spacecraft states is the same as the format of the output data file of the 
:class:`orbitpy.propagator` module (see :ref:`propagator_module`). The states must be of the type ``CARTESIAN_EARTH_CENTERED_INERTIAL``.

``PointingOptionsCoverage.execute`` function
...............................................

The coverage calculation can be executed using the ``execute(.)`` function. The instrument and the mode of the instrument (in the spacecraft) can be specified 
by means of their respective identifiers (in the ``instru_id``, ``mode_id`` input arguments). If not specified, the first instrument in the list of spacecraft's instruments, the first mode of the instrument (see the docs of :class:`instrupy.base.Instrument`)
in the list of modes of the instrument shall be selected.
A ``CoverageOutputInfo`` object containing meta-info about the results is returned at the end of execution of the function.

Output data file format
.........................

The output of executing the coverage calculator is a csv data file containing the access data.

*  The first row contains the coverage calculation type.
*  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
*  The third row contains the time-step size in seconds. 
*  The fourth row contains the mission duration in days.
*  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

Description of the coverage data is given below:

.. csv-table:: Coverage data description
      :header: Column, Data type, Units, Description
      :widths: 10,10,10,30

      time index, int, , Access time-index.
      pnt-opt index, int, , "Pointing options index. The indexing starts from 0, where 0 is the first pointing-option in the list of instrument pointing-options."
      lat [deg], float, degrees, Latitude of accessed ground-location.
      lon [deg], float, degrees, Longitude of accessed ground-location.


*POINTING OPTIONS WITH GRID COVERAGE*
--------------------------------------

This type of coverage calculations is similar to the :ref:`grid_cov_desc`, except that the coverage calculations are carried out for the list of pointing-options
(see :ref:`pointing_opt_cov_desc`) available for an instrument. 

``PointingOptionsWithGridCoverage.execute`` function
.......................................................

The function behavior is similar to the ``execute`` function of the ``GridCoverage`` object. Coverage calculations are performed for a specific instrument and mode. 
A key difference is that only the scene-field-of-view of the instrument is considered (no scope to use field-of-regard) in the coverage calculation. 

Output data file format
.........................

The output of executing the coverage calculator is a csv data file containing the access data.

*  The first row contains the coverage calculation type.
*  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
*  The third row contains the time-step size in seconds. 
*  The fourth row contains the mission duration in days.
*  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 

Description of the coverage data is given below:

.. csv-table:: Coverage data description
      :header: Column, Data type, Units, Description
      :widths: 10,10,10,30

      time index, int, , Access time-index.
      pnt-opt index, int, , "Pointing options index. The indexing starts from 0, where 0 is the first pointing-option in the list of instrument pointing-options."
      GP index, integer, , Grid-point index.
      lat [deg], float, degrees, Latitude corresponding to the GP index.
      lon [deg], float, degrees, Longitude corresponding to the GP index.

Helper functions
-------------------

``helper_extract_coverage_parameters_of_spacecraft``
.......................................................

``find_in_cov_params_list``
.............................

``filter_mid_interval_access``
.................................

Examples
^^^^^^^^^

1. *GRID COVERAGE example*
   
   The following snippet of code initializes and executes coverage calculation for a spacecraft in an equatorial orbit, and a grid along the
   equator. The spacecraft is aligned to the nadir-pointing frame (:class:`instrupy.util.ReferenceFrame.NADIR_POINTING`) and the instrument in turn is
   aligned to the spacecraft body frame (:class:`instrupy.util.ReferenceFrame.SC_BODY_FIXED`). The access data the grid-points accessed at every time tick
   of the mission. The interval between the time-ticks is equal to the propagation step-size which here is 2 seconds.

   .. code-block:: python

         from orbitpy.util import OrbitState, Spacecraft, SpacecraftBus
         from orbitpy.propagator import J2AnalyticalPropagator
         from orbitpy.coveragecalculator import GridCoverage
         from orbitpy.grid import Grid
         from instrupy.base import Instrument
         import os
         
         out_dir = os.path.dirname(os.path.realpath(__file__))
         
         # initialize J2 analytical propagator with 2 secs propagation step-size
         j2_prop = J2AnalyticalPropagator.from_dict({"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':2} )
         
         # initialize orbit (initial state of the satellite)
         orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                              "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6378+500, "ecc": 0.001, "inc": 0, "raan": 20, "aop": 0, "ta": 120}
                              })
         bus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}) # bus is aligned to the NADIR_POINTING frame.
         instru = Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":30}, 
                                       "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}}) # instrument is aligned to the bus
         # spacecraft with 1 instrument
         sc = Spacecraft(orbitState=orbit, spacecraftBus=bus, instrument=instru)
         
         state_cart_file = os.path.dirname(os.path.realpath(__file__)) + '/cart_state.csv'
         
         # execute the propagator for duration of 0.1 days 
         j2_prop.execute(sc, None, state_cart_file, None, duration=0.1) 
         
         # make the Grid object
         grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})
         
         # set output file path
         out_file_access = out_dir + '/access.csv'
         
         # run the coverage calculator
         cov_cal = GridCoverage(grid=grid, spacecraft=sc, state_cart_file=state_cart_file)
         out_info = cov_cal.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access, filter_mid_acc=False)
         
         access.csv
         -----------
         GRID COVERAGE
         Epoch [JDUT1] is 2458265.0
         Step size [s] is 2.0
         Mission Duration [Days] is 0.1
         time index,GP index,lat [deg],lon [deg]
         0,4303,0.0,76.0
         1,4303,0.0,76.0
         2,4303,0.0,76.0
         3,4303,0.0,76.0
         4,4303,0.0,76.0
         5,4303,0.0,76.0
         6,4303,0.0,76.0
         7,4303,0.0,76.0
         7,4304,0.0,78.0
         8,4303,0.0,76.0
         8,4304,0.0,78.0
         9,4303,0.0,76.0
         9,4304,0.0,78.0
         10,4303,0.0,76.0
         10,4304,0.0,78.0
         11,4304,0.0,78.0
         12,4304,0.0,78.0
         ...
   
   In below snippet the ``filter_mid_acc`` flag is set to ``True`` instead of ``False``. Observe the difference in the output access data between the above result
   and the below result. In the below result only access at the middle of the access time-interval is shown. E.g. The access to the GP 4303 is from time-index = 0 to 10 
   and the mid-interval access is at time-index = 5.

   .. code-block:: python

      out_info = cov_cal.execute(instru_id=None, mode_id=None, use_field_of_regard=False, out_file_access=out_file_access, filter_mid_acc=True)

      access.csv
      -----------
      GRID COVERAGE
      Epoch [JDUT1] is 2458265.0
      Step size [s] is 2.0
      Mission Duration [Days] is 0.1
      time index,GP index,lat [deg],lon [deg]
      5,4303,0.0,76.0
      17,4304,0.0,78.0
      34,4305,0.0,80.0
      51,4306,0.0,82.0
      ...

2. *GRID COVERAGE example*
   
   In the below snippet, the satellite is equipped with two instruments with multiple modes. The second instrument, and second mode is selected for
   coverage calculation. The ``use_field_of_regard`` flag is set true to indicate that the field-of-regard should be considered for the coverage calculation.
   Note that in absence of the ``orientation`` specifications for the ``SpacecraftBus`` object, the default is assumed to be aligned to the nadir-pointing frame.
   In case of the instrument, the default orientation is aligned to the spacecraft bus.

   .. code-block:: python

      from orbitpy.util import OrbitState, Spacecraft, SpacecraftBus
      from orbitpy.propagator import J2AnalyticalPropagator
      from orbitpy.coveragecalculator import GridCoverage
      from orbitpy.grid import Grid
      from instrupy.base import Instrument
      import os

      out_dir = os.path.dirname(os.path.realpath(__file__))

      j2_prop = J2AnalyticalPropagator.from_dict({"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':2} )

      orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                        "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6378+500, "ecc": 0.001, "inc": 0, "raan": 20, "aop": 0, "ta": 120}
                        })
      bus = SpacecraftBus.from_dict({}) 
      instru1= Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":30}, "@id": "A"}) 
      instru2 = Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 10, "angleWidth": 5},
                                    "mode":[{"@id":1, "maneuver":{"maneuverType": "CIRCULAR", "diameter":10}}, 
                                             {"@id":2, "maneuver":{"maneuverType": "SINGLE_ROLL_ONLY", "A_rollMin":10, "A_rollMax":35}}],
                                    "@id": "B"})                             
      # spacecraft with 2 instruments
      sc = Spacecraft(orbitState=orbit, spacecraftBus=bus, instrument=[instru1, instru2])

      state_cart_file = os.path.dirname(os.path.realpath(__file__)) + '/cart_state.csv'

      # execute the propagator for duration of 0.1 days 
      j2_prop.execute(sc, None, state_cart_file, None, duration=0.1) 

      # make the Grid object
      grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":25, "latLower":-25, "lonUpper":180, "lonLower":-180, "gridRes": 2})

      # set output file path
      out_file_access = out_dir + '/access.csv'

      # run the coverage calculator
      cov_cal = GridCoverage(grid=grid, spacecraft=sc, state_cart_file=state_cart_file)
      out_info = cov_cal.execute(instru_id="B", mode_id=2, use_field_of_regard=True, out_file_access=out_file_access, filter_mid_acc=True) # select instru B, mode 2

      access.csv
      -----------
      GRID COVERAGE
      Epoch [JDUT1] is 2458265.0
      Step size [s] is 2.0
      Mission Duration [Days] is 0.1
      time index,GP index,lat [deg],lon [deg]
      2,3943,2.0,76.0
      17,3944,2.0,78.0
      34,3945,2.0,80.0
      51,3946,2.0,82.0
      68,3947,2.0,84.0         

3. *POINTING OPTIONS COVERAGE example*

   In the below snippet, the satellite is equipped with two instruments. The second instrument is associated with pointing-options and is selected for
   coverage calculation. 

   .. code-block:: python

      from orbitpy.util import OrbitState, Spacecraft, SpacecraftBus
      from orbitpy.propagator import J2AnalyticalPropagator
      from orbitpy.coveragecalculator import PointingOptionsCoverage
      from instrupy.base import Instrument
      import os

      out_dir = os.path.dirname(os.path.realpath(__file__))

      j2_prop = J2AnalyticalPropagator.from_dict({"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':2} )

      orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                     "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6378+500, "ecc": 0.001, "inc": 0, "raan": 20, "aop": 0, "ta": 120}
                     })
      bus = SpacecraftBus.from_dict({}) 
      instru1= Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":10}, "@id": "A"}) 
      instru2 = Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":5},
                                    "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":2.5, "zRotation":0},
                                                      {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-2.5, "zRotation":0}],
                                    "@id": "B"})                             
      # spacecraft with 2 instruments
      sc = Spacecraft(orbitState=orbit, spacecraftBus=bus, instrument=[instru1, instru2])

      state_cart_file = os.path.dirname(os.path.realpath(__file__)) + '/cart_state.csv'

      # execute the propagator for duration of 0.1 days 
      j2_prop.execute(sc, None, state_cart_file, None, duration=0.1) 

      # set output file path
      out_file_access = out_dir + '/access.csv'

      # run the coverage calculator
      cov_cal = PointingOptionsCoverage(spacecraft=sc, state_cart_file=state_cart_file)
      out_info = cov_cal.execute(instru_id="B", mode_id=None, out_file_access=out_file_access) # specify instrument "B"

      access.csv
      -----------
      POINTING OPTIONS COVERAGE
      Epoch [JDUT1] is 2458265.0
      Step size [s] is 2.0
      Mission Duration [Days] is 0.1
      time index,pnt-opt index,lat [deg],lon [deg]
      0,0,0.197,75.989
      0,1,-0.197,75.989
      1,0,0.197,76.108
      1,1,-0.197,76.108
      2,0,0.197,76.226

4. *POINTING OPTIONS WITH GRID COVERAGE example*
   
      In the below snippet, the satellite is equipped with two instruments with multiple modes. The second instrument with the pointing-options specifications is chosen for
      coverage calculations.  The ``filter_mid_acc`` flag is set to ``True`` to have only the access-times at the middle of access-intervals. The output csv file
      shows the grid-points accessed (if any) for each of the pointing-options at every time-step.
   
      .. code-block:: python

            from orbitpy.util import OrbitState, Spacecraft, SpacecraftBus
            from orbitpy.propagator import J2AnalyticalPropagator
            from orbitpy.coveragecalculator import PointingOptionsWithGridCoverage
            from orbitpy.grid import Grid
            from instrupy.base import Instrument
            import os
            
            out_dir = os.path.dirname(os.path.realpath(__file__))
            
            # initialize J2 analytical propagator with 2 secs propagation step-size
            j2_prop = J2AnalyticalPropagator.from_dict({"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':2} )
            
            # initialize orbit (initial state of the satellite)
            orbit = OrbitState.from_dict({"date":{"dateType":"GREGORIAN_UTC", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0},
                              "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6378+500, "ecc": 0.001, "inc": 0, "raan": 20, "aop": 0, "ta": 120}
                              })
            bus = SpacecraftBus.from_dict({"orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}}) # bus is aligned to the NADIR_POINTING frame.
            instru1= Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":10}, "@id": "A"}) 
            instru2 = Instrument.from_json({"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "circular", "diameter":20},
                                          "pointingOption":[{"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":10, "zRotation":0},
                                                            {"referenceFrame": "NADIR_POINTING", "convention": "XYZ", "xRotation":0, "yRotation":-10, "zRotation":0}],
                                          "@id": "B"}) 
            # spacecraft with 1 instrument
            sc = Spacecraft(orbitState=orbit, spacecraftBus=bus, instrument=[instru1, instru2])
            
            state_cart_file = os.path.dirname(os.path.realpath(__file__)) + '/cart_state.csv'
            
            # execute the propagator for duration of 0.1 days 
            j2_prop.execute(sc, None, state_cart_file, None, duration=0.1) 
            
            # make the Grid object
            grid = Grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":45, "latLower":-45, "lonUpper":180, "lonLower":-180, "gridRes": 1})
            
            # set output file path
            out_file_access = out_dir + '/access.csv'
            
            # run the coverage calculator
            cov_cal = PointingOptionsWithGridCoverage(grid=grid, spacecraft=sc, state_cart_file=state_cart_file)
            out_info = cov_cal.execute(instru_id="B", mode_id=None, out_file_access=out_file_access, filter_mid_acc=True)

            access.csv
            -----------
            POINTING OPTIONS WITH GRID COVERAGE
            Epoch [JDUT1] is 2458265.0
            Step size [s] is 2.0
            Mission Duration [Days] is 0.1
            time index,pnt-opt index,GP index,lat [deg],lon [deg]
            2,1,28958,-1.0,75.71
            3,0,28599,1.0,76.0
            6,1,28959,-1.0,76.71300000000001
            8,0,28600,1.0,77.0
            ...
   
   


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.coveragecalculator.CoverageCalculatorFactory
   orbitpy.coveragecalculator.GridCoverage
   orbitpy.coveragecalculator.PointingOptionsCoverage
   orbitpy.coveragecalculator.PointingOptionsWithGridCoverage

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.coveragecalculator.helper_extract_coverage_parameters_of_spacecraft
   orbitpy.coveragecalculator.find_in_cov_params_list
   orbitpy.coveragecalculator.filter_mid_interval_access