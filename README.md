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

## Install

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`

1. Make sure the `instrupy` package (dependency) has been installed.
2. Run `make` from the main git directory.
4. Run `make runtest`. This runs all the tests and can be used to verify the package.

Find the documentation in: `/docs/_build/html/index.html#`

Note that this installation also automatically installs the package `propcov` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

## Directory structure

├───bin
├───docs
├───orbitpy
│   ├───docs
│   │   └───_build
│   │       ├───doctrees
│   │       └───html
│   │           ├───_images
│   │           ├───_sources
│   │           └───_static
│   │               ├───css
│   │               │   └───fonts
│   │               ├───fonts
│   │               │   ├───Lato
│   │               │   └───RobotoSlab
│   │               └───js
│   ├───oci
│   │   └───bin
│   ├───tests
│   │   ├───orbitpropcov
│   │   │   └───OrbitPropCovGrid
│   │   │       └───temp
│   │   │           └───test_STK_coverage
│   │   │               ├───01
│   │   │               ├───02
│   │   │               ├───03
│   │   │               ├───04
│   │   │               ├───05
│   │   │               ├───06
│   │   │               ├───07
│   │   │               ├───08
│   │   │               ├───09
│   │   │               ├───10
│   │   │               ├───11
│   │   │               └───12
│   │   └───validation
│   │       └───temp
│   │           └───test_STK_coverage
│   │               ├───01
│   │               ├───02
│   │               ├───03
│   │               ├───04
│   │               ├───05
│   │               ├───06
│   │               ├───07
│   │               ├───08
│   │               ├───09
│   │               ├───10
│   │               ├───11
│   │               └───12
│   └───__pycache__
├───OrbitPy.egg-info
├───propcov
│   ├───.vscode
│   ├───build
│   │   ├───lib.linux-x86_64-3.8
│   │   └───temp.linux-x86_64-3.8
│   │       ├───CMakeFiles
│   │       │   ├───3.20.2
│   │       │   │   ├───CompilerIdC
│   │       │   │   │   └───tmp
│   │       │   │   └───CompilerIdCXX
│   │       │   │       └───tmp
│   │       │   ├───CMakeTmp
│   │       │   └───propcov.dir
│   │       │       └───src
│   │       ├───extern
│   │       │   ├───gmatutil
│   │       │   │   └───CMakeFiles
│   │       │   │       └───GmatUtil.dir
│   │       │   │           ├───base
│   │       │   │           └───util
│   │       │   │               ├───interpolator
│   │       │   │               └───matrixoperations
│   │       │   └───pybind11
│   │       │       └───CMakeFiles
│   │       └───lib
│   │           └───propcov-cpp
│   │               └───CMakeFiles
│   │                   └───PropCovCpp.dir
│   ├───extern
│   │   ├───gmatutil
│   │   │   ├───base
│   │   │   ├───include
│   │   │   └───util
│   │   │       ├───interpolator
│   │   │       └───matrixoperations
│   │   ├───json
│   │   └───pybind11
│   │       ├───.github
│   │       │   ├───ISSUE_TEMPLATE
│   │       │   └───workflows
│   │       ├───docs
│   │       │   ├───advanced
│   │       │   │   ├───cast
│   │       │   │   └───pycpp
│   │       │   ├───cmake
│   │       │   └───_static
│   │       ├───include
│   │       │   └───pybind11
│   │       │       └───detail
│   │       ├───pybind11
│   │       ├───tests
│   │       │   ├───extra_python_package
│   │       │   ├───extra_setuptools
│   │       │   ├───test_cmake_build
│   │       │   │   ├───installed_embed
│   │       │   │   ├───installed_function
│   │       │   │   ├───installed_target
│   │       │   │   ├───subdirectory_embed
│   │       │   │   ├───subdirectory_function
│   │       │   │   └───subdirectory_target
│   │       │   └───test_embed
│   │       └───tools
│   ├───lib
│   │   └───propcov-cpp
│   │       └───polygon
│   ├───propcov.egg-info
│   ├───src
│   └───tests
│       ├───tests-cpp
│       │   ├───bin
│       │   └───old
│       └───tests-python
├───TBD
│   ├───bin
│   ├───examples
│   │   ├───20201102_500kmSAR
│   │   │   ├───comm
│   │   │   └───sat11
│   │   ├───20210419_500kmSARConstellation
│   │   │   ├───sat1
│   │   │   ├───sat2
│   │   │   └───sat3
│   │   ├───example1
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat21
│   │   │   └───sat31
│   │   ├───example10
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat12
│   │   │   ├───sat21
│   │   │   └───sat22
│   │   ├───example11
│   │   │   ├───comm
│   │   │   └───sat11
│   │   ├───example12
│   │   │   ├───comm
│   │   │   ├───satISS
│   │   │   ├───satSentinel1A
│   │   │   └───satSentinel1B
│   │   ├───example2
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   └───sat12
│   │   ├───example3
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat12
│   │   │   ├───sat21
│   │   │   └───sat22
│   │   ├───example4
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat12
│   │   │   ├───sat13
│   │   │   ├───sat14
│   │   │   ├───sat15
│   │   │   ├───sat16
│   │   │   ├───sat17
│   │   │   └───sat18
│   │   ├───example5
│   │   ├───example6
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat21
│   │   │   └───sat31
│   │   ├───example7
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat21
│   │   │   └───sat31
│   │   ├───example8
│   │   │   ├───comm
│   │   │   ├───sat1
│   │   │   ├───sat2
│   │   │   └───sat3
│   │   ├───example9
│   │   │   ├───comm
│   │   │   ├───sat11
│   │   │   ├───sat12
│   │   │   ├───sat13
│   │   │   ├───sat14
│   │   │   ├───sat15
│   │   │   ├───sat16
│   │   │   ├───sat17
│   │   │   ├───sat18
│   │   │   ├───sat21
│   │   │   ├───sat22
│   │   │   ├───sat23
│   │   │   ├───sat24
│   │   │   ├───sat25
│   │   │   ├───sat26
│   │   │   ├───sat27
│   │   │   ├───sat28
│   │   │   ├───sat31
│   │   │   ├───sat32
│   │   │   ├───sat33
│   │   │   ├───sat34
│   │   │   ├───sat35
│   │   │   ├───sat36
│   │   │   ├───sat37
│   │   │   └───sat38
│   │   └───exampleTest
│   │       ├───comm
│   │       └───sat11
│   ├───oc
│   │   └───src
│   │       └───main
│   └───oci
└───tests
    ├───temp
    ├───test_coveragecalculator
    │   └───temp
    ├───test_data
    ├───util
    └───validation
        ├───GMAT
        │   ├───01
        │   ├───02
        │   ├───03
        │   ├───04
        │   ├───05
        │   ├───06
        │   ├───07
        │   └───08
        ├───STK
        │   ├───test_coveragecalculator_GridCoverage_with_STK
        │   │   ├───Accesses
        │   │   └───States
        │   └───test_propagation_with_STK
        │       ├───01
        │       ├───02
        │       ├───03
        │       ├───04
        │       ├───05
        │       ├───06
        │       ├───07
        │       └───08
        └───temp
            └───test_propagation_with_STK
                ├───01
                ├───02
                ├───03
                ├───04
                ├───05
                ├───06
                ├───07
                └───08
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