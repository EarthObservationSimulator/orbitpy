"""Unit tests for orbitpy.propagator module.
"""
import json
import os, shutil
import sys
import unittest
import random
import numpy as np
import pandas as pd

from orbitpy.util import OrbitState, Spacecraft
from orbitpy.propagator import PropagatorFactory, PropagatorOutputInfo, J2AnalyticalPropagator, SGP4Propagator
import orbitpy.propagator
from instrupy import Instrument

RE = 6378.137 # radius of Earth in kilometers
class TestPropagatorModuleFunction(unittest.TestCase):

    def test_compute_time_step(self):
        """ Test that the time-step computed with precomputed values for fixed orbit altitude and sensor Along-Track **FOR** 
        
        .. todo:: Include tests with instrument maneuverability.

        """
        
        # FOR = FOV for the below cases since default "FIXED" manueverability is used. The crosstrack FOV does not influence the results.
        instru1 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 15, "angleWidth": 0.01}}')
        instru2 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 25, "angleWidth": 0.01}}')
        instru3 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 35, "angleWidth": 0.01}}')
        instru4 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "Rectangular", "angleHeight": 150, "angleWidth": 0.01}}')
        instru5 = Instrument.from_json('{"@type": "Basic Sensor","fieldOfViewGeometry": {"shape": "CIRCULAR", "diameter": 136.03734762889385}}')

        orbit1 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+500, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit2 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+710, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit3 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+510, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
        orbit4 = OrbitState.from_dict({"date":{"@type":"JULIAN_DATE_UT1", "jd":2459270.75},"state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": RE+1000, "ecc": 0.001, "inc": 0, "raan": 0, "aop": 0, "ta": 0}})
       
        # single satellite, multiple instruments
        sats = [Spacecraft(orbitState=orbit1, instrument=[instru1, instru2])]
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, 1), 18.6628, places=4)

        # single satellite, single instrument
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1])]
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, 1), 27.7324, places=4)

        # test with multiple satellites.
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1]),
                Spacecraft(orbitState=orbit2, instrument=[instru1, instru2, instru3]),
                Spacecraft(orbitState=orbit3, instrument=[instru2]),
                Spacecraft(orbitState=orbit3, instrument=[instru1])]
        x = orbitpy.propagator.compute_time_step(sats, 1)        

        sats = [Spacecraft(orbitState=orbit3, instrument=[instru1])]
        y = orbitpy.propagator.compute_time_step(sats, 1)
        self.assertAlmostEqual(x, y)

        # test with non-unitary time-resolution factor
        sats = [Spacecraft(orbitState=orbit2, instrument=[instru1])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, f), 27.7324*f, places=4)

        # test when along-track fov is larger than the horizon angle = 119.64321275051853 deg
        sats = [Spacecraft(orbitState=orbit4, instrument=[instru4])]
        f = random.random()
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats, f), 1057.437400519928*f)

        # result with satellite, no instruments is same as satellite with instrument of fov=horizon angle
        sats1 = [Spacecraft(orbitState=orbit1)] 
        sats2 = [Spacecraft(orbitState=orbit1, instrument=[instru5])]
        self.assertAlmostEqual(orbitpy.propagator.compute_time_step(sats1, 0.25), orbitpy.propagator.compute_time_step(sats2, 0.25))  # horizon angle = 136.03734762889385

class TestPropagatorFactory(unittest.TestCase):
  
    class DummyNewPropagator:
        def __init__(self, *args, **kwargs):
            pass
            
        def from_dict(self):
            return TestPropagatorFactory.DummyNewPropagator()

    def test___init__(self):
        factory = PropagatorFactory()

        # test the built-in propagators are registered
        self.assertIn('J2 ANALYTICAL PROPAGATOR', factory._creators)
        self.assertEqual(factory._creators['J2 ANALYTICAL PROPAGATOR'], J2AnalyticalPropagator)

    def test_register_propagator(self):
        factory = PropagatorFactory()
        factory.register_propagator('New Propagator', TestPropagatorFactory.DummyNewPropagator)
        self.assertIn('New Propagator', factory._creators)
        self.assertEqual(factory._creators['New Propagator'], TestPropagatorFactory.DummyNewPropagator)
        # test the built-in propagators remain registered after registration of new propagator
        self.assertIn('J2 ANALYTICAL PROPAGATOR', factory._creators)
        self.assertEqual(factory._creators['J2 ANALYTICAL PROPAGATOR'], J2AnalyticalPropagator)

    def test_get_propagator(self):
        
        factory = PropagatorFactory()
        # register dummy propagator
        factory.register_propagator('New Propagator', TestPropagatorFactory.DummyNewPropagator)
        
        # test the propgator model classes can be obtained depending on the input specifications
        # J2 ANALYTICAL PROPAGATOR
        specs = {"@type": 'J2 ANALYTICAL PROPAGATOR'} # in practice additional propagator specs shall be present in the dictionary
        j2_prop = factory.get_propagator(specs)
        self.assertIsInstance(j2_prop, J2AnalyticalPropagator)

        # SGP4 PROPAGATOR
        specs = {"@type": 'SGP4 PROPAGATOR'} # in practice additional propagator specs shall be present in the dictionary
        sgp4_prop = factory.get_propagator(specs)
        self.assertIsInstance(sgp4_prop, SGP4Propagator)

        # DummyNewPropagator
        specs = {"@type": 'New Propagator'} # in practice additional propagator specs shall be present in the dictionary
        new_prop = factory.get_propagator(specs)
        self.assertIsInstance(new_prop, TestPropagatorFactory.DummyNewPropagator)


class TestSGP4Propagator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)
    
    def setUp(self):
        # setup a simple random propagation test case
        factory = PropagatorFactory()
        self.step_size = 0.5 + random.random()
        specs = {"@type": 'SGP4 PROPAGATOR', 'stepSize':self.step_size } 
        self.sgp4_prop = factory.get_propagator(specs)

        self.duration=random.random()
        self.sma = RE+random.uniform(350,850)
        
        # circular orbit
        orbit = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                                       "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": self.sma, 
                                                "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                                                "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                                       })

        self.spacecraft = Spacecraft(orbitState=orbit)
        self.out_file_cart = self.out_dir+'/test_prop_cart.csv'
        self.out_file_kep = self.out_dir+'/test_prop_kep.csv'

        # run the propagator
        out_info = self.sgp4_prop.execute(self.spacecraft, None, self.out_file_cart, self.out_file_kep, self.duration)

        # test the output info object
        '''
        self.assertEqual(out_info, PropagatorOutputInfo.from_dict({'propagatorType': 'SGP4 PROPAGATOR', 
                                                              'spacecraftId': self.spacecraft._id, 
                                                              'stateCartFile': self.out_file_cart,
                                                              'stateKeplerianFile': self.out_file_kep ,
                                                              'startDate': self.spacecraft.orbitState.get_julian_date() ,
                                                              'duration': self.duration }))
        '''
    
    def test_from_json(self):       

        o = SGP4Propagator.from_dict({"@type": "SGP4 PROPAGATOR", "stepSize": 0.5})
        self.assertIsInstance(o, SGP4Propagator)
        self.assertEqual(o.stepSize, 0.5)
        self.assertIsNone(o._id)

        o = SGP4Propagator.from_dict({"@type": "SGP4 PROPAGATOR", "stepSize": 1, "@id":"abc"})
        self.assertIsInstance(o, SGP4Propagator)
        self.assertEqual(o.stepSize, 1)
        self.assertEqual(o._id, "abc")

        o = SGP4Propagator.from_dict({"@type": "SGP4 PROPAGATOR", "stepSize": 1.5, "@id":123})
        self.assertIsInstance(o, SGP4Propagator)
        self.assertEqual(o.stepSize, 1.5)
        self.assertEqual(o._id, 123)

        # test default step size
        o = SGP4Propagator.from_dict({"@type": "SGP4 PROPAGATOR"})
        self.assertIsInstance(o, SGP4Propagator)
        self.assertIsNone(o.stepSize)
        self.assertIsNone(o._id)
    
    def test_execute_1(self):
        ############# Test the output file formats #############
        
        ############# test the data format in the Cartesian state output file #############
        epoch_JDUT1 = pd.read_csv(self.out_file_cart, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.00000)

        _step_size = pd.read_csv(self.out_file_cart, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(self.out_file_cart, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(self.out_file_cart, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"x [km]")
        self.assertEqual(column_headers.iloc[0][2],"y [km]")
        self.assertEqual(column_headers.iloc[0][3],"z [km]")
        self.assertEqual(column_headers.iloc[0][4],"vx [km/s]")
        self.assertEqual(column_headers.iloc[0][5],"vy [km/s]")
        self.assertEqual(column_headers.iloc[0][6],"vz [km/s]")
        
        data = pd.read_csv(self.out_file_cart, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(data["time index"].iloc[0],0)
        self.assertEqual(data["time index"].iloc[1],1)
        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic

        ############# test the data format in the Keplerian state output file #############
        epoch_JDUT1 = pd.read_csv(self.out_file_kep, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.00000)

        _step_size = pd.read_csv(self.out_file_kep, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(self.out_file_kep, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(self.out_file_kep, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"sma [km]")
        self.assertEqual(column_headers.iloc[0][2],"ecc")
        self.assertEqual(column_headers.iloc[0][3],"inc [deg]")
        self.assertEqual(column_headers.iloc[0][4],"raan [deg]")
        self.assertEqual(column_headers.iloc[0][5],"aop [deg]")
        self.assertEqual(column_headers.iloc[0][6],"ta [deg]")

        data = pd.read_csv(self.out_file_kep, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(data["time index"].iloc[0],0)
        self.assertEqual(data["time index"].iloc[1],1)
        # check that the number of time-steps is reasonable
        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic
    
'''
class TestJ2AnalyticalPropagator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create new working directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.out_dir = os.path.join(dir_path, 'temp')
        if os.path.exists(cls.out_dir):
            shutil.rmtree(cls.out_dir)
        os.makedirs(cls.out_dir)

    def setUp(self):
        # setup a simple random propagation test case
        factory = PropagatorFactory()
        self.step_size = 0.5 + random.random()
        specs = {"@type": 'J2 ANALYTICAL PROPAGATOR', 'stepSize':self.step_size } 
        self.j2_prop = factory.get_propagator(specs)

        self.duration=random.random()
        self.sma = RE+random.uniform(350,850)
        
        # circular orbit
        orbit = OrbitState.from_dict({"date":{"@type":"GREGORIAN_UT1", "year":2018, "month":5, "day":26, "hour":12, "minute":0, "second":0}, # JD: 2458265.00000
                                       "state":{"@type": "KEPLERIAN_EARTH_CENTERED_INERTIAL", "sma": self.sma, 
                                                "ecc": 0, "inc": random.uniform(0,180), "raan": random.uniform(0,360), 
                                                "aop": random.uniform(0,360), "ta": random.uniform(0,360)}
                                       })

        self.spacecraft = Spacecraft(orbitState=orbit)
        self.out_file_cart = self.out_dir+'/test_prop_cart.csv'
        self.out_file_kep = self.out_dir+'/test_prop_kep.csv'

        # run the propagator
        out_info = self.j2_prop.execute(self.spacecraft, None, self.out_file_cart, self.out_file_kep, self.duration)

        # test the output info object
        
        self.assertEqual(out_info, PropagatorOutputInfo.from_dict({'propagatorType': 'J2 ANALYTICAL PROPAGATOR', 
                                                              'spacecraftId': self.spacecraft._id, 
                                                              'stateCartFile': self.out_file_cart,
                                                              'stateKeplerianFile': self.out_file_kep ,
                                                              'startDate': self.spacecraft.orbitState.get_julian_date() ,
                                                              'duration': self.duration }))

    def test_from_json(self):       

        o = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 0.5})
        self.assertIsInstance(o, J2AnalyticalPropagator)
        self.assertEqual(o.stepSize, 0.5)
        self.assertIsNone(o._id)

        o = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1, "@id":"abc"})
        self.assertIsInstance(o, J2AnalyticalPropagator)
        self.assertEqual(o.stepSize, 1)
        self.assertEqual(o._id, "abc")

        o = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR", "stepSize": 1.5, "@id":123})
        self.assertIsInstance(o, J2AnalyticalPropagator)
        self.assertEqual(o.stepSize, 1.5)
        self.assertEqual(o._id, 123)

        # test default step size
        o = J2AnalyticalPropagator.from_dict({"@type": "J2 ANALYTICAL PROPAGATOR"})
        self.assertIsInstance(o, J2AnalyticalPropagator)
        self.assertIsNone(o.stepSize)
        self.assertIsNone(o._id)

    def test_to_dict(self):
        pass

    def test___eq__(self):
        pass

    def test_execute_1(self):
        ############# Test the output file formats #############
        
        ############# test the data format in the Cartesian state output file #############
        epoch_JDUT1 = pd.read_csv(self.out_file_cart, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.00000)

        _step_size = pd.read_csv(self.out_file_cart, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(self.out_file_cart, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(self.out_file_cart, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"x [km]")
        self.assertEqual(column_headers.iloc[0][2],"y [km]")
        self.assertEqual(column_headers.iloc[0][3],"z [km]")
        self.assertEqual(column_headers.iloc[0][4],"vx [km/s]")
        self.assertEqual(column_headers.iloc[0][5],"vy [km/s]")
        self.assertEqual(column_headers.iloc[0][6],"vz [km/s]")
        
        data = pd.read_csv(self.out_file_cart, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(data["time index"].iloc[0],0)
        self.assertEqual(data["time index"].iloc[1],1)
        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic

        ############# test the data format in the Keplerian state output file #############
        epoch_JDUT1 = pd.read_csv(self.out_file_kep, skiprows = [0], nrows=1, header=None).astype(str) # 2nd row contains the epoch
        epoch_JDUT1 = float(epoch_JDUT1[0][0].split()[3])
        self.assertEqual(epoch_JDUT1, 2458265.00000)

        _step_size = pd.read_csv(self.out_file_kep, skiprows = [0,1], nrows=1, header=None).astype(str) # 3rd row contains the stepsize
        _step_size = float(_step_size[0][0].split()[4])
        self.assertAlmostEqual(_step_size, self.step_size)

        _duration = pd.read_csv(self.out_file_kep, skiprows = [0,1,2], nrows=1, header=None).astype(str) # 4th row contains the mission duration
        _duration = float(_duration[0][0].split()[4])
        self.assertAlmostEqual(_duration, self.duration)

        column_headers = pd.read_csv(self.out_file_kep, skiprows = [0,1,2,3], nrows=1, header=None).astype(str) # 5th row contains the columns headers
        self.assertEqual(column_headers.iloc[0][0],"time index")
        self.assertEqual(column_headers.iloc[0][1],"sma [km]")
        self.assertEqual(column_headers.iloc[0][2],"ecc")
        self.assertEqual(column_headers.iloc[0][3],"inc [deg]")
        self.assertEqual(column_headers.iloc[0][4],"raan [deg]")
        self.assertEqual(column_headers.iloc[0][5],"aop [deg]")
        self.assertEqual(column_headers.iloc[0][6],"ta [deg]")

        data = pd.read_csv(self.out_file_kep, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        self.assertEqual(data["time index"].iloc[0],0)
        self.assertEqual(data["time index"].iloc[1],1)
        # check that the number of time-steps is reasonable
        self.assertAlmostEqual((data["time index"].iloc[-1] + 1)*_step_size, self.duration*86400, delta=self.step_size) # almost equal, probably due to errors introduced by floating-point arithmetic
    
    def test_execute_2(self):
        """ Test the satellite altitude, orbital time-period, speed.""" 
        cart_data = pd.read_csv(self.out_file_cart, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        cart_ds = cart_data.sample().reset_index() # randomly select a row (time) altitude should be same since circular orbit

        kep_data = pd.read_csv(self.out_file_kep, skiprows = [0,1,2,3]) # 5th row header, 6th row onwards contains the data
        kep_ds = kep_data.sample().reset_index() # randomly select a row (time) altitude should be same since circular orbit

        ##### altitude test ##### 
        alt_in =  self.sma - RE
        # cartesian output
        cart_alt_out = np.linalg.norm([cart_ds["x [km]"], cart_ds["y [km]"], cart_ds["z [km]"]]) - RE 
        self.assertAlmostEqual(alt_in, cart_alt_out, delta=20) # 20km difference possible?
        # keplerian output
        kep_alt_out = kep_ds['sma [km]'].values  - RE 
        self.assertAlmostEqual(kep_alt_out, alt_in, delta=20)

        ##### orbital speed test ##### 
        orb_sp_in = np.sqrt(3.9860044188e14/(self.sma*1e3)) 
        # cartesian output
        cart_orb_sp_out = np.linalg.norm([cart_ds["vx [km/s]"], cart_ds["vy [km/s]"], cart_ds["vz [km/s]"]])
        self.assertAlmostEqual(cart_orb_sp_out, orb_sp_in*1e-3, delta=0.2) # 0.2km/s difference possible?
        
    def test_execute_3(self):
        """ Check prograde and retrograd -icity of the orbits."""
        pass

class TestPropagatorOutputInfo(unittest.TestCase): #TODO
    pass

'''