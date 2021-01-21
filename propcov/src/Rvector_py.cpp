#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../lib/gmatutil/include/utildefs.hpp"
#include "../lib/gmatutil/util/Rvector.hpp"


namespace py = pybind11;

PYBIND11_MODULE(propcov, m)
{
    py::class_<Rvector>(m, "Rvector")
        .def(py::init());
        //.def(py::init<int>(), py::arg("size"));
        //.def(py::init<const std::vector<double> &>(), py::arg("ra"));
        
}