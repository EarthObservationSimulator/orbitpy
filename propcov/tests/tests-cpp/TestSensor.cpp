/**
 * Tests for the Sensor (base) class. A ConicalSensor object is considered since the Sensor class is cannot be instantiated.
 * The tests are however aimed to the Sensor (base) class.
 * TODO: Add tests for the coordinate conversion utilities. An issue is that they are protected members.
*/
#include <iostream>
#include <string>
#include <ctime>
#include <cmath>
#include <tuple>
#include <math.h>
#include <vector>
#include <numeric>
#include "ConicalSensor.hpp"
#include "Rmatrix33.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for the Spacecraft-body to Sensor rotation matrix.
class ScBody2SensorRotationMatrixTestFixture: public testing::TestWithParam<std::tuple<double, double, double, double, double, double, std::vector<std::vector<double>>>>{
    public:
    protected:
        ConicalSensor sen = ConicalSensor(25.0*PI/180); // a ConicalSensor object is considered since the virtual Sensor class cannot be instantiated.
};
TEST_P(ScBody2SensorRotationMatrixTestFixture, ScBody2SensorRotationWorks){
    std::tuple<double, double, double, double, double, double, std::vector<std::vector<double>>> param = GetParam();
    double seq1                                 = std::get<0>(param);
    double seq2                                 = std::get<1>(param);
    double seq3                                 = std::get<2>(param);
    double angle1                               = std::get<3>(param);
    double angle2                               = std::get<4>(param);
    double angle3                               = std::get<5>(param);
    std::vector<std::vector<double>> trueRotB2S = std::get<6>(param);
    
    sen.SetSensorBodyOffsetAngles(angle1, angle2, angle3, seq1, seq2, seq3);
    Rmatrix33 testRotB2S = sen.GetBodyToSensorMatrix(0);    

    double tolerance = 1e-4;
    //std::cout << testRotB2S.GetElement(0, 0) << "\n";
    EXPECT_NEAR(testRotB2S.GetElement(0, 0), trueRotB2S[0][0], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(0, 1), trueRotB2S[0][1], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(0, 2), trueRotB2S[0][2], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(1, 0), trueRotB2S[1][0], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(1, 1), trueRotB2S[1][1], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(1, 2), trueRotB2S[1][2], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(2, 0), trueRotB2S[2][0], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(2, 1), trueRotB2S[2][1], tolerance);
    EXPECT_NEAR(testRotB2S.GetElement(2, 2), trueRotB2S[2][2], tolerance);

}

INSTANTIATE_TEST_CASE_P(ConeClocktoRADEC, ConeClocktoRADECTestFixture, testing::Values(
    std::make_tuple(0, 0, 0, PI/2) // cone, clock, ra, dec (all in radians)
    ));      
INSTANTIATE_TEST_CASE_P(ScBody2SensorRotMat, ScBody2SensorRotationMatrixTestFixture, testing::Values(
    std::make_tuple(1,2,3,0,0,0, std::vector<std::vector<double>> {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}), // seq1, seq2, seq3, angle1, angle2, angle3 (in degrees)
    // truth data from https://rip94550.wordpress.com/2010/08/30/rotations-from-one-euler-angle-sequence-to-another/
    std::make_tuple(3,2,1,0.2*180/PI, 0.25*180/PI, 0.3*180/PI, std::vector<std::vector<double>> {{0.949599, 0.192493, -0.247404}, {-0.118141, 0.950819, 0.286333}, {0.290353, -0.242673, 0.925637}}),
    // Validate that the rotation matrix is for coordinate-system rotation (https://mathworld.wolfram.com/RotationMatrix.html)
    std::make_tuple(1,2,3,30,0,0, std::vector<std::vector<double>> {{1, 0, 0}, {0, std::cos(30*PI/180), std::sin(30*PI/180)}, {0, -std::sin(30*PI/180), std::cos(30*PI/180)}}),
    std::make_tuple(1,2,3,0,30,0, std::vector<std::vector<double>> {{std::cos(30*PI/180), 0, -std::sin(30*PI/180)}, {0, 1, 0}, {std::sin(30*PI/180), 0, std::cos(30*PI/180)}}),
    std::make_tuple(1,2,3,0,0,30, std::vector<std::vector<double>> {{std::cos(30*PI/180), std::sin(30*PI/180), 0}, {-std::sin(30*PI/180), std::cos(30*PI/180), 0}, {0, 0, 1}})

    ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}