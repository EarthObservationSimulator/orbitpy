"""Unit tests for orbitpy.contactfinder module.
"""
import unittest
import os, shutil
import sys
import pandas as pd
import csv

from instrupy.util import Entity, Constants, MathUtilityFunctions, GeoUtilityFunctions
import orbitpy.util
from orbitpy.util import Spacecraft, GroundStation
from orbitpy.propagator import J2AnalyticalPropagator, PropagatorFactory
from orbitpy.contactfinder import ContactFinder

class TestContactFinder(unittest.TestCase):

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
        cls.duration = 0.1
        j2_prop = factory.get_propagator({"@type": 'J2 Analytical Propagator', "stepSize": cls.step_size})
        
        # sentinel1A
        cls.spcA = Spacecraft.from_dict({"name":"sentinel1A", "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                         }})
        cls.state_cart_file_sentinel1A = cls.out_dir + '/test_cov_cart_states_sentinel1A.csv'
        j2_prop.execute(spacecraft=cls.spcA, out_file_cart=cls.state_cart_file_sentinel1A, duration=cls.duration)

        # sentinel1B
        cls.spcB = Spacecraft.from_dict({"name":"sentinel1B", "orbitState": {"date":{"dateType":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"stateType": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                         }})
        cls.state_cart_file_sentinel1B = cls.out_dir + '/test_cov_cart_states_sentinel1B.csv'
        j2_prop.execute(spacecraft=cls.spcB, out_file_cart=cls.state_cart_file_sentinel1B, duration=cls.duration)

        # Ground stations
        cls.gs1 = GroundStation.from_dict({"@id":1231, "name": "gs1", "latitude": 85, "longitude": -45, "minElevation":7 })
        cls.gs2 = GroundStation.from_dict({"@id":833, "name": "gs2", "latitude": -88, "longitude": 25, "minElevation":12 })

    def test_execute_data_format(self):

        ########### entityA = Spacecraft, entityB = GroundStation ###########
        ContactFinder.execute(self.spcA, self.gs1, self.out_dir, self.state_cart_file_sentinel1A, None, None, 'INTERVAL', 0)

        out_file = self.out_dir + "/sentinel1A_to_gs1.csv"

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcA._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.gs1._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(list(data.columns)[0], 'start index')
        self.assertEqual(list(data.columns)[1], 'end index')

        ########### entityA = GroundStation, entityB = Spacecraft ###########
        ContactFinder.execute(self.gs2, self.spcB, self.out_dir, None, self.state_cart_file_sentinel1B, None, 'DETAIL', 0)

        out_file = self.out_dir + "/sentinel1B_to_gs2.csv"

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcB._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.gs2._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(list(data.columns)[0], 'time index')
        self.assertEqual(list(data.columns)[1], 'access')
        self.assertEqual(list(data.columns)[2], 'range [km]')
        self.assertEqual(list(data.columns)[3], 'elevation [deg]')

        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic

        ########### entityA = Spacecraft, entityB = Spacecraft. output filename specified ###########
        ContactFinder.execute(self.spcA, self.spcB, self.out_dir, self.state_cart_file_sentinel1A, self.state_cart_file_sentinel1B, 'spcA_to_spcB.csv', 'DETAIL', 10)
        out_file = self.out_dir + "/spcA_to_spcB.csv"

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcA._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.spcB._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(list(data.columns)[0], 'time index')
        self.assertEqual(list(data.columns)[1], 'access')
        self.assertEqual(list(data.columns)[2], 'range [km]')
        
        ########### entityA = GroundStation, entityB = GroundStation ###########
        with self.assertRaises(Exception):
            ContactFinder.execute(self.gs1, self.gs2, self.out_dir, None, None, None, 'INTERVAL', 0)


    def test_execute_ground_stn_contact(self):
        """ Test against GMAT truth data. This validates both the propgation of the satellite and the 
            ground-station contacts.

        GMAT contact data results:
        
        Target: Sentinel1A

        Observer: GroundStation1
        Start Time (UTC)            Stop Time (UTC)               Duration (s)         
        28 Jan 2021 13:48:49.557    28 Jan 2021 13:59:14.101      624.54459040    
        28 Jan 2021 15:26:51.299    28 Jan 2021 15:37:16.655      625.35573284    
        28 Jan 2021 17:04:57.038    28 Jan 2021 17:15:18.740      621.70165640    
        28 Jan 2021 18:43:13.645    28 Jan 2021 18:53:25.040      611.39420030    
        28 Jan 2021 20:21:47.313    28 Jan 2021 20:31:38.523      591.21018058    
        28 Jan 2021 22:00:41.185    28 Jan 2021 22:10:01.340      560.15570710    
        28 Jan 2021 23:39:53.219    28 Jan 2021 23:48:35.914      522.69565989    
        29 Jan 2021 01:19:15.119    29 Jan 2021 01:27:25.251      490.13180420    
        29 Jan 2021 02:58:34.334    29 Jan 2021 03:06:31.195      476.86127324    
        29 Jan 2021 04:37:40.269    29 Jan 2021 04:45:50.273      490.00346269    
        29 Jan 2021 06:16:29.476    29 Jan 2021 06:25:11.971      522.49477208    
        29 Jan 2021 07:55:03.904    29 Jan 2021 08:04:23.818      559.91435135    
        29 Jan 2021 09:33:26.610    29 Jan 2021 09:43:17.587      590.97618844    
        29 Jan 2021 11:11:40.052    29 Jan 2021 11:21:51.289      611.23740769    
        29 Jan 2021 12:49:46.417    29 Jan 2021 13:00:08.032      621.61532363    


        Number of events : 15

        Target: Sentinel1B

        Observer: GroundStation1
        Start Time (UTC)            Stop Time (UTC)               Duration (s)         
        28 Jan 2021 13:49:41.856    28 Jan 2021 13:56:53.997      432.14128754    
        28 Jan 2021 15:28:16.445    28 Jan 2021 15:35:44.990      448.54498333    
        28 Jan 2021 17:06:45.303    28 Jan 2021 17:14:29.554      464.25133171    
        28 Jan 2021 18:45:09.911    28 Jan 2021 18:53:06.500      476.58959962    
        28 Jan 2021 20:23:32.052    28 Jan 2021 20:31:36.413      484.36139004    
        28 Jan 2021 22:01:53.777    28 Jan 2021 22:10:01.183      487.40635630    
        28 Jan 2021 23:40:17.464    28 Jan 2021 23:48:23.305      485.84091989    
        29 Jan 2021 01:18:45.625    29 Jan 2021 01:26:45.213      479.58849077    
        29 Jan 2021 02:57:20.351    29 Jan 2021 03:05:08.974      468.62302835    
        29 Jan 2021 04:36:02.640    29 Jan 2021 04:43:36.350      453.70949119    
        29 Jan 2021 06:14:51.832    29 Jan 2021 06:22:08.886      437.05351007    
        29 Jan 2021 07:53:45.433    29 Jan 2021 08:00:47.785      422.35252488    
        29 Jan 2021 09:32:39.652    29 Jan 2021 09:39:33.497      413.84478367    
        29 Jan 2021 11:11:30.678    29 Jan 2021 11:18:25.042      414.36446942    


        Number of events : 14

        """
        pass

    def test_find_all_pairs(self):
        pass