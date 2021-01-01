# OrbitPy

This package contain set of modules to compute orbit data of satellites. It performs the following functions:

1. Computation of satellite state (position and velocity) data.
2. Generation of grid-of-points at a (user-defined or auto) angular resolution.
3. Computation of Field Of Regard (FOR) based on the manueverability and sensor specifications, mounting.
4. Computation of satellite access intervals over given set of grid points for the length of the mission. 
5. Computation of inter-satellite communication time intervals.
6. Computation of ground-station contact time intervals.

## Install

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`, `gfortran`

1. Make sure the `instrupy` package (dependency) has been installed. It can be installed by running `make` in the `instruments/instrupy/` directory.
2. Navigate to the `orbits/oc/` directory and run `make`. 
3. Navigate to the `orbits/orbitpy/` directory and run `make`.
4. Execute `make runtest` to run tests and verify *OK* message. (Currently none.)
5. Run an example, by running the following command from the `orbits` directory: `python orbitpy/bin/run_mission.py orbitpy/examples/example1/`.
   See the results in the `orbitpy/examples/example1/` folder. More description of the examples is given in the documentation.

Find the documentation in: `/orbitpy/docs/_build/html/index.html#`

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

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)