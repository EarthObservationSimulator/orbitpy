#include "DiscretizedSensor.hpp"
#include <gtest/gtest.h>

TEST(RADECToCartesian,AllZeros)
{
	AnglePair RADEC = {0.0,0.0};
	Rvector3 heading;
	Rvector3 expectedHeading(1.0,0.0,0.0);
	
	heading = RADECToCartesian(RADEC);
	
	ASSERT_EQ(expectedHeading,heading);
}	

TEST (RADECToCartesian,Z_AXIS)
{
	double tolerance = 0.00000000001;
	Rvector3 heading;
	Real expectedXVal = 0.0, expectedYVal = 0.0, expectedZVal = 1.0;
	Real zVal,xVal,yVal;
	AnglePair RADEC = {pi/2.0,pi/2.0};
	
	heading = RADECToCartesian(RADEC);
	xVal = heading[0];
	yVal = heading[1];
	zVal = heading[2];
	
	ASSERT_NEAR(expectedXVal,xVal,tolerance);
	ASSERT_NEAR(expectedYVal,yVal,tolerance);
	ASSERT_NEAR(expectedZVal,zVal,tolerance);
}

TEST (RADECToCartesian,45_DEG)
{
	double tolerance = 0.00000000001;
	Rvector3 heading;
	Real expectedXVal = sqrt(2)/2.0, expectedYVal = sqrt(2)/2.0, expectedZVal = 0.0;

	Real xVal,yVal,zVal;
	AnglePair RADEC = {pi/4,0.0};
	
	heading = RADECToCartesian(RADEC);
	xVal = heading[0];
	yVal = heading[1];
	zVal = heading[2];
	
	ASSERT_NEAR(expectedXVal,xVal,tolerance);
	ASSERT_NEAR(expectedYVal,yVal,tolerance);
	ASSERT_NEAR(expectedZVal,zVal,tolerance);
}


TEST(DiscretizedSensor,FOV)
{
	double tolerance = 0.00000000001;
	DiscretizedSensor testSensor = DiscretizedSensor(pi/4.0,pi/4.0,1,2);
	
	Real expectedwFOV = pi/4.0;
	Real expectedhFOV = pi/8.0;
	
	Real wFOV = testSensor.getwFOV();
	Real hFOV = testSensor.gethFOV();
	
	ASSERT_NEAR(expectedwFOV,wFOV,tolerance);
	ASSERT_NEAR(expectedhFOV,hFOV,tolerance);
}

TEST(GenerateCorners,NumCorners)
{
	DiscretizedSensor testSensor = DiscretizedSensor(pi/4.0,pi/4.0,4,5);
	int expectedNumCorners = 30;
	int numCorners;
	
	std::vector<AnglePair> cornerHeadings = testSensor.generateCorners();
	
	numCorners = cornerHeadings.size();
	
	EXPECT_EQ(expectedNumCorners,numCorners);
}

TEST(GenerateRADEC,45_45_1_2)
{
	double tolerance = 0.00000000001;
	DiscretizedSensor testSensor = DiscretizedSensor(pi/4.0,pi/4.0,1,2);
	std::vector<AnglePair> RADEC = testSensor.generateRADEC();
	Real expectedRA0,expectedEL0,expectedRA1,expectedEL1;
	
	expectedRA0 = pi/2.0;
	expectedEL0 = pi/16.0;
	
	expectedRA1 = pi/2.0;
	expectedEL1 = -pi/16.0;
	
	ASSERT_NEAR(expectedRA0,RADEC[0][0],tolerance);
	ASSERT_NEAR(expectedEL0,RADEC[0][1],tolerance);
	
	ASSERT_NEAR(expectedRA1,RADEC[1][0],tolerance);
	ASSERT_NEAR(expectedEL1,RADEC[1][1],tolerance);
}

TEST(GenerateCorners,45_45_1_2)
{
	double tolerance = 0.00000000001;
	DiscretizedSensor testSensor = DiscretizedSensor(pi/4.0,pi/4.0,1,2);
	std::vector<AnglePair> RADEC = testSensor.generateCorners();
	
	Real expectedRA0,expectedRA1,expectedRA2,expectedRA3,expectedRA4,expectedRA5,expectedRA6;
	
	// Only testing centerline elevations.
	Real expectedEL1,expectedEL4;
	
	expectedRA0 = pi/2.0 + pi/8.0;
	expectedRA1 = pi/2.0 + pi/8.0;
	expectedRA2 = pi/2.0 + pi/8.0;
	expectedRA3 = pi/2.0 - pi/8.0;
	expectedRA4 = pi/2.0 - pi/8.0;
	expectedRA5 = pi/2.0 - pi/8.0;
	
	expectedEL1 = 0;
	expectedEL4 = 0;
	
	ASSERT_NEAR(expectedRA0,RADEC[0][0],tolerance);
	ASSERT_NEAR(expectedRA1,RADEC[1][0],tolerance);
	ASSERT_NEAR(expectedRA2,RADEC[2][0],tolerance);
	ASSERT_NEAR(expectedRA3,RADEC[3][0],tolerance);
	ASSERT_NEAR(expectedRA4,RADEC[4][0],tolerance);
	ASSERT_NEAR(expectedRA5,RADEC[5][0],tolerance);
	
	ASSERT_NEAR(expectedEL1,RADEC[1][1],tolerance);
	ASSERT_NEAR(expectedEL4,RADEC[4][1],tolerance);
}

TEST(GetPoleHeadings,45_45_2_2)
{
	double tolerance = 0.00000000001;
	DiscretizedSensor testSensor = DiscretizedSensor(pi/4.0,pi/4.0,2,2);
	std::vector<Rvector3> poles = testSensor.generatePoles();
	
	Real xVal1 = poles[1][0];
	Real yVal1 = poles[1][1];
	Real zVal1 = poles[1][2];
	
	Real xVal4 = poles[4][0];
	Real yVal4 = poles[4][1];
	Real zVal4 = poles[4][2];
	
	Real expectedXVal1 = 0;
	Real expectedYVal1 = 0;
	Real expectedZVal1 = 1;
	
	Real expectedXVal4 = 1;
	Real expectedYVal4 = 0;
	Real expectedZVal4 = 0;
	
	ASSERT_EQ(6,poles.size());
	
	ASSERT_NEAR(expectedXVal1,xVal1,tolerance);
	ASSERT_NEAR(expectedYVal1,yVal1,tolerance);
	ASSERT_NEAR(expectedZVal1,zVal1,tolerance);
	
	ASSERT_NEAR(expectedXVal4,xVal4,tolerance);
	ASSERT_NEAR(expectedYVal4,yVal4,tolerance);
	ASSERT_NEAR(expectedZVal4,zVal4,tolerance);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
