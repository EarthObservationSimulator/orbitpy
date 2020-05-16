""" 
.. module:: util

:synopsis: *Collection of utlity functions used by the :code:`orbitpy` package. 
            Note that many other utility functions are imported from the :code:`instrupy` package too.*

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
    
    """
    def __init__(self, sat_id=str(), epoch=str(), sma=float(), ecc=float(), inc=float(), raan=float(), aop=float(), ta=float(), 
                 duration=float(), cov_grid_fl=str(), sen_fov_geom=str(), sen_orien=str(), sen_clock=str(), 
                 sen_cone=str(), yaw180_flag = int(), step_size=float(), sat_state_fl=str(), sat_acc_fl=str(), popts_fl=str()):
        self.sat_id = str(sat_id) if sat_id else None
        self.epoch = str(epoch) if epoch else None
        self.sma = float(sma) if sma else None
        self.ecc = float(ecc) if ecc else None
        self.inc = float(inc) if inc else None
        self.raan = float(raan) if raan else None
        self.aop = float(aop) if aop else None 
        self.ta = float(ta) if ta else None
        self.duration = float(duration) if duration else None
        self.cov_grid_fl = str(cov_grid_fl) if cov_grid_fl else None 
        self.sen_fov_geom = str(sen_fov_geom) if sen_fov_geom else None
        self.sen_orien = str(sen_orien) if sen_orien else None 
        self.sen_clock = str(sen_clock) if sen_clock else None 
        self.sen_cone = str(sen_cone) if sen_cone else None 
        self.yaw180_flag = int(yaw180_flag) if yaw180_flag else None
        self.step_size = float(step_size) if step_size else None
        self.sat_state_fl = str(sat_state_fl) if sat_state_fl else None
        self.sat_acc_fl = str(sat_acc_fl) if sat_acc_fl else None
        self.popts_fl = str(popts_fl) if popts_fl else None

class OrbitPyDefaults(object):
    """ Enumeration of various default values used by package **OrbitPy**.
    """
    grid_res_fac = 0.9
    time_res_fac = 0.25

