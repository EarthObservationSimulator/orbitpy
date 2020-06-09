"""Unit tests for orbitpy.preprocess module.
"""
'''
   :code:`/temp/` folder contains temporary files produced during the run of the tests below. Some of the parameters are chosen
   randomly for the tests (and compared with corresponding outputs), hence each test is run with different inputs, and expected 
   outputs. 
'''

import unittest
import json
import numpy
import sys, os

import unittest
import json
import numpy
import sys, os, shutil
import subprocess
import numpy as np
import pandas as pd
import random

from orbitpy.preprocess import PreProcess, Satellite, OrbitParameters, InstrumentCoverageParameters
from orbitpy.util import PropagationCoverageParameters, CoverageCalculationsApproach

RE = 6378.137 # [km] radius of Earth

class TestPreProcess(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # Create new directory to store output of all the class functions. 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        out_dir = os.path.join(dir_path, 'temp')
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        super(TestPreProcess, self).__init__(*args, **kwargs)

    def test_walker_orbits_1(self):
        """ Test the calculation of Keplerian elements of the orbits given the Walker Delta constellation
            parameters using partial truth data from SMAD 4th ed, pg. 274, Table 10.26.
        """
        # partial truth data from SMAD 4th ed, Pg. 274, Table 10.26.
        data = {"numberSatellites": 15, "numberPlanes": 5, "relativeSpacing": 1, "alt": 500, "ecc": 0.2, "inc": 54, "aop": 0}
        orbits = PreProcess.walker_orbits(data)
        self.assertEqual(len(orbits), 15) # 15 satellites, hence 15 orbits

        # all orbits have the same inclination, altitude and eccentrivity
        for orb in orbits:
            self.assertEqual(orb.inc, 54)
            self.assertAlmostEqual(orb.sma, RE+500, delta= 5)
            self.assertEqual(orb.ecc, 0.2)
            self.assertEqual(orb.aop, 0)
        
        # 3 satellites per plane, consecutive 3 satellites shall have the same RAAN
        plane1_raan = orbits[0].raan
        self.assertEqual(plane1_raan, orbits[1].raan)
        self.assertEqual(plane1_raan, orbits[2].raan)

        plane2_raan = orbits[3].raan
        self.assertEqual(plane2_raan, orbits[4].raan)
        self.assertEqual(plane2_raan, orbits[5].raan)

        plane3_raan = orbits[6].raan
        self.assertEqual(plane3_raan, orbits[7].raan)
        self.assertEqual(plane3_raan, orbits[8].raan)

        plane4_raan = orbits[9].raan
        self.assertEqual(plane4_raan, orbits[10].raan)
        self.assertEqual(plane4_raan, orbits[11].raan)

        plane5_raan = orbits[12].raan
        self.assertEqual(plane5_raan, orbits[13].raan)
        self.assertEqual(plane5_raan, orbits[14].raan)

        # the raans are uniformly spaced
        raan_spacing = 72
        self.assertEqual(plane2_raan-plane1_raan, raan_spacing)
        self.assertEqual(plane3_raan-plane2_raan, raan_spacing)
        self.assertEqual(plane4_raan-plane3_raan, raan_spacing)
        self.assertEqual(plane5_raan-plane4_raan, raan_spacing)
        self.assertEqual(plane5_raan-plane1_raan, 360 - raan_spacing)

        # check inplane spacing between satellites
        in_plane_spc = 120
        self.assertEqual(orbits[1].ta - orbits[0].ta, in_plane_spc)
        self.assertEqual(orbits[2].ta - orbits[1].ta, in_plane_spc)

        self.assertEqual(orbits[4].ta - orbits[3].ta, in_plane_spc)
        self.assertEqual(orbits[5].ta - orbits[4].ta, in_plane_spc)

        self.assertEqual(orbits[7].ta - orbits[6].ta, in_plane_spc)
        self.assertEqual(orbits[8].ta - orbits[7].ta, in_plane_spc)

        self.assertEqual(orbits[10].ta - orbits[9].ta, in_plane_spc)
        self.assertEqual(orbits[11].ta - orbits[10].ta, in_plane_spc)

        self.assertEqual(orbits[13].ta - orbits[12].ta, in_plane_spc)
        self.assertEqual(orbits[14].ta - orbits[13].ta, in_plane_spc)

        # check phase difference between adjacent planes
        phase_diff = 24
        self.assertEqual(orbits[3].ta - orbits[0].ta, phase_diff)
        self.assertEqual(orbits[6].ta - orbits[3].ta, phase_diff)
        self.assertEqual(orbits[9].ta - orbits[6].ta, phase_diff)
        self.assertEqual(orbits[12].ta - orbits[9].ta, phase_diff)

    def test_walker_orbits_2(self):
        """ Test the calculation of Keplerian elements of the orbits given the Walker Delta constellation
            parameters using fixed inputs and expected outputs. """
        data = {"numberSatellites": 6, "numberPlanes": 3, "relativeSpacing": 2, "alt": 700, "ecc": 0.001, "inc": 98, "aop": 10}
        orbits = PreProcess.walker_orbits(data)

        self.assertEqual(len(orbits), 6) # 6 satellites, hence 24 orbits
        # all orbits have the same inclination, altitude and eccentrivity
        for orb in orbits:
            self.assertEqual(orb.inc, 98)
            self.assertAlmostEqual(orb.sma, RE+700, delta= 5)
            self.assertEqual(orb.ecc, 0.001)
            self.assertEqual(orb.aop, 10)
        
        # 3 satellites per plane, consecutive 3 satellites shall have the same RAAN
        plane1_raan = orbits[0].raan
        self.assertEqual(plane1_raan, orbits[1].raan)

        plane2_raan = orbits[2].raan
        self.assertEqual(plane2_raan, orbits[3].raan)

        plane3_raan = orbits[4].raan
        self.assertEqual(plane3_raan, orbits[5].raan)

        # the raans are uniformly spaced
        raan_spacing = 120
        self.assertEqual(plane2_raan-plane1_raan, raan_spacing)
        self.assertEqual(plane3_raan-plane2_raan, raan_spacing)
        self.assertEqual(plane3_raan-plane1_raan, 360 - raan_spacing)

        # check inplane spacing between satellites
        in_plane_spc = 180
        self.assertEqual(orbits[1].ta - orbits[0].ta, in_plane_spc)
        self.assertEqual(orbits[3].ta - orbits[2].ta, in_plane_spc)
        self.assertEqual(orbits[5].ta - (-360+orbits[4].ta), in_plane_spc)

        # check phase difference between adjacent planes
        phase_diff = 360/6 * 2
        self.assertEqual(orbits[2].ta - orbits[0].ta, phase_diff)
        self.assertEqual(orbits[4].ta - orbits[2].ta, phase_diff)

    def test_compute_time_step(self):
        """ Test that the time-step computed with precomputed values for fixed orbit altitude and sensor Along-Track **FOR** """
        sats = [Satellite(orbit = OrbitParameters(sma = RE+500), ics_for = [InstrumentCoverageParameters(fov_at = 15), InstrumentCoverageParameters(fov_at = 25)])]
        self.assertAlmostEqual(PreProcess.compute_time_step(sats, 1),18.6628, delta = 1)

        sats = [Satellite(orbit = OrbitParameters(sma = RE+710), ics_for = [InstrumentCoverageParameters(fov_at = 15)])]
        self.assertAlmostEqual(PreProcess.compute_time_step(sats, 1), 27.2836, delta = 1)

        # test with multiple satellites. minimum calculate time-step must be chosen.
        sats = [Satellite(orbit = OrbitParameters(sma = RE+710), ics_for = [InstrumentCoverageParameters(fov_at = 15)]),
                Satellite(orbit = OrbitParameters(sma = RE+710), ics_for = [InstrumentCoverageParameters(fov_at = 25), InstrumentCoverageParameters(fov_at = 35)]),
                Satellite(orbit = OrbitParameters(sma = RE+510), ics_for = [InstrumentCoverageParameters(fov_at = 25)]),
                Satellite(orbit = OrbitParameters(sma = RE+510), ics_for = [InstrumentCoverageParameters(fov_at = 15)])]
        x = PreProcess.compute_time_step(sats, 1)        
        sats = [Satellite(orbit = OrbitParameters(sma = RE+510), ics_for = [InstrumentCoverageParameters(fov_at = 15)])]
        y = PreProcess.compute_time_step(sats, 1)
        self.assertAlmostEqual(x, y)

        # test with time-resolution factor
        sats = [Satellite(orbit = OrbitParameters(sma = RE+710), ics_for = [InstrumentCoverageParameters(fov_at = 15)])]
        f = random.random()
        self.assertAlmostEqual(PreProcess.compute_time_step(sats, f), 27.2836*f, delta = 1)

        # test when along-track fov is larger than the horizon angle = 119.64321275051853 deg
        sats = [Satellite(orbit = OrbitParameters(sma = RE+1000), ics_for = [InstrumentCoverageParameters(fov_at = 150)])]
        f = random.random()
        self.assertAlmostEqual(PreProcess.compute_time_step(sats, f), 1057.437400519928*f, delta = 1)

    def test_compute_grid_res(self):
        """Test that the grid-resolution computed with precomputed for fixed values of orbit altitute and a sensor FOV (not the FOR)"""

        # the smallest fov dimension must be chosen
        sats = [Satellite(orbit = OrbitParameters(sma = RE+700), ics_fov = [InstrumentCoverageParameters(fov_at = 10, fov_ct = 20)])]
        self.assertAlmostEqual(PreProcess.compute_grid_res(sats, 1), 1.100773132953890, delta = 0.01)

        # list of satellites, choose smallest grid resolution
        sats = [Satellite(orbit = OrbitParameters(sma = RE+710), ics_fov = [InstrumentCoverageParameters(fov_at = 10, fov_ct = 20)]),
                Satellite(orbit = OrbitParameters(sma = RE+710), ics_fov = [InstrumentCoverageParameters(fov_at = 10, fov_ct = 5), InstrumentCoverageParameters(fov_at = 10, fov_ct = 15)]),
                Satellite(orbit = OrbitParameters(sma = RE+510), ics_fov = [InstrumentCoverageParameters(fov_at = 10, fov_ct = 25)]),
                Satellite(orbit = OrbitParameters(sma = RE+510), ics_fov = [InstrumentCoverageParameters(fov_at = 2, fov_ct = 20)])]
        x = PreProcess.compute_grid_res(sats, 1)
        sats = [Satellite(orbit = OrbitParameters(sma = RE+510), ics_fov = [InstrumentCoverageParameters(fov_at = 2, fov_ct = 20)])]
        y = PreProcess.compute_grid_res(sats, 1)
        self.assertAlmostEqual(x, y)

        # test with grid-resolution factor
        sats = [Satellite(orbit = OrbitParameters(sma = RE+1100), ics_fov = [InstrumentCoverageParameters(fov_at = 25, fov_ct = 25), InstrumentCoverageParameters(fov_at = 30, fov_ct = 35), InstrumentCoverageParameters(fov_at = 25, fov_ct = 55)])]
        f = random.random()
        self.assertAlmostEqual(PreProcess.compute_grid_res(sats, f), 4.4012*f, delta = 0.01)


        # test when along-track fov is larger than the horizon angle = 119.64321275051853 deg
        sats = [Satellite(orbit = OrbitParameters(sma = RE+1000), ics_fov = [InstrumentCoverageParameters(fov_at = 150, fov_ct = 180)])]
        f = random.random()
        self.assertAlmostEqual(PreProcess.compute_grid_res(sats, f), 60.3568*f, delta = 1)





    
