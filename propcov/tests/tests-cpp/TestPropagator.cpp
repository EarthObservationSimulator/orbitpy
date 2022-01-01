#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "OrbitState.hpp"
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include "Rvector6.hpp"

#include "Propagator.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for propagation (without drag)
class PropagatorWithoutDragTestFixture: public testing::TestWithParam<std::tuple<double, Rvector6, double, Rvector6>>{
    public:
    protected:
        AbsoluteDate            *startDate;
        OrbitState              *startState;
        Spacecraft              *sat;
        Propagator              *prop;
        AbsoluteDate            *toDate;
        NadirPointingAttitude    *attitude;
        LagrangeInterpolator     *interp;
        
};
TEST_P(PropagatorWithoutDragTestFixture, PropagationWithoutDragWorks){
    std::tuple<double, Rvector6, double, Rvector6> param = GetParam();
    double startJdDate            = std::get<0>(param);
    Rvector6 startKepState      = std::get<1>(param);
    double stepSize             = std::get<2>(param);
    Rvector6 trueEndKepState    = std::get<3>(param);
    
    // initialize start date
    startDate = new AbsoluteDate();
    startDate->SetJulianDate(startJdDate);
    // initialize start state
    startState = new OrbitState();
    startState->SetKeplerianState(startKepState[0], startKepState[1], startKepState[2], startKepState[3], startKepState[4], startKepState[5]);
    
    //
    attitude = new NadirPointingAttitude();
    interp = new LagrangeInterpolator("PropcovCppLagrangeInterpolator", 6, 7);

    // initialize spacecraft
    sat = new Spacecraft(startDate, startState, attitude, interp);
    prop = new Propagator(sat);

    // set the date to which propagation should occur
    toDate = new AbsoluteDate();
    toDate->SetJulianDate(startJdDate);
    toDate->Advance(stepSize);

    // propagate
    prop->Propagate(*toDate);

    OrbitState  *endOrbitState = sat->GetOrbitState();
    Rvector6    testEndKepState = endOrbitState->GetKeplerianState();

    double tolerance = 1.0e-5;
    EXPECT_NEAR(testEndKepState[0], trueEndKepState[0], tolerance);
    EXPECT_NEAR(testEndKepState[1], trueEndKepState[1], tolerance);
    EXPECT_NEAR(testEndKepState[2], trueEndKepState[2], tolerance);
    EXPECT_NEAR(testEndKepState[3], trueEndKepState[3], tolerance);
    EXPECT_NEAR(testEndKepState[4], trueEndKepState[4], tolerance);
    EXPECT_NEAR(testEndKepState[5], trueEndKepState[5], tolerance);

    delete(startDate);
    delete(startState);
    delete(sat);
    delete(prop);
    delete(toDate);
}

     
INSTANTIATE_TEST_CASE_P(PropWODrag, PropagatorWithoutDragTestFixture, testing::Values(
    /// using STK J2 Analytical propagator data as truth
    // almost 0 eccentricity
    std::make_tuple(2457473.00, 
                    Rvector6(6500, 0.002, 45.0*PI/180, 75.0*PI/180, 10.0*PI/180, 270.0*PI/180), 
                    86400.0, 
                    Rvector6(6500.0,0.002, 45.0*PI/180, 68.4059136572242*PI/180, 16.9940847530552*PI/180, 116.731954192478*PI/180)) // initial date in JD, initial Keplerian state (km, radians), step-size in seconds, true Keplerian state at end of propagation
    /*
    // using STK J2 Analytical propagator data as truth
    std::make_tuple(2458265,
                    Rvector6(7578.378000000010, 0.000000000000000, 45.78650000000000*PI/180, 98.87969999999998*PI/180, 0.000000000000000*PI/180, 353.5698899999999*PI/180),
                    50950,
                    Rvector6(7578.378000000004, 0.000000000000000, 45.78649995368721*PI/180, 96.63823784912909*PI/180, 0.000000000000000*PI/180, 270.2531716833215*PI/180)),
    // 180 deg inclination
    std::make_tuple(2458265,
                    Rvector6(7578.378,  0.0,  180*PI/180, 98.8797*PI/180, 75.78089*PI/180, 277.789*PI/180),
                    86390,
                    Rvector6(7578.378000000016, 0.000000000000001, 179.9999988096703*PI/180, 200.3180216695994*PI/180, 0.000000000000000*PI/180, 162.7724798737503*PI/180))
    */
));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}