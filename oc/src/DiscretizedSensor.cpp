#include "DiscretizedSensor.hpp"
#include "RealUtilities.hpp"

// Utilities
Rvector3 RADECToCartesian(AnglePair RADEC)
{
	Real x,y,z;
	Rvector3 heading;
	
	x = cos(RADEC[1])*cos(RADEC[0]);
	y = cos(RADEC[1])*sin(RADEC[0]);
	z = sin(RADEC[1]);
	
	heading = Rvector3(x,y,z);
	
	return heading;
}

// Constructor
DiscretizedSensor::DiscretizedSensor(Real angleWidthIn, Real angleHeightIn, Integer widthDetectorsIn, Integer heightDetectorsIn)
 : angleWidth(angleWidthIn),
   angleHeight(angleHeightIn),
   widthDetectors(widthDetectorsIn),
   heightDetectors(heightDetectorsIn),
   wFOV(angleWidthIn/(double)widthDetectorsIn),
   hFOV(angleHeightIn/(double)heightDetectorsIn),
   Sensor()
{
	std::vector<AnglePair> RADEC = generateRADEC();
	generateCartesianHeadings(RADEC); 
}

// Destructor
DiscretizedSensor::~DiscretizedSensor()
{
}

std::vector<AnglePair> DiscretizedSensor::generateRADEC()
{
	std::vector<AnglePair> pointList(widthDetectors*heightDetectors);
	
	// Starting from the left col and moving right col by col
	for(int i = 0;i < widthDetectors;i++)
	{	
		// Starting from the top row and moving down row by row
		for(int j = 0;j < heightDetectors;j++)
		{
			Real a = angleWidth/2.0 - (i + .5)*wFOV;
			Real RA = pi/2.0 + a;
			
			Real b = angleHeight/2.0 - (j + .5)*hFOV;
			
			// Lb is the declination, see SMAD 4th ed. p. 167
			Real Lb = atan(tan(b)*cos(a));
			
			pointList[i*heightDetectors + j] = {RA,Lb};
		}
	}
	return pointList;
}


void DiscretizedSensor::generateCartesianHeadings(std::vector<AnglePair> RADECVector)
{
	int numPts = RADECVector.size();
	cartesianHeadings.resize(numPts);
	
	for(int i = 0; i < RADECVector.size();i++)
	{
		cartesianHeadings[i] = RADECtoUnitVec(RADECVector[i][0],RADECVector[i][1]);
	}
}

bool DiscretizedSensor::CheckTargetVisibility(Real fakeVal1,Real fakeVal2)
{
	return false;
}

Real DiscretizedSensor::getwFOV()
{
	return wFOV;
}

Real DiscretizedSensor::gethFOV()
{
	return hFOV;
}

std::vector<Rvector3> DiscretizedSensor::getCartesianHeadings()
{
	return cartesianHeadings;
}


