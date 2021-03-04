""" 
.. module:: propagator

:synopsis: *Module providing classes and functions to handle orbit propagation.*

"""
import numpy as np
from collections import namedtuple

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
        const1 = factory.get_constellation_model('SGP4')

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

    :ivar timeStep: Orbit propagation time-step. Default is False.
    :vartype timeStep: float

    :ivar timeStepResFac: Time-resolution factor used to determine the propagation time-step. (Default value is 0.25.)
    :vartype timeStepResFac: float

    :ivar _id: Unique constellation identifier.
    :vartype _id: str

    """
    def __init__(self, timeStep=None, timeStepResFac=None, _id=None):
        timeStep = float(timeStep) if timeStep is not None and timeStep is not False else False
        timeStepResFac = float(timeStepResFac) if timeStepResFac is not None else 0.25
        super(J2AnalyticalPropagator, self).__init__(_id, "J2 Analytical Propagator")

    @staticmethod
    def from_dict(d):
        return J2AnalyticalPropagator(timeStep = d.get('timeStep', None),
                                      timeStepResFac = d.get('timeStepResFac', None))

    def to_dict(self):
        """ Translate the J2AnalyticalPropagator object to a Python dictionary such that it can be uniquely reconstructed back from the dictionary.
        
        :return: J2AnalyticalPropagator object as python dictionary
        :rtype: dict
        
        """
        pass

    def __repr__(self):
        return "J2AnalyticalPropagator.from_dict({})".format(self.to_dict())

    def __eq__(self, other):
        # Equality test is simple one which compares the data attributes.Note that _id data attribute may be different
        if(isinstance(self, other.__class__)):
            return (self.timeStep == other.timeStep and self.timeStepResFac == other.timeStepResFac) 
                
        else:
            return NotImplemented

    def execute(self, spacecraft, time_interval=None):
        pass

