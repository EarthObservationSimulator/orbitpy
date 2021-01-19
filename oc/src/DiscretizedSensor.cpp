#include "DiscretizedSensor.hpp"
#include "RealUtilities.hpp"


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

/**
 * Constructor
 *
 * Fully builds the DiscretizedSensor object by constructing lists of heading locations of pixel 
 * centers,corners,and poles, specified as unit vectors in the sensor frame.
 *
 * @param angleWidthIn The FOV angle in the row direction (along the y axis in the sensor frame)
 * @param angleHeightIn The FOV angle in the column direction (along the x axis in the sensor frame)
 * @param widthDetectorsIn Number of detectors in the row direction
 * @param heightDetectorsIn Number of detectors in the column direction
 * @return the constructed DiscretizedSensor object, ready to use.
 *
 */
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
	
	centerHeadings = genCartesianHeadings(RADEC);
	cornerHeadings = genCartesianHeadings(corners);
	poleHeadings = generatePoles();
}

/**
 * Destructor.
 *
 */
DiscretizedSensor::~DiscretizedSensor()
{
}

/**
 * Generates vector of right ascension and declination values of pixel centers.
 *
 * For ease of construction, angles are specified in an intermediate coordinate frame, with the y
 * axis pointing down sensor boresight and the x axis pointing along the sensor rows. The
 * genCartesianHeadings function must be used to transform to the sensor frame after.
 *
 * @return A vector of right ascension and declination values.
 *
 */
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

/**
 * Generates vector of right ascension and declination values of pixel corners.
 *
 * For ease of construction, angles are specified in an intermediate coordinate frame,
 * the sensor construction frame, with the y axis pointing down sensor boresight and the
 * x axis pointing along the sensor rows. The genCartesianHeadings function must be used to
 * transform to the sensor frame after.
 *
 * @return A vector of right ascension and declination values.
 *
 */
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

/**
 * 
 * Generates a vector of cartesian unit vectors from a vector of RA/DEC headings.
 *
 * Headings will also be transformed from the sensor construction frame to the sensor frame.
 * The sensor frame boresight is along the Z axis, the pixel columns are along the X axis,
 * and the pixel rows are along the Y axis.
 *
 * @param RADECVector A vector of AnglePairs in the sensor construction frame.
 * @return A vector of cartesian unit vectors (Rvector3 objects) in the sensor frame.
 *
 */
std::vector<Rvector3> DiscretizedSensor::genCartesianHeadings(std::vector<AnglePair> RADECVector)
{
	int numPts = RADECVector.size();
	std::vector<Rvector3> headings(numPts);
	Rvector3 heading;
	Real temp;
	
	for(int i = 0; i < RADECVector.size();i++)
	{
		heading = RADECtoUnitVec(RADECVector[i][0],RADECVector[i][1]);
		
		// Align z axis with boresight.

		temp = heading[1];
		
		// New Y axis is old X axis
		heading[1] = heading[0];
		
		// New X axis is old Z axis
		heading[0] = heading[2];
		
		// New Z axis is old Y axis
		heading[2] = temp;
		
		headings[i] = heading;
	}
	
	return headings;
}

/**
 *
 * Generates a vector of cartesian unit vectors of poles representing the pixel edges
 *
 * cornerheadings class member must already be initialized. The column rows are constructed by 
 * crossing the corner in the first column of the ith row with the corner in the second column of
 * the ith row. The column poles are constructed by crossing the corner in the first row of the 
 * ith column with the corner in the second row of the ith column.
 *
 * @return @return A vector of cartesian unit vectors (Rvector3 objects) in the sensor frame
 *
 */
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
		
		poles[i] = Cross(cornerHeadings[index2],cornerHeadings[index1]);
		poles[i].Normalize();
		
		if(i >= numRowPoles/2)
		{
			poles[i] = Cross(cornerHeadings[index1],cornerHeadings[index2]);
			poles[i].Normalize();
		}
		
	}
	
	// Starting from left col and moving right col by col
	for(int i = 0;i < numColPoles;i++)
	{
		// Index of topmost corner of col i
		int index1 = getIndex(0,i,numRowPoles);
		// Index of next value of col i 
		int index2 = getIndex(1,i,numRowPoles);
		
		poles[i + numRowPoles] = Cross(cornerHeadings[index1],cornerHeadings[index2]);
		poles[i + numRowPoles].Normalize();
		
		
		// New code
		if(i >= numColPoles/2)
		{
			poles[i + numRowPoles] = Cross(cornerHeadings[index2],cornerHeadings[index1]);
			poles[i + numRowPoles].Normalize();
		}
		
	}
	
	return poles;
}

/**
 *
 * Returns the array index of the pixel element at a particular row, column location.
 *
 * @param row  The pixel row number, with index starting at zero
 * @param col  The pixel column number, with index starting at zero
 * @param numRows  The total number of rows of pixels
 *
 */
Integer DiscretizedSensor::getIndex(Integer row,Integer col,Integer numRows)
{
	// Index of leftmost corner of column col + index of row
	return col*numRows + row;
}

/**
 *
 * Dummy function to satisfy Sensor class contract.
 *
 * @param fakeVal1  Dummy variable
 * @param fakeVal2  Dummy variable
 * @return boolean false
 *
 */
bool DiscretizedSensor::CheckTargetVisibility(Real fakeVal1,Real fakeVal2)
{
	return false;
}

/**
 *
 * Returns the class member wFOV, the field of view in the row direction
 *
 * @return  The wFov class member
 *
 */
Real DiscretizedSensor::getwFOV()
{
	return wFOV;
}

/**
 *
 * Returns the class member hFOV, the field of view in the column direction
 *
 * @return  The hFov class member
 *
 */
Real DiscretizedSensor::gethFOV()
{
	return hFOV;
}

/**
 *
 * Returns a vector of unit vectors (Rvector3) of the pixel centers.
 *
 * @return  The centerHeadings class member
 *
 */
std::vector<Rvector3> DiscretizedSensor::getCenterHeadings()
{
	return centerHeadings;
}

/**
 *
 * Returns a vector of unit vectors (Rvector3) of the pixel corners.
 *
 * @return  The cornerHeadings class member
 *
 */
std::vector<Rvector3> DiscretizedSensor::getCornerHeadings()
{
	return cornerHeadings;
}

/**
 *
 * Returns a vector of unit vectors (Rvector3) of the pixel poles.
 *
 * @return  The poleHeadings class member
 *
 */
std::vector<Rvector3> DiscretizedSensor::getPoleHeadings()
{
	return poleHeadings;
}
	


