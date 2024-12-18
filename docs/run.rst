.. _run:

Run
=======

There are two ways to access the functionalities provided by the OrbitPy package.

.. _run_json_specs_file:

Execution with a JSON mission specifications file
**************************************************

The simplest way to access the functionalities of the OrbitPy package is by defining a JSON file (to be named as ``MissionSpecs.json``) 
with the mission specifications in a user-directory (accompanied with the necessary auxillary files such as grid-data).
The ``bin/run_mission.py`` script can be invoked with the argument as the user-directory. 
It performs the following functions:

1. Propagate all the satellites over the time-interval defined by the epoch and duration.
2. Calculate coverage for all the satellites in the mission.
3. Calculate data metrics corresponding to each possible observation (from coverage calculations). 
4. Calculate ground-station and inter-satellite contact intervals.
5. Calculate eclipse periods for each satellite.

The ``bin/run_mission.py`` script simply invokes the :class:`orbitpy.mission` module. Please refer to :ref:`mission_module` for description
of valid JSON key/value pairs which can be used in the mission specifications JSON file.

.. note:: In case of coverage calculations for the case of sensor FOVs described by spherical-polygon vertices (including Rectangular FOV) the default ``DirectSphericalPIP`` method is used.
    
*Example*

The following JSON snippet defines a spacecraft with an circular field-of-view instrument. Two rectangular grids are also defined 
as regions of interest. The orbit is propagated for a duration of 0.25 days from the epoch of 1/Jan/2021 12:00:00. Coverage is 
calculated over the two grids. Data metrics corresponding to the accesses over the grid-points is calculated. Information about 
the results (file locations, assigned unique identifiers, etc) is displayed.

.. code-block:: javascript
    
    MissionSpecs.json
    -----------------

    {   
        "epoch":{"@type":"GREGORIAN_UT1", "year":2021, "month":1, "day":12, "hour":12, "minute":0, "second":0},
        "duration": 0.25,
        "spacecraft": [{
            "@id": "sp1", "name": "Mars",
            "spacecraftBus":{"name": "BlueCanyon", "mass": 20, "volume": 0.5,
                            "orientation":{"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}
                            },
            "instrument": {"name": "Alpha", "mass":10, "volume":12.45, "dataRate": 40, "bitsPerPixel": 8, "power": 12,
                            "orientation": {"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"},
                            "fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter":5 },
                            "maneuver":{"maneuverType": "CIRCULAR", "diameter":10},
                            "@id":"bs1", "@type":"Basic Sensor"},
            "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":2, "day":25, "hour":6, "minute":0, "second":0},
                            "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6878.137, "ecc": 0.001, "inc": 45, "raan": 35, "aop": 145, "ta": -25}
                            } 
            }        
        ],
        "grid": [{"@type": "autogrid", "@id": 1, "latUpper":2, "latLower":0, "lonUpper":180, "lonLower":-180, "gridRes": 1}, 
                {"@type": "autogrid", "@id": 2, "latUpper":22, "latLower":20, "lonUpper":180, "lonLower":-180, "gridRes": 1}],
        "settings": {"coverageType": "GRID COVERAGE"}
    }

    >> python bin/run_mission.py examples/simple_mission1/

The example can be run using the following command from the main repo directory 

``python bin/run_mission.py examples/simple_mission1/``

The information about the output files (names, locations) generated by running the script is printed on console.

The files/folders expected upon the completion is given below.

.. code-block:: bash

        └───example1
                │   grid0.csv
                │   grid1.csv
                │   MissionSpecs.json
                │
                ├───comm
                └───sat0
                        access_instru0_mode0_grid0.csv
                        access_instru0_mode0_grid1.csv
                        datametrics_instru0_mode0_grid0.csv
                        datametrics_instru0_mode0_grid1.csv
                        eclipses.csv
                        state_cartesian.csv
                        state_keplerian.csv

*   ``grid0.csv`` and ``grid1.csv`` contain the grid-data (lat/lon coords of the grid-points) of the two regions.
*   ``sat0`` folder contains the files specific to the satellite.
*   ``state_cartesian.csv`` contains the satellite states in Cartesian coordinate system in the Earth Centered Inertial frame.
*   ``state_keplerian.csv`` contains the satellite Keplerian states in the Earth Centered Inertial frame.
*   ``access_instru0_mode0_grid0.csv`` and ``access_instru0_mode0_grid1`` contain the coverage data for each of the grids separately.
*   ``datametrics_instru0_mode0_grid0.csv`` and ``datametrics_instru0_mode0_grid1`` contain the datametrics data for each of the grids separately.

Execution by writing custom python script
********************************************

The OrbitPy modules can be imported in user python scripts and used to configure and execute a mission. This option offers the 
maximum flexibility. 

Most of the OrbitPy objects can be initialized via JSON strings or python dictionaries using the ``from_json(.)`` or ``from_dict(.)``
functions. They can also be converted back to python dictionaries using the ``to_dict(.)`` function. This offers a user-friendly way
in working with the objects. See example below of a grid object initialized using python dictionary:

.. code-block:: python

    grid1 = orbitpy.grid.from_dict({"@type": "autogrid", "@id": 1, "latUpper":20, "latLower":15, "lonUpper":80, "lonLower":45, "gridRes": 1})


Detailed documentation on all the OrbitPy modules can be found in :ref:`api_reference`. Another useful source of example usage of the OrbitPy modules 
is to see the test files of the corresponding modules in the ``/tests/`` directory. 


*Example*

The below snippet initializes a satellite, computes appropriate time-step for a custom time-resolution factor and propagates the 
orbit.

.. code-block:: python
        
        import os        
        import orbitpy.propagator
        from orbitpy.util import OrbitState, Spacecraft
        from orbitpy.propagator import PropagatorFactory
        from instrupy import Instrument

        orbit = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7031, "ecc": 0.001, "inc": 35, "raan": 0, "aop": 0, "ta": 20}})
        instru = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 15, "angleWidth": 5}}')
        sat = Spacecraft(orbitState=orbit, instrument=[instru])

        step_size = orbitpy.propagator.compute_time_step([sat], 0.5) #  compute time-step for a time resolution factor of 0.5
        duration = 1.5 # 1.5 days duration

        factory = PropagatorFactory()

        specs = {"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':step_size} 
        j2_prop = factory.get_propagator(specs)

        out_file_kep = os.path.dirname(os.path.realpath(__file__)) + '/states.csv'

        out_info = j2_prop.execute(sat, None, None, out_file_kep, duration)

        print(out_info) # print meta-data of the results

        >> PropagatorOutputInfo.from_dict({'@type': 'Propagator Output Info', 'propagatorType': 'J2 ANALYTICAL PROPAGATOR', 
                                           'spacecraftId': None, 'stateCartFile': None, 'stateKeplerianFile': 'C/workspace/states.csv', 
                                           'startDate': 2459270.75, 'duration': 1.5, '@id': None})