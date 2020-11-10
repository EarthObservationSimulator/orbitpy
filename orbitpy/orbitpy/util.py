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

class CoverageCalculationsApproach(EnumEntity):
    """ Enumeration of recognized approaches to calculation coverage."""
    PNTOPTS_WITH_GRIDPNTS = "PNTOPTS_WITH_GRIDPNTS"
    GRIDPNTS = "GRIDPNTS"
    PNTOPTS = "PNTOPTS"
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
        self.sen_fov_geom = str(sen_fov_geom) 
        self.sen_orien = str(sen_orien) 
        self.sen_clock = str(sen_clock) 
        self.sen_cone = str(sen_cone) 
        self.purely_sidelook = bool(purely_sidelook) 
        self.yaw180_flag = int(yaw180_flag) 
        self.step_size = float(step_size) 
        self.sat_state_fl = str(sat_state_fl) 
        self.sat_acc_fl = str(sat_acc_fl) 
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


