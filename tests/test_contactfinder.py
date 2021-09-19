"""Unit tests for orbitpy.contactfinder module.
"""
import unittest
import os, shutil
import pandas as pd
import datetime

from orbitpy.util import Spacecraft, GroundStation
from orbitpy.propagator import PropagatorFactory
from orbitpy.contactfinder import ContactFinder, ContactFinderOutputInfo

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
        cls.duration = 1
        j2_prop = factory.get_propagator({"@type": 'J2 ANALYTICAL PROPAGATOR', "stepSize": cls.step_size})
        
        # sentinel1A
        cls.spcA = Spacecraft.from_dict({"name":"sentinel1A", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 273.932} \
                                         }})
        cls.state_cart_file_sentinel1A = cls.out_dir + '/cart_states_sentinel1A.csv'
        j2_prop.execute(spacecraft=cls.spcA, out_file_cart=cls.state_cart_file_sentinel1A, duration=cls.duration)

        # sentinel1B
        cls.spcB = Spacecraft.from_dict({"name":"sentinel1B", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":12, "minute":38, "second":58}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1816, "raan": 38.1151, "aop": 84.837, "ta": 275.3} \
                                         }})
        cls.state_cart_file_sentinel1B = cls.out_dir + '/cart_states_sentinel1B.csv'
        j2_prop.execute(spacecraft=cls.spcB, out_file_cart=cls.state_cart_file_sentinel1B, duration=cls.duration)

        # Test satellite close to sentinel1A
        cls.spcC = Spacecraft.from_dict({"name":"testSat", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 38.3243, "aop": 86.2045, "ta": 250} \
                                         }})
        cls.state_cart_file_spcC = cls.out_dir + '/cart_states_spcC.csv'
        j2_prop.execute(spacecraft=cls.spcC, out_file_cart=cls.state_cart_file_spcC, duration=cls.duration)
        
        # Another test satellite, 90 deg RAAN offset from spcC
        cls.spcD = Spacecraft.from_dict({"name":"testSat", "orbitState": {"date":{"@type":"GREGORIAN_UTC", "year":2021, "month":1, "day":28, "hour":13, "minute":29, "second":2}, \
                                                         "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": 7073.9, "ecc": 0.000133, "inc": 98.1818, "raan": 90+38.3243, "aop": 86.2045, "ta": 250} \
                                         }})
        cls.state_cart_file_spcD = cls.out_dir + '/cart_states_spcD.csv'
        j2_prop.execute(spacecraft=cls.spcD, out_file_cart=cls.state_cart_file_spcD, duration=cls.duration)

        # Ground stations
        cls.gs1 = GroundStation.from_dict({"@id":1231, "name": "gs1", "latitude": 85, "longitude": -45 }) # by default "minimumElevation":7
        cls.gs2 = GroundStation.from_dict({"@id":833, "name": "gs2", "latitude": -88, "longitude": 25, "minimumElevation":12 })

    def test_execute_data_format(self):

        ########### entityA = Spacecraft, entityB = GroundStation, INTERVAL out_type, default output filename ###########
        out_info = ContactFinder.execute(self.spcA, self.gs1, self.out_dir, self.state_cart_file_sentinel1A, None, None, ContactFinder.OutType.INTERVAL, 0)
        out_file = self.out_dir + "/sentinel1A_to_gs1.csv"

        self.assertEqual(out_info, ContactFinderOutputInfo.from_dict({"entityAId": self.spcA._id,
                                                                      "entityBId": self.gs1._id, # note that the entities are swapped
                                                                      "entityAStateCartFile": self.state_cart_file_sentinel1A,
                                                                      "entityBStateCartFile": None, # note here that modeId is None
                                                                      "contactFile": out_file,
                                                                      "outType": ContactFinder.OutType.INTERVAL,
                                                                      "opaqueAtmosHeight": 0,
                                                                      "startDate": 2459243.0618287036,
                                                                      "duration": self.duration, "@id":None}))   

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcA._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.gs1._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) 
        self.assertEqual(list(data.columns)[0], 'start index')
        self.assertEqual(list(data.columns)[1], 'end index')

        ########### entityA = GroundStation, entityB = Spacecraft, DETAIL out_type, default output filename ###########
        out_info = ContactFinder.execute(self.gs2, self.spcB, self.out_dir, None, self.state_cart_file_sentinel1B, None, ContactFinder.OutType.DETAIL, None)
        out_file = self.out_dir + "/sentinel1B_to_gs2.csv"
        self.assertEqual(out_info, ContactFinderOutputInfo.from_dict({"entityAId": self.spcB._id,
                                                                      "entityBId": self.gs2._id, # note that the entities are swapped
                                                                      "entityAStateCartFile": self.state_cart_file_sentinel1B,
                                                                      "entityBStateCartFile": None, # note here that modeId is None
                                                                      "contactFile": out_file,
                                                                      "outType": ContactFinder.OutType.DETAIL,
                                                                      "opaqueAtmosHeight": 0,
                                                                      "startDate": 2459243.027060185,
                                                                      "duration": self.duration, "@id":None}))        

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcB._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.gs2._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.027060185)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) 
        self.assertEqual(list(data.columns)[0], 'time index')
        self.assertEqual(list(data.columns)[1], 'access')
        self.assertEqual(list(data.columns)[2], 'range [km]')
        self.assertEqual(list(data.columns)[3], 'elevation [deg]')

        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic

        ########### entityA = Spacecraft, entityB = Spacecraft. output filename specified ###########
        ContactFinder.execute(self.spcA, self.spcC, self.out_dir, self.state_cart_file_sentinel1A, self.state_cart_file_spcC, 'spcA_to_spcC.csv', ContactFinder.OutType.DETAIL, 10)
        out_file = self.out_dir + "/spcA_to_spcC.csv"

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcA._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.spcC._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) 
        self.assertEqual(list(data.columns)[0], 'time index')
        self.assertEqual(list(data.columns)[1], 'access')
        self.assertEqual(list(data.columns)[2], 'range [km]')
        
        ########### entityA = GroundStation, entityB = GroundStation, should raise Error ###########
        with self.assertRaises(Exception):
            ContactFinder.execute(self.gs1, self.gs2, self.out_dir, None, None, None, ContactFinder.OutType.INTERVAL, 0)

    def test_execute_ground_stn_contact_Sentinel1A_gs1(self):
        """ Test against GMAT truth data. This validates both the propgation of the satellite and the 
            ground-station contacts. The results are approximately equal.
            
        The Sentinel1A satellite was simulated in GMAT with gs1  ground-stations in the ``setUpClass``, to yield the following contact data:

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

        """
        ContactFinder.execute(self.spcA, self.gs1, self.out_dir, self.state_cart_file_sentinel1A, None, None, ContactFinder.OutType.INTERVAL, 0)
        data = pd.read_csv(self.out_dir + "/sentinel1A_to_gs1.csv", skiprows = [0,1,2])
        # Epoch: 2021 Jan 28, 13:29:2
        epoch = datetime.datetime(2021, 1, 28, 13, 29, 2)
        
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 13, 48, 50)-epoch).total_seconds(), data['start index'][0], delta=3)
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 13, 59, 14)-epoch).total_seconds(), data['end index'][0], delta=7)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28,  15,26,51)-epoch).total_seconds(), data['start index'][1], delta=14)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 15,37,17)-epoch).total_seconds(), data['end index'][1], delta=18)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 17,4,57)-epoch).total_seconds(), data['start index'][2], delta=26)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 17,15,19)-epoch).total_seconds(), data['end index'][2], delta=29)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 18,43,14)-epoch).total_seconds(), data['start index'][3], delta=37)    
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 18,53,25)-epoch).total_seconds(), data['end index'][3], delta=41)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 20,21,47)-epoch).total_seconds(), data['start index'][4], delta=49)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 20,31,39)-epoch).total_seconds(), data['end index'][4], delta=52)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 22,0,41)-epoch).total_seconds(), data['start index'][5], delta=61)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 22,10,1)-epoch).total_seconds(), data['end index'][5], delta=64)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 23,39,53)-epoch).total_seconds(), data['start index'][6], delta=73)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 23,48,36)-epoch).total_seconds(), data['end index'][6], delta=75) 

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 1,19,15)-epoch).total_seconds(), data['start index'][7], delta=85)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 1,27,25)-epoch).total_seconds(), data['end index'][7], delta=87)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 2,58,34)-epoch).total_seconds(), data['start index'][8], delta=97)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 3,6,31)-epoch).total_seconds(), data['end index'][8], delta=99)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 4,37,40)-epoch).total_seconds(), data['start index'][9], delta=108)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 4,45,50)-epoch).total_seconds(), data['end index'][9], delta=112)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 6,16,29)-epoch).total_seconds(), data['start index'][10], delta=119)    
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 6,25,12)-epoch).total_seconds(), data['end index'][10], delta=123) 
       
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 7,55,4)-epoch).total_seconds(), data['start index'][11], delta=129)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 8,4,24)-epoch).total_seconds(), data['end index'][11], delta=134)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 9,33,27)-epoch).total_seconds(), data['start index'][12], delta=140)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 9,43,18)-epoch).total_seconds(), data['end index'][12], delta=145)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 11,11,40)-epoch).total_seconds(), data['start index'][13], delta=151) 
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 11,21,51)-epoch).total_seconds(), data['end index'][13], delta=156)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 12,49,46)-epoch).total_seconds(), data['start index'][14], delta=162)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 13,0,8)-epoch).total_seconds(), data['end index'][14], delta=167)
            
    def test_execute_ground_stn_contact_Sentinel1B_gs2(self):
        """ Test against GMAT truth data. This validates both the propgation of the satellite and the 
            ground-station contacts. The results are approximately equal.
            
        The Sentinel1B satellite was simulated in GMAT with gs2 ground-stations in the ``setUpClass``, to yield the following contact data:

        GMAT contact data results:

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
        ContactFinder.execute(self.spcB, self.gs2, self.out_dir, self.state_cart_file_sentinel1B, None, None, ContactFinder.OutType.INTERVAL, 0)
        data = pd.read_csv(self.out_dir + "/sentinel1B_to_gs2.csv", skiprows = [0,1,2])
        # Epoch: 2021 Jan 28, 13:29:2
        epoch = datetime.datetime(2021, 1, 28, 12, 38, 58)
        
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 13, 49, 42)-epoch).total_seconds(), data['start index'][0], delta=11)
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 13, 56, 54)-epoch).total_seconds(), data['end index'][0], delta=14)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 15,28,16)-epoch).total_seconds(), data['start index'][1], delta=22)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 15,35,45)-epoch).total_seconds(), data['end index'][1], delta=25)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 17,6,45)-epoch).total_seconds(), data['start index'][2], delta=34)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 17,14,30)-epoch).total_seconds(), data['end index'][2], delta=36)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 18,45,10)-epoch).total_seconds(), data['start index'][3], delta=45)    
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 18,53,7)-epoch).total_seconds(), data['end index'][3], delta=48)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 20,23,32)-epoch).total_seconds(), data['start index'][4], delta=56)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 20,31,36)-epoch).total_seconds(), data['end index'][4], delta=60)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 22,1,54)-epoch).total_seconds(), data['start index'][5], delta=67)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 22,10,1)-epoch).total_seconds(), data['end index'][5], delta=71)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 23,40,17)-epoch).total_seconds(), data['start index'][6], delta=79)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 28, 23,48,23)-epoch).total_seconds(), data['end index'][6], delta=82) 

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 1,18,46)-epoch).total_seconds(), data['start index'][7], delta=90)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 1,26,45)-epoch).total_seconds(), data['end index'][7], delta=93)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 2,57,20)-epoch).total_seconds(), data['start index'][8], delta=102)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 3,5,9)-epoch).total_seconds(), data['end index'][8], delta=105)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 4,36,3)-epoch).total_seconds(), data['start index'][9], delta=113)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 4,43,36)-epoch).total_seconds(), data['end index'][9], delta=116)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 6,14,52)-epoch).total_seconds(), data['start index'][10], delta=125)    
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 6,22,9)-epoch).total_seconds(), data['end index'][10], delta=128) 

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 7,53,45)-epoch).total_seconds(), data['start index'][11], delta=137)  
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 8,0,47)-epoch).total_seconds(), data['end index'][11], delta=140)  

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 9,32,40)-epoch).total_seconds(), data['start index'][12], delta=148)   
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 9,39,33)-epoch).total_seconds(), data['end index'][12], delta=152)

        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 11,11,31)-epoch).total_seconds(), data['start index'][13], delta=160) 
        self.assertAlmostEqual((datetime.datetime(2021, 1, 29, 11,18,25)-epoch).total_seconds(), data['end index'][13], delta=163)
    
    def test_execute_intersat_contact_precomputed(self):
        """ Test against precomputed data.
        """
        ############### check the spcA to spcC contacts ###############        
        ContactFinder.execute(self.spcA, self.spcC, self.out_dir, self.state_cart_file_sentinel1A, self.state_cart_file_spcC, 'spcA_to_spcC.csv', ContactFinder.OutType.INTERVAL, 10)
        out_file = self.out_dir + "/spcA_to_spcC.csv"   

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcA._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.spcC._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) 
        self.assertEqual(list(data.columns)[0], 'start index')
        self.assertEqual(list(data.columns)[1], 'end index')

        # contact throughout the mission
        self.assertEqual(len(data.index), 1)
        self.assertEqual(data['start index'][0], 0)
        self.assertEqual(data['end index'][0], 86400)

        ############### check the spcC to spcD contacts ###############
        ContactFinder.execute(self.spcC, self.spcD, self.out_dir, self.state_cart_file_spcC, self.state_cart_file_spcD, 'spcC_to_spcD.csv', ContactFinder.OutType.INTERVAL, 10)
        out_file = self.out_dir + "/spcC_to_spcD.csv"

        first_line = pd.read_csv(out_file, nrows=1, header=None).astype(str) # 1st row contains the entity ids
        self.assertEqual(str(first_line[0][0]).split(' ')[5], str(self.spcC._id)) # the ids are converted to string (if not already a string) and compared
        self.assertEqual(str(first_line[0][0]).split(' ')[10], str(self.spcD._id))

        epoch_JDUT1 = pd.read_csv(out_file, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertAlmostEqual(epoch_JDUT1, 2459243.0618287036)

        _step_size = pd.read_csv(out_file, skiprows = [0,1], nrows=1, header=None).astype(str) 
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, 1)

        data = pd.read_csv(out_file, skiprows = [0,1,2]) 
        self.assertEqual(list(data.columns)[0], 'start index')
        self.assertEqual(list(data.columns)[1], 'end index')

        # contact throughout the mission
        self.assertEqual(len(data.index), 29)
        self.assertEqual(data['start index'][0], 1272)
        self.assertEqual(data['end index'][0], 2477)
        self.assertEqual(data['start index'][1], 4235)
        self.assertEqual(data['end index'][1], 5442)
        self.assertEqual(data['start index'][2], 7200)
        self.assertEqual(data['end index'][2], 8405)
        self.assertEqual(data['start index'][3], 10163)
        self.assertEqual(data['end index'][3], 11370)
        self.assertEqual(data['start index'][4], 13128)
        self.assertEqual(data['end index'][4], 14333)
        self.assertEqual(data['start index'][5], 16091)
        self.assertEqual(data['end index'][5], 17299)
        self.assertEqual(data['start index'][6], 19056)
        self.assertEqual(data['end index'][6], 20262)
        self.assertEqual(data['start index'][7], 22020)
        self.assertEqual(data['end index'][7], 23227)
        self.assertEqual(data['start index'][8], 24985)
        self.assertEqual(data['end index'][8], 26190)
        self.assertEqual(data['start index'][9], 27948)
        self.assertEqual(data['end index'][9], 29155)
        self.assertEqual(data['start index'][10], 30913)
        self.assertEqual(data['end index'][10], 32118)
        self.assertEqual(data['start index'][11], 33876)
        self.assertEqual(data['end index'][11], 35083)
        self.assertEqual(data['start index'][12], 36841)
        self.assertEqual(data['end index'][12], 38047)
        self.assertEqual(data['start index'][13], 39804)
        self.assertEqual(data['end index'][13], 41012)
        self.assertEqual(data['start index'][14], 42770)
        self.assertEqual(data['end index'][14], 43975)
        self.assertEqual(data['start index'][15], 45733)
        self.assertEqual(data['end index'][15], 46940)
        self.assertEqual(data['start index'][16], 48698)
        self.assertEqual(data['end index'][16], 49903)
        self.assertEqual(data['start index'][17], 51661)
        self.assertEqual(data['end index'][17], 52868)
        self.assertEqual(data['start index'][18], 54626)
        self.assertEqual(data['end index'][18], 55831)
        self.assertEqual(data['start index'][19], 57589)
        self.assertEqual(data['end index'][19], 58797)
        self.assertEqual(data['start index'][20], 60554)
        self.assertEqual(data['end index'][20], 61760)
        self.assertEqual(data['start index'][21], 63518)
        self.assertEqual(data['end index'][21], 64725)
        self.assertEqual(data['start index'][22], 66483)
        self.assertEqual(data['end index'][22], 67688)
        self.assertEqual(data['start index'][23], 69446)
        self.assertEqual(data['end index'][23], 70653)
        self.assertEqual(data['start index'][24], 72411)
        self.assertEqual(data['end index'][24], 73616)
        self.assertEqual(data['start index'][25], 75374)
        self.assertEqual(data['end index'][25], 76581)
        self.assertEqual(data['start index'][26], 78339)
        self.assertEqual(data['end index'][26], 79545)
        self.assertEqual(data['start index'][27], 81302)
        self.assertEqual(data['end index'][27], 82510)
        self.assertEqual(data['start index'][28], 84268)
        self.assertEqual(data['end index'][28], 85473)

    def test_find_all_pairs(self): #TODO
        pass