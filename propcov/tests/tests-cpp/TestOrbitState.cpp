#include "OrbitState.hpp"
#include "Rvector6.hpp"
#include <gtest/gtest.h>

# define PI 3.14159265358979323846 /* pi */

// Parameterized tests for Keplerian to Cartesian conversion
class Kep2CartConversionFixture: public testing::TestWithParam<std::tuple<Rvector6, Rvector6>>{
    public:
    protected:
        // create the earth
        OrbitState state = OrbitState();
};
TEST_P(Kep2CartConversionFixture, Kep2CartConversionWorks){
    std::tuple<Rvector6, Rvector6> param = GetParam();
    Rvector6 kepState       = std::get<0>(param);
    Rvector6 trueCartState  = std::get<1>(param);

    state.SetKeplerianVectorState(kepState);
    Rvector6 testCartOut = state.GetCartesianState();

    double tolerance = 1e-5;
    EXPECT_NEAR(testCartOut[0], trueCartState[0], tolerance);
    EXPECT_NEAR(testCartOut[1], trueCartState[1], tolerance);
    EXPECT_NEAR(testCartOut[2], trueCartState[2], tolerance);
    EXPECT_NEAR(testCartOut[3], trueCartState[3], tolerance);
    EXPECT_NEAR(testCartOut[4], trueCartState[4], tolerance);
    EXPECT_NEAR(testCartOut[5], trueCartState[5], tolerance);
}
// Parameterized tests for Cartesian to Keplerian conversion
class Cart2KepConversionFixture: public testing::TestWithParam<std::tuple<Rvector6, Rvector6>>{
    public:
    protected:
        // create the earth
        OrbitState state = OrbitState();
};
TEST_P(Cart2KepConversionFixture, Cart2KepConversionWorks){
    std::tuple<Rvector6, Rvector6> param = GetParam();
    Rvector6 cartState     = std::get<0>(param);
    Rvector6 trueKepState  = std::get<1>(param);

    state.SetCartesianState(cartState);
    Rvector6 testKepOut = state.GetKeplerianState();

    EXPECT_NEAR(testKepOut[0], trueKepState[0], 1e-2);
    EXPECT_NEAR(testKepOut[1], trueKepState[1], 1e-5);
    EXPECT_NEAR(testKepOut[2], trueKepState[2], 1e-5);
    EXPECT_NEAR(testKepOut[3], trueKepState[3], 1e-5);
    EXPECT_NEAR(testKepOut[4], trueKepState[4], 1e-5);
    EXPECT_NEAR(testKepOut[5], trueKepState[5], 1e-5);
}

INSTANTIATE_TEST_CASE_P(Cart2Kep, Cart2KepConversionFixture, testing::Values( 
    std::make_tuple(Rvector6(-2436.063522947054,  2436.063522947055, 5967.112612227063,
                             -5.385803634090905, -5.378203080755706, 0.009308738717021944), // x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s]
                    Rvector6(6900,0.002,PI/3,PI/4,PI/4,PI/4) // sma, ecc, inc, raan, aop, ta
                    ),
    // truth data from https://elainecoe.github.io/orbital-mechanics-calculator/calculator.html
    std::make_tuple(Rvector6(5635.532744258228, -3941.435355496131, -109.89457937927526,
                             6.7, 3.2, 1),
                    Rvector6(6668.1609545680685,0.48662628626097326,9.345082638008284*PI/180,330.6038697790278*PI/180,232.0455606236203*PI/180,122.30754270280369*PI/180)
                    )
    ));
INSTANTIATE_TEST_CASE_P(Kep2Cart, Kep2CartConversionFixture, testing::Values( 
    std::make_tuple(Rvector6(6900,0.002,PI/3,PI/4,PI/4,PI/4),
                    Rvector6(-2436.063522947054,  2436.063522947055, 5967.112612227063,
                             -5.385803634090905, -5.378203080755706, 0.009308738717021944)
                    ),
    // truth data from https://elainecoe.github.io/orbital-mechanics-calculator/calculator.html
    std::make_tuple(Rvector6(6668.1609545680685,0.48662628626097326,9.345082638008284*PI/180,330.6038697790278*PI/180,232.0455606236203*PI/180,122.30754270280369*PI/180),
                    Rvector6(5635.532744258228, -3941.435355496131, -109.89457937927526, 6.7, 3.2, 1)
                    )
    ));

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}