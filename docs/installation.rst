Installation
==============

Requires: Unix-like operating system, ``python 3.8``, ``pip``, ``gcc``, ``cmake``

It is recommended to carry out the installation in a `conda` environment. Instructions are available in the README file of the InstruPy package.

**Steps**

1. Make sure the ``instrupy`` package (dependency) has been installed.

2. Run ``make`` from the main git directory.
   
   All the below dependencies are automatically installed. If any errors are encountered please check that the following dependencies are 
    installed:

    * :code:`numpy`
    * :code:`pandas`
    * :code:`scipy`
    * :code:`sphinx`
    * :code:`sphinx_rtd_theme==0.5.2`
  
3. Run ``make runtest``. This runs all the tests and can be used to verify the package.

4. Find the documentation in: ``/docs/_build/html/index.html#``

Note that this installation also automatically installs the package ``propcov`` which consists of python wrapper and C++ source code which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection.

In order to uninstall run ``make bare`` in the terminal.

---
**NOTE**

The OrbitPy installation also automatically installs the package ``propcov`` which consists of python wrapper of C++ classes which provide the functionality for orbit propagation, coverage calculations and sensor pixel-array projection. The python bound C++ objects are implemented in OrbitPy.

The ``make runtest`` does *not* run the tests of the ``propcov`` library. Please see the ``README.MD`` in the ``propcov`` folder on how to run it's tests.

Documentation of the ``propcov`` library is available in the Word document ``propcov/docs/propcov-cpp.docx``.

---

If using a Windows system, one may consider setting up a virtual-machine with Ubuntu (or similar) OS. VMware Workstation player is available free for non-commercial, personal or home use. VMWare tools may need to be installed separately after the player installation.

[https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html](https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html)

Ubuntu virtual machine images for VMWare and VirtualBox are available here:
[https://www.osboxes.org/ubuntu/](https://www.osboxes.org/ubuntu/)

The present version of OrbitPy has been tested on Ubuntu 18.04.3.