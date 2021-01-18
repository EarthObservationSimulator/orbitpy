#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "utildefs.hpp"
#include "Rvector.hpp"

namespace py = pybind11;

PYBIND11_MODULE(propcov, m)
{
    py::class_<Element>(m, "Rvector")
        .def(py::init())
        .def(py::init<int>(), py::arg("size"));
        //.def(py::init<std::vector<double>>(), py::arg("ra"));
        
}