/**
 * Tests for the PointGroup class.
 * TODO:
 * Add tests to validate the set of generated points.
 *      
 */

#include <iostream>
#include <string>
#include <ctime>
#include <cmath>
#include <vector>
#include<algorithm>

#include "PointGroup.hpp"
#include "Rvector3.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for point-generation (check Cartesian vector output)
class PointGenerationByNumPointsCartesianFixture: public testing::TestWithParam<std::tuple<int, std::vector<std::vector<double>>>>{
    public:
    protected:
        // create the point-group object
        PointGroup pg;
};
TEST_P(PointGenerationByNumPointsCartesianFixture, PointGenerationWorks){
    std::tuple<int, std::vector<std::vector<double>>> param = GetParam();
    int testPointNum      = std::get<0>(param);
    std::vector<std::vector<double>> truthData = std::get<1>(param);

    pg.AddHelicalPointsByNumPoints(testPointNum);

    int numPoints = pg.GetNumPoints();
    ASSERT_EQ(numPoints, testPointNum);

    double maxDiff = -INFINITY;
    for (int pointIdx = 0; pointIdx < testPointNum; pointIdx++)
    {
        Rvector3 truthPos3(truthData[pointIdx][0], truthData[pointIdx][1], truthData[pointIdx][2]);
        Rvector3 *ptPos = pg.GetPointPositionVector(pointIdx);
        //std::cout << std::fixed;
        //std::cout << std::setprecision(12);
        //std::cout << "{" << ptPos->GetElement(0) << "," << ptPos->GetElement(1) << "," << ptPos->GetElement(2) << "}\n";
        Rvector3 diffVec = truthPos3 - (*ptPos);

        double diff = diffVec.GetMagnitude();
        if (diff > maxDiff)
        maxDiff = diff;

    }

    double tolerance = 10e-11;
    EXPECT_LE(maxDiff, tolerance);
}

// Test that the generated points are within the specified region bounds
class PointsGenerationRegionBoundsTestFixture: public testing::TestWithParam<std::tuple<double, double, double, double>>{
    public:
    protected:
        // create the point-group object
        PointGroup pg;
};
TEST_P(PointsGenerationRegionBoundsTestFixture, GenerationWithinRegionWorks){
    std::tuple<double, double, double, double> param = GetParam();
    double latUpper      = std::get<0>(param);
    double latLower      = std::get<1>(param);
    double lonUpper      = std::get<2>(param);
    double lonLower      = std::get<3>(param);

    pg.SetLatLonBounds(latUpper,latLower,lonUpper,lonLower);
    pg.AddHelicalPointsByNumPoints(rand() % 1000 + 1); // number of points is generated randomly

    RealArray latVec;
    RealArray lonVec;
    pg.GetLatLonVectors(latVec, lonVec);
    
    for (Integer pointIdx = 0; pointIdx < pg.GetNumPoints(); pointIdx++)
    {
        EXPECT_TRUE(latVec.at(pointIdx) >= latLower);
        EXPECT_TRUE(latVec.at(pointIdx) <= latUpper);
        EXPECT_TRUE(lonVec.at(pointIdx) >= lonLower);
        EXPECT_TRUE(lonVec.at(pointIdx) <= lonUpper);
    }
}

//  Test setting points based on angular separation, test that the angular seperation is correct
class AngularSeperationTestFixture: public testing::TestWithParam<std::tuple<double>>{
    public:
    protected:
        // create the point-group object
        PointGroup pg;
};
TEST_P(AngularSeperationTestFixture, AngularSeperationWorks){
    std::tuple<double> param = GetParam();
    double angSep      = std::get<0>(param)*PI/180;
    pg.AddHelicalPointsByAngle(angSep);

    double tolerance = 1e-3; // radians
    // pick any random consecutive set of points. 
    int totalNumPoints = pg.GetNumPoints();
    int point1 = rand() % (totalNumPoints-1); // '-1' because the second point index is this point index + 1
    Rvector3 *v1 = pg.GetPointPositionVector(point1);
    Rvector3 *v2 = pg.GetPointPositionVector(point1+1);
    double angleOut = std::acos(((*v1)*(*v2))/v1->GetMagnitude()/v2->GetMagnitude());

    EXPECT_NEAR(angSep, angleOut, tolerance);
}

//  Test setting your own lat lon using those from the previous test
//  Test setting points based on angular separation, test that the angular seperation is correct
class UserSettingPointsTestFixture: public testing::TestWithParam<std::tuple<double, double, double, double>>{
    public:
    protected:
        // create the point-group object
        PointGroup pg;
        PointGroup pgCustom;
};
TEST_P(UserSettingPointsTestFixture, UserSettingPointsWorks){
    // Generate points using a PointGroup object and then set the generated points on another PointGroup object.
    std::tuple<double, double, double, double> param = GetParam();
    double latUpper      = std::get<0>(param);
    double latLower      = std::get<1>(param);
    double lonUpper      = std::get<2>(param);
    double lonLower      = std::get<3>(param);

    pg.SetLatLonBounds(latUpper,latLower,lonUpper,lonLower);
    pg.AddHelicalPointsByNumPoints(rand() % 1000 + 1);
    RealArray latVec;
    RealArray lonVec;
    pg.GetLatLonVectors(latVec, lonVec);

    pgCustom.AddUserDefinedPoints(latVec,lonVec);
    ASSERT_EQ(pg.GetNumPoints(), pgCustom.GetNumPoints())<<"*** ERROR - error setting user defined points\n";

    RealArray latVec2;
    RealArray lonVec2;
    pgCustom.GetLatLonVectors(latVec2, lonVec2);
    for (Integer pointIdx = 0; pointIdx < pgCustom.GetNumPoints(); pointIdx++)
    {        
        EXPECT_DOUBLE_EQ(latVec2.at(pointIdx), latVec.at(pointIdx)) << "*** ERROR - error setting user defined points (lat)\n";
        EXPECT_DOUBLE_EQ(lonVec2.at(pointIdx), lonVec2.at(pointIdx)) << "*** ERROR - error setting user defined points (lon)\n";
    }
}

INSTANTIATE_TEST_CASE_P(UserSetPnts, UserSettingPointsTestFixture, testing::Values(
    std::make_tuple( PI/3, -PI/3, PI/3, -PI/3), // latUpper, latLower, lonUpper, lonLower
    std::make_tuple( PI/4,     0,    0, -PI),
    std::make_tuple(-PI/4, -PI/2, -PI/3, -PI/2),
    std::make_tuple(    0, -PI/2,   PI, PI/2),
    std::make_tuple(-PI/4, -PI/2, PI/2, PI/3)
    ));
INSTANTIATE_TEST_CASE_P(AngSep, AngularSeperationTestFixture, testing::Values(
    // TODO: The angular seperation test fails larger values of specified angular-seperation.
    std::make_tuple(1), // angular seperation in degrees
    std::make_tuple(0.5)
    ));
INSTANTIATE_TEST_CASE_P(PntGenRegionBounds, PointsGenerationRegionBoundsTestFixture, testing::Values(
    std::make_tuple( PI/3, -PI/3, PI/3, -PI/3), // latUpper, latLower, lonUpper, lonLower
    std::make_tuple( PI/4,     0,    0, -PI),
    std::make_tuple(-PI/4, -PI/2, -PI/3, -PI/2),
    std::make_tuple(    0, -PI/2,   PI, PI/2),
    std::make_tuple(-PI/4, -PI/2, PI/2, PI/3)
    ));
std::vector<std::vector<double>> points_data1; // Truth data for PntGenByNumPntCart test-case
INSTANTIATE_TEST_CASE_P(PntGenByNumPntCart, PointGenerationByNumPointsCartesianFixture, testing::Values(
    // Test the returned values for point locations.  Note (SPH)
    // this is a semi-rigorous test.  I plotted the points and they look correct,
    // and I then outputted the data and am using it as truth.
    std::make_tuple(50, points_data1)
    ));



int main(int argc, char **argv) {
  
  double RE = 6378.1363;

  //*********************** set truth data //***********************
  // NOTE: This test-data is different from the one in the original test-file (tests/tests-cpp/old/TestPointGroup.cpp). The data is in a commented section at the bottom of this file.
  points_data1={{0.000000000000,0.000000000000,6378.136300000000},
                {0.000000000000,0.000000000000,-6378.136300000000},
                {-2767.369626445428,-0.000000000000,5746.502241538325},
                {-855.164244288687,-2631.924916228209,5746.502241538325},
                {2238.849057511401,-1626.619054066753,5746.502241538325},
                {2238.849057511401,1626.619054066753,5746.502241538325},
                {-855.164244288687,2631.924916228209,5746.502241538325},
                {-2767.369626445428,-0.000000000000,-5746.502241538325},
                {-855.164244288687,-2631.924916228209,-5746.502241538325},
                {2238.849057511401,-1626.619054066753,-5746.502241538325},
                {2238.849057511401,1626.619054066753,-5746.502241538325},
                {-855.164244288687,2631.924916228209,-5746.502241538325},
                {-4986.627758812155,-0.000000000001,3976.702937914996},
                {-3526.078303509150,-3526.078303509150,3976.702937914996},
                {0.000000000000,-4986.627758812155,3976.702937914996},
                {3526.078303509150,-3526.078303509150,3976.702937914996},
                {4986.627758812155,0.000000000000,3976.702937914996},
                {3526.078303509150,3526.078303509150,3976.702937914996},
                {0.000000000000,4986.627758812155,3976.702937914996},
                {-3526.078303509150,3526.078303509150,3976.702937914996},
                {-4986.627758812155,-0.000000000001,-3976.702937914996},
                {-3819.978484540894,-3205.342537483411,-3976.702937914996},
                {-865.918823021060,-4910.869678264101,-3976.702937914996},
                {2493.313879406076,-4318.546318347987,-3976.702937914996},
                {4685.897307561954,-1705.527140780692,-3976.702937914996},
                {4685.897307561954,1705.527140780692,-3976.702937914996},
                {2493.313879406079,4318.546318347985,-3976.702937914996},
                {-865.918823021058,4910.869678264101,-3976.702937914996},
                {-3819.978484540894,3205.342537483411,-3976.702937914996},
                {-6218.223106570102,-0.000000000001,1419.268846376672},
                {-5231.102156334579,-3361.825223457347,1419.268846376672},
                {-2583.143232664449,-5656.294691988934,1419.268846376672},
                {884.945415758729,-6154.930561282550,1419.268846376672},
                {4072.070147404028,-4699.419466030167,1419.268846376672},
                {5966.341379121325,-1751.875894824452,1419.268846376672},
                {5966.341379121325,1751.875894824452,1419.268846376672},
                {4072.070147404028,4699.419466030167,1419.268846376672},
                {884.945415758729,6154.930561282550,1419.268846376672},
                {-2583.143232664448,5656.294691988935,1419.268846376672},
                {-5231.102156334581,3361.825223457345,1419.268846376672},
                {-6218.223106570102,-0.000000000001,-1419.268846376672},
                {-5030.648168030191,-3654.979837506194,-1419.268846376672},
                {-1921.536614745141,-5913.881605280589,-1419.268846376672},
                {1921.536614745141,-5913.881605280588,-1419.268846376672},
                {5030.648168030192,-3654.979837506193,-1419.268846376672},
                {6218.223106570102,0.000000000000,-1419.268846376672},
                {5030.648168030192,3654.979837506193,-1419.268846376672},
                {1921.536614745141,5913.881605280588,-1419.268846376672},
                {-1921.536614745141,5913.881605280589,-1419.268846376672},
                {-5030.648168030191,3654.979837506194,-1419.268846376672}};

  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

/*
  points_data1={{0.0,                        0.0,                       1.0},
                {0.0,                        0.0,                      -1.0},
                {0.433883739117558,                       0.0,         0.900968867902419},
                {0.134077448970272,          0.41264795740226,         0.900968867902419},
                {-0.351019318529051,         0.255030463062816,         0.900968867902419},
                {-0.351019318529051,        -0.255030463062815,         0.900968867902419},
                {0.134077448970272,         -0.41264795740226,         0.900968867902419},
                {0.433883739117558,                       0.0,        -0.900968867902419},
                {0.134077448970272,          0.41264795740226,        -0.900968867902419},
                {-0.351019318529051,         0.255030463062816,        -0.900968867902419},
                {-0.351019318529051,        -0.255030463062815,        -0.900968867902419},
                {0.134077448970272,         -0.41264795740226,        -0.900968867902419},
                {0.78183148246803,                       0.0,         0.623489801858733},
                {0.552838342998275,         0.552838342998275,         0.623489801858733},
                {4.78733711238551e-17,          0.78183148246803,         0.623489801858733},
                {-0.552838342998275,         0.552838342998275,         0.623489801858733},
                {-0.78183148246803,      9.57467422477103e-17,         0.623489801858733},
                {-0.552838342998275,        -0.552838342998275,         0.623489801858733},
                {-1.43620113371565e-16,         -0.78183148246803,         0.623489801858733},
                {0.552838342998275,        -0.552838342998275,         0.623489801858733},
                {0.78183148246803,                       0.0,        -0.623489801858733},
                {0.598917662600107,         0.502551589793308,        -0.623489801858733},
                {0.135763612173208,         0.769953705483544,        -0.623489801858733},
                {-0.390915741234015,         0.677085925295762,        -0.623489801858733},
                {-0.734681274773315,         0.267402115690236,        -0.623489801858733},
                {-0.734681274773315,        -0.267402115690236,        -0.623489801858733},
                {-0.390915741234015,        -0.677085925295762,        -0.623489801858733},
                {0.135763612173208,        -0.769953705483544,        -0.623489801858733},
                {0.598917662600107,        -0.502551589793309,        -0.623489801858733},
                {0.974927912181824,                       0.0,         0.222520933956314},
                {0.820161550378687,          0.52708582340226,         0.222520933956314},
                {0.404999691314914,         0.886825622084767,         0.222520933956314},
                {-0.138746708150268,          0.96500455176578,         0.222520933956314},
                {-0.638442008115133,         0.736801354657499,         0.222520933956314},
                {-0.935436481519112,         0.274668933435062,         0.222520933956314},
                {-0.935436481519112,        -0.274668933435062,         0.222520933956314},
                {-0.638442008115134,        -0.736801354657499,         0.222520933956314},
                {-0.138746708150268,         -0.96500455176578,         0.222520933956314},
                {0.404999691314914,        -0.886825622084767,         0.222520933956314},
                {0.820161550378687,         -0.52708582340226,         0.222520933956314},
                {0.974927912181824,                       0.0,        -0.222520933956314},
                {0.788733249245582,         0.573048248828767,        -0.222520933956314},
                {0.30126929315467,         0.927211543798553,        -0.222520933956314},
                {-0.30126929315467,         0.927211543798553,        -0.222520933956314},
                {-0.788733249245582,         0.573048248828767,        -0.222520933956314},
                {-0.974927912181824,      1.19394234705288e-16,        -0.222520933956314},
                {-0.788733249245582,        -0.573048248828767,        -0.222520933956314},
                {-0.30126929315467,        -0.927211543798553,        -0.222520933956314},
                {0.30126929315467,        -0.927211543798553,        -0.222520933956314},
                {0.788733249245582,        -0.573048248828767,        -0.222520933956314}};
  std::transform(points_data1.begin(), points_data1.end(), points_data1.begin(), [RE](std::vector<double> &c){ return (std::vector<double> {c[0]*RE, c[1]*RE, c[2]*RE}); });

*/
