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
		
		sensor = new DiscretizedSensor(pi/3.0,pi/3.0,1,3);
		attitude = new NadirPointingAttitude();
		epoch = new AbsoluteDate();
		state = new OrbitState();
		state->SetKeplerianState(7000.0,0.0,0.0,0.0,0.0,2.0);
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

class TestDiscreteCoverageChecker_Corners : public ::testing::Test {

	protected:
	void SetUp() override 
	{
		Real angle1 = 0.0,angle2 = 0.0,angle3 = 0.0;
		int seq1 = 1,seq2 = 2,seq3 = 3;
		
		sensor = new DiscretizedSensor(pi/3.0,pi/3.0,2,4);
		attitude = new NadirPointingAttitude();
		epoch = new AbsoluteDate();
		state = new OrbitState();
		state->SetKeplerianState(7000.0,0.0,0.0,0.0,0.0,2.0);
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

// Test 300 m altitude at 0,0 ssp
// Make sure latitude is symmetric about equator
TEST_F(TestDiscreteCoverageChecker,projectionAlg_4)
{
	double tolerance = 0.00000000001;
	
	// Expected output
	Real expectedSum = 0;

	Real clock = 0.0,cone = pi/4.0;
	Real clock2 = pi;
	Rvector3 sphericalPos(0,0,300);
	AnglePair latLon,latLon2;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	latLon2 = coverage->projectionAlg(clock2,cone,sphericalPos);
	
	Real lat = latLon[0];
	Real lat2 = latLon2[0];
	
	Real latSum = lat + lat2;
	
	EXPECT_TRUE(lat > 0);
	EXPECT_TRUE(lat2 < 0);
	
	EXPECT_NEAR(expectedSum,latSum,tolerance);
}


// Checks that nadir pointing sensor in equatorial orbit
// is symmetric about the equator, with center pixel pointing
// to SSP.
TEST_F(TestDiscreteCoverageChecker,checkIntersection)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF = {0,7000.0,0,-10.0,0,0};
	
	// Expected output
	Real expectedLon = pi/2, expectedLat = 0.0;
	Real expectedLonDiff = 0.0, expectedLatSum = 0.0;	
	
	std::vector<AnglePair> intersection;
	Real lat,lon,lonDiff,latSum;
	
	intersection = coverage->checkIntersection(state_ECF);
	
	// Lat and lon of center pixel
	lat = intersection[1][0];
	lon = intersection[1][1];
	
	// Should be no difference in longitude along a center column
	// for nadir pointing sensor in equatorial orbit
	
	// Sum between 0th and second pixel latitudes
	// should be zero if they are symmetric about the equator.
	latSum = intersection[0][0] + intersection[2][0];
	
	EXPECT_EQ(intersection.size(),sensor->getCenterHeadings().size());
	EXPECT_NEAR(expectedLon,lon,tolerance);
	EXPECT_NEAR(expectedLat,lat,tolerance);
	EXPECT_NEAR(expectedLon,intersection[0][1],tolerance);
	EXPECT_NEAR(expectedLon,intersection[2][1],tolerance);
	
	EXPECT_NEAR(expectedLatSum,latSum,tolerance);
}

TEST_F(TestDiscreteCoverageChecker_Corners,checkCornerIntersection)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF = {0,7000.0,0,-10.0,0,0};
	std::vector<AnglePair> intersection;
	
	// Center column of corners should all have longitude
	// equal to the longitude of the SSP
	Real expectedLon = pi/2.0;
	// Center row of corners should all have latitude
	// equal to the latitude of the SSP
	Real expectedLat = 0.0;
	
	intersection = coverage->checkCornerIntersection(state_ECF);
	
	// Center column corresponds to index's 5-9
	EXPECT_NEAR(expectedLon,intersection[5][1],tolerance);
	EXPECT_NEAR(expectedLon,intersection[6][1],tolerance);
	EXPECT_NEAR(expectedLon,intersection[7][1],tolerance);
	EXPECT_NEAR(expectedLon,intersection[8][1],tolerance);
	EXPECT_NEAR(expectedLon,intersection[9][1],tolerance);
	
	// 2, 7, and 12 are indices of center row
	EXPECT_NEAR(expectedLat,intersection[2][0],tolerance);
	EXPECT_NEAR(expectedLat,intersection[7][0],tolerance);
	EXPECT_NEAR(expectedLat,intersection[12][0],tolerance);
	
	// Left column of corners should all have longitude
	// less than the longitude of the SSP
	EXPECT_TRUE(intersection[0][1] < expectedLon);
	EXPECT_TRUE(intersection[1][1] < expectedLon);
	EXPECT_TRUE(intersection[2][1] < expectedLon);
	EXPECT_TRUE(intersection[3][1] < expectedLon);
	EXPECT_TRUE(intersection[4][1] < expectedLon);
	
	// Left column of corners should all have longitude
	// greater than the longitude of the SSP
	EXPECT_TRUE(intersection[10][1] > expectedLon);
	EXPECT_TRUE(intersection[11][1] > expectedLon);
	EXPECT_TRUE(intersection[12][1] > expectedLon);
	EXPECT_TRUE(intersection[13][1] > expectedLon);
	EXPECT_TRUE(intersection[14][1] > expectedLon);
	
	// Top row of corners should all have latitude
	// greater than the latitude of the SSP
	EXPECT_TRUE(intersection[0][0] > expectedLat);
	EXPECT_TRUE(intersection[5][0] > expectedLat);
	EXPECT_TRUE(intersection[10][0] > expectedLat);
	
	// Bottom row of corners should all have latitude
	// less than the latitude of the SSP
	EXPECT_TRUE(intersection[4][0] < expectedLat);
	EXPECT_TRUE(intersection[9][0] < expectedLat);
	EXPECT_TRUE(intersection[14][0] < expectedLat);
}

/*
// Still needs working ECF_N conversion
TEST_F(TestDiscreteCoverageChecker,checkPoleIntersection_1)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF = {7000,0,0,7,0,0};
	
	// Expected output
	std::vector<Rvector3> poles;
	
	poles = coverage->checkPoleIntersection(state_ECF);

	EXPECT_EQ(6,poles.size());
	
	// The poles for each row should have zero Y value.
	EXPECT_NEAR(0.0,poles[0][1],tolerance);
	EXPECT_NEAR(0.0,poles[1][1],tolerance);
	EXPECT_NEAR(0.0,poles[2][1],tolerance);
	EXPECT_NEAR(0.0,poles[3][1],tolerance);
	
	// The pole for first column should have negative Y value
	
	//debug
	EXPECT_EQ(poles[4][0],poles[5][0]);
	EXPECT_EQ(poles[4][1],poles[5][1]);
	EXPECT_EQ(poles[4][2],poles[5][2]);	
}
*/

TEST_F(TestDiscreteCoverageChecker,getNadirToSpacecraftAccessMatrix)
{
	double tolerance = 0.00000000001;
	// Since nadir frame x axis of this state is already aligned with North,
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

TEST_F(TestDiscreteCoverageChecker,getNadirToSpacecraftAccessMatrix_2)
{
	double tolerance = 0.00000000001;
	// Since nadir frame x axis of this state is already aligned with North,
	// nadir frame should be alligned with SA frame.
	Rvector6 state_ECF(0,7000.0,0,-10.0,0,0);
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

TEST_F(TestDiscreteCoverageChecker,getSensorToSpacecraftAccessMatrix)
{
	double tolerance = 0.00000000001;
	// All frames should be alligned with SA, resulting
	// In an identity matrix.
	Rvector6 state_ECF(0,7000.0,0,-10.0,0,0);
	Rmatrix33 SA_S;
	
	SA_S = coverage->getSensorToSpacecraftAccessMatrix(state_ECF);
	
	EXPECT_NEAR(1.0,SA_S.GetElement(0,0),tolerance);
	EXPECT_NEAR(1.0,SA_S.GetElement(1,1),tolerance);
	EXPECT_NEAR(1.0,SA_S.GetElement(2,2),tolerance);
	
	// Off-diagonals should be 0
	EXPECT_NEAR(0.0,SA_S.GetElement(0,1),tolerance);
	EXPECT_NEAR(0.0,SA_S.GetElement(0,2),tolerance);
	EXPECT_NEAR(0.0,SA_S.GetElement(1,0),tolerance);
	EXPECT_NEAR(0.0,SA_S.GetElement(1,2),tolerance);
	EXPECT_NEAR(0.0,SA_S.GetElement(2,0),tolerance);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
