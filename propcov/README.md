
# PROPCOV

The `propcov` package consists of C++ source files wrapped with python using `pybind11`. The C++ classes and functions
are made available as python objects to be used by the main `orbitpy` package.

## Use of `pybind11` for wrapping C++ with python

`pybind11 version 2.6.2` is used to bind the C++ source to python. It uses CMake for the build process.

https://pybind11.readthedocs.io/en/stable/basics.html

The directory structure and build is based on the *cmake_example* git-repo available in https://github.com/pybind/cmake_example.

THe file `src/main.cpp` contains the python bindings of the C++ classes which are used by OrbitPy. Note that not all the available C++
classes are bound.

### Notes

* `cmake`, `gcc` are primary requirements.

* The primary work needed to utilize `pybind11` is to:

    * The `pybind11` source folder in `propcov/extern/`
    
    * The `CMakeLists.txt` in the `propcov` folder and other subfolders where the C++ source files are located. 

    * The `pyproject.toml` file in the `propcov` folder.

    * The `setup.py` file in the `propcov` folder.

* The `propcov/src/main.cpp` source ile contains the wrapping code of the C++ sources. Note that not all the C++ source is currently wrapped.

* When the `propcov` package is installed a `build` folder and `***.so` library file is created along with `***.egg-info`. These must be deleted in the un-installation process so as to allow for smooth re-installation.

* The `Makefile` present in the `propcov` folder is to facilitate easy installation, cleanup of the `propcov` package. 

* The Makefiles in the `extern/gmatutil/`, `lib/propcov-cpp/` are to facilitate a separate build process (not associated with `cmake`). The builds are triggered when running the Makefile in the `tests/` folder.

## Installation

**Requires:** Unix-like operating system, `python 3.8`, `pip`, `gcc`, `cmake`.

**To install:** Run `make` from the main git directory.

In case of MacOS, there may arise a compiler selection error, in which case please try the installation after running:
```
Export CC=gcc 
```
Also please refer to: https://stackoverflow.com/questions/24380456/how-can-i-make-cmake-use-gcc-instead-of-clang-on-mac-os-x

## Directory structure

```
C:.
├───extern (external libraries)
│   ├───gmatutil (`gmatutil` library from GMAT2020a)
│   │   ├───base
│   │   ├───include
│   │   └───util
│   │       ├───interpolator
│   │       └───matrixoperations
│   ├───json (JSON C++ library)
│   └───pybind11 (pybind11 library)
│       
├───lib (source library)
│   └───propcov-cpp  (cpp library which is wrapped)
│       └───polygon
├───src
│
├───docs
│   │
│   └───tatc_docs (docs from the TAT-C project)
│
└───tests
    └───tests-cpp (cpp tests on the `propcov-cpp` library)
        ├───bin
        └───old
    └───tests-python (python tests on the wrapped `src`)

```

The `gmatutil` folder is a copy of the same folder from the GMAT2020a repository, except:

1. The `util/datawriter` folder was removed.
2. The `base` folder was added containing `ExponentialAtmosphere.hpp` and `ExponentialAtmosphere.cpp`
3. The CMakeLists.txt file was revised according to the changes 1,2 and additional removals (see the file for details).
4. The CmakeLists.txt was modifed to output a static library with target-name `GmatUtil` with the flags `POSITION_INDEPENDENT_CODE ON`.

## Tests

The folder `tests/test-cpp/` contains C++ tests of the `propcov` C++ classes. GoogleTest (GTest) library is used and must be installed to run the tests. [This link](https://www.eriksmistad.no/getting-started-with-google-test-on-ubuntu/) provides good tutorial on installing GTest on Ubuntu.

To run the tests navigate to `tests/` folder and run `make all` followed by `make runtest`.

Running `make all` from the `tests` directory shall trigger clean-up and build of the sources in the `extern/gmatutil` folder and the `lib/propcov-cpp` folder. The test-files in the `tests/test-cpp` folder are built and the executables written in the `tests/build` folder. The executables can be run one after another using the `make runtest` command. 

## Documentation

The `docs/propcov-cpp_description.doc` contains description of the `lib\propocov-cpp\` C++ classes.

The `docs/tatc_docs` contains **old** (March 2019) documentation of most of the `lib\propocov-cpp\` C++ classes which was developed during the course of the TAT-C project. Note that some of the classes referred to in the documentation might have changed since the docs  was made.

## Known Issues

* Passing `propcov` objects as arguments in functions shows *pass-by-reference* C++ behavior.

    Modification of the `propcov` objects within the function to which they have been passed *seems* to result in modification of the parent 
    object outside the function, i.e. it is a pass-by-reference. This behavior is to still confirmed and investigated. 

    In order to bypass this undesired behavior, a copy of the original argument is made within the function and the copy is used. Example in the `orbitpy.propagator.J2AnalyticalPropagator.execute(.)` function, the following snippet is used to make a copy of the `start_date` function argument.

    ```
    _start_date = propcov.AbsoluteDate()
    _start_date.SetJulianDate(start_date.GetJulianDate())
    ```

    Also note that in order to make a deep-copy, we need to initialize a new object with the same object parameters as the original object as seen in the above example.
## Credits and Acknowledgments

This work has been funded by grants from the National Aeronautics and Space Administration (NASA) Earth Science Technology Office (ESTO) through the Advanced Information Systems Technology (AIST) Program.

`propcov` uses:

* GMAT2020a `gmatutil` source (https://sourceforge.net/p/gmat/git/ci/GMAT-R2020a/tree/src/gmatutil/)
* Pybind11 version 2.6.2 (https://pybind11.readthedocs.io/en/stable/basics.html)
* JSON for Modern C++ (https://github.com/nlohmann/json)
* GoogleTest (https://github.com/google/googletest)

## Questions?

Please contact Vinay (vinay.ravindra@nasa.gov)
