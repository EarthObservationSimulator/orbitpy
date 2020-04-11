""" 
.. module:: util

:synopsis: *Utilities*

"""
import json
from enum import Enum
from numbers import Number
import numpy
import math

class FileUtilityFunctions:

    @staticmethod
    def from_json(json_doc):
        """Parses a dictionary from a JSON-formatted string, dictionary, or file."""
        # convert json string or file to dictionary (if necessary)
        if isinstance(json_doc, str):
            json_doc = json.loads(json_doc)
        elif hasattr(json_doc, 'read'):
            json_doc = json.load(json_doc)
        # if pre-formatted, return directly
        if (json_doc is None or isinstance(json_doc, Number)):
            return json_doc
        # if list, recursively parse each element and return mapped list
        if isinstance(json_doc, list):
            return map(lambda e: FileUtilityFunctions.from_json(e), json_doc)
        # otherwise use class method to initialize from normalized dictionary
        return json_doc 

class EnumEntity(str, Enum):
    """Enumeration of recognized types."""

    @classmethod
    def get(cls, key):
        """Attempts to parse a type from a string, otherwise returns None."""
        if isinstance(key, cls):
            return key
        elif isinstance(key, list):
            return list(map(lambda e: cls.get(e), key))
        else:
            try: return cls(key.upper())
            except: return None


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

class Constants(object):
    """ Enumeration of various constants used by package **OrbitPy**. Unless indicated otherwise, the constants 
        are in S.I. units. 
    """
    radiusOfEarthInKM = 6378.137 # Nominal equatorial radius of Earth [km]
    grid_res_fac = 0.9
    GMe = 3.986004418e14*1e-9 # product of Gravitaional constant and Mass of Earth [km^3 s^-2]
    time_res_fac = 0.25


class MathUtilityFunctions:
    """ Class aggregating various mathematical computation functions used in the OrbitPy package. """

    @staticmethod
    def latlonalt_To_Cartesian(lat_deg, lon_deg, alt_km):
        """ *LLA to ECEF vector considering Earth as sphere with a radius equal to the equatorial radius.*

            :param lat_deg: [deg] geocentric latitude 
            :paramtype: float

            :param lon_deg: [deg] geocentric longitude
            :paramtype lon_deg: float

            :param alt_km: [km] Altitude
            :paramtype alt_km: float

            :return: [km] Position vector in ECEF
            :rtype: float, list
        
        """
        lat = numpy.deg2rad(lat_deg)
        if lon_deg<0:
            lon_deg = 360 + lon_deg
        lon = numpy.deg2rad(lon_deg)
        R = Constants.radiusOfEarthInKM + alt_km
        position_vector_km = numpy.array( [(numpy.cos(lon) * numpy.cos(lat)) * R,
                                (numpy.sin(lon) * numpy.cos(lat)) * R,
                                    numpy.sin(lat) * R] )     

        return position_vector_km
    
    @staticmethod
    def geo2eci(gcoord, JDtime):
        """ *Convert geographic spherical coordinates to Earth-centered inertial coords.*    
             
        :param gcoord: geographic coordinates of point [latitude [deg] ,longitude [deg], altitude]. Geographic coordinates assume the Earth is a perfect sphere, with radius 
                     equal to its equatorial radius.
        :paramtype  gcoord: list, float

        :param JDtime: Julian Day time.
        :paramtype JDtime: float

        :return: A 3-element array of ECI [X,Y,Z] coordinates in same units as that of the supplied altitude. The TOD epoch is the supplied JDtime.                           
        :rtype: float

        .. seealso:: 
            * :mod:`JD2GMST`
            * `IDL Astronomy Users Library <https://idlastro.gsfc.nasa.gov/ftp/pro/astro/geo2eci.pro>`_
        
        EXAMPLES:

        .. code-block:: python

               ECIcoord = geo2eci([0,0,0], 2452343.38982663)
               print(ECIcoord)
              -3902.9606       5044.5548       0.0000000
        
        (The above is the ECI coordinates of the intersection of the equator and
        Greenwich's meridian on 2002/03/09 21:21:21.021)            
        
        """
        lat = numpy.deg2rad(gcoord[0])
        lon = numpy.deg2rad(gcoord[1])
        alt = gcoord[2]
               
        gst = MathUtilityFunctions.JD2GMST(JDtime)
        
        angle_sid=gst*2.0*numpy.pi/24.0 # sidereal angle

        theta = lon + angle_sid # azimuth
        r = ( alt + Constants.radiusOfEarthInKM ) * numpy.cos(lat)
        X = r*numpy.cos(theta)
        Y = r*numpy.sin(theta)
        Z = ( alt + Constants.radiusOfEarthInKM )*numpy.sin(lat)
                
        return [X,Y,Z]
        
   
    @staticmethod
    def normalize(v):
        """ Normalize a input vector.

            :param v: Input vector
            :paramtype v: list, float

            :return: Normalized vector
            :rtype: :obj:`numpy.array`, float
        
        """
        v = numpy.array(v)
        norm = numpy.linalg.norm(v)
        if(norm == 0):
            raise Exception("Encountered division by zero in vector normalization function.")
        return v / norm

            
        
    
    @staticmethod
    def angle_between_vectors(vector1, vector2):
        """ Find angle between two input vectors in radians. Use the dot-product relationship to obtain the angle.
        
            :param vector1: Input vector 1
            :paramtype vector1: list, float

            :param vector2: Input vector 2
            :paramtype vector2: list, float

            :return: [rad] Angle between the vectors, calculated using dot-product relationship.
            :rtype: float

        """
        unit_vec1 = MathUtilityFunctions.normalize(vector1)
        unit_vec2 = MathUtilityFunctions.normalize(vector2)
        return numpy.arccos(numpy.dot(unit_vec1, unit_vec2))


    @staticmethod
    def JD2GMST(JD):
        """ Convert Julian Day to Greenwich Mean Sidereal Time.
            Reference `USNO NAVY <https://aa.usno.navy.mil/faq/docs/GAST.php>`_

            :param JD: Julian Date UT1
            :paramtype JD: float

            :return: [hrs] Greenwich Mean Sidereal Time at the corresponding JD
            :rtype: float

        """
        _x = round(JD) + 0.5
        if(_x > JD):
            JD0 = round(JD) - 0.5
        else:
            JD0 = round(JD) + 0.5
      
        D = JD - 2451545.0
        D0 = JD0 - 2451545.0
        H = (JD - JD0)*24.0
        T = D / 36525.0

        # Greenwich mean sidereal time in hours
        GMST = 6.697374558 + 0.06570982441908*D0 + 1.00273790935*H + 0.000026*T**2
        
        GMST = GMST % 24

        return GMST
   
    @staticmethod
    def checkLOSavailability(object1_pos, object2_pos, obstacle_radius):
        """ Determine if line-of-sight exists
             Algorithm from Page 198 Fundamental of Astrodynamics and Applications, David A.Vallado is used. The first algorithm
             described is used.

             :param object1_pos: Object 1 position vector
             :paramtype object1_pos: float

             :param object2_pos: Object2 position vector
             :paramtype object2_pos: float

             :param obstacle_radius: Radius of spherical obstacle
             :paramtype obstacle_radius: float

             :return: T/F flag indicating availability of line of sight from object1 to object2.
             :rtype: bool

             .. note: The frame of reference for describing the object positions must be centered at spherical obstacle.
        
        """        
        obstacle1_unitVec = MathUtilityFunctions.normalize(object1_pos)
        obstacle2_unitVec = MathUtilityFunctions.normalize(object2_pos)  

        # This condition tends to give a numerical error, so solve for it independently.
        eps = 0.001
        x = numpy.dot(obstacle1_unitVec, obstacle2_unitVec)
        
        if((x > -1-eps) and (x < -1+eps)):
            return False
        else:
            theta  = numpy.arccos(x)
                
        obj1_r = numpy.linalg.norm(object1_pos)
        if(obj1_r - obstacle_radius > 1e-5):
            theta1 = numpy.arccos(obstacle_radius/obj1_r)
        elif(abs(obj1_r - obstacle_radius) < 1e-5):
            theta1 =  0.0
        else:
            return False # object1 is inside the obstacle

        obj2_r = numpy.linalg.norm(object2_pos)
        if(obj2_r - obstacle_radius > 1e-5):
            theta2 = numpy.arccos(obstacle_radius/obj2_r)
        elif(abs(obj2_r - obstacle_radius) < 1e-5):
            theta2 =  0.0
        else:
            return False # object2 is inside the obstacle
                
        if (theta1 + theta2 < theta):
            return False
        else:
            return True     
