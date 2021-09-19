"""Unit tests for orbitpy.contactfinder module.
"""
import unittest
import os, shutil
import sys
import pandas as pd
import csv
import datetime

from instrupy.util import Entity, Constants, MathUtilityFunctions, GeoUtilityFunctions
import orbitpy.util
from orbitpy.util import Spacecraft, GroundStation
from orbitpy.propagator import J2AnalyticalPropagator, PropagatorFactory
from orbitpy.eclipsefinder import EclipseFinder, EclipseFinderOutputInfo

class TestEclipseFinder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(cls.dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

        # make and run the propagator for the spacecraft
        factory = PropagatorFactory()
        cls.step_size = 1
        cls.duration = 1
        j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": cls.step_size})
        
        
        # Jaxel, expected eclipse period = 35% of orbit
        cls.jaxel = Spacecraft.from_dict({"name":"Jaxel", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2018, "month":12, "day":15, "hour":0, "minute":0, "second":0}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 6873.9, "ecc": 0.0001, "inc": 97.24, "raan": 46.10, "aop": 150, "ta": 210} \
                                         }})
        cls.state_cart_file_jaxel = cls.out_dir + '/cart_states_jaxel.csv'
        j2_prop.execute(spacecraft=cls.jaxel, out_file_cart=cls.state_cart_file_jaxel, duration=cls.duration)

        # sentinel1A in dawn-dusk orbit
        cls.sentinel1A = Spacecraft.from_dict({"name":"sentinel1A", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                         }})
        cls.state_cart_file_sentinel1A = cls.out_dir + '/cart_states_sentinel1A.csv'
        j2_prop.execute(spacecraft=cls.sentinel1A, out_file_cart=cls.state_cart_file_sentinel1A, duration=cls.duration)


    def test_execute_data_format(self):

        ########### Jaxel ###########
        # OutType.INTERVAL format, no output filename
        out_info = EclipseFinder.execute(self.jaxel, self.out_dir, self.state_cart_file_jaxel, None, EclipseFinder.OutType.INTERVAL)
        out_file = self.out_dir + "/eclipse.csv"

        self.assertEqual(out_info, EclipseFinderOutputInfo.from_dict({"spacecraftId": self.jaxel._id,
                                                                      "stateCartFile": self.state_cart_file_jaxel,
                                                                      "eclipseFile": out_file,
                                                                      "outType": EclipseFinder.OutType.INTERVAL,
                                                                      "startDate": 2458467.5,
                                                                      "duration": self.duration, "@id":None}))   

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the spacecraft id
        self.assertEqual(str(first_line[0][0]).split(' ')[6], str(self.jaxel._id)) # the id is converted to string (if not already a string) and compared

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2458467.5)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2])
        self.assertEqual(list(data.columns)[0], 'start index')
        self.assertEqual(list(data.columns)[1], 'end index')

        # OutType.DETAIL format, custom output filename        
        out_info = EclipseFinder.execute(self.jaxel, self.out_dir, self.state_cart_file_jaxel, "eclipse_detail.csv", EclipseFinder.OutType.DETAIL)
        out_file = self.out_dir + "/eclipse_detail.csv"

        self.assertEqual(out_info, EclipseFinderOutputInfo.from_dict({"spacecraftId": self.jaxel._id,
                                                                      "stateCartFile": self.state_cart_file_jaxel,
                                                                      "eclipseFile": out_file,
                                                                      "outType": EclipseFinder.OutType.DETAIL,
                                                                      "startDate": 2458467.5,
                                                                      "duration": self.duration, "@id":None}))   

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the spacecraft id
        self.assertEqual(str(first_line[0][0]).split(' ')[6], str(self.jaxel._id)) # the id is converted to string (if not already a string) and compared

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2458467.5)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2])
        self.assertEqual(list(data.columns)[0], 'time index')
        self.assertEqual(list(data.columns)[1], 'eclipse')
    
    def test_execute_Sentinel1A_dawn_dusk(self):
       """ Dawn-dust orbit shall result in no eclipse periods. """
       EclipseFinder.execute(self.sentinel1A, self.out_dir, self.state_cart_file_sentinel1A, None, EclipseFinder.OutType.INTERVAL)
       out_file = self.out_dir + "/eclipse.csv"
       data = pd.read_csv(out_file, skiprows = [0,1,2])
       self.assertEqual(len(data.index), 0)
       self.assertEqual(list(data.columns)[0], 'start index')
       self.assertEqual(list(data.columns)[1], 'end index')
    
    def test_execute_jaxel_precomputed(self):
        """ Compare with precomputed results. The truth data was produced on 5 May 2021."""
        EclipseFinder.execute(self.jaxel, self.out_dir, self.state_cart_file_jaxel, None, EclipseFinder.OutType.INTERVAL)
        out_file = self.out_dir + "/eclipse.csv"
        data = pd.read_csv(out_file, skiprows = [0,1,2])
        self.assertEqual(data['start index'][0], 0)
        self.assertEqual(data['end index'][0], 1359)
        self.assertEqual(data['start index'][1], 5065)
        self.assertEqual(data['end index'][1], 7038)
        self.assertEqual(data['start index'][2], 10744)
        self.assertEqual(data['end index'][2], 12717)
        self.assertEqual(data['start index'][3], 16424)
        self.assertEqual(data['end index'][3], 18397)
        self.assertEqual(data['start index'][4], 22103)
        self.assertEqual(data['end index'][4], 24076)
        self.assertEqual(data['start index'][5], 27782)
        self.assertEqual(data['end index'][5], 29755)
        self.assertEqual(data['start index'][6], 33462)
        self.assertEqual(data['end index'][6], 35434)
        self.assertEqual(data['start index'][7], 39141)
        self.assertEqual(data['end index'][7], 41114)
        self.assertEqual(data['start index'][8], 44820)
        self.assertEqual(data['end index'][8], 46793)
        self.assertEqual(data['start index'][9], 50500)
        self.assertEqual(data['end index'][9], 52472)
        self.assertEqual(data['start index'][10], 56179)
        self.assertEqual(data['end index'][10], 58151)
        self.assertEqual(data['start index'][11], 61858)
        self.assertEqual(data['end index'][11], 63831)
        self.assertEqual(data['start index'][12], 67538)
        self.assertEqual(data['end index'][12], 69510)
        self.assertEqual(data['start index'][13], 73217)
        self.assertEqual(data['end index'][13], 75189)
        self.assertEqual(data['start index'][14], 78896)
        self.assertEqual(data['end index'][14], 80868)
        self.assertEqual(data['start index'][15], 84576)
        self.assertEqual(data['end index'][15], 86400)



        