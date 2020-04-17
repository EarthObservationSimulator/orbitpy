""" 
.. module:: util

:synopsis: *Utilities*

"""
import json
from enum import Enum
from numbers import Number
import numpy
import math
from instrupy.util import *

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

    :ivar cov_grid_fl: Filepath with name to the coverage grid data
    :vartype cov_grid_fl: str

    :ivar sen_fov_geom: FOV geometry of the sensor (perhaps corresponding to a Field of Regard)
    :vartype sen_fov_geom:  str

    :ivar sen_orien: Sensor (perhaps corresponding to a Field of Regard) orientation specification in the following CSV string format: :code:`Euler Seq1, Euler Seq2, Euler Seq3, Euler Angle1, Euler Angle2,, Euler Angle3`. Angles are specifed in degrees.
    :vartype sen_orien:  str

    :ivar sen_clock: Sensor (perhaps corresponding to a Field of Regard) clock angles in degrees in CSV string format.
    :vartype sen_clock: str

    :ivar sen_cone: Sensor (perhaps corresponding to a Field of Regard) cone angles in degrees in CSV string format.
    :vartype sen_cone: str

    :ivar yaw180_flag: Flag indicating if FOR includes the FOV defined by the above clock, cone angles rotated by 180 deg around the satellite yaw axis.
    :vartype yaw180_flag: int

    :ivar step_size: Propagation step size in seconds.
    :vartype step_size: float

    :ivar sat_state_fl: Filepath with name to write the resulting satellite states.
    :vartype sat_state_fl: str

    :ivar sat_acc_fl: Filepath with name to write the resulting satellite access data over the grid of points given in the coverage grid file.
    :vartype sat_acc_fl: str
    
    """
    def __init__(self, sat_id=str(), epoch=str(), sma=float(), ecc=float(), inc=float(), raan=float(), aop=float(), ta=float(), 
                 duration=float(), cov_grid_fl=str(), sen_fov_geom=str(), sen_orien=str(), sen_clock=str(), 
                 sen_cone=str(), yaw180_flag = int(), step_size=float(), sat_state_fl=str(), sat_acc_fl=str()):
        self.sat_id = str(sat_id) 
        self.epoch = str(epoch) 
        self.sma = float(sma) 
        self.ecc = float(ecc) 
        self.inc = float(inc)
        self.raan = float(raan) 
        self.aop = float(aop) 
        self.ta = float(ta) 
        self.duration = float(duration) 
        self.cov_grid_fl = str(cov_grid_fl)  
        self.sen_fov_geom = str(sen_fov_geom) 
        self.sen_orien = str(sen_orien)  
        self.sen_clock = str(sen_clock)  
        self.sen_cone = str(sen_cone)  
        self.yaw180_flag = int(yaw180_flag) 
        self.step_size = float(step_size)
        self.sat_state_fl = str(sat_state_fl) 
        self.sat_acc_fl = str(sat_acc_fl) 

class OrbitPyDefaults(object):
    """ Enumeration of various constants used by package **OrbitPy**. Unless indicated otherwise, the constants 
        are in S.I. units. 
    """
    grid_res_fac = 0.9
    time_res_fac = 0.25

