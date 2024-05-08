""" 
.. module:: propagator

:synopsis: *Module providing classes and functions to handle orbit propagation.*

"""
import numpy as np
from collections import namedtuple
import csv
import copy 

import propcov
from instrupy.util import Entity, Constants
from orbitpy.util import OutputInfoUtility
import orbitpy.util

from skyfield.api import EarthSatellite, load
from sgp4.api import Satrec, WGS72
from skyfield.elementslib import osculating_elements_of
from skyfield.positionlib import ICRF
from skyfield.framelib import ICRS
from skyfield.sgp4lib import TEME
from skyfield.api import Distance, Velocity

from sgp4.ext import rv2coe

def compute_time_step(spacecraft, time_res_fac):
    """ Compute time step to be used for orbit propagation based on list of input spacecrafts (considering the orbit sma and the sensor field-of-regard.)
    
    The propagation time step is calculated based on the time taken to cover the length (along-track) of the sensor field-of-**regard** footprint 
    and a time-resolution factor (:code:`time_res_fac`) (default = 0.25). 
    Smaller :code:`time_res_fac` implies higher precision in calculation of the access interval over a grid-point. 
    Note that in case of sensors with circular FOV there is always a chance that grid-points are missed during the access calculations.

    The field-of-regard is assumed to be oriented about the nadir (aligned to the ``NADIR_POINTING`` frame) and the calculated time-step is based on the 
    resulting along-track footprint length. Only ``CIRCULAR`` and ``RECTANGULAR`` field-of-regard spherical geometry shapes are supported. In case of ``RECTANGULAR``
    shaped spherical geometry note that the FOV/FOR angle-height would correspond to the along-track FOV/FOR.

    .. note:: The field-of-**regard** is considered here, and not the field-of-**view**.
    
    :param spacecraft: List of spacecrafts in the mission.
    :paramtype spacecraft: list, :class:`orbitpy:util.Spacecraft`

    :param time_res_fac: Factor which decides the time resolution of orbit propagation.
    :paramtype time_res_fac: float    

    :return: Minimum required propagation time step in seconds.
    :rtype: float      

    """
    RE = Constants.radiusOfEarthInKM
    GMe = Constants.GMe

    params = orbitpy.util.helper_extract_spacecraft_params(spacecraft) # obtain list of tuples of relevant spacecraft parameters

    # Iterate over each tuple and compute the corresponding time-step. Choose the minimum required time-step.
    min_t_step = 10000 # some high value
    for p in params:
        sma = p.sma # orbit semi-major axis
        for_at = p.for_height # note that field of regard is considered not field of view
                              # for_at stands for the along-track field-of-regard

        if for_at is None:
            # no instruments specified, hence no field-of-regard to consider, hence consider the entire horizon angle as FOR
            f = RE/sma
            for_at = np.rad2deg(2*np.arcsin(f))
        
        # calculate horizon angle
        f = RE/sma
        horizon_angle = np.rad2deg(2*np.arcsin(f))
        if(for_at > horizon_angle):
            for_at = horizon_angle # use the horizon angle if the instrument AT-FOR is larger than the horizon angle
        satVel = np.sqrt(GMe/sma)
        satGVel = f * satVel
        sinRho = RE/sma
        hfor_deg = for_at/2 # half-angle        
        
        # below snippet is needed because sometimes when for_at = horizon angle, it leads to x slightly greater then 1 due to floating-point errors.
        x = np.sin(np.deg2rad(hfor_deg))/sinRho
        if abs(np.sin(np.deg2rad(hfor_deg)) - sinRho) < 1e-7:
            x = 1
        elev_deg = np.rad2deg(np.arccos(x))        

        lambda_deg = 90 - hfor_deg - elev_deg # half-earth centric angle 
        eca_deg = lambda_deg*2 # total earth centric angle
        AT_FP_len = RE * np.deg2rad(eca_deg) # along-track footprint length           
        t_AT_FP = AT_FP_len / satGVel # find time taken by satellite to go over distance = along-track length
        tstep = time_res_fac * t_AT_FP
        if(tstep < min_t_step):
            min_t_step = tstep 

    return min_t_step    

class PropagatorFactory:
    """ Factory class which allows to register and invoke the appropriate propagator class. 
    
    :class:`J2AnalyticalPropagator` class is registered in the factory. 
    Additional user-defined propagator classes can be registered as shown below: 

    Usage: 
    
    .. code-block:: python
        
        factory = orbitpy.PropagatorFactory()
        factory.register_propagator('SGP4', SGP4Propagator)
        prop = factory.get_propagator('SGP4')

    :ivar _creators: Dictionary mapping propagator type label to the appropriate propagator class. 
    :vartype _creators: dict

    """
    def __init__(self):
        self._creators = {}
        self.register_propagator('J2 ANALYTICAL PROPAGATOR', J2AnalyticalPropagator)
        self.register_propagator('SGP4 PROPAGATOR', SGP4Propagator)

    def register_propagator(self, _type, creator):
        """ Function to register propagators.

        :var _type: Propagator type (label).
        :vartype _type: str

        :var creator: Propagator class.
        :vartype creator: Propagator class.

        """
        self._creators[_type] = creator

    def get_propagator(self, specs):
        """ Function to get the appropriate propagator instance.

        :var specs: Propagator specifications which also contains a valid propagator
                    type in the "@type" dict key. The propagator type is valid if it has been
                    registered with the ``PropagatorFactory`` instance.
        :vartype _type: dict

        :return: The appropriate propagator object initialized to the input specifications.
        :rtype: :class:`orbitpy.propagator.J2AnalyticalPropagator` or custom propagator class.
        
        """
        _type = specs.get("@type", None)
        if _type is None:
            raise KeyError('Propagator type key/value pair not found in specifications dictionary.')

        creator = self._creators.get(_type)
        if not creator:
            raise ValueError(_type)
        return creator.from_dict(specs)

class SGP4Propagator(Entity):
    """A Simplified General Perturbations 4 (SGP4) orbit propagator class.
    THe implementation of this class is basically a wrapper around the Skyfield SGP4 orbit propagator.

    The instance variable(s) correspond to the propagator setting(s). 

    :ivar stepSize: Orbit propagation time-step.
    :vartype stepSize: float or None

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, stepSize=None, _id=None):
        self.stepSize = float(stepSize) if stepSize is not None else None
        super(SGP4Propagator, self).__init__(_id, "SGP4 PROPAGATOR")
    
    @staticmethod
    def from_dict(d):
        """ Parses an SGP4Propagator object from a normalized JSON dictionary.
        
        :param d: Dictionary with the SGP4 PROPAGATOR specifications.

                Following keys are to be specified.
                
                * "stepSize": (float) Step size in seconds. Default value is 60s.
                * "@id": (str) Propagator identifier (unique). Default: A random string.

        :paramtype d: dict

        :return: ``SGP4Propagator`` object.
        :rtype: :class:`orbitpy.propagate.SGP4Propagator`

        """ 
        return SGP4Propagator(stepSize = d.get('stepSize', None), 
                                _id = d.get('@id', None))

    def to_dict(self):
        """ Translate the SGP4Propagator object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``SGP4Propagator`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "SGP4 PROPAGATOR",
                     "stepSize": self.stepSize,
                     "@id": self._id})

    def __repr__(self):
        return "SGP4Propagator.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.stepSize == other.stepSize)                
        else:
            return NotImplemented
    
    def execute(self, spacecraft, start_date=None, out_file_cart=None, out_file_kep=None, duration=1):
        """ Execute orbit propagation of the input spacecraft (single) and write to a csv data-file."""

        #### Get the mission start date ####
        if(start_date is None):
            start_date = spacecraft.orbitState.date       
        _start_date = start_date.GetJulianDate() # Get the Julian Date from the ``propcov.AbsoluteDate`` object 

        #### Build a Skyfield satellite object from orbital elements ####
        ''' Stick to using WGS72 based on the following discussion: https://github.com/dnwrnr/sgp4/issues/15
            Quote: " Note that the Python SGP4 implementation - which is an extremely close port of the official C++ version - strongly recommends 
                  sticking with WGS72 instead of WGS84, see https://pypi.org/project/sgp4/#gravity "
        '''
        # Get the instantaneous Cartesian elements (in CARTESIAN_EARTH_CENTERED_INERTIAL (J2000) frame) of the spacecraft
        sat_epoch_state = spacecraft.orbitState.to_dict()
        _state = sat_epoch_state['state']
        _epoch = sat_epoch_state['date']

        _pos = np.array([_state['x'], _state['y'], _state['z']])
        _pos = Distance(km = _pos) # convert to Skyfield object
        _vel = np.array([_state['vx'], _state['vy'], _state['vz']])
        _vel = Velocity(km_per_s = _vel) # convert to Skyfield object
        ts_epoch = load.timescale()
        epoch = ts_epoch.ut1_jd(_epoch['jd']) #  satellite epoch (which could be different from the mission epoch)
        # print("\n Satellite epoch in UTC is: ", propagate_time.utc_jpl())

        #### get the orbit state in TEME frame using SkyField ####
        # reference: https://rhodesmill.org/skyfield/positions.html#coordinates-in-other-reference-frames
        # https://rhodesmill.org/skyfield/api-position.html#skyfield.positionlib.ICRF.from_time_and_frame_vectors
        # build the Skyfield Position object 
        # ICRF frame ~ J2000, see: https://rhodesmill.org/skyfield/positions.html#the-icrs-reference-system-and-j2000

        # https://space.stackexchange.com/questions/25988/sgp4-teme-frame-to-j2000-conversion
        # https://github.com/skyfielders/python-skyfield/blob/6fa3f4654c1c552c1522d61246267d032f25ea2e/skyfield/sgp4lib.py (TEME reference frame)
        # https://github.com/skyfielders/python-skyfield/blob/6fa3f4654c1c552c1522d61246267d032f25ea2e/skyfield/framelib.py (Reference frames)
        # https://rhodesmill.org/skyfield/api.html#reference-frames        
        # https://github.com/skyfielders/python-skyfield/issues/384

        # get the satellite state in TEME frame
        skyfield_icrs_position =   ICRF.from_time_and_frame_vectors(epoch, ICRS, _pos, _vel)
        print(skyfield_icrs_position.frame_xyz_and_velocity(ICRS))
        print(skyfield_icrs_position.frame_xyz_and_velocity(TEME))
        (skyfield_teme_pos, skyfield_teme_vel) = skyfield_icrs_position.frame_xyz_and_velocity(TEME)
        
        # get the mean Keplerian elements from the instantaneous TEME Cartesian coordinates
        MU_Earth = 3.98600e5 # gravitational parameter  km3 / s2
        (_p, _a, _ecc, _incl, _omega, _argp, _nu, _m, _arglat, _truelon, _lonper) = rv2coe(skyfield_teme_pos.km, skyfield_teme_vel.km_per_s, MU_Earth) # note that the angles are in radians
        _mean_motion = 60.0 * np.sqrt(MU_Earth/ (_a*_a*_a)) # semimajor axis (_a) units are in km. Obtained mean motion is in rad per minute.

        satrec = Satrec()
        # TODO: The second derivative of mean motion needs to be calculated.
        satrec.sgp4init(
            WGS72,           # gravity model
            'i',             # 'a' = old AFSPC mode, 'i' = improved mode
            5,               # satnum: Satellite number
            18441.785,       # epoch: days since 1949 December 31 00:00 UT
            2.8098e-05,      # bstar: drag coefficient (/earth radii)
            6.969196665e-13, # ndot: ballistic coefficient (radians/minute^2)
            0.0,             # nddot: second derivative of mean motion (radians/minute^3)
            _ecc,       # ecco: eccentricity
            _argp, # argpo: argument of perigee (radians)
            _incl, # inclo: inclination (radians)
            _m, # mo: mean anomaly (radians)
            _mean_motion, # no_kozai: mean motion (radians/minute)
            _omega, # nodeo: right ascension of ascending node (radians)
        )
        ts = load.timescale()
        sat = EarthSatellite.from_satrec(satrec, ts) # wrap into a Skyfield object
        print('Satellite number:', sat.model.satnum)
        print('Epoch:', sat.epoch.utc_jpl())

        # Prepare output files in which results shall be written
        if out_file_cart:
            cart_file = open(out_file_cart, 'w', newline='')
            cart_writer = csv.writer(cart_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            cart_writer.writerow(["Satellite states are in CARTESIAN_EARTH_CENTERED_INERTIAL (equatorial-plane) frame."])
            cart_writer.writerow(["Epoch [JDUT1] is {}".format(_start_date)])
            cart_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            cart_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            cart_writer.writerow(['time index','x [km]','y [km]','z [km]','vx [km/s]','vy [km/s]','vz [km/s]'])

        if out_file_kep:
            kep_file = open(out_file_kep, 'w', newline='')
            kep_writer = csv.writer(kep_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            kep_writer.writerow(["Satellite states as KEPLERIAN_EARTH_CENTERED_INERTIAL elements."])
            kep_writer.writerow(["Epoch [JDUT1] is {}".format(_start_date)])
            kep_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            kep_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            kep_writer.writerow(['time index','sma [km]','ecc','inc [deg]','raan [deg]','aop [deg]','ta [deg]'])
        


        # Propagate at time-resolution = stepSize. 
        # Take into advantage the vectorized nature of Skyfield's functions
        _seconds = np.arange(0, duration*86400.0, self.stepSize)
        indices = np.arange(len(_seconds))

        propagate_time =  ts.ut1_jd(_start_date + _seconds) 
        
        geocentric = sat.at(propagate_time) # in GCRS (ECI) coordinates. GCRS ~ J2000, and is treated as the same in OrbitPy See: https://rhodesmill.org/skyfield/earth-satellites.html#generating-a-satellite-position

        # write state            
        if out_file_cart:
            pos = geocentric.position.km
            vel = geocentric.velocity.km_per_s

            # Transpose the arrays to get rows of data
            data = np.vstack((indices, pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])).T
            cart_writer.writerows(data)

        if out_file_kep:
            osc_elements = osculating_elements_of(geocentric) # TODO: Verify that the produced elements are in the same reference frame as the reference frame of the position object. (It is likely this is true.)
            sma = osc_elements.semi_major_axis.km
            ecc = osc_elements.eccentricity
            inc = osc_elements.inclination.degrees
            raan = osc_elements.longitude_of_ascending_node.degrees
            aop = osc_elements.argument_of_periapsis.degrees
            ta = osc_elements.true_anomaly.degrees

            # Transpose the arrays to get rows of data
            data = np.vstack((indices, sma, ecc, inc, raan, aop, ta)).T
            kep_writer.writerows(data)
        
        if out_file_cart:
            cart_file.close()
        if out_file_kep:
            kep_file.close()


class J2AnalyticalPropagator(Entity):
    """A J2 ANALYTICAL PROPAGATOR class.

    The instance variable(s) correspond to the propagator setting(s). 

    :ivar stepSize: Orbit propagation time-step.
    :vartype stepSize: float or None

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, stepSize=None, _id=None):
        self.stepSize = float(stepSize) if stepSize is not None else None
        super(J2AnalyticalPropagator, self).__init__(_id, "J2 ANALYTICAL PROPAGATOR")

    @staticmethod
    def from_dict(d):
        """ Parses an J2AnalyticalPropagator object from a normalized JSON dictionary.
        
        :param d: Dictionary with the J2 ANALYTICAL PROPAGATOR specifications.

                Following keys are to be specified.
                
                * "stepSize": (float) Step size in seconds. Default value is 60s.
                * "@id": (str) Propagator identifier (unique). Default: A random string.

        :paramtype d: dict

        :return: ``J2AnalyticalPropagator`` object.
        :rtype: :class:`orbitpy.propagate.J2AnalyticalPropagator`

        """ 
        return J2AnalyticalPropagator(stepSize = d.get('stepSize', None), 
                                           _id = d.get('@id', None))

    def to_dict(self):
        """ Translate the J2AnalyticalPropagator object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``J2AnalyticalPropagator`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "J2 ANALYTICAL PROPAGATOR",
                     "stepSize": self.stepSize,
                     "@id": self._id})

    def __repr__(self):
        return "J2AnalyticalPropagator.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes. Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.stepSize == other.stepSize)
                
        else:
            return NotImplemented

    def execute(self, spacecraft, start_date=None, out_file_cart=None, out_file_kep=None, duration=1):
        """ Execute orbit propagation of the input spacecraft (single) and write to a csv data-file.

        The computed satellite states are in the Earth Centered Inertial frame, identical to EarthMJ2000Eq used in NASA GMAT software. 
        For more description see: `GMAT CoordinateSystem <http://gmat.sourceforge.net/docs/nightly/html/CoordinateSystem.html>`_
        
        :param spacecraft: Spacecraft whose orbit is to be propagated.
        :paramtype spacecraft: :class:`orbitpy.util.Spacecraft`

        :param out_file_cart: File name with path of the file in which the orbit states in ``CARTESIAN_EARTH_CENTERED_INERTIAL`` are written.
                               If ``None`` the file is not written.

                               *  The first row specifies if the states are in ``CARTESIAN_EARTH_CENTERED_INERTIAL`` or ``KEPLERIAN_EARTH_CENTERED_INERTIAL`` reference frame.
                               *  The second row containing the mission epoch in Julian Day UT1. The time (index) in the state data is referenced to this epoch.
                               *  The third row contains the time-step size in seconds. 
                               *  The fourth row contains the mission duration in days.
                               *  The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 

                                Note that time associated with a row is:  ``time = epoch (in JDUT1) + time-index * time-step-size (in secs) * (1/86400)`` 
                                Description of the data (comma-seperated) is given below:

                               .. csv-table:: CARTESIAN_EARTH_CENTERED_INERTIAL state data description
                                    :header: Column, Data type, Units, Description
                                    :widths: 10,10,10,40

                                    time index, int, , Time-index
                                    x [km], float, km, X component of spacecraft position.
                                    y [km], float, km, Y component of spacecraft position.
                                    z [km], float, km, Z component of spacecraft position.
                                    vx [km/s], float, km per sec, X component of spacecraft velocity.
                                    vy [km/s], float, km per sec, Y component of spacecraft velocity.
                                    vz [km/s], float, km per sec, Z component of spacecraft velocity.


        :paramtype out_file_cart: str

        :param out_file_kep: File name with path of the file in which the orbit states in ``KEPLERIAN_EARTH_CENTERED_INERTIAL`` are written.
                                If ``None`` the file is not written. The output data format is similar to the data format of the *out_file_cart*
                                file, except the columns headers are as follows:

                                .. csv-table:: KEPLERIAN_EARTH_CENTERED_INERTIAL state data description
                                    :header: Column, Data type, Units, Description
                                    :widths: 10,10,5,40

                                    time index, int, , Time-index
                                    sma [km], float, km, Orbit semi-major axis dimension.
                                    ecc, float, , Orbit eccentricity
                                    inc [deg], float, degrees, Orbit inclination
                                    raan [deg], float, degrees, Orbit right ascension of ascending node
                                    aop [deg], float, degrees, Orbit argument of Perigee
                                    ta [deg], float, degrees, True Anomaly

        :paramtype out_file_kep: str

        :param start_date: Time start for propagation. If ``None``, the date at which the spacecraft orbit-state is referenced shall be used as the start date.
        :paramtype start_date: :class:`orbitpy.propcov.AbsoluteDate`

        :param duration: Time duration propagation in days.  Default is 1 day.
        :paramtype duration: float

        :return: Propagator output info.
        :rtype: :class:`orbitpy.propagator.PropagatorOutputInfo`
        

        """
        # form the propcov.Spacecraft object
        attitude = propcov.NadirPointingAttitude()
        interp = propcov.LagrangeInterpolator()

        # following snippet is required, because any copy, changes to the propcov objects in the input spacecraft is reflected outside the function.
        spc_date = propcov.AbsoluteDate()
        spc_date.SetJulianDate(spacecraft.orbitState.date.GetJulianDate())
        spc_orbitstate = propcov.OrbitState()
        spc_orbitstate.SetCartesianState(spacecraft.orbitState.state.GetCartesianState())
        
        spc = propcov.Spacecraft(spc_date, spc_orbitstate, attitude, interp, 0, 0, 0, 1, 2, 3) # TODO: initialization to the correct orientation of spacecraft is not necessary for the purpose of orbit-propagation, so ignored for time-being.
        
        if(start_date is None):
            start_date = spacecraft.orbitState.date

        # following snippet is required, because any copy, changes to the input start_date is reflected outside the function. (Similar to pass by reference in C++.)
        # so instead a separate copy of the start_date is made and is used within this function.
        _start_date = propcov.AbsoluteDate()
        _start_date.SetJulianDate(start_date.GetJulianDate())

        # form the propcov.Propagator object
        prop = propcov.Propagator(spc)

        # Prepare output files in which results shall be written
        if out_file_cart:
            cart_file = open(out_file_cart, 'w', newline='')
            cart_writer = csv.writer(cart_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            cart_writer.writerow(["Satellite states are in CARTESIAN_EARTH_CENTERED_INERTIAL (equatorial-plane) frame."])
            cart_writer.writerow(["Epoch [JDUT1] is {}".format(_start_date.GetJulianDate())])
            cart_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            cart_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            cart_writer.writerow(['time index','x [km]','y [km]','z [km]','vx [km/s]','vy [km/s]','vz [km/s]'])

        if out_file_kep:
            kep_file = open(out_file_kep, 'w', newline='')
            kep_writer = csv.writer(kep_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            kep_writer.writerow(["Satellite states as KEPLERIAN_EARTH_CENTERED_INERTIAL elements."])
            kep_writer.writerow(["Epoch [JDUT1] is {}".format(_start_date.GetJulianDate())])
            kep_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            kep_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            kep_writer.writerow(['time index','sma [km]','ecc','inc [deg]','raan [deg]','aop [deg]','ta [deg]'])

        # propagate to the specified start date since the date at which the orbit-state is defined
        # could be different from the specified start_date (propagation could be either forwards or backwards)
        prop.Propagate(_start_date)
        date = _start_date
        # Propagate at time-resolution = stepSize. Store the orbit-state at each time-step.
        number_of_time_steps = int(duration*86400/ self.stepSize)
        for idx in range(0,number_of_time_steps+1):            
            # write state            
            if out_file_cart:
                cart_state = spc.GetCartesianState().GetRealArray()
                cart_writer.writerow([idx, cart_state[0], cart_state[1], cart_state[2], cart_state[3], cart_state[4], cart_state[5]])
            if out_file_kep:
                kep_state = spc.GetKeplerianState().GetRealArray()
                kep_writer.writerow([idx, kep_state[0], kep_state[1], np.rad2deg(kep_state[2]), 
                                          np.rad2deg(kep_state[3]), np.rad2deg(kep_state[4]), np.rad2deg(kep_state[5])])
            # propagate by 1 time-step
            date.Advance(self.stepSize)
            prop.Propagate(date)
            
        if out_file_cart:
            cart_file.close()
        if out_file_kep:
            kep_file.close()

        return PropagatorOutputInfo.from_dict({'propagatorType': 'J2 ANALYTICAL PROPAGATOR', 
                                               'spacecraftId': spacecraft._id,
                                               'stateCartFile': out_file_cart,
                                               'stateKeplerianFile': out_file_kep,
                                               'startDate': start_date.GetJulianDate(),
                                               'duration': duration})

class PropagatorOutputInfo(Entity):
    """ Class to hold information about the results of the propagation. An object of this class is returned upon the execution
        of the propagator.
    
    :ivar propagatorType: Type of orbit propagator which produced the results.
    :vartype propagatorType: str

    :ivar spacecraftId: Spacecraft identifier for which propagation was carried out.
    :vartype spacecraftId: str or int

    :ivar stateCartFile: State file (filename with path) where the time-series of the cartesian states of the spacecraft are saved.
    :vartype stateCartFile: str

    :ivar stateKeplerianFile: State file (filename with path) where the time-series of the Keplerian states of the spacecraft are saved.
    :vartype stateKeplerianFile: str

    :ivar startDate: Time start for propagation in Julian Date UT1.
    :vartype startDate: float

    :ivar duration: Time duration propagation in days.
    :vartype duration: float

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, propagatorType=None, spacecraftId=None, stateCartFile=None, stateKeplerianFile=None, 
                 startDate=None, duration=None, _id=None):
        self.propagatorType = propagatorType if propagatorType is not None else None
        self.spacecraftId = spacecraftId if spacecraftId is not None else None
        self.stateCartFile = str(stateCartFile) if stateCartFile is not None else None
        self.stateKeplerianFile = str(stateKeplerianFile) if stateKeplerianFile is not None else None
        self.startDate = float(startDate) if startDate is not None else None
        self.duration = float(duration) if duration is not None else None

        super(PropagatorOutputInfo, self).__init__(_id, OutputInfoUtility.OutputInfoType.PropagatorOutputInfo.value)
    
    @staticmethod
    def from_dict(d):
        """ Parses an ``PropagatorOutputInfo`` object from a normalized JSON dictionary.
        
        :param d: Dictionary with the PropagatorOutputInfo attributes.
        :paramtype d: dict

        :return: ``PropagatorOutputInfo`` object.
        :rtype: :class:`orbitpy.propagator.PropagatorOutputInfo`

        """
        return PropagatorOutputInfo( propagatorType = d.get('propagatorType', None),
                                     spacecraftId = d.get('spacecraftId', None),
                                     stateCartFile = d.get('stateCartFile', None),
                                     stateKeplerianFile = d.get('stateKeplerianFile', None),
                                     startDate = d.get('startDate', None),
                                     duration = d.get('duration', None),
                                     _id  = d.get('@id', None))

    def to_dict(self):
        """ Translate the ``PropagatorOutputInfo`` object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: ``PropagatorOutputInfo`` object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": OutputInfoUtility.OutputInfoType.PropagatorOutputInfo.value,
                     "propagatorType": self.propagatorType,
                     "spacecraftId": self.spacecraftId,
                     "stateCartFile": self.stateCartFile,
                     "stateKeplerianFile": self.stateKeplerianFile,
                     "startDate": self.startDate,
                     "duration": self.duration,
                     "@id": self._id})

    def __repr__(self):
        return "PropagatorOutputInfo.from_dict({})".format(self.to_dict())
    
    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes.Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.propagatorType==other.propagatorType) and (self.spacecraftId==other.spacecraftId) and (self.stateCartFile==other.stateCartFile) and \
                    (self.stateKeplerianFile==other.stateKeplerianFile) and (self.startDate==other.startDate) and (self.duration==other.duration) 
                
        else:
            return NotImplemented
    
    def check_loose_equality(self, other):
        """ Check for equality with another ``PropagatorOutputInfo`` object considering only some instance variables.

            :param other: The other ``PropagatorOutputInfo`` object with which the comparision shall be done.
            :paramtype other: :class:`orbitpy.propagator.PropagatorOutputInfo`

        """
        if(isinstance(self, other.__class__)):
            return (self.spacecraftId==other.spacecraftId)
                
        else:
            return False

