"""Unit tests for orbitpy.mission module.

The following tests are framed to test the different possible ways in which the mission can be framed in the JSON string and called to execute.
In each test, the output is tested with the results as computed on 14 April 2021 (thus representing the "truth" data). 
The truth data is present in the folder ``test_data``.

**Tests:**

* ``test_execute_1``: 1 satellite, no instrument ; propagation only.
* ``test_execute_2``: 1 satellite, 1 instrument ; propagation, grid-coverage, data-metrics calculation.
* ``test_execute_3``: 1 satellite, 1 instrument, 1 ground-station ; propagation, pointing-options coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_execute_4``: 1 satellite, 1 instrument, 1 ground-station ; propagation, pointing-options with grid-coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_execute_5``: 1 satellite, multiple instruments, multiple ground-stations ; propagation, grid-coverage, data-metrics calculation, contact-finder (ground-station only).
* ``test_execute_6``: Multiple satellites from constellation, 1 instrument each ; propagation, pointing-options coverage, data-metrics calculation, contact-finder (inter-satellite only).
* ``test_execute_7``: Multiple satellites from constellation, multiple-instruments per satellite ; propagation, pointing-options with grid-coverage, data-metrics calculation, contact-finder (inter-satellite only).
* ``test_execute_8``: Multiple satellites from list, multiple instruments per satellite, multiple ground-stations ; propagation, grid-coverage, data-metrics calculation, contact-finder (ground-station and inter-satellite).

"""
import json
import os, shutil
import sys
import unittest
import random
import numpy as np
import pandas as pd

from orbitpy.mission import Mission

class TestMission(unittest.TestCase):

    def test_from_dict(self):
        pass

    def test_execute_1(self):
        pass