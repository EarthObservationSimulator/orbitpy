""" 
.. module:: util

:synopsis: *Collection of utility classes and functions used by the :code:`orbitpy` package. 
            Note that some utility classes/functions are imported from the :code:`instrupy` package.*

"""
import numpy as np
import uuid
from collections import namedtuple
import pandas as pd
from datetime import datetime

import requests
import json

from skyfield.api import EarthSatellite, load # Skyfield package is used to convert the TLEs to ECI coords at a specified epoch.

import propcov
from instrupy.util import Entity, EnumEntity, Constants, Orientation
from instrupy.base import Instrument

class OrbitPyDefaults(object):
    """ Enumeration of various default values used by package **OrbitPy**.
        NOT USED.
    """
    grid_res_fac = 0.9
    time_res_fac = 0.25

class StateType(EnumEntity):
    KEPLERIAN_EARTH_CENTERED_INERTIAL = "KEPLERIAN_EARTH_CENTERED_INERTIAL"
    CARTESIAN_EARTH_CENTERED_INERTIAL = "CARTESIAN_EARTH_CENTERED_INERTIAL"
    CARTESIAN_EARTH_FIXED = "CARTESIAN_EARTH_FIXED"

class DateType(EnumEntity):
    GREGORIAN_UT1 = "GREGORIAN_UT1"
    JULIAN_DATE_UT1 = "JULIAN_DATE_UT1"        

class OrbitState(Entity):
    """ Class to store and handle the orbit state (i.e. the date, position and velocity of satellite).
        The :class:`propcov.AbsoluteDate` and :class:`propcov.OrbitState` objects are used to maintain the 
        date and state respectively. Note that :class:`propcov.OrbitState` and :class:`orbitpy.util.OrbitState`
        classes are different. The class also provides several staticmethods to convert propcov-class representations 
        to/from inbuilt python datatypes.
        
        The class also supports initialization with TLE or OMM. It maintains a ``tle`` instance member.
        The ``tle`` instance member is valid only if the instantiation was done using a TLE.
        The class does *not* support obtaining a TLE if the instantiation was done using Cartesian or Keplerian elements.

    :ivar date: Date at which the orbit state is defined (epoch).
    :vartype date: :class:`propcov.AbsoluteDate`

    :ivar state: Satellite state (satellite position, velocity).
    :vartype state: :class:`propcov.OrbitState`

    :ivar tle: Orbit state (epoch, satellite position, velocity) in Two Line Element format. 
                Dictionary with the following keys:

                * tle_line0 : (str) TLE line 0 string. The first line contains the satellite name, and the next two lines are the two line elements.
                * tle_line1 : (str) TLE line 1 string. 
                * tle_line2 : (str) TLE line 2 string. 

    :vartype tle: dict

    :ivar _id: Unique identifier.
    :vartype _id: str
    
    """
    def __init__(self, date=None, state=None, tle=None, _id=None):

        self.date = date if date is not None and isinstance(date, propcov.AbsoluteDate) else None
        self.state = state if state is not None and isinstance(state, propcov.OrbitState) else None
        self.tle = tle if tle is not None and isinstance(tle, dict) and len(tle) == 3 and all(isinstance(key, str) for key in tle) else None
        super(OrbitState, self).__init__(_id, "OrbitState")   

    @staticmethod
    def from_dict(d): 
        """ Parses orbit state from a dictionary.

        :param d: Dictionary with the date and state description. Refer to the ``date_from_dict`` and ``state_from_dict`` and ``from_tle``
                  for description of the expected dictionary key/value pairs.
        
        :return: Parsed python object. 
        :rtype: :class:`orbitpy.util.OrbitState`

        """
        date = None
        state = None
        tle = None
        if d.get('tle') is not None:
            (date, state, tle) = OrbitState.from_tle(d.get("tle"))
        elif d.get('omm') is not None:
            (date, state, tle) = OrbitState.from_omm(d.get("omm"))
        else:
            date = OrbitState.date_from_dict(d.get("date", None))
            state = OrbitState.state_from_dict(d.get("state", None))

        return OrbitState(date=date, state=state, tle=tle, _id=d.get("@id", None))

    def to_dict(self, state_type=None):
        """ Translate the OrbitState object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.

        :param state_type: Indicate either "CARTESIAN_EARTH_CENTERED_INERTIAL" or "KEPLERIAN_EARTH_CENTERED_INERTIAL". Default is "CARTESIAN_EARTH_CENTERED_INERTIAL".
        :paramtype state_type: str

        :returns: ``OrbitState`` as a python dictionary.
        :rtype: dict

        """        
        return dict({"date": OrbitState.date_to_dict(self.date), 
                     "state": OrbitState.state_to_dict(self.state, state_type), 
                     "tle": OrbitState.tle_to_dict(self.tle),
                     "@id": self._id})
    
    def get_cartesian_earth_centered_inertial_state(self):
        """ Get Cartesian Earth Centered Inertial position, velocity.

        :returns: Satellite position, velocity as a list.
        :rtype: list, float

        """
        return self.state.GetCartesianState().GetRealArray()

    def get_keplerian_earth_centered_inertial_state(self):
        """ Get Keplerian Earth Centered Inertial position, velocity.

        :returns: The six orbit Keplerian elements.
        :rtype: namedtuple, (float)

        """        
        state = self.state.GetKeplerianState().GetRealArray()
        kep_state = namedtuple("KeplerianState", ["sma", "ecc", "inc", "raan", "aop", "ta"])
        return kep_state(state[0], state[1], state[2], state[3], state[4], state[5])

    def __eq__(self, other):
        """ Simple equality check. Returns True if the class attributes are equal, else returns False.
        """
        if(isinstance(self, other.__class__)):
            return (self.date == other.date and self.state == other.state and self.tle==other.tle)
        else:
            return NotImplemented

    def __repr__(self):
        return "OrbitState.from_dict({})".format(self.to_dict())

    @staticmethod
    def date_from_dict(d):
        """ Get the ``propcov.AbsoluteDate`` object from the input dictionary.

        :param d: Dictionary with the date description. 
            
            In case of ``GREGORIAN_UT1`` date type the following keys apply: year (int), month (int), day (int), hour (int), minute (int) and second (float).

            In case of ``JULIAN_DATE_UT1`` date type the following keys apply: jd (float)

        :paramtype d: dict

        :returns: ``propcov`` date object.
        :rtype: :class:`propcov.AbsoluteDate`

        """
        date = propcov.AbsoluteDate()
        if d is not None:            
            if(DateType.get(d["@type"]) == DateType.GREGORIAN_UT1):
                try:
                    date.SetGregorianDate(year=d["year"], month=d["month"], day=d["day"], hour=d["hour"], minute=d["minute"], second=d["second"])
                except:
                    raise Exception("Something wrong in setting of Gregorian UT1 date object. Check that the year, month, day, hour, second key/value pairs have been specified in the input dictionary.")
        
            elif(DateType.get(d["@type"]) == DateType.JULIAN_DATE_UT1):
                try:
                    date.SetJulianDate(jd=d["jd"])
                except:
                    raise Exception("Something wrong in setting of Julian UT1 date object. Check that the jd key/value pair has been specified in the input dictionary.")
            else:
                raise Exception("Please specify correct Date Type")
        else:
            raise Exception("Please specify a date.")
        
        return date

    @staticmethod
    def state_from_dict(d):
        """ Get the ``propcov.OrbitState`` object from the input dictionary.

        :param d: Dictionary with the date description. 
            
            In case of ``KEPLERIAN_EARTH_CENTERED_INERTIAL`` state type the following keys apply: 
            
            * sma : (float) Semimajor axis length in kilometers.
            * ecc : (float) Eccentricity.
            * inc : (float) Inclination in degrees.
            * raan: (float) Right Ascension of Ascending Node in degrees.
            * aop : (float) Argument of perigee in degrees.
            *  ta : (float) True Anomaly in degrees.

            In case of `CARTESIAN_EARTH_CENTERED_INERTIAL` state type the following keys apply: 
            
            * x  : (km) satellite x-position
            * y  : (km) satellite x-position
            * z  : (km) satellite x-position
            * vx : (km/s) satellite x-velocity
            * vy : (km/s) satellite y-velocity
            * vz : (km/s) satellite z-velocity

        :paramtype d: dict

        :returns: ``propcov`` state object.
        :rtype: :class:`propcov.OrbitState`

        """
        state = propcov.OrbitState()
        stateType = d.get('@type', None)
        state_type = StateType.get(stateType) if stateType is not None else None
        
        if state_type is not None:
            if state_type == StateType.KEPLERIAN_EARTH_CENTERED_INERTIAL:
                try: 
                    # angles must be converted to radians
                    state.SetKeplerianState(SMA=d["sma"], ECC=d["ecc"], INC=np.deg2rad(d["inc"]), RAAN=np.deg2rad(d["raan"]), AOP=np.deg2rad(d["aop"]), TA=np.deg2rad(d["ta"]))
                except:
                    raise Exception("Something wrong in setting of state object with Keplerian parameters. Check that the sma, ecc, inc, raan, aop and ta key/value pairs have been specified in the input dictionary.")                
            elif state_type == StateType.CARTESIAN_EARTH_CENTERED_INERTIAL:
                try:
                    state.SetCartesianState(propcov.Rvector6([d["x"], d["y"], d["z"], d["vx"], d["vy"], d["vz"]]))
                except:
                    raise Exception("Some wrong in setting of state object with Cartesian ECI parameters. Check that the x, y, z, vx, vy, vz key/value pairs are specified in the input dictionary.")
            else:
                raise NotImplementedError
        else:
            raise Exception("Please enter a state-type (@type) specification.")

        return state

    @staticmethod
    def from_tle(tle_dict):
        """ Get the ``propcov.AbsoluteDate`` and ``propcov.OrbitState`` objects from an input Two Line Element (TLE)

        :param tle_dict: Dictionary with the TLE.
            
            The following keys apply:

            * tle_line0 : (str) TLE line 0 string. The first line contains the satellite name, and the next two lines are the two line elements.
            * tle_line1 : (str) TLE line 1 string. 
            * tle_line2 : (str) TLE line 2 string. 

            e.g., 
                {
                    "tle_line0": "AQUA",
                    "tle_line1": "27424U 02022A   24052.86568623  .00001525  00000-0  33557-3 0  9991",
                    "tle_line2": "2 27424  98.3176   1.9284 0001998  92.8813 328.6214 14.58896689159754"
                }

        :paramtype tle_dict: dict

        :returns: ``propcov`` date object and state objects.
        :rtype: :class:`propcov.AbsoluteDate`, :class:`propcov.OrbitState`

        """
        date = propcov.AbsoluteDate()
        state = propcov.OrbitState()
        try:                 
            # Use Skyfield library
            ts = load.timescale()

            # Parse TLE string
            satellite = EarthSatellite(tle_dict["tle_line1"], tle_dict["tle_line2"], tle_dict["tle_line0"], ts)

            #print(satellite)
            
            # What is the time scale in the time indicated in the TLE?
            # "time is either in UTC or UT1, and conclude that the difference does not really matter because SGP4 just isn't accurate enough in predicting satellite positions for <1 second to matter."
            # Refer to the paper here: https://celestrak.org/publications/AIAA/2006-6753/
            # https://space.stackexchange.com/questions/13825/how-to-obtain-utc-of-the-epoch-time-in-a-satellite-tle-two-line-element
            tle_epoch = satellite.epoch
            tle_geocentric = satellite.at(tle_epoch) # Position is in GCRS (ECI) coordinates. GCRS ~ J2000, and is treated as the same in OrbitPy
                                                     # Following link documents that the position is in GCRS coordinates: https://rhodesmill.org/skyfield/earth-satellites.html

            pos = tle_geocentric.position.km
            vel = tle_geocentric.velocity.km_per_s

            #print(tle_epoch.ut1)
            #print(satellite.epoch.utc_jpl())
            #print(pos)
            #print(vel)
            
            date.SetJulianDate(jd=tle_epoch.ut1)
            state.SetCartesianState(propcov.Rvector6([pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]]))

        except:
            raise Exception("Error while setting the orbit state from TLE")
        
        return (date, state, tle_dict)
    
    @staticmethod
    def from_omm(omm_dict):
        """ Process orbital data from the Orbit Mean-Elements Message (OMM) format.
            Processing is carried out by extracting the TLEs from the OMM, and then using the ``from_tle()`` function.
        
            Space-Track.org and Celestrak.com recommend that developers migrate their software to use the OMM standard 
            (displayed in /class/gp/ as the /format/xml/) for all GP ephemerides because, again, legacy fixed-width TLE 
            or 3LE format lacks support for numbers above 99,999.

            :param omm_dict: Keplerian element set in Orbit Mean-Elements Message (OMM) that complies with CCSDS Recommended Standard 502.0-B-3.    
                             For an example run this query on a browser: https://www.space-track.org/basicspacedata/query/class/gp/norad_cat_id/25544/format/json
            :paramtype omm_dict: dict

            :returns: ``propcov`` date object and state objects.
            :rtype: :class:`propcov.AbsoluteDate`, :class:`propcov.OrbitState`

        """
        tle_dict = {
                    "tle_line0": omm_dict["TLE_LINE0"],
                    "tle_line1": omm_dict["TLE_LINE1"],
                    "tle_line2": omm_dict["TLE_LINE2"]
                }
        (date, state, tle) = OrbitState.from_tle(tle_dict)
        return (date, state, tle)

    def tle_to_dict(tle_dict):
       """ Get a Python dictionary representation of the input ``tle`` dict.

        :param tle: Orbit state (epoch, satellite position, velocity) in Two Line Element format. 
                Dictionary with the following keys:

                * tle_line0 : (str) TLE line 0 string. The first line contains the satellite name, and the next two lines are the two line elements.
                * tle_line1 : (str) TLE line 1 string. 
                * tle_line2 : (str) TLE line 2 string. 

        :paramtype tle: dict

        :returns: Python dictionary representation of the input tle. 
        :rtype: dict

       """
       return tle_dict 

    @staticmethod
    def date_to_dict(date):
        """ Get a Python dictionary representation of the input ``propcov`` date object. 

        :param date: ``propcov`` date object.
        :paramtype date: :class:`propcov.AbsoluteDate`

        :returns: Python dictionary representation of the input date. 
        :rtype: dict

        """
        return { "@type": "JULIAN_DATE_UT1", "jd": date.GetJulianDate()}

    @staticmethod
    def state_to_dict(state, state_type=None):
        """ Get a Python dictionary representation of the input ``propcov`` state object. Description shall be in 
            CARTESIAN_EARTH_CENTERED_INERTIAL or KEPLERIAN_EARTH_CENTERED_INERTIAL.

        :param date: ``propcov`` state object.
        :paramtype date: :class:`propcov.OrbitState`

        :param state_type: Indicate either "CARTESIAN_EARTH_CENTERED_INERTIAL" or "KEPLERIAN_EARTH_CENTERED_INERTIAL". Default is "CARTESIAN_EARTH_CENTERED_INERTIAL".
        :paramtype state_type: str

        :returns: Python dictionary representation of the input state. 
        :rtype: dict

        """
        state_type = StateType.get(state_type) if state_type is not None else StateType.CARTESIAN_EARTH_CENTERED_INERTIAL # default
        if state_type == StateType.CARTESIAN_EARTH_CENTERED_INERTIAL:
            state_list = state.GetCartesianState().GetRealArray()
            return {"@type": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": state_list[0], "y": state_list[1], "z": state_list[2], 
                    "vx": state_list[3], "vy": state_list[4], "vz": state_list[5]}
        elif state_type == StateType.KEPLERIAN_EARTH_CENTERED_INERTIAL:
            state_list = state.GetKeplerianState().GetRealArray()
            return {"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": state_list[0], "ecc": state_list[1], "inc": np.rad2deg(state_list[2]), 
                "raan": np.rad2deg(state_list[3]), "aop": np.rad2deg(state_list[4]), "ta": np.rad2deg(state_list[5])}        

    def get_julian_date(self):
        """ Get Julian Date UT1.

        :returns: Julian date UT1
        :rtype: float

        """
        return self.date.GetJulianDate()     

class SpacecraftBus(Entity):
    """ Class to store and handle the spacecraft bus attributes.

    :ivar name: Name of the bus.
    :vartype name: str

    :ivar mass: (kg) Mass of the bus.
    :vartype mass: float

    :ivar volume: (m3) Volume of the bus.
    :vartype volume: float
    
    :ivar orientation: Bus orientation. Can be specified with respect to any one of the reference frames defined in :class:`instrupy.util.ReferenceFrame`
    :vartype orientation: :class:`instrupy.util.Orientation`

    :ivar solar_panel_config: Solar panel configuration
    :vartype solar_panel_config: str #@TODO: revise

    :ivar _id: Unique identifier.
    :vartype _id: str
    
    """
    def __init__(self, name=None, mass=None, volume=None, orientation=None, solarPanelConfig=None, _id=None):

        self.name = str(name) if name is not None else None
        self.mass = float(mass) if mass is not None else None
        self.volume = float(volume) if volume is not None else None
        self.orientation = orientation if orientation is not None and isinstance(orientation, Orientation) else None
        self.solarPanelConfig = solarPanelConfig if solarPanelConfig is not None else None
        super(SpacecraftBus, self).__init__(_id, "SpacecraftBus")   

    @staticmethod
    def from_dict(d):
        """ Parses ``SpacecraftBus`` object from a dictionary.

        :param d: Dictionary with the spacecraft bus properties.
        
        :return: Parsed python object. 
        :rtype: :class:`orbitpy.util.SpacecraftBus`

        """
        default_orien = dict({"referenceFrame": "NADIR_POINTING", "convention": "REF_FRAME_ALIGNED"}) #  default orientation = referenced and aligned to the NADIR_POINTING frame.
        return SpacecraftBus(
                name = d.get("name", None),
                mass = d.get("mass", None),
                volume = d.get("volume", None),
                solarPanelConfig = d.get("solarPanelConfig", None),
                orientation = Orientation.from_json(d.get("orientation", default_orien)),
                _id = d.get("@id", None)
                )

    def to_dict(self, state_type=None):
        """ Translate the SpacecraftBus object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.

        :returns: SpacecraftBus specifications as python dictionary.
        :rtype: dict

        """        
        orientation_dict = self.orientation.to_dict() if self.orientation is not None and isinstance(self.orientation, Orientation) else None
        return dict({"name": self.name,
                     "mass": self.mass,
                     "volume": self.volume,
                     "solarPanelConfig": self.solarPanelConfig, 
                     "orientation": orientation_dict, 
                     "@id": self._id
                    })
    
    def __repr__(self):
        return "SpacecraftBus.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        """ Simple equality check. Returns True if the class attributes are equal, else returns False. 
            Note that _id data attribute may be different.
        """
        if(isinstance(self, other.__class__)):
            return (self.name == other.name and self.mass == other.mass and self.volume == other.volume \
                    and self.orientation==other.orientation and self.solarPanelConfig == other.solarPanelConfig)
        else:
            return NotImplemented

class Spacecraft(Entity):
    """ Class to store and handle the spacecraft attributes.

    :ivar name: Name of the spacecraft.
    :vartype name: str

    :ivar orbitState: Orbit specifications of the spacecraft (defined at a specific time).
    :vartype orbitState: :Class:`orbitpy.util.OrbitState`

    :ivar spacecraftBus: Spacecraft bus.
    :vartype spacecraftBus: :class:`orbitpy.util.SpacecraftBus`
    
    :ivar instrument: List of instrument(s) belonging to the spacecraft. 
    :vartype instrument: list, :class:`instrupy.Instrument`

    :ivar _id: Unique identifier.
    :vartype _id: str
    
    """
    def __init__(self, name=None, orbitState=None, spacecraftBus=None, instrument=None, _id=None):

        self.name = str(name) if name is not None else None
        self.orbitState = orbitState if orbitState is not None and isinstance(orbitState, OrbitState) else None
        self.spacecraftBus = spacecraftBus if spacecraftBus is not None and isinstance(spacecraftBus, SpacecraftBus) else None
        self.instrument = None
        if instrument is not None and isinstance(instrument, list):
            if all(isinstance(x, Instrument) for x in instrument):
                self.instrument = instrument
        elif(isinstance(instrument, Instrument)): # make into list if not list
            self.instrument = [instrument]
        super(Spacecraft, self).__init__(_id, "Spacecraft") 

    @staticmethod
    def from_dict(d):
        """ Parses ``Spacecraft`` object from a dictionary.

        :param d: Dictionary with the spacecraft properties.

            The following key/value pairs are expected:: 
                
                * "name" : (str) Name of the spacecraft.
                * "orbitState" : (dict) Spacecraft orbit-state specification (see :class:`orbitpy.util.OrbitState.from_dict`).
                * "spacecraftBus" : (dict) Spacecraft bus specification (see :class:`orbitpy.util.SpacecraftBus.from_dict`). 
                                     If missing or :class:`None`, a bus with the orientation in the ``NADIR_POINTING`` frame and convention ``REF_FRAME_ALIGNED`` is assigned. 
                * "instrument": (list, dict) Instrument(s) specification (see :class:`instrupy.base.Instrument.from_dict`).
                * "@id": (str/int) Spacecraft unique identifier. If missing, a random string is assigned.

        :paramtype d: dict
        
        :return: Parsed python object. 
        :rtype: :class:`orbitpy.util.Spacecraft`

        """
        instru_dict = d.get("instrument", None)
        instrument = None
        if instru_dict is not None:
            if isinstance(instru_dict, list): # multiple instruments in the spacecraft
                instrument = [Instrument.from_dict(x) for x in instru_dict]
            else:
                instrument = [Instrument.from_dict(instru_dict)]
        orbitstate_dict = d.get("orbitState", None)
        spacecraft_bus_dict = d.get("spacecraftBus", None)
        return Spacecraft(
                name = d.get("name", None),
                orbitState = OrbitState.from_dict(orbitstate_dict) if orbitstate_dict else None,
                spacecraftBus = SpacecraftBus.from_dict(spacecraft_bus_dict) if spacecraft_bus_dict else SpacecraftBus.from_dict({'orientation':{'referenceFrame': 'NADIR_POINTING', 'convention':'REF_FRAME_ALIGNED'}}),
                instrument = instrument,
                _id = d.get("@id", str(uuid.uuid4()))
                )

    def to_dict(self):
        """ Translate the Spacecraft object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.

        :returns: ``Spacecraft`` object as python dictionary.
        :rtype: dict

        """        
        orbitState_dict = self.orbitState.to_dict() if self.orbitState is not None and isinstance(self.orbitState, OrbitState) else None
        spacecraftBus_dict = self.spacecraftBus.to_dict() if self.spacecraftBus is not None and isinstance(self.spacecraftBus, SpacecraftBus) else None
        instrument_dict = None
        if self.instrument is not None:
            if isinstance(self.instrument, list): # multiple instruments in the spacecraft
                instrument_dict = [x.to_dict() for x in self.instrument]
            else:
                instrument_dict = [self.instrument.to_dict()]
        return dict({"name": self.name,
                     "orbitState": orbitState_dict,
                     "spacecraftBus": spacecraftBus_dict,
                     "instrument": instrument_dict, 
                     "@id": self._id
                    })

    def __repr__(self):
        return "Spacecraft.from_dict({})".format(self.to_dict())
    
    def add_instrument(self, new_instru):
        """ Add input instrument to the spacecraft's list of instruments.

            :param new_instru: New instrument(s) to be added to the spacecraft. 
            :paramtype new_instru: :class:`instrupy.base.Instrument` or list, :class:`instrupy.base.Instrument`
            
        """
        new_instru = initialize_object_list(new_instru, Instrument) # make into list if not already a list
        if isinstance(self.instrument, Instrument):
            self.instrument = [self.instrument] # make into list
        if isinstance(self.instrument, list):
            self.instrument.extend(new_instru) 
        else:
            self.instrument = new_instru 
    
    def get_id(self):
        """ Get spacecraft identifier.

        :returns: spacecraft identifier.
        :rtype: str or int

        """
        return self._id
    
    def get_instrument(self, sensor_id=None):
        """ Get ``Instrument`` object (from a list of instruments present in the ``Spacecraft`` object.) corresponding to the specified sensor id.

        :param sensor_id: Instrument identifier. If ``None``, the first instrument in the list of instruments is returned.
        :paramtype sensor_id: str or int

        :return: Instrument corresponding to the input sensor id. If not match not found, return ``None``.
        :rtype: :class:`instrupy.Instrument` or None

        """
        # check if spacecraft has no instruments and return None
        if self.instrument is None:
            return None
        # if sensor_id is not specified, return first instrument in the list
        if(sensor_id==None):
            return self.instrument[0]
        # search matching instrument id
        for x in self.instrument:
            if(x.get_id() == sensor_id):
                return x
        return None

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.name == other.name and self.orbitState == other.orbitState and self.spacecraftBus == other.spacecraftBus \
                    and self.instrument==other.instrument)                
        else:
            return NotImplemented    

class GroundStation(Entity):
    """ Class to store and handle the ground-station attributes.

    :ivar name: Name of the ground-station
    :vartype name: str

    :ivar latitude: [deg] Geocentric latitude coordinates of the ground-station.
    :vartype latitude: float

    :ivar longitude: [deg] Geocentric longitude coordinates of the ground-station.
    :vartype longitude: float
    
    :ivar altitude: [km] Altitude of the ground-station.
    :vartype altitude: float

    :ivar minimumElevation: [deg] Minmum required elevation (angle from ground-plane to satellite) for communication with satellite. 
    :vartype minimumElevation: float

    :ivar _id: Unique identifier.
    :vartype _id: str
    
    """
    def __init__(self, name=None, latitude=None, longitude=None, altitude=None, minimumElevation=None, _id=None):

        self.name = str(name) if name is not None else None
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.altitude = float(altitude) if altitude is not None else None
        self.minimumElevation = float(minimumElevation) if minimumElevation is not None else None

        super(GroundStation, self).__init__(_id, "GroundStation")   

    @staticmethod
    def from_dict(d):
        """ Parses ``GroundStation`` object from a dictionary.

        :param d: Dictionary with the ground-station properties. 

                The following key/value pairs are expected:

                * "name" : (str) Name of the ground-station.
                * "latitude": (float) geocentric latitude coordinates of the ground-station in degrees.
                * "longitude": (float) geocentric longitude coordinates of the ground-station in degrees.
                * "altitude": (float) ground-station altitude in kilometers. If not defined, value of 0km is assigned.
                * "minimumElevation": (float) Minimum required elevation (angle from ground-plane to satellite in degrees) for communication with satellite. If not defined, value of 7 deg is assigned.
                * "@id": (str/int) Unique ground-station identifier. If not defined, a random string is assigned.

        
        :return: Parsed python object. 
        :rtype: :class:`orbitpy.util.GroundStation`

        """
        return GroundStation(
                name = d.get("name", None),
                latitude = d.get("latitude", None),
                longitude = d.get("longitude", None),
                altitude = d.get("altitude", 0), # Altitude default value is 0km
                minimumElevation = d.get("minimumElevation", 7), # 7 deg minimum elevation default
                _id = d.get("@id", str(uuid.uuid4())) # random default id
                )

    def to_dict(self):
        """ Translate the ``GroundStation`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.

        :returns: ``GroundStation`` object as python dictionary.
        :rtype: dict

        """        
        return dict({"name": self.name,
                     "latitude": self.latitude,
                     "longitude": self.longitude,
                     "altitude": self.altitude, 
                     "minimumElevation": self.minimumElevation, 
                     "@id": self._id
                    })
    
    def __repr__(self):
        return "GroundStation.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        """ Simple equality check. Returns True if the class attributes are equal, else returns False. 
            Note that _id data attribute may be different.
        """
        if(isinstance(self, other.__class__)):
            return (self.name == other.name and self.latitude == other.latitude and self.longitude == other.longitude \
                    and self.altitude==other.altitude and self.minimumElevation == other.minimumElevation)
        else:
            return NotImplemented
    
    def get_coords(self):
        """ Get coordinates of the ground-station.

        :return: Ground-station position (latitude in degrees, longitude in degrees, altitude in kilometers)
        :rtype: tuple, (float, float, float)
        
        """
        return (self.latitude, self.longitude, self.altitude)


def helper_extract_spacecraft_params(spacecraft):
    """ Helper function for the time step and grid resolution computation which returns tuples 
        of spacecraft id, instrument id, mode id, semi-major axis, sensor FOV height, FOV width, sceneFOV height, sceneFOV width, FOR height and FOR width. 
        The height and width of the sensor FOV/sceneFOV/FOR correspond to the along-track and cross-track directions when the sensor
        is aligned to the NADIR_POINTING_FRAME.

    :param spacecraft: List of spacecrafts in the mission.
    :paramtype spacecraft: list, :class:`orbitpy:util.Spacecraft`

    :return: Tuples with spacecraft id, instrument id, mode id, semi-major axis, sensor FOV height, FOV width, sceneFOV height, sceneFOV width, FOR height and FOR width.
             of all input spacecrafts. None is returned if no spacecrafts are specified.
    :rtype: list, namedtuple, <str/int, str/int, str/int, float, float, float, float, float, float, float> or None

    """
    _p = namedtuple("sc_params", ["sc_id", "instru_id", "mode_id", "sma", "fov_height", "fov_width", "scfov_height", "scfov_width", "for_height", "for_width"])
    params = []

    if spacecraft:
        if not isinstance(spacecraft, list): 
            spacecraft = [spacecraft] # make into list
    else:
        return None

    for sc in spacecraft: # iterate over all satellites
        sc_id = sc.get_id()
        sma = sc.orbitState.get_keplerian_earth_centered_inertial_state().sma  

        if sc.instrument is not None:
            for instru in sc.instrument: # iterate over each instrument
                instru_id = instru.get_id()
                mode_id = instru.get_mode_id()

                for mode_id in instru.get_mode_id():# iterate over each mode in the instrument

                    field_of_view  = instru.get_field_of_view(mode_id)
                    [fov_height, fov_width] = field_of_view.sph_geom.get_fov_height_and_width()

                    scene_field_of_view  = instru.get_scene_field_of_view(mode_id)
                    [scfov_height, scfov_width] = scene_field_of_view.sph_geom.get_fov_height_and_width()

                    field_of_regard  = instru.get_field_of_regard(mode_id) 

                    if field_of_regard is None or []: # if FOR is None, use sceneFOV for FOR
                        field_of_regard = [instru.get_scene_field_of_view(mode_id)]
                    
                    for x in field_of_regard: # iterate over the field_of_regard list
                        [for_height, for_width] = x.sph_geom.get_fov_height_and_width()

                        params.append(_p(sc_id, instru_id, mode_id, sma, fov_height, fov_width, scfov_height, scfov_width, for_height, for_width))
        else:
            params.append(_p(sc_id, None, None, sma, None, None, None, None, None, None))
    return params

def extract_auxillary_info_from_state_file(state_file):
    """ Extract auxillary information (epoch, step-size, duration) from the propagated states file.

    :param state_file: 
    :paramtype state_file: str

    :return: Tuple of Epoch in Julian Date UT1, propagation step-size in seconds and propagation duration in days.
    :rtype: nametuple, (float, float, float)

    """
    epoch_JDUT1 = pd.read_csv(state_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
    epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])

    step_size = pd.read_csv(state_file, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
    step_size = float(step_size[0][0].split()[4])

    duration = pd.read_csv(state_file, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
    duration = float(duration[0][0].split()[4])

    state_aux_info = namedtuple("state_aux_info", ["epoch_JDUT1", "step_size", "duration"])
    
    return state_aux_info(epoch_JDUT1, step_size, duration)

def dictionary_list_to_object_list(d, cls):
    """ Utility function to convert list of dictionaries to list of corresponding objects. 
        The objects must have the function ``from_dict(.)`` associated with it.
    
    :param d: List of dictionaries.
    :paramtype d: list, dict

    :param cls: Class to which each dictionary is to be converted into.
    :paramtype cls: cls

    :return: List of objects.
    :rtype: list, cls

    """
    obj_list = None
    if d is not None:
        if isinstance(d, list):
            obj_list = [cls.from_dict(x) for x in d]
        else:
            obj_list = [cls.from_dict(d)] 
    return obj_list

def object_list_to_dictionary_list(obj_list):
    """ Utility function to convert list of objects to list of dictionaries. 
        The objects must have the function ``to_dict(.)`` associated with it.
    
        :param obj_list: List of objects.
        :paramtype obj_list: list, cls or cls

        :return: List of dictionaries.
        :rtype: list, dict

    """
    dict_list = None
    if obj_list is not None:
        if isinstance(obj_list, list):
            dict_list = [x.to_dict() for x in obj_list]
        else:
            dict_list = [obj_list.to_dict()] 
    return dict_list

def initialize_object_list(inp, cls):
    """ Utility function to return list of objects from a valid input (a single object or list of objects where each object is of the class ``cls``).
        If invalid input ``None`` is returned. 
    
    :param inp: Input.
    :paramtype inp: (list, cls) or cls

    :param cls: Class of each element of the list.
    :paramtype cls: cls

    :return: List of objects if valid input else None.
    :rtype: list, cls or None

    """
    obj_list = None
    if inp is not None and isinstance(inp, list):
        if all(isinstance(x, cls) for x in inp):
            obj_list = inp
    if inp is not None and isinstance(inp, cls): # make into list if not list
        obj_list = [inp]
    return obj_list

def add_to_list(existing_list, inp_list):
    """ Add input list to an existing list. The existing "list" and input "list" are checked to see if they are list instances, 
        and if not configured to be a lists. The existing list is extended with the input list.

        :param existing_list: Existing list, which needs to be extended. Can be made of heterogenous objects.
        :paramtype existing_list: list

        :param inp_list: Input list. Can be made of heterogenous objects.
        :paramtype inp_list: list

        :return: Extended list.
        :rtype: list

    """
    if inp_list is not None:
        if not isinstance(inp_list, list):
            inp_list = [inp_list] # make to list

    if existing_list is not None:
        if not isinstance(existing_list, list):
            existing_list = [existing_list] # make to list
        existing_list.extend(inp_list)
    else:
        existing_list = inp_list
    
    return existing_list

def calculate_inclination_circular_SSO(altitude_km):
    """ Calculate the inclination of a circular (ecc=0) orbit with the input altitude.

        :param altitude_km: Altitude of the orbit in kilometers.
        :paramtype altitude_km: float

    """
    # circular SSO with fixed altitude specified, 
    e = 0
    Re = Constants.radiusOfEarthInKM 
    sma = Re + altitude_km
    J2  = 0.0010826269      # Second zonal gravity harmonic of the Earth
    we = 1.99106e-7    # Mean motion of the Earth in its orbit around the Sun [rad/s]
    mu    = 398600.440      # Earth’s gravitational parameter [km^3/s^2]
    n = np.sqrt(mu/(sma**3)) # Mean motion [s-1]
    h = sma*(1 - e**2)    # note that here h is *NOT* the altitude!!

    tol = 1e-10         # Error tolerance
    # Initial guess for the orbital inclination
    i0 = 180/np.pi*np.arccos(-2/3*(h/Re )**2*we/(n*J2))
    err = 1e1
    while(err >= tol):
        # J2 perturbed mean motion
        _np  = n*(1 + (1.5*J2*(Re/h))**2*np.sqrt(1 - e**2)*(1 - (3/2*np.sin(np.deg2rad(i0))**2)))
        i = 180/np.pi*(np.arccos(-2/3*((h/Re)**2)*we/(_np*J2)))
        err = abs(i - i0)
        i0 = i
    return i

class OutputInfoUtility:
    """ Class with utility classes, functions to handle the output-info objects, i.e. objects of the classes:
        
        * :class:`orbitpy.propagator.PropagatorOutputInfo` 
        * :class:`orbitpy.contactfinder.ContactFinderOutputInfo` 
        * :class:`orbitpy.coveragecalculator.CoverageOutputInfo` 
        * :class:`orbitpy.datametricscalculator.DataMetricsOutputInfo` 
        * :class:`orbitpy.eclipsefinder.EclipseFinderOutputInfo` 
        * :class:`orbitpy.grid.GridOutputInfo`
    
    """

    class OutputInfoType(EnumEntity):
        """ Types of output-info objects.
        """
        PropagatorOutputInfo = "PROPAGATOR OUTPUT INFO"
        ContactFinderOutputInfo = "CONTACT FINDER OUTPUT INFO"
        CoverageOutputInfo = "COVERAGE OUTPUT INFO"
        DataMetricsOutputInfo = "DATAMETRICS OUTPUT INFO"
        EclipseFinderOutputInfo = "ECLIPSE FINDER OUTPUT INFO"
        GridOutputInfo = "GRID OUTPUT INFO"

    @staticmethod
    def locate_output_info_object_in_list(out_info_list, out_info_type, **kwargs):
        """ Locate an output-info object from list of output-info objects with parameters
            as that given by the input arguments.

            :param out_info_list: List of output-info objects.
            :paramtype: list, output-info objects
            
            :param out_info_type: The *type* of the output-info object.
            :paramtype out_info_type: :class:`orbitpy.util.OutputInfoUtility.OutputInfoType`

            :param \**kwargs: Keyword arguments. Depending on the output-info type of interest, there are different keywords expected.
                            
                                .. csv-table::
                                    :header: Output-info type, Keyword(s), Description
                                    :widths: 10,10,10

                                    ``PropagatorOutputInfo``, ``spacecraft_id``, Spacecraft-identifier of the propagated spacecraft.
                                    ``CoverageOutputInfo``, "``inp_cov_type``, ``spacecraft_id``, ``inp_instru_id``, ``inp_mode_id``, ``inp_grid_id``", "Coverage-type and identifiers of spacecraft, instrument, mode, grid."

            
            :return: The output-info object with parameters matched to the input arguments.
            :rtype: output-info object

        """
        if not out_info_list: # if None or []
            return None

        if not isinstance(out_info_list, list):
            out_info_list = [out_info_list] # make into list
        
        result = None
        # If the object to-be-found is of type 'PROPAGATOR OUTPUT INFO'        
        if out_info_type == OutputInfoUtility.OutputInfoType.PropagatorOutputInfo.value:
            inp_spc_id = kwargs.get('spacecraft_id') # spacecraft-id of interest
            for oi in out_info_list:
                if oi._type == OutputInfoUtility.OutputInfoType.PropagatorOutputInfo.value: # check object type
                    if oi.spacecraftId == inp_spc_id: # check for matching spacecraft-id
                        result = oi
                        break
        
        # If the object to-be-found is of type 'COVERAGE OUTPUT INFO'        
        if out_info_type == OutputInfoUtility.OutputInfoType.CoverageOutputInfo.value:
            inp_cov_type = kwargs.get('coverage_type') # coverage-type of interest
            inp_spc_id = kwargs.get('spacecraft_id') # spacecraft-id of interest
            inp_instru_id = kwargs.get('instru_id') # instrument-id of interest
            inp_mode_id = kwargs.get('mode_id') # instrument mode-id of interest
            inp_grid_id = kwargs.get('grid_id') # grid-id of interest
            
            for oi in out_info_list:
                if oi._type == OutputInfoUtility.OutputInfoType.CoverageOutputInfo.value: # check object type
                    if ((oi.coverageType==inp_cov_type) and (oi.spacecraftId==inp_spc_id) and (oi.instruId==inp_instru_id) and (oi.modeId==inp_mode_id) and (oi.gridId==inp_grid_id)):
                        result = oi
                        break

        return result

    @staticmethod
    def delete_output_info_object_in_list(out_info_list, other_out_info_object):
        """ Remove an output-info object from list of output-info objects which has "loose"-equality with the other
            output-info object. Loose equality requires only some of the instance variables of the two objects to match. 
            Please see the ``check_loose_equality`` function of the respective output-info class to know which instance variables care compared.

            :param out_info_list: List of output-info objects.
            :paramtype: list, output-info objects

            :param other_out_info_object: Output-info object(s) with which comparison for loose-equality shall be made. Can be a list.
            :paramtype other_out_info_object: output-info object or list, output-info object
            
            :return: (Potentially) reduced list of output-info objects with an deleted object. 
            :rtype: list, output-info objects

        """
        if not out_info_list: # if None or []
            return None

        if not isinstance(out_info_list, list):
            out_info_list = [out_info_list] # make into list

        if other_out_info_object is None:
            return out_info_list

        if not isinstance(other_out_info_object, list):
            other_out_info_object = [other_out_info_object]  # make into list

        for ooi in other_out_info_object:
            for indx, oi in enumerate(out_info_list):
                if oi.check_loose_equality(ooi):
                    del out_info_list[indx] # delete the corresponding output-info object
        
        return out_info_list
    
class SpaceTrackAPI:
    """ Class which enables interface to SpaceTrack.org and the retreival of the most recent 
    available satellite orbit data close to a given target date. Note that the data is available
    at a latency from the time of measurement of the satellite state.

    Initialize SpaceTrackAPI instance with credentials from a JSON file in the following format: 
    {
        "username": "xxxx",
        "password":  "xxxx"
    }
    """
    def __init__(self, credentials_file):
        with open(credentials_file, 'r') as file:
            credentials = json.load(file)
        self.username = credentials.get('username')
        self.password = credentials.get('password')
        self.session = None

    def login(self):
        # URL for the login page
        login_url = "https://www.space-track.org/ajaxauth/login"

        # Payload data for the login request
        payload = {
            "identity": self.username,
            "password": self.password,
        }

        # Create a session to persist cookies across requests
        self.session = requests.Session()

        # Send a POST request to the login URL with the payload data
        response = self.session.post(login_url, data=payload)

        # Check if the login was successful (status code 200)
        if response.status_code == 200:
            print("Login successful")
        else:
            print("Login failed")

    def get_closest_omm(self, norad_id, target_date_time):
        if not self.session:
            print("Session not initialized. Please login first.")
            return

        # Validate that target_date_time is a string in the format %Y-%m-%dT%H:%M:%S
        try:
            tdt_datetime = datetime.strptime(target_date_time, "%Y-%m-%dT%H:%M:%S") # datetime object
            tdt = tdt_datetime.strftime("%Y-%m-%dT%H:%M:%S") #ensure the format is correct
        except ValueError:
            print("Invalid target_date_time format. It should be a string in the format '%Y-%m-%dT%H:%M:%S'. E.g., 2024-04-09T01:00:00")
            return
        
        # URL to retrieve the closest available OMM (see the CREATION_DATE and not the EPOCH_DATE) for the specified satellite before and closest to the target datetime
        omm_url = f"https://www.space-track.org/basicspacedata/query/class/omm/NORAD_CAT_ID/{norad_id}/CREATION_DATE/<{tdt}/orderby/EPOCH%20desc/limit/1/format/json"
        
        # Send a GET request to retrieve the closest OMM data
        response = self.session.get(omm_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            closest_omm = response.json()
            if closest_omm:
                #print(f"Closest *available* OMM data for satellite with NORAD ID {norad_id} *at* {tdt}:")
                #print(json.dumps(closest_omm, indent=4))
                result_omm = closest_omm[0]
                retrieved_CD = result_omm['CREATION_DATE']
                retrieved_CD_datetime = datetime.strptime(retrieved_CD, "%Y-%m-%dT%H:%M:%S") # convert to datetime object
                # Make sure that the retrieved CREATION_DATE is before the target date-time
                if retrieved_CD_datetime > tdt_datetime:
                    raise ValueError(f"The retrieved OMM CREATION_DATE {retrieved_CD} is after the target date-time {tdt}. Something wrong.")
                # Check if the retrieved CREATION_DATE is more than 1 day before the target date-time
                if (tdt_datetime - retrieved_CD_datetime).days > 1:
                    raise ValueError(f"The retrieved OMM CREATION_DATE {retrieved_CD} is not within 1 day before the target date-time {tdt}. Something wrong.")

                #print(f"Closest *available* OMM data for satellite with NORAD ID {norad_id} *at* {tdt} (CREATION_DATE: {retrieved_CD}):")
                return closest_omm[0] # dictionary in a list is returned
            else:
                print(f"No OMM found for satellite with NORAD ID {norad_id}. It is possible the satellite has been launched after the specified target date-time.")
        else:
            print(f"Failed to retrieve OMM data for satellite with NORAD ID {norad_id}")

    def logout(self):
        if not self.session:
            print("Session not initialized.")
            return

        # Clear session cookies
        self.session.cookies.clear()
        print("Logged out successfully")