## Directory structure
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