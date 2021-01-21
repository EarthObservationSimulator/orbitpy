from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext

import sys
import glob

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

#files = sorted(glob.glob('lib/**/*.hpp', recursive = True))
#files.extend(sorted(glob.glob('lib/**/*.cpp', recursive = True)))
#files.extend(["src/outer_Rvector.cpp"])
files = ["src/main.cpp"]
include_dirs= ["lib/gmatutil/base", "lib/gmatutil/include", "lib/gmatutil/util", "lib/propcov-cpp"]
ext_modules = [
    Pybind11Extension("propcov",
        files,
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name="propcov",
    version=__version__,
    description="Wrap the propcov cpp classes with PyBind11.",
    long_description="",
    ext_modules=ext_modules,
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
