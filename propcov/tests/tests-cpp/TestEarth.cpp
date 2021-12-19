/**
 * Tests for the Earth class.
 * TODO:
 * Add tests for:
 *      GetSunPositionInBodyCoords, FixedToTopocentric, FixedToTopo, GetEarthSunDistRaDec, GetBodyFixedState(with velocity vector) functions.
 */
#include <iostream>
#include <string>
#include <ctime>
#include <cmath>
#include <tuple>
#include <math.h>
#include <vector>
#include <numeric>
#include "Rvector3.hpp"
#include "Earth.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

//------------------------------------------------------------------------------
// Real vectorError (Rvector3 &v1 Rvector3 &v2)
//------------------------------------------------------------------------------
Real vectorError (Rvector3 &v1, Rvector3 &v2)
{
    Rvector3 diff = v1 - v2;
    return diff*diff;
}

// Parameterized tests for Julian Date to GMT conversion
class computeGMTTestFixture: public testing::TestWithParam<std::tuple<double, double>>{
    public:
    protected:
        // create the earth
        Earth earth;
};
TEST_P(computeGMTTestFixture, GMTCompWorks){

    std::tuple<double, double> param = GetParam();
    double jd = std::get<0>(param);
    double true_GMT = std::get<1>(param);

    double tolerance = 1e-5;

    // Need to verify the sign. compares hi-fi output from GMAT/STK with low-fi model in TAT-C, hence the loose tolerance
    EXPECT_LE(fabs(earth.ComputeGMT(jd)*180.0/PI - true_GMT)/true_GMT, tolerance);
}

// Parameterized tests for body-fixed state conversions (Spherical/ Caretisan/ Ellipsoid)
class computeBFStateConvertFixture: public testing::TestWithParam<std::tuple<Rvector3, std::string, std::string, Rvector3>>{
    public:
    protected:
        // create the earth
        Earth earth;
};
TEST_P(computeBFStateConvertFixture, BFStateConversionWorks){

    std::tuple<Rvector3, std::string, std::string, Rvector3> param = GetParam();
    Rvector3 startVector   = std::get<0>(param);
    std::string fromType   = std::get<1>(param);
    std::string toType     = std::get<2>(param);
    Rvector3 truthVector   = std::get<3>(param);

    Rvector3 testVector;
    testVector = earth.Convert(startVector, fromType, toType);

    double tolerance = 1e-10;
    if(fromType=="Ellipsoid" or toType=="Ellipsoid"){
      tolerance = 1e-6;
    }
    EXPECT_LE(vectorError(truthVector, testVector), tolerance);
}

// Parameterized tests for sun-vector calculation
class SunVectorTestFixture: public testing::TestWithParam<std::tuple<double, std::string, Rvector3>>{
    public:
    protected:
        // create the earth
        Earth earth;
};
TEST_P(SunVectorTestFixture, SunVectorTestWorks){

    std::tuple<double, std::string, Rvector3> param = GetParam();
    double jd   = std::get<0>(param);
    std::string outType   = std::get<1>(param);
    Rvector3 sunTruth     = std::get<2>(param);

    Rvector3 sunTest = earth.GetSunPositionInBodyCoords(jd, outType);
    double tolerance = 1e-10;
    EXPECT_LE(vectorError(sunTest, sunTruth), tolerance);
}

// Parameterized tests for eci to ecef conversion
class I2BConversionFixture: public testing::TestWithParam<std::tuple<Rvector3, double, std::string, Rvector3>>{
    public:
    protected:
        // create the earth
        Earth earth;
};
TEST_P(I2BConversionFixture, I2BConversionWorks){
    std::tuple<Rvector3, double, std::string, Rvector3> param = GetParam();
    Rvector3 inertialVec   = std::get<0>(param);
    double jd   = std::get<1>(param);
    std::string outType   = std::get<2>(param);
    Rvector3 truthVec     = std::get<3>(param);

    Rvector3 testVec = earth.InertialToBodyFixed(inertialVec, jd, outType);
    double tolerance = 1e-6;
    EXPECT_LE(vectorError(testVec, truthVec), tolerance);
}

// Parameterized tests for geocentric to geodetic latitude conversion
class Geo2GeodLatConversionFixture: public testing::TestWithParam<std::tuple<double, double>>{
    public:
    protected:
        // create the earth
        Earth earth;
};
TEST_P(Geo2GeodLatConversionFixture, Geo2GeodLatConversionWorks){
    std::tuple<double, double> param = GetParam();
    double geoLat   = std::get<0>(param);
    double geodLatTruth     = std::get<1>(param);

    double geodLatTest = earth.GeocentricToGeodeticLat(geoLat);
    double tolerance = 1e-5;
    EXPECT_NEAR(geodLatTest, geodLatTruth, tolerance);
}
      
INSTANTIATE_TEST_CASE_P(Geo2GeodLat, Geo2GeodLatConversionFixture, testing::Values(
    std::make_tuple(0,0),
    std::make_tuple(90*PI/180,90*PI/180),
    // Truth from https://www.vcalc.com/equation/?uuid=dfe99a6b-0b39-11ec-993a-bc764e203090
    std::make_tuple(35*PI/180, 35.181*PI/180),
    std::make_tuple(-75*PI/180, -75.096*PI/180),
    std::make_tuple(-78.65*PI/180, -78.724*PI/180)
    ));
INSTANTIATE_TEST_CASE_P(I2B, I2BConversionFixture, testing::Values(
    // ********* Ellipsoid representation *********
    std::make_tuple(Rvector3(-2436.063522947054, 2436.063522947055, 5967.112612227063), 2457769.43773277, "Ellipsoid", Rvector3(1.04987919204, 0.730506078412, 528.147942517)),
    
    // ********* Spherical representation *********
    // Truth data from https://idlastro.gsfc.nasa.gov/ftp/pro/astro/geo2eci.pro (see example)
    std::make_tuple(Rvector3(-3902.9606, 5044.5548, 0.0000000), 2452343.38982663, "Spherical", Rvector3(0, 0, 0)),
    std::make_tuple(Rvector3(6378.137+600,0,0), 2452343.38982663, "Spherical", Rvector3(0.0000000, 232.27096*PI/180, 600.00000))
    ));
INSTANTIATE_TEST_CASE_P(SunVector, SunVectorTestFixture, testing::Values(
    // ********* Ellipsoid representation *********
    std::make_tuple(2457769.43773277, "Ellipsoid", Rvector3(-0.3656482498, 3.5748963692, 147151685.1403646800))
    ));
INSTANTIATE_TEST_CASE_P(StateConversion, computeBFStateConvertFixture, testing::Values( 
    // ********* Spherical to Cartesian *********
    std::make_tuple(Rvector3(-63*PI/180, 18*PI/180, 200), "Spherical", "Cartesian", Rvector3(2840.246009, 922.8518705, -5861.16236)), // vector entries: latitude in radions, longitude in radions, height in km, initial conditions based on location of SXM
    // Truth data from https://keisan.casio.com/exec/system/1359534351
    std::make_tuple(Rvector3(45*PI/180, -110*PI/180, 200), "Spherical", "Cartesian", Rvector3(-1590.88781, -4370.928341, 4651.444785)),
    std::make_tuple(Rvector3(45*PI/180, 250*PI/180, 200), "Spherical", "Cartesian", Rvector3(-1590.88781, -4370.928341, 4651.444785)),
    std::make_tuple(Rvector3(-45*PI/180, 250*PI/180, 500), "Spherical", "Cartesian", Rvector3(-1663.441241, -4570.267248, -4863.57682)),
    
    // ********* Cartesian to Spherical *********
    std::make_tuple(Rvector3(2840.246009, 922.8518705	, -5861.16236), "Cartesian", "Spherical", Rvector3(-63*PI/180, 18*PI/180, 200)),
    std::make_tuple(Rvector3(-1590.88781, -4370.928341	, 4651.444785), "Cartesian", "Spherical", Rvector3(45*PI/180, 250*PI/180, 200)),
    std::make_tuple(Rvector3(-1590.88781, -4370.928341	, 4651.444785), "Cartesian", "Spherical", Rvector3(45*PI/180, 250*PI/180, 200)),
    std::make_tuple(Rvector3(-1663.441241, -4570.267248	, -4863.57682), "Cartesian", "Spherical", Rvector3(-45*PI/180, 250*PI/180, 500)),    

    // ********* spherical to ellipsoid test *********
    std::make_tuple(Rvector3(45*PI/180, -110*PI/180, 200), "Spherical", "Ellipsoid", Rvector3(45.1862594670*PI/180, 2*PI-109.9999999740*PI/180, 210.717424)),
    std::make_tuple(Rvector3(-63*PI/180, 18*PI/180, 200), "Spherical", "Ellipsoid", Rvector3(-63.1502616600*PI/180, 18.0000000010*PI/180, 216.993271)),

    // ********* ellipsoid to spherical test *********
    std::make_tuple(Rvector3(45.1862594670*PI/180, -109.9999999740*PI/180, 210.717424), "Ellipsoid", "Spherical", Rvector3(45*PI/180, 2*PI-110*PI/180, 200)),
    std::make_tuple(Rvector3(-63.1502616600*PI/180, 18.0000000010*PI/180, 216.993271), "Ellipsoid", "Spherical", Rvector3(-63*PI/180, 18*PI/180, 200)),

    // ********* cartesian to ellipsoid test *********
    // truth data from http://ir.lib.ncku.edu.tw/bitstream/987654321/39750/1/
    // Pg.6 in "TRANSFORMATION OF CARTESIAN TO GEODETIC COORDINATES WITHOUT ITERATIONS" By Rey-Jer You1
    std::make_tuple(Rvector3(-2259.148993, 3912.960837, 4488.055516), "Cartesian", "Ellipsoid", Rvector3(45*PI/180, 120*PI/180, 1)),
    // truth data from https://www.apsalin.com/cartesian-to-geodetic-on-ellipsoid/
    std::make_tuple(Rvector3(-2000.000993, 6532.960837, 8888.055516), "Cartesian", "Ellipsoid", Rvector3(52.5560897200*PI/180, 107.0214479510*PI/180, 4845.895909)),
    std::make_tuple(Rvector3(-1590.88781, -4370.928341, 4651.444785), "Cartesian", "Ellipsoid", Rvector3(45.1862594670*PI/180, 2*PI-109.9999999740*PI/180, 210.717424)),

    // ********* ellipsoid to cartesian test *********
    std::make_tuple(Rvector3(45*PI/180, 120*PI/180, 1), "Ellipsoid", "Cartesian", Rvector3(-2259.148993, 3912.960837, 4488.055516) ),
    // truth data from https://www.apsalin.com/cartesian-to-geodetic-on-ellipsoid/
    std::make_tuple(Rvector3(52.5560897200*PI/180, 107.0214479510*PI/180, 4845.895909), "Ellipsoid", "Cartesian",Rvector3(-2000.000993, 6532.960837, 8888.055516))
    ));
INSTANTIATE_TEST_CASE_P(GMT, computeGMTTestFixture, testing::Values( 
    std::make_tuple(2457260.12345679, 198.002628503035),
    //Truth data from http://neoprogrammics.com/sidereal_time_calculator/index.php
    std::make_tuple(2459578.196527777778, 349.1096376055),
    std::make_tuple(2454695.5, 325.7426487531)
    ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

