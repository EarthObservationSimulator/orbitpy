#ifndef DiscretizedSensor_hpp
#define DiscretizedSensor_hpp

#include "gmatdefs.hpp"
#include "Sensor.hpp"
#include <math.h>

typedef std::array<Real,2> AnglePair;

const double pi = 3.14159265358979323846;

// Utilities
Rvector3 RADECToCartesian(AnglePair RADEC);

class DiscretizedSensor : public Sensor
{
public:

	// Class construction/destruction
	DiscretizedSensor(Real angleWidthIn, Real angleHeightIn, Integer widthDetectors, Integer heightDetectors);
	~DiscretizedSensor();
	
	// Generate a vector of RA/DEC headings of the centers
	virtual std::vector<AnglePair> generateRADEC();
	
	// Generate a vector of cartesian headings of the poles
	virtual std::vector<Rvector3> generatePoles();
	
	// Generate a vector of RA/DEC headings of the corners
	virtual std::vector<AnglePair> generateCorners();
	
	/*
	// Convert a vector of right ascension and declination values
	// into a vector of cartesian values.
	virtual void generateCartesianHeadings(std::vector<AnglePair> RADEC);
	*/
	
	// Convert a vector of right ascension and declination values
	// into a vector of cartesian values.
	virtual std::vector<Rvector3> genCartesianHeadings(std::vector<AnglePair> RADEC);
	
	// Get the index of an element at row, col on the focal plane array
	Integer getIndex(Integer row,Integer col,Integer numRows);
	
	// To satisfy sensor class contract
	bool CheckTargetVisibility(Real,Real);
	
	// Getters and Setters
	Real getwFOV();
	Real gethFOV();
	std::vector<Rvector3> getCartesianHeadings();
	std::vector<Rvector3> getCornerHeadings();
	std::vector<Rvector3> getPoleHeadings();

protected:

	Real angleWidth;
	Real angleHeight;
	Integer widthDetectors;
	Integer heightDetectors;
	Real wFOV;
	Real hFOV;
	
	// All cartesian
	std::vector<Rvector3> cartesianHeadings;
	std::vector<Rvector3> cornerHeadings;
	std::vector<Rvector3> poleHeadings;
};
#endif // DiscretizedSensor_hpp
