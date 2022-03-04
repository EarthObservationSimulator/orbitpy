Installation
==============

Requires: Unix-like operating system, ``python 3.8``, ``pip``, ``gcc``, ``make``, ``cmake``

It is recommended to carry out the installation in a ``conda`` environment. Instructions are available in the ``README.md`` file of the InstruPy package.

**Steps**

1. Install ``instrupy`` package (dependency).

2. Run ``make`` from the root repo directory.
   
   All the below dependencies are automatically installed. If any errors are encountered please check that the following dependencies are installed:

    * :code:`numpy`
    * :code:`pandas`
    * :code:`scipy`
    * :code:`sphinx`
    * :code:`sphinx_rtd_theme==0.5.2`
  
3. Run ``make runtest``. This runs all the tests and can be used to verify the package.

4. Find the documentation in: ``/docs/_build/html/index.html#``

Note that this installation automatically installs the package ``propcov`` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

In order to uninstall run ``make bare`` in the terminal.

.. note::   *   The OrbitPy installation also automatically installs the package ``propcov`` which binds C++ classes with Python to provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection. The python bound C++ objects are implemented in OrbitPy.

            *   The ``make runtest`` does *not* run the tests of the ``propcov`` library. Please see the ``README.MD`` in the ``propcov`` folder on how to run it's tests.

            *   Documentation of the ``propcov`` library is available in the Word document ``propcov/docs/propcov-cpp.docx``.