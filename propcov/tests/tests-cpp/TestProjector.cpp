#include "Projector.hpp"
#include <gtest/gtest.h>
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include <math.h>

class TestProjector : public ::testing::Test {

	protected:
	void SetUp() override 
	{
		Real angle1 = 0.0,angle2 = 0.0,angle3 = 0.0;
		int seq1 = 1,seq2 = 2,seq3 = 3;
		
		sensor = new DiscretizedSensor(pi/3.0,pi/3.0,1,3);
		attitude = new NadirPointingAttitude();
		epoch = new AbsoluteDate();
		epoch->SetJulianDate(GmatTimeConstants::JD_OF_J2000);
		state = new OrbitState();
		state->SetKeplerianState(7000.0,0.0,0.0,0.0,0.0,2.0);
		interpolator = new LagrangeInterpolator();
		sat = new Spacecraft(epoch,state,attitude,interpolator,angle1,angle2,angle2,seq1,seq2,seq3);
		
		sat->AddSensor(sensor);
		
		coverage = new Projector(sat,sensor);
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
	Projector* coverage;
};

class TestProjector_Corners : public ::testing::Test {

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
		
		coverage = new Projector(sat,sensor);
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
	Projector* coverage;
};

// Tests each basis vector conversion to clock/cone angles.
TEST_F(TestProjector,unitVectorToClockCone)
{
	double tolerance = 0.00000000001;
	
	std::vector<AnglePair> clocksCones;
	std::vector<Rvector3> cartesianHeadings(3);
	
	// Test each basis vector
	cartesianHeadings[0] = {1.0,0,0};
	cartesianHeadings[1] = {0,1.0,0};
	cartesianHeadings[2] = {0,0,1.0};
	
	clocksCones = coverage->unitVectorToClockCone(cartesianHeadings);
	
	// Clock angle of X basis vector should be 0
	EXPECT_NEAR(0,clocksCones[0][0],tolerance);
	// Clock angle of Y basis vector should be pi/2
	EXPECT_NEAR(pi/2,clocksCones[1][0],tolerance);
	
	// Cone angle of X basis vector should be pi/2
	EXPECT_NEAR(pi/2,clocksCones[0][1],tolerance);
	// Cone angle of Y basis vector should be pi/2
	EXPECT_NEAR(pi/2,clocksCones[1][1],tolerance);
	// Cone angle of Z basis vector should be pi/2
	EXPECT_NEAR(0,clocksCones[2][1],tolerance);
}

// Test clock = 0,cone = 0, at lat = 0, lon = 0, alt = 300
TEST_F(TestProjector,projectionAlg)
{
	double tolerance = 0.00000000001;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(0.0,0.0,300);
	AnglePair latLon;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lat = latLon[0];
	Real lon = latLon[1];
	
	// Expected Longitude and Latitude are equal to SSP (0)
	EXPECT_NEAR(0,lon,tolerance);
	EXPECT_NEAR(0,lat,tolerance);
}

// Test clock = 0, cone = 0, at lat = pi/4,lon = pi/4, alt = 300
TEST_F(TestProjector,projectionAlg_2)
{
	double tolerance = 0.00000000001;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(pi/4.0,pi/4.0,300);
	AnglePair latLon;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lat = latLon[0];
	Real lon = latLon[1];
	
	// Expected Longitude and Latitude are equal to SSP (pi/4)
	EXPECT_NEAR(pi/4,lon,tolerance);
	EXPECT_NEAR(pi/4,lat,tolerance);
}

// Test clock = 0, cone = 0, at lat = -pi/4,lon = pi/4, alt = 300
TEST_F(TestProjector,projectionAlg_3)
{
	double tolerance = 0.00000000001;

	Real clock = 0.0,cone = 0.0;
	Rvector3 sphericalPos(-pi/4.0,pi/4.0,300);
	AnglePair latLon;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	Real lon = latLon[1];
	Real lat = latLon[0];
	
	// Expected Longitude and Latitude are equal to SSP (-pi/4,pi/4)
	EXPECT_NEAR(pi/4,lon,tolerance);
	EXPECT_NEAR(-pi/4,lat,tolerance);
}

// Test clock = 0,cone = pi/4, at lat = 0, lon = 0, alt = 300
// Test clock = pi,cone = pi/4, at lat = 0, lon = 0, alt = 300
// Check that latitude is symmetric about equator
// Check that longitudes are equal
TEST_F(TestProjector,projectionAlg_4)
{
	double tolerance = 0.00000000001;

	Real clock = 0.0,cone = pi/4.0;
	Real clock2 = pi;
	Rvector3 sphericalPos(0,0,300);
	AnglePair latLon,latLon2;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	latLon2 = coverage->projectionAlg(clock2,cone,sphericalPos);
	
	Real lat = latLon[0];
	Real lat2 = latLon2[0];
	
	Real lon = latLon[1];
	Real lon2 = latLon[1];
	
	Real latSum = lat + lat2;
	
	EXPECT_TRUE(lat > 0);
	EXPECT_TRUE(lat2 < 0);
	
	// Sum of the latitudes should be zero if symmetric
	EXPECT_NEAR(0,latSum,tolerance);
	// Longitudes should be equal
	EXPECT_NEAR(lon,lon2,tolerance);
}


// Test wide range of outputs at wide range of clock and cone angles
// All cone angles are less than the horizon
// Check if any NaN's are produced
TEST_F(TestProjector,projectionAlg_5)
{
	const int numVals = 500;
	double tolerance = 0.00000000001;
	
	Real h = 300;
	Rvector3 sphericalPos(0,0,h);
	Earth* centralBody = new Earth();
	Real radius = centralBody->GetRadius();
	
	// Angular radius of the earth (horizon angle)
	Real rho = asin(radius/(radius+h));
	
	// 5 degrees offset to make sure points don't reach horizon
	Real offset = .0872;
	Real maxAngle = rho - offset;
	Real coneStep = maxAngle/numVals;
	
	Real clockStep = (2*pi)/numVals;
	
	Real clock = 0;
	Real cone = 0;
	AnglePair latLon;
	for (int i = 0;i < numVals;i++)
	{
		clock = clock + clockStep;
		cone = cone + coneStep;
		
		latLon = coverage->projectionAlg(clock,cone,sphericalPos);
		
		EXPECT_TRUE(!isnan(latLon[1]));
		EXPECT_TRUE(!isnan(latLon[0]));
	}
}

// Check that point on horizon is not NaN.
// Check that point slightly past horizon is NaN.
TEST_F(TestProjector,ProjectionAlg_6)
{
	double tolerance = 0.00000000001;
	
	Real h = 300;
	Rvector3 sphericalPos(0,0,h);
	Earth* centralBody = new Earth();
	Real radius = centralBody->GetRadius();
	
	// Angular radius of the earth (horizon angle)
	Real rho = asin(radius/(radius+h));
	
	Real clock = 0;
	Real cone = rho;
	AnglePair latLon;
	
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
		
	EXPECT_TRUE(!isnan(latLon[1]));
	EXPECT_TRUE(!isnan(latLon[0]));
	
	// A little less than .01 deg
	cone = rho + .001;
	latLon = coverage->projectionAlg(clock,cone,sphericalPos);
	
	EXPECT_TRUE(isnan(latLon[1]));
	EXPECT_TRUE(isnan(latLon[0]));
}


// Checks that nadir pointing sensor in equatorial orbit
// is symmetric in latitude about the equator, with center 
// pixel pointing to SSP.
// Checks that longitude of pixels are equal.
TEST_F(TestProjector,checkIntersection)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF = {0,7000.0,0,-10.0,0,0};
	
	CoordsPair latLonCart;
	
	std::vector<AnglePair> intersection;
	Real lat,lon,lonDiff,latSum;
	
	latLonCart = coverage->checkIntersection(state_ECF);
	intersection = latLonCart.first;
	
	// Lat and lon of center pixel
	lat = intersection[1][0];
	lon = intersection[1][1];
	
	latSum = intersection[0][0] + intersection[2][0];
	
	
	// Center pixel longitude should be pi/2
	EXPECT_NEAR(pi/2,lon,tolerance);
	// Center pixel latitude should be zero
	EXPECT_NEAR(0,lat,tolerance);
	
	
	// Should be no difference in longitude along a center column
	// for nadir pointing sensor in equatorial orbit	
	EXPECT_NEAR(intersection[0][1],intersection[2][1],tolerance);
	
	// Sum of 0th and second pixel latitudes
	// should be zero if they are symmetric about the equator.
	EXPECT_NEAR(0,latSum,tolerance);
}

// Checks relative locations of corners for nadir pointing sensor
// in equatorial orbit.
TEST_F(TestProjector_Corners,checkCornerIntersection)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF = {0,7000.0,0,-10.0,0,0};
	std::vector<AnglePair> intersection;
	
	CoordsPair latLonCart;
	
	// Center column of corners should all have longitude
	// equal to the longitude of the SSP
	Real expectedLon = pi/2.0;
	// Center row of corners should all have latitude
	// equal to the latitude of the SSP
	Real expectedLat = 0.0;
	
	latLonCart = coverage->checkCornerIntersection(state_ECF);
	intersection = latLonCart.first;
	
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
	
	// Right column of corners should all have longitude
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


// Checks relative locations of poles for nadir pointing sensor
// in equatorial orbit. Satellite position alligned with X axis,
// velocity alligned with Y axis
TEST_F(TestProjector,checkPoleIntersection)
{
	double tolerance = 0.00000000001;
	Rvector6 state_ECF(7000,0,0,0,7,0);
	
	std::vector<Rvector3> poles;
	std::vector<AnglePair> anglePoles;
	
	CoordsPair latLonCart;
	
	latLonCart = coverage->checkPoleIntersection(state_ECF);
	poles = latLonCart.second;
	
	// Check that there are 6 poles.
	EXPECT_EQ(6,poles.size());
	
	// The poles for each row should have zero Y value.
	EXPECT_NEAR(0.0,poles[0][1],tolerance);
	EXPECT_NEAR(0.0,poles[1][1],tolerance);
	EXPECT_NEAR(0.0,poles[2][1],tolerance);
	EXPECT_NEAR(0.0,poles[3][1],tolerance);
	
	// The first and second poles should have positive Z values
	EXPECT_TRUE(poles[0][2] > 0);
	EXPECT_TRUE(poles[1][2] > 0);
	// The second and third poles should have positive Z values
	EXPECT_TRUE(poles[2][2] < 0);
	EXPECT_TRUE(poles[3][2] < 0);
	
	// The pole for first column should have negative Y value
	EXPECT_TRUE(poles[4][1] < 0);
	// The pole for second column should have negative Y value
	EXPECT_TRUE(poles[5][1] > 0);
}



// Checks relative locations of poles for nadir pointing sensor
// in equatorial orbit. Satellite position alligned with Y axis,
// velocity alligned with -X axis
TEST_F(TestProjector,checkPoleIntersection_2)
{
	double tolerance = 0.00000000001;
	
	Rvector6 state_ECF(0,7000,0,-7,0,0);
	std::vector<Rvector3> poles;
	
	CoordsPair latLonCart;
	
	latLonCart = coverage->checkPoleIntersection(state_ECF);
	poles = latLonCart.second;	

	// Check that there are 6 poles.
	EXPECT_EQ(6,poles.size());
	
	// The poles for each row should have zero X value.
	EXPECT_NEAR(0.0,poles[0][0],tolerance);
	EXPECT_NEAR(0.0,poles[1][0],tolerance);
	EXPECT_NEAR(0.0,poles[2][0],tolerance);
	EXPECT_NEAR(0.0,poles[3][0],tolerance);
	
	// The first and second poles should have positive Z values
	EXPECT_TRUE(poles[0][2] > 0);
	EXPECT_TRUE(poles[1][2] > 0);
	// The second and third poles should have negative Z values
	EXPECT_TRUE(poles[2][2] < 0);
	EXPECT_TRUE(poles[3][2] < 0);
	
	// The pole for first column should have positive X value
	EXPECT_TRUE(poles[4][0] > 0);
	// The pole for second column should have negative X value
	EXPECT_TRUE(poles[5][0] < 0);
}


// Checks that the identity matrix is returned when the Nadir and
// spacecraft access frames are alligned.
TEST_F(TestProjector,getNadirToSpacecraftAccessMatrix)
{
	double tolerance = 0.00000000001;
	
	// Since nadir frame x axis of this state is already aligned with North,
	// nadir frame should be alligned with SA frame.
	Rvector6 state_ECF(7000.0,0,0,0,10.0,0);
	Rmatrix33 SA_N;
	
	SA_N = coverage->getNadirToSpacecraftAccessMatrix(state_ECF);
	
	// Diagonals should be 1
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

// Checks that the identity matrix is returned when the Nadir and
// spacecraft access frames are alligned.
TEST_F(TestProjector,getNadirToSpacecraftAccessMatrix_2)
{
	double tolerance = 0.00000000001;
	
	// Since nadir frame x axis of this state is already aligned with North,
	// nadir frame should be alligned with SA frame.
	Rvector6 state_ECF(0,7000.0,0,-10.0,0,0);
	Rmatrix33 SA_N;
	
	SA_N = coverage->getNadirToSpacecraftAccessMatrix(state_ECF);
	
	// Diagonals should be 1
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

TEST_F(TestProjector,getSensorToSpacecraftAccessMatrix)
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
