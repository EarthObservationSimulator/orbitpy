#include <tuple>
#include <math.h>
#include <vector>
#include "ConicalSensor.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for the Spacecraft-body to Sensor rotation matrix.
class ScBody2SensorRotationMatrixTestFixture: public testing::TestWithParam<std::tuple<double, double>>{
    public:
    protected:
        ConicalSensor sen = ConicalSensor(25*PI/180);
};
TEST_P(ScBody2SensorRotationMatrixTestFixture, ScBody2SensorRotationWorks){
    std::tuple<double, double> param = GetParam();
    double senFov       = std::get<0>(param);
    double targetCone   = std::get<1>(param);

    sen.SetFieldOfView(senFov);
    bool inView = sen.CheckTargetVisibility(targetCone);

    if(targetCone < senFov)
        ASSERT_TRUE(inView);
    else
        ASSERT_FALSE(inView);
}

     
INSTANTIATE_TEST_CASE_P(ScBody2SensorRotMat, ScBody2SensorRotationMatrixTestFixture, testing::Values(
    std::make_tuple(30*PI/180, 20*PI/180), // fov in radians
    std::make_tuple(30*PI/180, 0*PI/180),
    std::make_tuple(30*PI/180, 90*PI/180),
    std::make_tuple(30*PI/180, 370*PI/180), // TODO: This test should technically fail, but is not failing.
    std::make_tuple(30*PI/180, 30*PI/180)
    ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}