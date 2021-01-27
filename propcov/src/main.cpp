#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../extern/gmatutil/util/Rvector.hpp"

namespace py = pybind11;

template<typename T, typename A>
std::string vector_to_string(std::vector<T,A> const& v){
    std::stringstream ss;
    for(size_t i = 0; i < v.size(); ++i)
    {
    if(i != 0)
        ss << ",";
    ss << v[i];
    }
    std::string s = ss.str();
    return s;
}

PYBIND11_MODULE(propcov, m)
{
    py::class_<Rvector>(m, "Rvector")
        .def(py::init())
        .def(py::init<int>(), py::arg("size"))
        .def(py::init<const RealArray &>(), py::arg("ra"))
        .def("GetMagnitude", &Rvector::GetMagnitude)
        .def("__repr__",
              [](const Rvector &x){
                  std::string r("Rvector(");
                  r += vector_to_string(x.GetRealArray());
                  r += ")";
                  return r;
              }
            )
        
        ;
        

        // ,def_property_readonly("x", &Point::x) // To access member-function 'Point::x()' without ()
        // .def_property("size_bound", &Criteria::size::bound, &Criteria::set_size_bound) # read, write property
        // using py::arg to name and specify default values
        // include __hash__, __eq__, __repr__ functions
}