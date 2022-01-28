/**
 * Tests for the RectangularSensor class.
 * Note that the target points have to be in the Query frame before checking for target visibility.
*/

#include <tuple>
#include <math.h>
#include <vector>
#include "RectangularSensor.hpp"
#include "Rvector.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for evaluating target points in/out sensor FOV.
class CheckTargetVisibilityTestFixture: public testing::TestWithParam<std::tuple<Real, Real, double, double, bool>>{
    public:
    protected:
        RectangularSensor *sen;
};
TEST_P(CheckTargetVisibilityTestFixture, CheckTargetVisibilityWorks){
    std::tuple<Real, Real, double, double, bool> param = GetParam();
    Real angleHeight     = std::get<0>(param);
    Real angleWidth    = std::get<1>(param);
    double targetCone   = std::get<2>(param);
    double targetClock  = std::get<3>(param);
    bool trueVisibility  = std::get<4>(param);

    sen = new RectangularSensor(angleHeight, angleWidth);
    
    bool testVisibility = sen->CheckTargetVisibility(targetCone, targetClock);

    ASSERT_TRUE(trueVisibility==testVisibility);

}

INSTANTIATE_TEST_CASE_P(ChkTargVis, CheckTargetVisibilityTestFixture, testing::Values(
      // *********** rectangular sensor 30deg X 10 deg ***********
      // check clock angle 90 deg, -90 deg (along-track)
      std::make_tuple(30*PI/180, 10*PI/180, // angleHeight, angleWidth, targetCone, targetClock, trueVisibility (angles in radians)
                              16*PI/180, 90*PI/180, false),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              14*PI/180, 90*PI/180, true),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              16*PI/180, -90*PI/180, false),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              14*PI/180, -90*PI/180, true),
      // check clock angle 0 deg, 180 deg (cross-track)
      std::make_tuple(30*PI/180, 10*PI/180, 
                              6*PI/180, 0*PI/180, false),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              4*PI/180, 0*PI/180, true),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              6*PI/180, 180*PI/180, false),
      std::make_tuple(30*PI/180, 10*PI/180, 
                              4*PI/180, 180*PI/180, true)
    
   ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}