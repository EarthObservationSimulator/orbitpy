""" 
.. module:: constellation

:synopsis: *Collection of different types satellite constellation classes to be used for handling
            storage of the respective constellation model parameters and generation of orbits of the
            satellites in the constellation.* 

"""

import uuid

import propcov
from .util import OrbitState
from instrupy.util import Entity, Constants

class ConstellationFactory:
    """ Factory class which allows to register and invoke the appropriate constellation-model class. 
    See https://realpython.com/factory-method-python/#supporting-additional-formats
    
    :class:`WalkerDeltaConstellation` and :class:`TrainConstellation` constellation-model classes are registered 
    in the factory. Additional user-defined constellation-model classes can be registered as shown below: 

    Usage: 
    
    Initializing in-built constellation object.

    .. code-block:: python
    
        factory = ConstellationFactory()
        specs = {"@type": 'Walker Delta Constellation', "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}, "numberSatellites": 2, "numberPlanes": 1,
                            "relativeSpacing": 1, "alt": 500, "ecc": 0.001, "inc": 45, "aop": 135, "@id": "abc"}
        wd_model = factory.get_constellation_model(specs)
    
    Registering and initializing a custom constellation object.

    .. code-block:: python

        class NewConstellation2021():
            def __init__(self, alt):
               self.alt = alt
               
            @staticmethod
            def from_dict(d):
               return NewConstellation2021(alt = d.get('alt', 0))
            
            def __eq__(self, other):
               if(isinstance(self, other.__class__)):
                     return (self.alt==other.alt)
               else:
                     return NotImplemented 
            
            def generate_orbits(self):

               orbits = []
               date = propcov.AbsoluteDate()
               state_dict = {"stateType":"KEPLERIAN_EARTH_CENTERED_INERTIAL",  "sma": 6378 + self.alt, "ecc": 0, "inc": 0, "raan": 0, "aop": 0, "ta": 0}
               state = OrbitState.state_from_dict(state_dict)
               orbits.append(OrbitState(date, state, 0))

               return orbits

        factory = ConstellationFactory()
        factory.register_constellation_model('New Constellation 2021', NewConstellation2021) # register user defined constellation
        specs = {'@type': 'New Constellation 2021', 'alt': 700}
        const1 = factory.get_constellation_model(specs) # initialization of the constellation object const1

    :ivar _creators: Dictionary mapping constellation type label to the appropriate constellation class. 
    :vartype _creators: dict

    """
    def __init__(self):
        self._creators = {}
        self.register_constellation_model('Walker Delta Constellation', WalkerDeltaConstellation)
        self.register_constellation_model('Train Constellation', TrainConstellation)

    def register_constellation_model(self, _type, creator):
        """ Function to register constellations.

        :var _type: Constellation type (label).
        :vartype _type: str

        :var creator: Constellation class.
        :vartype creator: Constellation class.

        """
        self._creators[_type] = creator

    def get_constellation_model(self, specs):
        """ Function to get the appropriate constellation-model instance.

        :var specs: Constellation-model specifications which also contains a valid constellation
                    type in the "@type" dict key. The constellation type is valid if it has been
                    registered with the ``ConstellationFactory`` instance.
        :vartype _type: dict

        :return: The appropriate constellation object initialized to the input specifications.
        :rtype: :class:`orbitpy.constellation.WalkerDeltaConstellation` or :class:`orbitpy.constellation.TrainConstellation` or custom constellation class.
        
        """
        _type = specs.get("@type", None)
        if _type is None:
            raise KeyError('Constellation type key/value pair not found in specifications dictionary.')

        creator = self._creators.get(_type)
        if not creator:
            raise ValueError(_type)
        return creator.from_dict(specs)

class WalkerDeltaConstellation(Entity):
    """A Walker-Delta constellation class.

    The instance variables completely characterize the constellation. Refer to Space Mission Analysis and Design, 3rd ed, Section 7.6, Pg 194, 195.
      
    :ivar date: Date at which the constellation parameters are defined (Julian Date UT1).
    :vartype date: :class:`propcov.AbsoluteDate`

    :ivar numberSatellites: Number of satellites in the constellation.
    :vartype numberSatellites: int

    :ivar numberPlanes: Number of orbital planes.
    :vartype numberPlanes: int

    :ivar relativeSpacing: Factor controlling the spacing between the satellites in different planes.
    :vartype relativeSpacing: int

    :ivar alt: Altitude in kilometers.
    :vartype alt: float

    :ivar ecc: Orbit eccentricity.
    :vartype ecc: float

    :ivar inc: Orbit inclination in degrees.
    :vartype inc: float

    :ivar aop: Orbit argument of perigee in degrees.
    :vartype aop: float

    :ivar _id: Unique constellation identifier.
    :vartype _id: str

    Usage:

    1. 
        .. code-block:: python

                factory = ConstellationFactory()
                specs = {"@type": 'Walker Delta Constellation', "date":{"dateType": "JULIAN_DATE_UT1", "jd":2459270.75}, "numberSatellites": 2, "numberPlanes": 1,
                        "relativeSpacing": 1, "alt": 500, "ecc": 0.001, "inc": 45, "aop": 135, "@id": "abc"}
                wd_model = factory.get_constellation_model(specs) # initialization
                print(wd_model.generate_orbits())

                >> [OrbitState.from_dict({'date': {'dateType': 'JULIAN_DATE_UT1', 'jd': 2451545.0}, 'state': {'stateType': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 7078.0, 'y': 0.0, 'z': 0.0, 'vx': -0.0, 'vy': 7.504359112788965, 'vz': 0.0}, '@id': 0})]     

    2.
        .. code-block:: python

                date =  OrbitState.date_from_dict({"dateType": "JULIAN_DATE_UT1", "jd":2459270.75})
                wd_model = WalkerDeltaConstellation( date=date, numberSatellites=2, numberPlanes=1, relativeSpacing=1, alt=500, ecc=0.001, inc=45, aop=135, _id="abc")
                print(wd_model.generate_orbits())

                >> [OrbitState.from_dict({'date': {'dateType': 'JULIAN_DATE_UT1', 'jd': 2451545.0}, 'state': {'stateType': 'CARTESIAN_EARTH_CENTERED_INERTIAL', 'x': 7078.0, 'y': 0.0, 'z': 0.0, 'vx': -0.0, 'vy': 7.504359112788965, 'vz': 0.0}, '@id': 0})]     


    """
    def __init__(self, date=None, numberSatellites=None, numberPlanes=None, relativeSpacing=None, alt=None, ecc=None, inc=None, aop=None, _id=None):
        
        self.date = date if date is not None and isinstance(date, propcov.AbsoluteDate) else None
        self.numberSatellites = int(numberSatellites) if numberSatellites is not None else None
        self.numberPlanes = int(numberPlanes) if numberPlanes is not None else None
        self.relativeSpacing = int(relativeSpacing) if relativeSpacing is not None else None
        self.alt = float(alt) if alt is not None else None
        self.ecc = float(ecc) if ecc is not None else None
        self.inc = float(inc) if inc is not None else None
        self.aop = float(aop) if aop is not None else None

        super(WalkerDeltaConstellation, self).__init__(_id, "Walker Delta Constellation")        

    @staticmethod
    def from_dict(d):
        """Parses an WalkerDeltaConstellation object from a normalized JSON dictionary.
        
        :param d: Dictionary with the constellation specifications.

                Following keys are to be specified.
                
                * "date": see :class:`orbitpy.util.OrbitState.date_from_dict`. Default: 2415019.5 JDUT1.
                * "@id": (str) Constellation identifier (unique). Default: A random string.
                * "numberSatellites": (int) Number of satellites in the constellation. Default: 3.
                * "numberPlanes": (int) Number of orbit planes in the constellation. Default: 3.
                * "relativeSpacing": (int) Factor controlling the spacing between the satellites in different planes. Default: 1.
                * "alt": (float) Altitude in kilometers. Default: 500.
                * "ecc": (float) Orbit eccentricity. Default: 0,
                * "inc": (float) Orbit inclination in degrees. Default: 98.22. 
                * "aop": (float) Orbit argument of perigee in degrees. Default: 135. 

        :paramtype d: dict

        :return: ``WalkerDeltaConstellation`` object.
        :rtype: :class:`orbitpy.constellation.WalkerDeltaConstellation`

        """
        _id = d.get("@id",str(uuid.uuid4()))
        date_dict = d.get("date",{"dateType": "JULIAN_DATE_UT1", "jd":2415019.5}) 
        if(date_dict):
            date = OrbitState.date_from_dict(date_dict)
        else:
            raise Exception("Please input date in the Walker Delta constellation specifications.")
        return WalkerDeltaConstellation( date              =  date,
                                         numberSatellites   = d.get("numberSatellites",3),
                                         numberPlanes       = d.get("numberPlanes",3),
                                         relativeSpacing    = d.get("relativeSpacing",1),
                                         alt                = d.get("alt",500),
                                         ecc                = d.get("ecc",0),
                                         inc                = d.get("inc",98.22),
                                         aop                = d.get("aop",135),
                                         _id                = _id
                                        )

    def to_dict(self):
        """ Translate the WalkerDeltaConstellation object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``WalkerDeltaConstellation`` object as python dictionary
        :rtype: dict
        
        """
        date_dict = OrbitState.date_to_dict(self.date)
        return { "date": date_dict,
                 "numberSatellites": self.numberSatellites,
                 "numberPlanes": self.numberPlanes,
                 "relativeSpacing": self.relativeSpacing,
                 "alt": self.alt,
                 "ecc": self.ecc,
                 "inc": self.inc,
                 "aop": self.aop,
                 "@id": self._id,
                 "@type": self._type}

    def __repr__(self):
        return "WalkerDeltaConstellation.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes.Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.date==other.date) and (self.numberSatellites==other.numberSatellites) and (self.numberPlanes==other.numberPlanes) and \
                    (self.relativeSpacing==other.relativeSpacing) and (self.alt==other.alt) and \
                   (self.ecc==other.ecc) and (self.inc==other.inc)  and (self.aop==other.aop) 
                
        else:
            return NotImplemented

    def generate_orbits(self):
        """ Process the Walker Delta constellation parameters to generate list of orbits containing their respective Keplerian elements.

        :returns: List of orbits in the constellation. 
        :rtype: list, :class:`orbitpy.util.OrbitState` 

        """        
        date = self.date
        num_sats = self.numberSatellites
        num_planes = self.numberPlanes
        rel_spc = self.relativeSpacing
        sma = Constants.radiusOfEarthInKM + self.alt
        ecc = self.ecc
        inc = self.inc
        aop = self.aop

        _id = self._id

        num_sats_pp = num_sats/num_planes
        if(not num_sats_pp.is_integer()):
            raise RuntimeError("Ratio of number of satellites to number of planes must be an integer.")
        else:
            num_sats_pp = int(num_sats_pp)

        print(".......Generating Walker Delta orbital Keplerian elements.......")
        print("orb_id, sma, ecc, inc, raan, aop, ta")
        orbits = [] #  list of orbits
        for pl_i in range(0,num_planes):
            raan = pl_i * 180.0/num_planes
            ta_ref = pl_i * rel_spc * 360.0/num_sats
            for sat_i in range(0,num_sats_pp):
                if _id is not None:
                    orb_id = _id + "_" + str(pl_i+1) + str(sat_i+1)
                else:
                    orb_id = str(pl_i+1) + str(sat_i+1)
                ta = (ta_ref + sat_i * 360.0/num_sats_pp)%360
                # construct the state object
                state_dict = {"stateType":"KEPLERIAN_EARTH_CENTERED_INERTIAL",  "sma": sma, "ecc": ecc, "inc": inc, "raan": raan, "aop": aop, "ta": ta}
                state = OrbitState.state_from_dict(state_dict)
                # append to list of orbits
                orbits.append(OrbitState(date, state, orb_id))
                print('{orb_id}, {sma}, {ecc}, {inc}, {raan}, {aop}, {ta}'.format(orb_id=orb_id, sma=sma, ecc=ecc, inc=inc, raan=raan, aop=aop, ta=ta))
        print(".......Done.......")
        return orbits

class TrainConstellation(Entity):
    """ TBD
    """
    def __init__(self):
        raise NotImplementedError

    def generate_orbits(self):
        pass