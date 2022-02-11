# OrbitPy

This package contain set of modules to compute *mission-data* of satellites. It can be used to perform the following calculations:

1. Generation of satellite orbits from constellation specifications.
2. Computation of propagated satellite state (position and velocity) data.
3. Generation of grid points at a (user-defined or auto) angular resolution over region of interest.
4. *Grid Coverage*: Computation of satellite access intervals over given set of grid points (*grid-coverage*) for the length of the mission.

        i. With consideration of satellite/sensor pointing (orientation) directions.
        ii. With consideration of sensor field-of-view (FOV) and field-of-regard (FOR).
5. *Pointing-options Coverage:* Computation of coverage in which set of pointing-options of the satellite/instrument are specified and accessed ground-locations (intersection of the pointing-axis with the Earth's surface) is calculated.
6. *Pointing-options with Grid Coverage*: Grid Coverage calculated for different satellite/instrument orientations.
7. Computation of inter-satellite communication (line-of-sight) time intervals.
8. Computation of ground-station contact time intervals.
9. Computation of satellite eclipse time-intervals.
10. Sensor pixel-array projection to simulated Level-2 satellite imagery.

The `orbitpy` package is built on top of the `propcov`package available in the `propcov` folder. Please refer to the `README.MD` file within the `propcov` folder for description of the respective package.

## Install

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`, `cmake`

It is recommended to carry out the installation in a `conda` environment. Instructions are available in the README file of the InstruPy package.

1.  Install the `instrupy` package (dependency).

2.  Run `make` from the main repo directory.

    All the below dependencies are automatically installed. If any errors are encountered please check that the following dependencies are 
    installed:

    * `numpy`
    * `pandas`
    * `scipy`
    * `sphinx`
    * `sphinx_rtd_theme==0.5.2`

3.  Run `make runtest`. This runs all the tests and can be used to verify the package.

4.  Find the documentation in: `/docs/_build/html/index.html#`

In order to uninstall run `make bare` in the terminal.


---
**NOTE**

The OrbitPy installation automatically installs the package `propcov` which consists of python binding of C++ classes which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection. The python bound C++ objects are implemented in OrbitPy.

The `make runtest` does *not* run the tests of the `propcov` library. Please see the `README.MD` in the `propcov` folder on how to run it's tests.

Documentation of the `propcov` library is available in the Word document `propcov/docs/propcov-cpp.docx`.

---

If using a Windows system, one may consider setting up a virtual-machine with Ubuntu (or similar) OS. VMware Workstation player is available free for non-commercial, personal or home use. VMWare tools may need to be installed separately after the player installation.

[https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html](https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html)

Ubuntu virtual machine images for VMWare and VirtualBox are available here:
[https://www.osboxes.org/ubuntu/](https://www.osboxes.org/ubuntu/)

The present version of OrbitPy has been tested on Ubuntu 18.04.3.

## Directory structure
```
├───docs (sphinx documentation)
├───orbitpy (folder with the source files)
├───propcov (propcov package)
├───TBD (To be determined, temporary folder with old files)
└───tests (folder with test scripts)
    ├───test_coveragecalculator (tests of the coveragecalculator module)
    ├───test_data (reference test checkpoint data)
    ├───util (util folder with supporting scripts for tests)
    └───validation (validation tests)
        ├───GMAT (GMAT reference data)
        └───STK (STK reference data)
            ├───test_coveragecalculator_GridCoverage_with_STK
            └───test_propagation_with_STK
```
## License and Copyright

Copyright 2022 Bay Area Environmental Research Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
## Credits and Acknowledgments

This work has been funded by grants from the National Aeronautics and Space Administration (NASA) Earth Science Technology Office (ESTO) through the Advanced Information Systems Technology (AIST) Program.

OrbitPy uses:

* GMAT2020a `gmatutil` source (https://sourceforge.net/p/gmat/git/ci/GMAT-R2020a/tree/src/gmatutil/)
* Pybind11 (https://pybind11.readthedocs.io/en/stable/basics.html)
* JSON for Modern C++ (https://github.com/nlohmann/json)
* GoogleTest (https://github.com/google/googletest)

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)

## Developer Tasks

### OrbitPy
- [ ] Incorporate artificial image synthesis involving the propcov classes `DiscretizedSensor`, `Projector` and the orbitpy `SensorPixelProjection` module. Add python-tests.
- [ ] Search for ‘Vinay’ and ‘TODO’ over all the files


### Propcov-cpp

- [ ] Explore the orbit interpolation functions.
- [ ] Make a C++ SystemTestDriver
- [ ] Add unconventional sensor FOV geometry shapes GTests for `GMATCustomSensor` and `DSPIPCustomSensor` class.
- [ ] Rename `TATCException` to `PropcovCppException`
- [ ] Add GTests for `Spacecraft`, `CoverageChecker`, `NadirPointingAttitude` and other classes. (There are in total 26 propcov-cpp active classes, of which currently there are GTests ofr 15 of these classes. Some tests in the `tests/tests-cpp/old` folder can be rewritten into the GTest format.)
- [ ] Consider avoiding virtual functions since it has runtime costs associated with it??

### Tips
Errors in the propcov-cpp classes are sometime not visible (i.e. not displayed) when the propcov package is installed. The package installation can happen, but import will not work. In such cases run `make` from propcov-cpp -> tests, and debug any errors.