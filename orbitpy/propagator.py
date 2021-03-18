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
import orbitpy.util

def compute_time_step(spacecraft, time_res_fac):
    """ Compute time step to be used for orbit propagation based on list of input spacecrafts (considering the orbit sma and the sensor field-of-regard.)
    
    The propagation time step is selected based on the time taken to cover the length (along-track) of the sensor footprint from it's field-of-**regard** 
    and a time-resolution factor (:code:`time_res_fac`) which is typically set to 0.25. Smaller :code:`time_res_fac` implies higher precision
    in calculation of the access interval over a grid-point. In case of CIRCULAR sensors there is always a chance that a grid-point
    is missed during the access calculations.

    The field-of-regard is assumed to be oriented about the nadir (aligned to the NADIR_POINTING frame) and the calculated time-step is based on the 
    resulting along-track footprint length. Only CIRCULAR and RECTANGULAR field-of-regard spherical geometry shapes are supported. In case of RECTANGULAR
    shaped spherical geometry note that the FOV/FOR angle-height would correspond to the along-track FOV/FOR.

    .. figure:: time_step_illus.png
        :scale: 75 %
        :align: center

        Illustration of possible inaccuracies due to a large time resolution factor (0.75 in above figure).
    
    :param spacecraft: List of spacecrafts in the mission.
    :paramtype spacecraft: list, :class:`orbitpy:util.Spacecraft`

    :param time_res_fac: Factor which decides the time resolution of orbit propagation.
    :paramtype time_res_fac: float    

    :return: Minimum require propagation time step in seconds.
    :rtype: float      
    
    .. note:: The field-of-**regard** is considered here, and not the field-of-**view**.

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
        
        # calculate maximum horizon angle
        f = RE/sma
        max_horizon_angle = np.rad2deg(2*np.arcsin(f))
        if(for_at > max_horizon_angle):
            for_at = max_horizon_angle # use the maximum horizon angle if the instrument AT-FOR is larger than the maximum horizon angle
        satVel = np.sqrt(GMe/sma)
        satGVel = f * satVel
        sinRho = RE/sma
        hfor_deg = for_at/2 # half-angle
        elev_deg = np.rad2deg(np.arccos(np.sin(np.deg2rad(hfor_deg))/sinRho))
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
        self.register_propagator('J2 Analytical Propagator', J2AnalyticalPropagator)

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
        
        """
        _type = specs.get("@type", None)
        if _type is None:
            raise KeyError('Propagator type key/value pair not found in specifications dictionary.')

        creator = self._creators.get(_type)
        if not creator:
            raise ValueError(_type)
        return creator.from_dict(specs)

class J2AnalyticalPropagator(Entity):
    """A J2 Analytical Propagator class.

    The instance variable(s) correspond to the propagator setting(s). 

    :ivar stepSize: Orbit propagation time-step. Default is False.
    :vartype stepSize: float

    :ivar _id: Unique identifier.
    :vartype _id: str

    """
    def __init__(self, stepSize=None, _id=None):
        self.stepSize = float(stepSize) if stepSize is not None and stepSize is not False else False
        super(J2AnalyticalPropagator, self).__init__(_id, "J2 Analytical Propagator")

    @staticmethod
    def from_dict(d):
        """ Parses an J2AnalyticalPropagator object from a normalized JSON dictionary.
        
        :param d: Dictionary with the J2 analytical propagator specifications.

                Following keys are to be specified.
                
                * "stepSize": (float) Step size in seconds. Default value is 60s.
                * "@id": (str) Propagator identifier (unique). Default: A random string.

        :paramtype d: dict

        :return: J2AnalyticalPropagator object.
        :rtype: :class:`orbitpy.propagate.J2AnalyticalPropagator`

        """ 
        return J2AnalyticalPropagator(stepSize = d.get('stepSize', 60), 
                                           _id = d.get('@id', None))

    def to_dict(self):
        """ Translate the J2AnalyticalPropagator object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: J2AnalyticalPropagator object as python dictionary
        :rtype: dict
        
        """
        return dict({"@type": "J2 Analytical Propagator",
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

        
        :param spacecraft: Spacecraft whose orbit is to be propagated.
        :paramtype spacecraft: :class:`orbitpy.util.Spacecraft`

        :param out_file_cart: File name with path of the file in which the orbit states in CARTESIAN_EARTH_CENTERED_INERTIAL are written.
                               If ``None`` the file is not written.

                               The format of the data of the output file is as follows:
                               The first four rows contain general information, with the second row containing the mission epoch in Julian Day UT1. The time
                               in the state data is referenced to this epoch. The third row contains the time-step size in seconds. 
                               The fifth row contains the columns headers and the sixth row onwards contains the corresponding data. 
                               Description of the data is given below:

                               .. csv-table:: CARTESIAN_EARTH_CENTERED_INERTIAL State data description
                                    :header: Column, Data type, Units, Description
                                    :widths: 10,10,5,40

                               time index, int, , Time-index
                               x [km], float, kilometers, X component of spacecraft position in CARTESIAN_EARTH_CENTERED_INERTIAL
                               y [km], float, kilometers, Y component of spacecraft position in CARTESIAN_EARTH_CENTERED_INERTIAL
                               z [km], float, kilometers, Z component of spacecraft position in CARTESIAN_EARTH_CENTERED_INERTIAL
                               vx [km], float, kilometers per sec, X component of spacecraft velocity in CARTESIAN_EARTH_CENTERED_INERTIAL
                               vy [km], float, kilometers per sec, Y component of spacecraft velocity in CARTESIAN_EARTH_CENTERED_INERTIAL
                               vz [km], float, kilometers per sec, Z component of spacecraft velocity in CARTESIAN_EARTH_CENTERED_INERTIAL


        :paramtype out_file_cart: str

        :param out_file_kep: File name with path of the file in which the orbit states in KEPLERIAN_EARTH_CENTERED_INERTIAL are written.
                                If ``None`` the file is not written. The output data format is similar to the data format of the *out_file_cart*
                                file, except the columns headers are as follows:

                                .. csv-table:: KEPLERIAN_EARTH_CENTERED_INERTIAL State data description
                                    :header: Column, Data type, Units, Description
                                    :widths: 10,10,5,40

                               time index, int, , Time-index
                               sma [km], float, kilometers, Orbit semi-major axis dimension.
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

        :return: 0 if success. The results are stored in a csv data-file at the indicated file-path.
        :rtype: int
        

        """
        # form the propcov.Spacecraft object
        earth = propcov.Earth()
        attitude = propcov.NadirPointingAttitude()
        interp = propcov.LagrangeInterpolator()

        spc = propcov.Spacecraft(spacecraft.orbitState.date, spacecraft.orbitState.state, attitude, interp, 0, 0, 0, 1, 2, 3) # TODO: initialization to the correct orientation of spacecraft is not necessary, so ignored for time-being.
        
        if(start_date is None):
            # following code sequence is required to make an *independent/8 copy of the spacecraft.orbitState.date object. 
            start_date = spacecraft.orbitState.date

        # form the propcov.Propagator object
        prop = propcov.Propagator(spc)

        # Prepare output files in which results shall be written
        if out_file_cart:
            cart_file = open(out_file_cart, 'w', newline='')
            cart_writer = csv.writer(cart_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            cart_writer.writerow(["Satellite states are in CARTESIAN_EARTH_CENTERED_INERTIAL (equatorial-plane) frame."])
            cart_writer.writerow(["Epoch [JDUT1] is {}".format(start_date.GetJulianDate())])
            cart_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            cart_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            cart_writer.writerow(['time index','x [km]','y [km]','z [km]','vx [km/s]','vy [km/s]','vz [km/s]'])

        if out_file_kep:
            kep_file = open(out_file_kep, 'w', newline='')
            kep_writer = csv.writer(kep_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            kep_writer.writerow(["Satellite states as KEPLERIAN_EARTH_CENTERED_INERTIAL elements."])
            kep_writer.writerow(["Epoch [JDUT1] is {}".format(start_date.GetJulianDate())])
            kep_writer.writerow(["Step size [s] is {}".format(self.stepSize)])
            kep_writer.writerow(["Mission Duration [Days] is {}".format(duration)])
            kep_writer.writerow(['time index','sma [km]','ecc','inc [deg]','raan [deg]','aop [deg]','ta [deg]'])

        # propagate from to the start date since the date at which the orbit-state is defined
        # could be different from the specified start_date (propagation could be either forwards or backwards)
        prop.Propagate(start_date)
        date = start_date
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

        return 0


