#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../extern/gmatutil/util/Rvector.hpp"
#include "../extern/gmatutil/util/TableTemplate.hpp"
#include "../extern/gmatutil/util/Rmatrix.hpp"
#include "../extern/gmatutil/util/Rvector3.hpp"
#include "../extern/gmatutil/util/Rvector6.hpp"
#include "../extern/gmatutil/util/interpolator/LagrangeInterpolator.hpp"
#include "../lib/propcov-cpp/AbsoluteDate.hpp"
#include "../lib/propcov-cpp/OrbitState.hpp"
#include "../lib/propcov-cpp/Earth.hpp"
#include "../lib/propcov-cpp/Attitude.hpp"
#include "../lib/propcov-cpp/NadirPointingAttitude.hpp"
#include "../lib/propcov-cpp/Spacecraft.hpp"
#include "../lib/propcov-cpp/Sensor.hpp"
#include "../lib/propcov-cpp/ConicalSensor.hpp"
#include "../lib/propcov-cpp/CustomSensor.hpp"
#include "../lib/propcov-cpp/Propagator.hpp"
#include "../lib/propcov-cpp/CoverageChecker.hpp"
#include "../lib/propcov-cpp/PointGroup.hpp"

#include "../lib/propcov-cpp/testclass.hpp"

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
    
    py::class_<Rmatrix33>(m, "Rmatrix33")
        .def(py::init())
        .def(py::init<Real, Real, Real, Real, Real, Real, Real, Real, Real>(), py::arg("a00"), py::arg("a01"), py::arg("a02"), py::arg("a10"), py::arg("a11"), py::arg("a12"), py::arg("a20"), py::arg("a21"), py::arg("a22"))
        .def("GetElement", &Rmatrix33::GetElement, py::arg("row"), py::arg("col"))
        .def("__repr__",
              [](const Rmatrix33 &x){
                  std::string r("Rmatrix33(");
                  r += std::to_string(x.GetElement(0,0)) + "," + std::to_string(x.GetElement(0,1)) + "," + std::to_string(x.GetElement(0,2)) + "," +
                       std::to_string(x.GetElement(1,0)) + "," + std::to_string(x.GetElement(1,1)) + "," + std::to_string(x.GetElement(1,2)) + "," +
                       std::to_string(x.GetElement(2,0)) + "," + std::to_string(x.GetElement(2,1)) + "," + std::to_string(x.GetElement(2,2))  ;
                  r += ")";
                  return r;
              }
            )
        ;
    
    py::class_<Rvector3, Rvector>(m, "Rvector3")
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

    py::class_<Rvector6, Rvector>(m, "Rvector6")
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
                AbsoluteDate    x;
                x.SetJulianDate(jd);
                return x; 
                }, 
                R"pbdoc(
                    Return an AbsoluteDate object initialized to the input Julian Date.
                    )pbdoc"
            )
        .def("SetGregorianDate", &AbsoluteDate::SetGregorianDate, py::arg("year"), py::arg("month"), py::arg("day"), py::arg("hour"), py::arg("minute"), py::arg("second"))
        .def("SetJulianDate", &AbsoluteDate::SetJulianDate, py::arg("jd"))
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
        .def("fromCartesianState", [](const Rvector6& cart) { 
                OrbitState    x;
                x.SetCartesianState(cart);
                return x; 
                },
                R"pbdoc(
                    Return an OrbitState object initialized to the input Keplerian state.
                    )pbdoc"
            )
        .def("SetKeplerianState", &OrbitState::SetKeplerianState, py::arg("SMA"), py::arg("ECC"), py::arg("INC"), py::arg("RAAN"), py::arg("AOP"), py::arg("TA"))
        .def("SetCartesianState", &OrbitState::SetCartesianState)
        .def("GetKeplerianState", &OrbitState::GetKeplerianState)
        .def("GetCartesianState", &OrbitState::GetCartesianState)
        .def("__repr__",
              [](OrbitState &x){ // const removed since OrbitState class throws error 
                  Rvector6 cartstate;
                  cartstate = x.GetCartesianState();
                  std::string r("OrbitState.fromCartesianState(Rvector6([");
                  r += vector_to_string(cartstate.GetRealArray());
                  r += "]))";
                  return r;
              }
            )
        ;

    py::class_<Earth>(m, "Earth")
        .def(py::init())
        .def("ComputeGMT", &Earth::ComputeGMT)
        .def("GetBodyFixedState", py::overload_cast<Rvector3, Real>(&Earth::GetBodyFixedState))
        .def("GetBodyFixedState", py::overload_cast<Rvector6, Real>(&Earth::GetBodyFixedState))
        .def("GetInertialToFixedRotation", &Earth::GetInertialToFixedRotation)
        .def("Convert", &Earth::Convert)
        .def("InertialToBodyFixed", &Earth::InertialToBodyFixed)
        .def("__repr__",
              [](Earth &x){ 
                  std::string r("Earth()");
                  return r;
              }
            )
        ;
       
    py::class_<Attitude>(m, "Attitude")
        ;

    py::class_<NadirPointingAttitude, Attitude>(m, "NadirPointingAttitude")
        .def(py::init())
        .def("__repr__",
              [](NadirPointingAttitude &x){ 
                  std::string r("NadirPointingAttitude()");
                  return r;
              }
            )
        ;
    
    py::class_<LagrangeInterpolator>(m, "LagrangeInterpolator")
        .def(py::init())
        .def("__repr__",
              [](LagrangeInterpolator &x){ 
                  std::string r("LagrangeInterpolator(");
                  r += x.GetName() + ',';
                  r += std::to_string(x.GetDimension()) + ',';
                  r += std::to_string(x.GetOrder());
                  r += ")";
                  return r;
              }
            )
        ;

    py::class_<Spacecraft>(m, "Spacecraft")

        .def(py::init<AbsoluteDate*, OrbitState*, Attitude*, LagrangeInterpolator*, Real, Real, Real, Integer, Integer, Integer>(),
                        py::arg("epoch"), py::arg("state"), py::arg("att"),py::arg("interp"), 
                        py::arg("angle1"), py::arg("angle2"), py::arg("angle3"), 
                        py::arg("seq1"), py::arg("seq2"), py::arg("seq3"))
        .def("GetCartesianState", &Spacecraft::GetCartesianState)
        .def("GetKeplerianState", &Spacecraft::GetKeplerianState)
        .def("AddSensor", &Spacecraft::AddSensor)
        .def("SetAttitude", &Spacecraft::SetAttitude)
        .def("GetBodyFixedToInertial", &Spacecraft::GetBodyFixedToInertial)
        .def("GetBodyFixedToReference", &Spacecraft::GetBodyFixedToReference)
        .def("GetNadirToBodyMatrix", &Spacecraft::GetNadirToBodyMatrix)
        .def("SetBodyNadirOffsetAngles", &Spacecraft::SetBodyNadirOffsetAngles)
        /// @todo write __repr__
        ;


    m.def("test", [](AbsoluteDate* epoch, OrbitState* state, Attitude* att, LagrangeInterpolator* interp) 
                    { 
                        AbsoluteDate* epoch_dup = epoch;
                        OrbitState* state_dup = state;
                        LagrangeInterpolator* interp_dup = interp;
                        Attitude* att_dup = att;

                        epoch_dup->GetJulianDate();
                        state_dup->GetCartesianState();

                        return interp->GetOrder(); 
                    }
            );

    py::class_<Sensor>(m, "Sensor")
        ;

    py::class_<ConicalSensor, Sensor>(m, "ConicalSensor")
        .def(py::init<Real>(), py::arg("halfAngle"), "Initialize Conical Sensor with half-angle in radians.")
        .def("SetFieldOfView", &ConicalSensor::SetFieldOfView)
        .def("GetFieldOfView", &ConicalSensor::GetFieldOfView)
        .def("__repr__",
              [](ConicalSensor &x){ 
                  std::string r("ConicalSensor(");
                  r += std::to_string(x.GetFieldOfView());
                  r += ")";
                  return r;
              }
            )
        ;
    
    py::class_<CustomSensor, Sensor>(m, "CustomSensor")
        .def(py::init<Rvector&, Rvector&>(), py::arg("coneAngleVecIn"), py::arg("clockAngleVecIn"), "Initialize Custom Sensor with cone, clock angles in radians.")
        .def("GetConeAngleVector", &CustomSensor::GetConeAngleVector)
        .def("GetClockAngleVector", &CustomSensor::GetClockAngleVector)
        .def("__repr__",
              [](CustomSensor &x){ 
                  Rvector coneAngleVec = x.GetConeAngleVector();
                  Rvector clockAngleVec = x.GetClockAngleVector();
                  std::string r("CustomSensor(Rvector(");
                  r += vector_to_string(coneAngleVec.GetRealArray()) + "),Rvector(" ;
                  r += vector_to_string(clockAngleVec.GetRealArray());
                  r += "))";
                  return r;
              }
            )
        ;

    py::class_<Propagator>(m, "Propagator")
        ;

    py::class_<CoverageChecker>(m, "CoverageChecker")
        ;

    py::class_<PointGroup>(m, "PointGroup")
        ;



    py::class_<testclass>(m, "testclass")
        ;    

        // ,def_property_readonly("x", &Point::x) // To access member-function 'Point::x()' without ()
        // .def_property("size_bound", &Criteria::size::bound, &Criteria::set_size_bound) # read, write property
        // using py::arg to name and specify default values
        // include __hash__, __eq__, __repr__ functions
}