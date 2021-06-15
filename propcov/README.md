
# PROPCOV

The `propcov` package consists of C++ source files wrapped with python using `pybind11`. The C++ classes and functions
are made available as python objects to be used by the main `orbitpy` package.

## Use of `pybind11` for wrapping C++ with python

`pybind11 version 2.6.2` is used to bind the C++ source to python. It uses CMake for the build process.

https://pybind11.readthedocs.io/en/stable/basics.html

The directory structure and build is based on the *cmake_example* git-repo available in https://github.com/pybind/cmake_example.

### Notes

> `cmake`, `gcc` are primary requirements.

> The primary work needed to utilize `pybind11` is to:

    * The `pybind11` source folder in `propcov/extern/`
    
    * The `CMakeLists.txt` in the `propcov` folder and other subfolders where the C++ source files are located. 

    * The `pyproject.toml` file in the `propcov` folder.

    * The `setup.py` file in the `propcov` folder.

> The `propcov/src/main.cpp` source ile contains the wrapping code of the C++ sources. Note that not all the C++ source is currently wrapped.

> When the `propcov` package is installed a `build` folder and `***.so` library file is created along with `***.egg-info`. These must be deleted in the un-installation process so as to allow for smooth re-installation.

> The `Makefile` present in the `propcov` folder is to facilitate easy installation, cleanup of the `propcov` package. It is not associated with the `cmake` build process.

## Installation

Requires: Unix-like operating system, `python 3.8`, `pip`, `gcc`, `cmake`

> Run `make` from the main git directory.

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



