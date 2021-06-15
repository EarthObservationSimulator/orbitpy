# OrbitPy

This package contain set of modules to compute *mission-data* of satellites. It performs the following functions:

1. Generation of satellite orbits from constellation specifications.
2. Computation of propagated satellite state (position and velocity) data.
3. Generation of grid-of-points at a (user-defined or auto) angular resolution over region of interest.
4. Computation of satellite access intervals over given set of grid points (*grid-coverage*) for the length of the mission.
     i. Consideration of sensor pointing directions.
    ii. Consideration of sensor field-of-view (FOV) and field-of-regard (FOR).
5. Computation of *pointing-options* coverage in which set of pointing-options of the instrument are specified and accessed ground-locations are calculated.
6. Computation of *pointing-options with grid coverage*.
7. Computation of inter-satellite communication (line-of-sight) time intervals.
8. Computation of ground-station contact time intervals.
9. Computation of satellite eclipse time-intervals.
10. Sensor pixel-array projection.

## Install

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`

1. Make sure the `instrupy` package (dependency) has been installed.
2. Run `make` from the main git directory.
4. Run `make runtest`. This runs all the tests and can be used to verify the package.

Find the documentation in: `/docs/_build/html/index.html#`

Note that this installation also automatically installs the package `propcov` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

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

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)