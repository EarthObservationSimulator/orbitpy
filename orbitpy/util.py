""" 
.. module:: util

:synopsis: *Collection of utlity functions used by the :code:`orbitpy` package. 
            Note that many other utility functions are imported from the :code:`instrupy` package too.*

"""
import json
from enum import Enum
from numbers import Number
import numpy as np
import math
import propcov
from instrupy.util import *
class CoverageCalculationsApproach(EnumEntity):
    """ Enumeration of recognized approaches to calculation coverage."""
    PNTOPTS_WITH_GRIDPNTS = "PNTOPTS_WITH_GRIDPNTS"
    GRIDPNTS = "GRIDPNTS"
    PNTOPTS = "PNTOPTS"
    SKIP = "SKIP"
class PropagationCoverageParameters():
    """ Data structure holding propagation and coverage parameters.
    
    :ivar sat_id: Satellite (Orbit) identifier
    :vartype sat_id: str

    :ivar epoch: Mission epoch in UTC Greogrian in the following CSV format: `'year,month,day,hr,min,secs'`
    :vartype epoch: str

    :ivar sma: Orbit semi-major axis in kilometers
    :vartype sma: float

    :ivar ecc: Orbit eccentricity 
    :vartype ecc: float

    :ivar inc: Orbit inclination in degrees
    :vartype inc: float

    :ivar raan: Orbit Right Ascension of Ascending Node in degrees
    :vartype raan: float

    :ivar aop: Orbit Argument of Perigee in degrees
    :vartype aop: float

    :ivar ta: Orbit True Anomaly in degrees
    :vartype ta: float
    
    :ivar duration: Mission duration in days
    :vartype duration: float

    :ivar cov_grid_fl: Filepath to the coverage grid data
    :vartype cov_grid_fl: str

    :ivar sen_fov_geom: FOV/FOR geometry of the sensor
    :vartype sen_fov_geom:  str

    :ivar sen_orien: Sensor orientation specification in the following CSV string format: :code:`Euler-Seq1, Euler-Seq2, Euler-Seq3, Euler-Angle1, Euler-Angle2,, Euler-Angle3`. Angles are specifed in degrees.
    :vartype sen_orien:  str

    :ivar sen_clock: Sensor FOV/FOR clock angles in degrees in CSV string format.
    :vartype sen_clock: str

    :ivar sen_cone: Sensor FOV/FOR cone angles in degrees in CSV string format.
    :vartype sen_cone: str

    :ivar purely_sidelook: Flag to specify if instrument operates in a strictly side-looking viewing geometry.
    :vartype purely_sidelook: bool

    :ivar yaw180_flag: Flag indicating if FOR includes the FOV defined by the above clock, cone angles rotated by 180 deg around the nadir.
    :vartype yaw180_flag:  (0/1)

    :ivar step_size: Propagation step size in seconds.
    :vartype step_size: float

    :ivar sat_state_fl: Filepath to write the resulting satellite states.
    :vartype sat_state_fl: str

    :ivar sat_acc_fl: Filepath to write the resulting satellite access data over the grid of points given in the coverage grid file.
    :vartype sat_acc_fl: str

    :ivar popts_fl: Filepath from which to read the pointing options
    :vartype popts_fl: str

    :ivar cov_calcs_app: Coverage caclulations approach
    :vartype cov_calcs_app: str

    :ivar do_prop: Flag indicating if propagation calculation is to be performed.
    :vartype do_prop: bool

    :ivar do_cov: Flag indicating if coverage calculation is to be performed.
    :vartype do_cov: bool
    
    """
    def __init__(self, sat_id=str(), epoch=str(), sma=float(), ecc=float(), inc=float(), raan=float(), aop=float(), ta=float(), 
                 duration=float(), cov_grid_fl=str(), sen_fov_geom=str(), sen_orien=str(), sen_clock=str(), 
                 sen_cone=str(), purely_sidelook = bool(), yaw180_flag = int(), step_size=float(), sat_state_fl=str(), 
                 sat_acc_fl=str(), popts_fl=str(), cov_calcs_app = str(), do_prop=bool(), do_cov=bool()):
        self.sat_id = str(sat_id)
        self.epoch = str(epoch) 
        self.sma = float(sma) 
        self.ecc = float(ecc) 
        self.inc = float(inc) 
        self.raan = float(raan) 
        self.aop = float(aop) 
        self.ta = float(ta)
        self.duration = float(duration) 
        self.cov_grid_fl = str(cov_grid_fl) if cov_grid_fl else None
        self.popts_fl = str(popts_fl) if popts_fl else None 
        self.sen_fov_geom = str(sen_fov_geom) if sen_fov_geom else None
        self.sen_orien = str(sen_orien) if sen_orien else None
        self.sen_clock = str(sen_clock) if sen_clock else None
        self.sen_cone = str(sen_cone) if sen_cone else None
        self.purely_sidelook = bool(purely_sidelook) if purely_sidelook else None
        self.yaw180_flag = int(yaw180_flag) if yaw180_flag is not None else None
        self.step_size = float(step_size) 
        self.sat_state_fl = str(sat_state_fl) 
        self.sat_acc_fl = str(sat_acc_fl) if sat_acc_fl else None
        self.cov_calcs_app = CoverageCalculationsApproach.get(cov_calcs_app) 
        self.do_prop = bool(do_prop) if do_prop is not None else True
        self.do_cov = bool(do_cov) if do_cov is not None else True

class OrbitPyDefaults(object):
    """ Enumeration of various default values used by package **OrbitPy**.
    """
    grid_res_fac = 0.9
    time_res_fac = 0.25
    
class Satellite():
    """ Data structure holding attributes of a Satellite. Note the implicit relation that the :code:`ics_fov`
        and :code:`ics_for` lists are linkes. I.e. :code:`ics_fov[0]` and :code:`ics_for[0]` refer to the FOV 
        and FOR of the first instrument on the satellite, and so on. 
    
    :ivar orbit: Orbital parameters of the satellite. 
    :vartype orbit: :class:`orbitpy.preprocess.OrbitParameters` 

    :ivar instru: List of Instruments
    :vartype instru: :class:`instrupy.public_library.Instrument` 

    :ivar dir_pth: Directory path which contains file relevant to the satellite
    :vartype dir_pth: str

    """ 
    def __init__(self, orbit = None, instru =None, dir_pth=None):

        self.orbit = orbit if orbit is not None else None
        self.instru = instru if instru is not None else None
        self.dir_pth =  dir_pth if dir_pth is not None else None


def calculate_inclination_circular_SSO(altitude_km):
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
    print(i0)
    err = 1e1
    while(err >= tol):
        # J2 perturbed mean motion
        _np  = n*(1 + (1.5*J2*(Re/h))**2*np.sqrt(1 - e**2)*(1 - (3/2*np.sin(np.deg2rad(i0))**2)))
        i = 180/np.pi*(np.arccos(-2/3*((h/Re)**2)*we/(_np*J2)))
        err = abs(i - i0)
        i0 = i
    return i

class StateType(EnumEntity):
    KEPLERIAN = "KEPLERIAN"
    CARTESIAN_EARTH_CENTERED_INERTIAL = "CARTESIAN_EARTH_CENTERED_INERTIAL"
    CARTESIAN_EARTH_FIXED = "CARTESIAN_EARTH_FIXED"

class DateType(EnumEntity):
    GREGORIAN_UTC = "GREGORIAN_UTC"
    JULIAN_DATE_UT1 = "JULIAN_DATE_UT1"        

class OrbitState(Entity):
    """ Class to store the orbit state (i.e. the date, position and velocity of satellite).
        The :class:`propcov.AbsoluteDate` and `propcov.OrbitState` objects are used to maintain the 
        date and state respectively. 

    :ivar date: Date at which the orbit state is defined.
    :vartype date: propcov.AbsoluteDate

    :ivar state: Orbit state (satellite position, velocity).
    :vartype state: propcov.OrbitState

    :ivar _id: Unique identifier.
    :vartype _id: str
    
    """
    def __init__(self, date=None, state=None, _id=None):

        self.date = date if date is not None and isinstance(date, propcov.AbsoluteDate) else None
        self.state = state if state is not None and isinstance(state, propcov.OrbitState) else None
        super(OrbitState, self).__init__(_id, "OrbitState")   

    @staticmethod
    def from_dict(d):
        """ Parses orbit state from a dictionary.

        :param d: Dictionary with the date and state description. 
        
        :return: Parsed python object. 
        :rtype: :class:`orbitpy.util.InitialOrbitState`

        """

        date = OrbitState.set_date(d.get("date", None))
        state = OrbitState.set_state(d.get("state", None))

        return OrbitState(date=date, state=state, _id=d.get("@id", None))

    def to_dict(self):
        state = self.get_cartesian_earth_centered_inertial_state()
        return dict({"date": { "dateType": "JULIAN_DATE_UT1", "jd": self.get_julian_date()}, 
                     "state": {"stateType": "CARTESIAN_EARTH_CENTERED_INERTIAL", "x": state[0], "y": state[1], "z": state[2], "vx": state[3], "vy": state[4], "vz": state[5]}, 
                     "@id": self._id})

    def get_julian_date(self):
        """ Get Julian Date UT1.

        :returns: Julian date UT1
        :rtype: float

        """
        return self.date.GetJulianDate()
    

    def get_cartesian_earth_centered_inertial_state(self):
        """ Get Cartesian Earth Centered Inertial position, velocity.

        :returns: Satellite position, velocity as a list.
        :rtype: list, float

        """
        return self.state.GetCartesianState().GetRealArray()

    def __eq__(self, other):
        """ Simple equality check. Returns True if the class attributes are equal, else returns False. 
        """
        return (self.date == other.date and self.state == other.state)

    def __repr__(self):
        return "OrbitState.from_dict({})".format(self.to_dict())

    @staticmethod
    def set_date(d):
        """ Set the instance date attribute from the input dictionary.

        :param d: Dictionary with the date description. 
            
            In case of ``GREGORIAN_UTC`` date type the following keys apply: year (int), month (int), day (int), hour (int), minute (int) and second (float).

            In case of `JULIAN_DATE_UT1` date type the following keys apply: jd (float)

        :paramtype d: dict

        :returns: ``propcov`` date object.
        :rtype: :class:`propcov.AbsoluteDate`

        """

        date = propcov.AbsoluteDate()
        if d is not None:            
            if(DateType.get(d["dateType"]) == DateType.GREGORIAN_UTC):
                try:
                    date.SetGregorianDate(year=d["year"], month=d["month"], day=d["day"], hour=d["hour"], minute=d["minute"], second=d["second"])
                except:
                    raise Exception("Something wrong in setting of Gregorian UTC date object. Check that the year, month, day, hour, second key/value pairs have been specified in the input dictionary.")
        
            elif(DateType.get(d["dateType"]) == DateType.JULIAN_DATE_UT1):
                try:
                    date.SetJulianDate(jd=d["jd"])
                except:
                    raise Exception("Something wrong in setting of Julian UT1 date object. Check that the jd key/value pair has been specified in the input dictionary.")
        else:
            raise Exception("Please specify a date.")
        
        return date

    @staticmethod
    def set_state(d):
        """ Set the instance state attribute from the input dictionary.

        :param d: Dictionary with the date description. 
            
            In case of ``KEPLERIAN`` date type the following keys apply: year (int), month (int), day (int), hour (int), minute (int) and second (float).

            In case of `CARTESIAN_EARTH_CENTERED_INERTIAL` date type the following keys apply: 
            
            * x  : (km) satellite x-position
            * y  : (km) satellite x-position
            * z  : (km) satellite x-position
            * vx : (km/s) satellite x-velocity
            * vy : (km/s) satellite y-velocity
            * vz : (km/s) satellite z-velocity

        :paramtype d: dict

        :returns: ``propcov`` date object.
        :rtype: :class:`propcov.OrbitState`

        """
        state = propcov.OrbitState()
        state_type = StateType.get(d.get('stateType', None))
        
        if state_type is not None:
            if state_type == StateType.KEPLERIAN:
                try:
                    state.SetKeplerianState(SMA=d["sma"], ECC=d["ecc"], INC=d["inc"], RAAN=d["raan"], AOP=d["aop"], TA=d["ta"])
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
            raise Exception("Please enter a stateType specification.")

        return state
