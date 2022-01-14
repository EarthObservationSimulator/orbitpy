/**
 * Tests for the GMATCustomSensor class.
 * TODO: Add tests for the protected/ private auxillary functions.
*/

#include <tuple>
#include <math.h>
#include <vector>
#include "GMATCustomSensor.hpp"
#include "Rvector.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for evaluating target points in/out sensor FOV.
class CheckTargetVisibilityTestFixture: public testing::TestWithParam<std::tuple<Rvector, Rvector, double, double, bool>>{
    public:
    protected:
        GMATCustomSensor *sen;
};
TEST_P(CheckTargetVisibilityTestFixture, CheckTargetVisibilityWorks){
    std::tuple<Rvector, Rvector, double, double, bool> param = GetParam();
    Rvector fovCone     = std::get<0>(param);
    Rvector fovClock    = std::get<1>(param);
    double targetCone   = std::get<2>(param);
    double targetClock  = std::get<3>(param);
    bool trueVisibility  = std::get<4>(param);

    sen = new GMATCustomSensor(fovCone, fovClock);
    bool testVisibility = sen->CheckTargetVisibility(targetCone, targetClock);

    ASSERT_TRUE(trueVisibility==testVisibility);

}

     
INSTANTIATE_TEST_CASE_P(ChkTargVis, CheckTargetVisibilityTestFixture, testing::Values(
    // make an approximate conical sensor with cone angle 30 deg
    std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
          Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
          1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
          3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
          4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 2*PI),
          25*PI/180, 5*PI/180, true), // (cone array, clock array, target cone, target clock, true visibility) all angles in radians
    std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
          Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
          1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
          3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
          4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0),
          35*PI/180, 5*PI/180, false),
    std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
          Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
          1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
          3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
          4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0),
          35*PI/180, 5*PI/180, false),
    // *********** rectangular sensor 30deg X 10 deg, (using only 4 (cone, clock) points and not 5 points ***********
    // check clock angle 90 deg, -90 deg (along-track)
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          16*PI/180, 90*PI/180, false),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          14*PI/180, 90*PI/180, true),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          16*PI/180, -90*PI/180, false),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          14*PI/180, -90*PI/180, true),
    // check clock angle 0 deg, 180 deg (cross-track)
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          6*PI/180, 0*PI/180, false),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          4*PI/180, 0*PI/180, true),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          6*PI/180, 180*PI/180, false),
    std::make_tuple(Rvector(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180)),
          Rvector(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180),
          4*PI/180, 180*PI/180, true)
 
   ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}