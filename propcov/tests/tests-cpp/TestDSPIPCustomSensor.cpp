/**
 * Tests for the DSPIPCustomSensor class.
 * Note that the target points have to be in the Query frame before checking for target visibility.
*/

#include <tuple>
#include <math.h>
#include <vector>
#include "polygon/DSPIPCustomSensor.hpp"
#include "Rvector.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for evaluating target points in/out sensor FOV.
class CheckTargetVisibilityTestFixture: public testing::TestWithParam<std::tuple<Rvector, Rvector, AnglePair, double, double, bool>>{
    public:
    protected:
        DSPIPCustomSensor *sen;
};
TEST_P(CheckTargetVisibilityTestFixture, CheckTargetVisibilityWorks){
    std::tuple<Rvector, Rvector, AnglePair, double, double, bool> param = GetParam();
    Rvector fovCone     = std::get<0>(param);
    Rvector fovClock    = std::get<1>(param);
    AnglePair contained = std::get<2>(param);
    double targetCone   = std::get<3>(param);
    double targetClock  = std::get<4>(param);
    bool trueVisibility  = std::get<5>(param);

    sen = new DSPIPCustomSensor(fovCone, fovClock, contained);
    
    AnglePair targetI{targetCone, targetClock}; // target in initial frame
    Rmatrix33 QI = sen->getQI();
    AnglePair targetQ; 
    targetQ = SlicedPolygon::toQueryFrame(QI, targetI); // target in query frame   
    
    bool testVisibility = sen->CheckTargetVisibility(targetQ[0], targetQ[1]);

    ASSERT_TRUE(trueVisibility==testVisibility);

}

Rvector conical_sensor_cone(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
          30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180);
Rvector conical_sensor_clk(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
          1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
          3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
          4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0);
// *********** rectangular sensor 30deg X 10 deg ***********
Rvector rect_sensor_cone(5, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180, 15.79322415135941*PI/180);
Rvector rect_sensor_clock(5, 71.98186515628623*PI/180, 108.01813484371377*PI/180, 251.98186515628623*PI/180, 288.01813484371377*PI/180, 71.98186515628623*PI/180);

INSTANTIATE_TEST_CASE_P(ChkTargVis, CheckTargetVisibilityTestFixture, testing::Values(
      /* Including below tests produces a strange error as follows:
      [  FAILED  ] 1 test, listed below:
      [  FAILED  ] ChkTargVis/CheckTargetVisibilityTestFixture.CheckTargetVisibilityWorks/1, where GetParam() = (0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988 0.5235987755982988
                  , 0                0.330693963535768 0.661387927071536 0.992081890607304 1.32277585414307 1.65346981767884 1.98416378121461 2.31485774475038 2.64555170828614 2.97624567182191 3.30693963535768 3.63763359889345 3.96832756242922 4.29902152596499 4.62971548950075 4.96040945303652 5.29110341657229 5.62179738010806 5.95249134364382 0.5235987755982988
                  , { 0, 0 }, 0.610865, 0.0872665, false)
      The arguments are not passed properly from the INSTANTIATE_TEST_CASE_P to the GetParam(). Note that the last element of the clock array is not what is expected.
      std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
            Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
            1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
            3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
            4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0),
            AnglePair {0,0},
            25*PI/180, 5*PI/180, true), // (cone array, clock array, contianed, target cone, target clock, true visibility) all angles in radians
      std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
            Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
            1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
            3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
            4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0),
            AnglePair {0,0},
            35*PI/180, 5*PI/180, false),
      std::make_tuple(Rvector(20, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180, 
            30*PI/180, 30*PI/180, 30*PI/180, 30*PI/180),
            Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
            1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
            3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
            4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 0),
            AnglePair {0,0},
            35*PI/180, 5*PI/180, false),
      */
      // make an approximate conical sensor with cone angle 30 deg
      std::make_tuple(conical_sensor_cone, conical_sensor_clk, AnglePair {0,0}, // (cone array, clock array, contianed, target cone, target clock, true visibility) all angles in radians
                        25*PI/180, 5*PI/180, true), 
      std::make_tuple(conical_sensor_cone, conical_sensor_clk, AnglePair {0,0},
                        35*PI/180, 5*PI/180, false),
      // using 2*PI rad as the end point instead of 0 rad and a different clock angle
      std::make_tuple(conical_sensor_cone,
            Rvector(20, 0, 0.330693963535768, 0.661387927071536, 0.992081890607304, 1.32277585414307,
            1.65346981767884, 1.98416378121461, 2.31485774475038, 2.64555170828614, 2.97624567182191,
            3.30693963535768, 3.63763359889345, 3.96832756242922, 4.29902152596499, 4.62971548950075,
            4.96040945303652, 5.29110341657229, 5.62179738010806, 5.95249134364382, 2*PI),
            AnglePair {0,0},
            35*PI/180, -5*PI/180, false),
      // *********** rectangular sensor 30deg X 10 deg ***********
      // check clock angle 90 deg, -90 deg (along-track)
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              16*PI/180, 90*PI/180, false),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              14*PI/180, 90*PI/180, true),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              16*PI/180, -90*PI/180, false),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              14*PI/180, -90*PI/180, true),
      // check clock angle 0 deg, 180 deg (cross-track)
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              6*PI/180, 0*PI/180, false),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              4*PI/180, 0*PI/180, true),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              6*PI/180, 180*PI/180, false),
      std::make_tuple(rect_sensor_cone, rect_sensor_clock, AnglePair {0,0}, 
                              4*PI/180, 180*PI/180, true)
    
   ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}