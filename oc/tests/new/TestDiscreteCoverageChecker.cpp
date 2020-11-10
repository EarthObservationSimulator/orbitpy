#include "DiscreteCoverageChecker.hpp"
#include <gtest/gtest.h>
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"

class TestDiscreteCoverageChecker : public ::testing::Test {

	protected:
	void SetUp() override 
	{
		Real angle1 = 0.0,angle2 = 0.0,angle3 = 0.0;
		int seq1 = 1,seq2 = 2,seq3 = 3;
		
		sensor = new DiscretizedSensor(pi/4.0,pi/4.0,1,2);
		attitude = new NadirPointingAttitude();
		epoch = new AbsoluteDate();
		state = new OrbitState();
		interpolator = new LagrangeInterpolator();
		sat = new Spacecraft(epoch,state,attitude,interpolator,angle1,angle2,angle2,seq1,seq2,seq3);
		
		sat->AddSensor(sensor);
		
		coverage = new DiscreteCoverageChecker(sat,sensor);
	}

  	void TearDown() override 
  	{
  		delete(sensor);
  		delete(attitude);
  		delete(epoch);
  		delete(state);
  		delete(interpolator);
  		delete(coverage);
  	}

	DiscretizedSensor* sensor;
	Attitude* attitude;
	AbsoluteDate* epoch;
	OrbitState* state;
	LagrangeInterpolator* interpolator;
	Spacecraft* sat;
	DiscreteCoverageChecker* coverage;
};

TEST_F(TestDiscreteCoverageChecker,unitVectorToClockCone)
{
	double tolerance = 0.00000000001;
	
	// Expected Output
	Real expectedClock0 = 0.0;
	Real expectedCone0 = pi/2;
	Real expectedClock1 = pi/2;
	Real expectedCone1 = pi/2;
	Real expectedCone2 = 0.0;
	
	std::vector<AnglePair> clocksCones;
	std::vector<Rvector3> cartesianHeadings(3);
	
	// Test each basis vector
	cartesianHeadings[0] = {1.0,0,0};
	cartesianHeadings[1] = {0,1.0,0};
	cartesianHeadings[2] = {0,0,1.0};
	
	clocksCones = coverage->unitVectorToClockCone(cartesianHeadings);
	
	EXPECT_NEAR(expectedClock0,clocksCones[0][0],tolerance);
	EXPECT_NEAR(expectedClock1,clocksCones[1][0],tolerance);
	
	EXPECT_NEAR(expectedCone0,clocksCones[0][1],tolerance);
	EXPECT_NEAR(expectedCone1,clocksCones[1][1],tolerance);
	EXPECT_NEAR(expectedCone2,clocksCones[2][1],tolerance);
}

// Test 300 m altitude at 0,0 SSP.
TEST_F(TestDiscreteCoverageChecker,projectionAlg)
{
	double tolerance = 0.00000000001;
	
	// Expected output
	Real expectedLon = 0.0, expectedLat = 0.0;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(0.0,0.0,300);
	AnglePair latLon;
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lon = latLon[1];
	Real lat = latLon[0];
	
	EXPECT_NEAR(expectedLon,lon,tolerance);
	EXPECT_NEAR(expectedLat,lat,tolerance);
}

// Test 300 m altitude at pi/4,pi/4 SSP.
TEST_F(TestDiscreteCoverageChecker,projectionAlg_2)
{
	double tolerance = 0.00000000001;
	
	// Expected output
	Real expectedLon = pi/4.0, expectedLat = pi/4.0;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(pi/4.0,pi/4.0,300);
	AnglePair latLon;
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lon = latLon[1];
	Real lat = latLon[0];
	
	EXPECT_NEAR(expectedLon,lon,tolerance);
	EXPECT_NEAR(expectedLat,lat,tolerance);
}

// Test 300 m altitude at -pi/4,pi/4 SSP.
TEST_F(TestDiscreteCoverageChecker,projectionAlg_3)
{
	double tolerance = 0.00000000001;
	
	// Expected output
	Real expectedLon = pi/4.0, expectedLat = -pi/4.0;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(-pi/4.0,pi/4.0,300);
	AnglePair latLon;
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lon = latLon[1];
	Real lat = latLon[0];
	
	EXPECT_NEAR(expectedLon,lon,tolerance);
	EXPECT_NEAR(expectedLat,lat,tolerance);
}

TEST_F(TestDiscreteCoverageChecker,getNadirToSpacecraftAccessMatrix)
{
	double tolerance = 0.00000000001;
	// Since x axis of this state is already aligned with North,
	// nadir frame should be alligned with SA frame.
	Rvector6 state_ECF(7000.0,0,0,0,10.0,0);
	Rmatrix33 SA_N;
	
	SA_N = coverage->getNadirToSpacecraftAccessMatrix(state_ECF);
	
	EXPECT_NEAR(1.0,SA_N.GetElement(0,0),tolerance);
	EXPECT_NEAR(1.0,SA_N.GetElement(1,1),tolerance);
	EXPECT_NEAR(1.0,SA_N.GetElement(2,2),tolerance);
	
	// Off-diagonals should be 0
	EXPECT_NEAR(0.0,SA_N.GetElement(0,1),tolerance);
	EXPECT_NEAR(0.0,SA_N.GetElement(0,2),tolerance);
	EXPECT_NEAR(0.0,SA_N.GetElement(1,0),tolerance);
	EXPECT_NEAR(0.0,SA_N.GetElement(1,2),tolerance);
	EXPECT_NEAR(0.0,SA_N.GetElement(2,0),tolerance);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
