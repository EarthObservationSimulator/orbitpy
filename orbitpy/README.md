This package contain set of modules to compute orbit data of satellites. It performs the following functions:

1. Computation of satellite state (position and velocity) data.
2. Generation of grid-of-points at a (user-defined or auto) angular resolution.
3. Computation of Field Of Regard (FOR) based on the manueverability and sensor specifications, mounting.
4. Computation of satellite access intervals over given set of grid points for the length of the mission. 
5. Computation of inter-satellite communication time intervals.
6. Computation of ground-station contact time intervals.

## Install

Requires: `python 3.8`, `gcc`, `gfortran`

1. Make sure the `instrupy` package (dependency) has been installed. It can be installed by running `make` in the `instruments/instrupy/` directory.
2. Navigate to the `orbits/oc/` directory and run `make`. 
3. Navigate to the `orbits/orbitpy/` directory and run `make`.
4. Execute `make runtest` to run tests and verify *OK* message. (Currently none.)
5. Run an example, by running the following command from the `orbits` directory: `python orbitpy/bin/run_mission.py orbitpy/examples/example1/`.
   See the results in the `orbitpy/examples/example1/` folder. Description of the examples in given in :ref:`examples` page. 

Find the documentation in: `orbits/orbitpy/docs/_build/html/user_json_desc.html`

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)