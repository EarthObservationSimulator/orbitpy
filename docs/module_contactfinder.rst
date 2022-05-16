``orbit.contactfinder`` --- Contact Finder Module
====================================================

Description
^^^^^^^^^^^^^
This module provides the class (``ContactFinder``) to compute line-of-sight (LOS) contact opportunities between two entities 
(satellite to ground-station or satellite to satellite). 

The :class:`instrupy.util.GeoUtilityFunctions.checkLOSavailability` function from the InstruPy package is called to determine if line-of-sight exists between two entities 
with the occluding body as Earth. The algorithm from Page 198, *Fundamental of Astrodynamics and Applications,* David A. Vallado is used (the first algorithm 
of the two described) to check for LOS.

In case of entity being a satellite, a data file with the satellite states at different times of the mission is required as input. At each of these times the LOS condition is evaluated
from the satellite to another entity (another satellite or ground-station). The format of the input data file of the satellite states is the same as the format of the output data file of the 
:class:`orbitpy.propagator` module (see :ref:`module_propagator`). The states must be of the type ``CARTESIAN_EARTH_CENTERED_INERTIAL``.

.. note:: The ``ContactFinder`` class is to be utilized by invoking the static-methods ``execute(.)`` and ``find_all_pairs(.)``, i.e. utilization of this
          class does **not** involve creation of a class instance.

.. warning:: In case of satellite-to-satellite contact finder the input time-series of the states of the two satellites must be in sync, i.e. the epoch, time-step and duration must be the same.

.. todo:: Include docs about find_all_pairs(.) function.

.. _contacts_file_format:

Output data file format
-------------------------
The results can be stored in a concise manner where the time-intervals at which the LOS exists are written and/or in a descriptive manner with 
information about range, elevation-angle (only in case of satellite to ground-station) at each time. Below is the description of the format of the 
output csv files. 

1. *INTERVAL Format*

   *  The first row indicates the entity identifiers of the entities between which the contacts were evaluated.
   *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
   *  The third row contains the time step-size in seconds. 

   The later lines contain the interval data in csv format with the following column headers:
     
   .. csv-table:: Contact file INTERVAL data format
            :header: Column, Data type, Units, Description
            :widths: 10,10,10,30

            start index, int, , Contact start time-index.
            stop index, int, , Contact stop time-index.

2. *DETAIL Format*

   *  The first row indicates the entity identifiers of the entities between which the contacts were evaluated.
   *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
   *  The third row contains the time step-size in seconds.

   The later lines contain the interval data in csv format with the following column headers:
   (The 'elevation [deg]' column appears only for the case of satellite-to-ground-station contact finder results.)

   .. csv-table:: Contact file DETAIL data format
            :header: Column, Data type, Units, Description
            :widths: 10,10,10,30

            time index, int, , Contact time-index.
            access, bool, , 'T' indicating True or F indicating False.
            range [km], float, kilometer, Distance between the two entities at the corresponding time.
            elevation [deg], float, degrees, Angle between the ground-plane and the ground-station to satellite line.

A ``ContactFinderOutputInfo`` object is also returned upon the execution of the contact finder (``ContactFinder.execute(.)``).
This object contains meta information about the results.

Examples
^^^^^^^^^

1. Satellite to satellite contacts

   ``spcA``, ``spcB`` satellites are defined and the orbits propagated to obtain the state information. The contact finder is executed by passing both the ``spcA`` and ``spcB`` objects,
   the path to the respective state files, a output filename (*spcA_to_spcB.csv*), path to the output directory, output format as ``INTERVAL`` and an opaque atmospheric height as 30km.
   The opaque atmospheric height (relevant only in case of satellite to satellite contact evaluation) adds to the Earth's radius and increases the occlusion area.

   .. code-block:: python

      import os   
      from orbitpy.util import Spacecraft
      from orbitpy.propagator import PropagatorFactory
      from orbitpy.contactfinder import ContactFinder
      
      out_dir = os.path.dirname(os.path.realpath(__file__))
      
      ''' Propagate satellites to obtain the state information.'''
      factory = PropagatorFactory()
      j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": 10})
      
      spcA = Spacecraft.from_dict({"name":"spcA", "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":1, "day":28, "hour":12, "minute":29, "second":2}, \
                                                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                    }})
      state_cart_file_spcA = out_dir + '/cart_states_spcA.csv'
      j2_prop.execute(spacecraft=spcA, out_file_cart=state_cart_file_spcA, duration=1)
      
      spcB = Spacecraft.from_dict({"name":"spcB", "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":1, "day":28, "hour":12, "minute":29, "second":2}, \
                                                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1816, "raan": 150, "aop": 84.837, "ta": 275.3} \
                                    }})
      state_cart_file_spcB = out_dir + '/cart_states_spcB.csv'
      j2_prop.execute(spacecraft=spcB, out_file_cart=state_cart_file_spcB, duration=1)
      
      """ Run the contact finder and store results in the directory specified by out_dir."""
      out_info = ContactFinder.execute(spcA, spcB, out_dir, state_cart_file_spcA, state_cart_file_spcB, "spcA_to_spcB.csv", ContactFinder.OutType.INTERVAL, 30)
      
      spcA_to_spcB.csv
      -----------------
      Contacts between Entity1 with id 83aca45e-9b13-4bc9-9a7a-cbf542aa6cca with Entity2 with id 6a0944c8-934c-410e-bfe2-0ec7d3c7000d
      Epoch [JDUT1] is 2459243.020162037
      Step size [s] is 10.0
      start index,end index
      99,197
      396,494
      692,790
      989,1087
      ...

2. Satellite to ground-station contacts
   
   ``spc`` satellite is defined and the orbit propagated to obtain the state information. The groundstation is defined by the ``gs`` object.
   The contact finder is executed by passing both the ``spc`` and ``gs`` objects, the path to the satellite state file, 
   path to the output directory and output format as ``DETAIL``. Since an output filename is not specified, the name *Euro_to_Atl.csv* is chosen
   where *Euro* is the name of satellite and *Atl* is name of ground-station.
   
   .. code-block:: python

      import os   
      from orbitpy.util import Spacecraft, GroundStation
      from orbitpy.propagator import PropagatorFactory
      from orbitpy.contactfinder import ContactFinder

      out_dir = os.path.dirname(os.path.realpath(__file__))

      ''' Propagate satellite to obtain the state information.'''
      factory = PropagatorFactory()
      j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": 10})

      spc = Spacecraft.from_dict({"name":"Euro", "orbitState": {"date":{"@type":"GREGORIAN_UT1", "year":2021, "month":1, "day":28, "hour":12, "minute":29, "second":2}, \
                                                      "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                 }})
      state_cart_file_spc = out_dir + '/cart_states_spc.csv'
      j2_prop.execute(spacecraft=spc, out_file_cart=state_cart_file_spc, duration=1)

      gs = GroundStation.from_dict({"@id":833, "name": "Atl", "latitude": -88, "longitude": 25, "minimumElevation":12 }) # by default the minimum elevation is 7 deg.

      """ Run the contact finder and store results in the directory specified by out_dir."""
      out_info = ContactFinder.execute(spc, gs, out_dir, state_cart_file_spc, None, None, ContactFinder.OutType.DETAIL, None)

      Euro_to_Atl.csv
      -----------------
      Contacts between Entity1 with id bd66e4c5-cb73-4c09-831a-5a75acd4300e with Entity2 with id 833
      Epoch [JDUT1] is 2459243.020162037
      Step size [s] is 10.0
      time index,access,range [km],elevation [deg]
      0,False,9448.07,
      1,False,9497.69,
      ...
      407,False,3090.93,
      408,False,3028.52,0.3
      409,False,2966.33,0.87
      410,False,2904.38,1.45
      ...


API
^^^^^

.. rubric:: Classes

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: classes_template.rst
   :recursive:

   orbitpy.contactfinder.ContactFinder
   orbitpy.contactfinder.ContactFinderOutputInfo

.. rubric:: Functions

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: functions_template.rst
   :recursive:

   orbitpy.contactfinder.ContactPairs