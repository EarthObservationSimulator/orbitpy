``orbit.eclipsefinder`` --- Eclipse Finder Module
===================================================

Description
^^^^^^^^^^^^^
This module provides the class (``EclipseFinder``) to compute eclipses time-intervals of a satellite (i.e. the times at which the satellite does not have 
a line-of-sight to the Sun).

The :class:`instrupy.util.GeoUtilityFunctions.SunVector_ECIeq` function from the InstruPy package is called to determine the Sun position in the
Earth Centered Inertial frame (equatorial plane) based on the algorithm in [1].
The :class:`instrupy.util.GeoUtilityFunctions.checkLOSavailability` function from the InstruPy package is called to determine if line-of-sight exists between the
satellite and the Sun with the occluding body as Earth based on the algorithm in [2].

A data file with the satellite states at different times of the mission is required as input. At each of these times the LOS condition is evaluated
from the satellite to the Sun. The format of the input data file of the satellite states is the same as the format of the output data file of the 
:class:`orbitpy.propagator` module (see :ref:`module_propagator`). The states must be of the type ``CARTESIAN_EARTH_CENTERED_INERTIAL``.

.. note:: The ``EclipseFinder`` class is to be utilized by invoking the static-methods ``execute(.)``, i.e. utilization of this
          class does **not** involve creation of a class instance.

References
------------
1. David A.Vallado, *Fundamental of Astrodynamics and Applications,* 4th ed, Page 280.
2. David A. Vallado, *Fundamental of Astrodynamics and Applications,* 4th ed, Page 198, (the first algorithm 
   of the two described).

Output data file format
-------------------------
The results can be stored in a concise manner where the time-intervals at which the eclipse exists are written and/or in a descriptive manner where
the presence of eclipse at each time tick is indicated as either True or False. Below is the description of the format of the 
output csv files. 

1. *INTERVAL*: 

    *  The first row indicates the spacecraft identifier for which the eclipses were evaluated.
    *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
    *  The third row contains the time step-size in seconds. 

    The later lines contain the interval data in csv format with the following column headers:
    
    .. csv-table:: Eclipse file INTERVAL data format
            :header: Column, Data type, Units, Description
            :widths: 10,10,10,30

            start index, int, , Eclipse start time-index.
            stop index, int, , Eclipse stop time-index.

2. *DETAIL*: 

    *  The first row indicates the spacecraft identifier for which the eclipses were evaluated.
    *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
    *  The third row contains the time step-size in seconds.

    The later lines contain the interval data in csv format with the following column headers:

    .. csv-table:: Eclipse file DETAIL data format
            :header: Column, Data type, Units, Description
            :widths: 10,10,10,30

            time index, int, , Time-index.
            eclipse, bool, , 'T' indicating True or F indicating False.

A ``EclipseFinderOutputInfo`` object is also returned upon the execution of the eclipse finder (``EclipseFinder.execute(.)``).
This object contains meta information about the results.

Example
^^^^^^^^^
   
   ``spc`` satellite is defined and the orbit propagated to obtain the state information.
   The eclipse finder is executed by passing the ``spc`` object, the path to the satellite state file, 
   path to the output directory and output format as ``INTERVAL``. Since an output filename is not specified, the name *eclipse.csv* is chosen.

   .. code-block:: python

      import os   
      from orbitpy.util import Spacecraft, GroundStation
      from orbitpy.propagator import PropagatorFactory
      from orbitpy.eclipsefinder import EclipseFinder

      out_dir = os.path.dirname(os.path.realpath(__file__))

      ''' Propagate satellite to obtain the state information.'''
      factory = PropagatorFactory()
      j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": 10})

      spc = Spacecraft.from_dict({"orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":1, "day":28, "hour":12, "minute":29, "second":2}, \
                                  "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 35, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                 }})
      state_cart_file_spc = out_dir + '/cart_states_spc.csv'
      j2_prop.execute(spacecraft=spc, out_file_cart=state_cart_file_spc, duration=1)

      """ Run the eclipse finder and store results in the directory specified by out_dir."""
      out_info = EclipseFinder.execute(spacecraft=spc, out_dir=out_dir, state_cart_fl=state_cart_file_spc, out_filename=None, out_type=ContactFinder.OutType.INTERVAL)

      Eclipse.csv
      -----------------
      Eclipse times for Spacecraft with id 80fe4d2e-2ff0-486d-b00e-3d74ffce0b2e
      Epoch [JDUT1] is 2459243.020162037
      Step size [s] is 10.0
      start index,end index
      49,257
      641,848
      1232,1440
      1824,2031
      2415,2623
      ...


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.eclipsefinder.EclipseFinder
   orbitpy.eclipsefinder.EclipseFinderOutputInfo
