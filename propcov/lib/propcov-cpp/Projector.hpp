#ifndef Projector_hpp
#define Projector_hpp

#include "gmatdefs.hpp"
#include "DiscretizedSensor.hpp"
#include "Spacecraft.hpp"
#include "Earth.hpp"
#include <math.h>
#include "BodyFixedStateConverter.hpp"

typedef std::pair<std::vector<AnglePair>,std::vector<Rvector3>> CoordsPair;

class Projector
{
public:

	// Class construction and destruction
	Projector(Spacecraft *sat,DiscretizedSensor *sensor);
	
	// Pixel center projection onto earth
	CoordsPair checkIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	CoordsPair checkIntersection();
	
	// Pole projection onto earth for each FPA row/col
	virtual CoordsPair checkPoleIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	virtual CoordsPair checkPoleIntersection();
	
	// Pixel corner projection onto earth
	CoordsPair checkCornerIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	CoordsPair checkCornerIntersection();
	
	// Core projection algorithm for a single heading
	AnglePair projectionAlg(Real clock,Real cone,const Rvector3 &sphericalPos);
	
	// Coordinate conversion
	std::vector<AnglePair> unitVectorToClockCone(const std::vector<Rvector3> &cartesianHeadings);
	Rvector6 getEarthFixedState(Real jd,const Rvector6 &state_I);
	Rvector3 latLonToCartesian(AnglePair latLon);
	AnglePair cartesianToLatLon(Rvector3 &cart);
	Real constrainLongitude(Real lon);
	
	// Matrix coordinate conversion
	Rmatrix33 getNadirToSpacecraftAccessMatrix(const Rvector6 &state_ECF);
	Rmatrix33 getSensorToSpacecraftAccessMatrix(const Rvector6 &state_ECF);
	Rmatrix33 getSensorToNadirMatrix();

protected:

	Spacecraft *sc;
   	Earth *centralBody;
   	DiscretizedSensor *sensor;
};
#endif // Projector_hpp
