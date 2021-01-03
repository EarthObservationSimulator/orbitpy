Tests
******

How to
======

Testing is done using the :mod:`unittest` module and :mod:`nose` module. Use the below command to run all the tests:

.. code-block:: shell

        make runtest

Testing strategies
==================

1. Test the expected format of the output files.
2. Use of random input values and calculated output values to validate the test.
       
        i.  Sometimes special cases are run, and some input values which do not make a difference to the 
            output are made random. Eg: In case of a equatorial orbit, the latitude of the location seen by
            a nadir-pointed sensor will always be 0 deg, irrespective of the chosen orbital altitude, raan, ta
            which can be used as random values.
        ii. In cases where the random input values do influence the output, the expected output is calculated 
            (as much as possible) from methods, code other than used by the :code:`OrbitPy` package. Sometimes
            the chosen validation methods are approximate in which case an *approximately equal to* assertion tests
            are used.
3. Using known inputs, and outputs from external sources (eg: literature, other orbital simulation softwares such as GMAT, STK)
4. Run tests after making any revisions to the code. This helps to check that the revisions do not have uninteded effects on the results.


Test Modules
============

:class:`test_OrbitPropCovGrid_1`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_OrbitPropCovGrid_1
   :members:

:class:`test_OrbitPropCovGrid_2`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_OrbitPropCovGrid_2
   :members:

:class:`test_OrbitPropCovGrid_3`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_OrbitPropCovGrid_3
   :members:
   
:class:`test_GMAT_propagation_OrbitPropCovGrid`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_GMAT_propagation_OrbitPropCovGrid
   :members:

:class:`test_STK_propagation_OrbitPropCovGrid`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_STK_propagation_OrbitPropCovGrid
   :members:
   
:class:`test_STK_coverage_OrbitPropCovGrid`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_STK_coverage_OrbitPropCovGrid
   :members:

:class:`test_OrbitPropCovPopts_1`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_OrbitPropCovPopts_1
   :members:

:class:`test_OrbitPropCovPopts_2`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_OrbitPropCovPopts_2
   :members:

:class:`test_GroundStationComm`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_GroundStationComm
   :members:

:class:`test_InterSatelliteComm`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_InterSatelliteComm
   :members:

:class:`test_PreProcess`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_PreProcess
   :members:
