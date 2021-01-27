## Directory structure
```
├───lib 
│   ├───gmatutil (`gmatutil` library from GMAT2020a)
│   │   ├───base
│   │   ├───include
│   │   └───util
│   │       ├───interpolator
│   │       └───matrixoperations
│   └───propcov-cpp (cpp library to be wrapped)
├───src (wrapper modules)
└───tests 
    ├───tests-cpp (cpp tests on the `propcov-cpp` library)
    │   ├───bin
    │   └───old
    └───tests-python (python tests on the wrapped `src`)
```

The `gmatutil` folder is a copy of the same folder from the GMAT2020a repository, except:

1. The `util/datawriter` folder was removed.
2. The `base` folder was added containing `ExponentialAtmosphere.hpp` and `ExponentialAtmosphere.cpp`
3. The CMakeLists.txt file was revised according to the changes 1,2 and additional removals (see the file for details).
4. The CmakeLists.txt was modifed to output a static library with target-name `GmatUtil` with the flags `POSITION_INDEPENDENT_CODE ON`.

## Other notes:

> `pyproject.toml` file is needed for the pybind11 to work.
