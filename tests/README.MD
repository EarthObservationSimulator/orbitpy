# Tests

## Description of test files

```
│   test_constellation.py 
│   test_contactfinder.py
│   test_datametricscalculator.py
│   test_eclipsefinder.py
│   test_grid.py
│   test_mission.py
│   test_propagator.py
│   test_util.py
│   __init__.py
│
├───test_coveragecalculator
│   │   test_coveragecalculator.py
│   │   test_coveragecalculator_gridcoverage.py
│   │   test_coveragecalculator_pointingoptionscoverage.py
│   │   test_coveragecalculator_pointingoptionswithgridcoverage.py
│   │   __init__.py
│
├───test_data -> Checkpoint data for comparison with future results.
│       accessData.csv
│       gridData.csv
│       midIntervalAccessData.csv
│
├───validation -> Validation with other software
│   │   test_coveragecalculator_GridCoverage_with_STK.py
│   │   test_propagator_J2AnalyticalPropagator_with_GMAT.py
│   │   test_propagator_J2AnalyticalPropagator_with_STK.py
│   │   __init__.py
│   │
│   ├───GMAT -> GMAT propagated state data 
│   │
│   ├───STK
│   │   ├───test_propagation_with_STK -> STK propagated state data
│   │   │
│   │   └───test_coveragecalculator_GridCoverage_with_STK -> STK coverage data
│   │
├───util -> Util folder for tests.
│   │   coverage.py
│   │   plot.py
│   │   spacecrafts.py -> Contains spacecraft specs.
│   │   __init__.py
│   │
```