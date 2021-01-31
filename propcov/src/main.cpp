#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../extern/gmatutil/util/Rvector.hpp"
#include "../extern/gmatutil/util/Rvector6.hpp"
#include "../lib/propcov-cpp/AbsoluteDate.hpp"
#include "../lib/propcov-cpp/OrbitState.hpp"

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
        .def("GetRealArray", &Rvector::GetRealArray)
        .def("__repr__",
              [](const Rvector &x){
                  std::string r("Rvector([");
                  r += vector_to_string(x.GetRealArray());
                  r += "])";
                  return r;
              }
            )
        
        ;
    
    py::class_<Rvector3>(m, "Rvector3")
        .def(py::init())
        .def(py::init<const RealArray&>())
        .def("Get", &Rvector3::Get)
        .def("GetRealArray", &Rvector3::GetRealArray)
        .def("__repr__",
              [](const Rvector3 &x){
                  std::string r("Rvector3([");
                  r += vector_to_string(x.GetRealArray());
                  r += "])";
                  return r;
              }
            )
        ;


    py::class_<Rvector6>(m, "Rvector6")
        .def(py::init())
        .def(py::init<const Real, const Real, const Real, const Real, const Real, const Real>())
        .def(py::init<const RealArray&>())
        .def("Get", &Rvector6::Get)
        .def("GetRealArray", &Rvector6::GetRealArray)
        .def("GetR", py::overload_cast<>(&Rvector6::GetR, py::const_))
        .def("GetV", py::overload_cast<>(&Rvector6::GetV, py::const_))
        .def("__repr__",
              [](const Rvector6 &x){
                  std::string r("Rvector6([");
                  r += vector_to_string(x.GetRealArray());
                  r += "])";
                  return r;
              }
            )

        ;

    py::class_<AbsoluteDate>(m, "AbsoluteDate")
        .def(py::init())
        .def("fromJulianDate", [](Real jd) { 
                AbsoluteDate    *date;
                date = new AbsoluteDate();
                date->SetJulianDate(jd);
                return date; 
                }, 
                R"pbdoc(
                    Return an AbsoluteDate object initialized to the input Julian Date.
                    )pbdoc"
            )
        .def("SetGregorianDate", &AbsoluteDate::SetGregorianDate)
        .def("SetJulianDate", &AbsoluteDate::SetJulianDate)
        .def("GetGregorianDate", &AbsoluteDate::GetGregorianDate)
        .def("GetJulianDate", &AbsoluteDate::GetJulianDate)
        .def("Advance", &AbsoluteDate::Advance)
        .def("__repr__",
              [](const AbsoluteDate &x){
                  std::string r("AbsoluteDate.fromJulianDate(");
                  r += std::to_string(x.GetJulianDate());
                  r += ")";
                  return r;
              }
            )
        ;
    
    py::class_<OrbitState>(m, "OrbitState")
        .def(py::init())
        ;
        

        // ,def_property_readonly("x", &Point::x) // To access member-function 'Point::x()' without ()
        // .def_property("size_bound", &Criteria::size::bound, &Criteria::set_size_bound) # read, write property
        // using py::arg to name and specify default values
        // include __hash__, __eq__, __repr__ functions
}