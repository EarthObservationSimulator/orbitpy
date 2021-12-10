# OrbitPy

This package contain set of modules to compute *mission-data* of satellites. It can be used to perform the following calculations:

1. Generation of satellite orbits from constellation specifications.
2. Computation of propagated satellite state (position and velocity) data.
3. Generation of grid-of-points at a (user-defined or auto) angular resolution over region of interest.
4. *Grid Coverage*: Computation of satellite access intervals over given set of grid points (*grid-coverage*) for the length of the mission.
        i. Consideration of sensor pointing directions.
        ii. Consideration of sensor field-of-view (FOV) and field-of-regard (FOR).
5. *Pointing-options Coverage:* Computation of coverage in which set of pointing-options of the instrument are specified and accessed ground-locations are calculated.
6. *Pointing-options with Grid Coverage*.
7. Computation of inter-satellite communication (line-of-sight) time intervals.
8. Computation of ground-station contact time intervals.
9. Computation of satellite eclipse time-intervals.
10. Sensor pixel-array projection.

The `orbitpy` package is built on top of the `propcov`package available in the `propcov` folder. Please refer to the README.MD file within the `propcov` folder for description of the respective package.

## Install

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`

1. Make sure the `instrupy` package (dependency) has been installed.
2. Run `make` from the main git directory.
3. Run `make runtest`. This runs all the tests and can be used to verify the package.

Find the documentation in: `/docs/_build/html/index.html#`

Note that this installation also automatically installs the package `propcov` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

In order to uninstall run `make bare` in the terminal.

Ask `make runtest` to also run the C++ tests (google tests) of the `propcov` library.

---
**NOTE**

The `make runtest` does *not* run the tests of the `propcov` library. Please see the `README.MD` in the `propcov` folder on how to run it's tests.

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

Copyright 2021 Bay Area Environmental Research Institute

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