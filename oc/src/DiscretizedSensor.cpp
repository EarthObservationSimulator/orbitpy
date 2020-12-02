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
	std::vector<AnglePair> corners = generateCorners();
	
	cartesianHeadings = genCartesianHeadings(RADEC);
	cornerHeadings = genCartesianHeadings(corners);
	poleHeadings = generatePoles();
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

std::vector<AnglePair> DiscretizedSensor::generateCorners()
{
	// Initialize point list with number of corners
	std::vector<AnglePair> pointList((widthDetectors+1)*(heightDetectors+1));
	
	// Starting from the left col and moving right col by col
	for(int i = 0;i < widthDetectors + 1;i++)
	{	
		// Starting from the top row and moving down row by row
		for(int j = 0;j < heightDetectors + 1;j++)
		{
			Real a = angleWidth/2.0 - i*wFOV;
			Real RA = pi/2.0 + a;
			
			Real b = angleHeight/2.0 - j*hFOV;
			
			// Lb is the declination, see SMAD 4th ed. p. 167
			Real Lb = atan(tan(b)*cos(a));
			
			pointList[i*(heightDetectors + 1) + j] = {RA,Lb};
		}
	}
	return pointList;
}

/*
void DiscretizedSensor::generateCartesianHeadings(std::vector<AnglePair> RADECVector)
{
	int numPts = RADECVector.size();
	cartesianHeadings.resize(numPts);
	
	for(int i = 0; i < RADECVector.size();i++)
	{
		cartesianHeadings[i] = RADECtoUnitVec(RADECVector[i][0],RADECVector[i][1]);
	}
}
*/

std::vector<Rvector3> DiscretizedSensor::genCartesianHeadings(std::vector<AnglePair> RADECVector)
{
	int numPts = RADECVector.size();
	std::vector<Rvector3> headings(numPts);
	
	for(int i = 0; i < RADECVector.size();i++)
	{
		headings[i] = RADECtoUnitVec(RADECVector[i][0],RADECVector[i][1]);
	}
	
	return headings;
}

std::vector<Rvector3> DiscretizedSensor::generatePoles()
{
	// Stored as rows, then columns
	int numRowPoles = heightDetectors + 1;
	int numColPoles = widthDetectors + 1;
	
	std::vector<Rvector3> poles(numRowPoles + numColPoles);
	
	// Starting from the top row and moving down row by row
	for(int i = 0;i < numRowPoles;i++)
	{	
		// Index of leftmost corner of row i
		int index1 = getIndex(i,0,numRowPoles);
		// Index of next value of row i
		int index2 = getIndex(i,1,numRowPoles);
		
		// Positive pole (not sure if important)
		poles[i] = Cross(cornerHeadings[index2],cornerHeadings[index1]);
		poles[i].Normalize();
	}
	
	// Starting from left col and moving right col by col
	for(int i = 0;i < numColPoles;i++)
	{
		// Index of topmost corner of col i
		int index1 = getIndex(0,i,numRowPoles);
		// Index of next value of col i 
		int index2 = getIndex(1,i,numRowPoles);
		
		// Not sure which side of pole to use
		poles[i + numRowPoles] = Cross(cornerHeadings[index2],cornerHeadings[index1]);
		poles[i + numRowPoles].Normalize();
	}
	
	return poles;
}

// Indexed at zero
Integer DiscretizedSensor::getIndex(Integer row,Integer col,Integer numRows)
{
	// Index of leftmost corner of column col + index of row
	return col*numRows + row;
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

std::vector<Rvector3> DiscretizedSensor::getCornerHeadings()
{
	return cornerHeadings;
}

std::vector<Rvector3> DiscretizedSensor::getPoleHeadings()
{
	return poleHeadings;
}
	


