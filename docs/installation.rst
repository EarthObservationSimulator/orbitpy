Installation
==============

Requires: Unix-like operating system, ``python 3.8``, ``pip``, ``gcc``

**Steps**

1. Make sure the ``instrupy`` package (dependency) has been installed.
2. Run ``make`` from the main git directory.
3. Run ``make runtest``. This runs all the tests and can be used to verify the package.

Find the documentation in: ``/docs/_build/html/index.html#``

Note that this installation also automatically installs the package ``propcov`` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

In order to uninstall run ``make bare`` in the terminal.

.. todo:: Ask `make runtest` to also run the C++ tests (google tests) of the `propcov` library.