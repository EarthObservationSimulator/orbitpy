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
4. Run tests after making any revisions to the code. This helps to check that the revisions do not have unintended effects on the results.

Refer to the page :ref:`external_validation` for description of the validation tests.


Test Modules
============

:class:`test_constellation`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_constellation
   :members:

:class:`test_propagator`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_propagator
   :members:

:class:`test_grid`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_grid
   :members:

:class:`test_contactfinder`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_contactfinder
   :members:

:class:`test_eclipsefinder`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_eclipsefinder
   :members:

:class:`test_coveragecalculator`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_coveragecalculator
   :members:

:class:`test_coveragecalculator_gridcoverage`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_coveragecalculator_gridcoverage
   :members:

:class:`test_coveragecalculator_pointingoptionscoverage`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_coveragecalculator_pointingoptionscoverage
   :members:

:class:`test_coveragecalculator_pointingoptionswithgridcoverage`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_coveragecalculator_pointingoptionswithgridcoverage
   :members:

:class:`test_datametricscalculator`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_datametricscalculator
   :members:

:class:`test_mission`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_mission
   :members:

:class:`test_util`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: test_util
   :members:
