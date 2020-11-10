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

	/// class construction/destruction
	DiscretizedSensor(Real angleWidthIn, Real angleHeightIn, Integer widthDetectors, Integer heightDetectors);
	~DiscretizedSensor();
	
	// Generate a vector of headings from the input, specified by
	// right ascension and declination.
	virtual std::vector<AnglePair> generateRADEC();
	
	// Convert a vector of right ascension and declination values
	// into a vector of cartesian values.
	virtual void generateCartesianHeadings(std::vector<AnglePair> RADEC);
	
	// To satisfy sensor class contract
	bool CheckTargetVisibility(Real,Real);
	
	// Getters and Setters
	
	Real getwFOV();
	Real gethFOV();
	virtual std::vector<Rvector3> getCartesianHeadings();

protected:

	Real angleWidth;
	Real angleHeight;
	Integer widthDetectors;
	Integer heightDetectors;
	Real wFOV;
	Real hFOV;
	
	std::vector<Rvector3> cartesianHeadings;
};
#endif // DiscretizedSensor_hpp
