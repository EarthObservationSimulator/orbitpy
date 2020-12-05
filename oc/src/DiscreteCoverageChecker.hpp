#ifndef DiscreteCoverageChecker_hpp
#define DiscreteCoverageChecker_hpp

#include "gmatdefs.hpp"
#include "DiscretizedSensor.hpp"
#include "Spacecraft.hpp"
#include "Earth.hpp"
#include <math.h>
#include "BodyFixedStateConverter.hpp"

class DiscreteCoverageChecker
{
public:

	// Class construction and destruction
	DiscreteCoverageChecker(Spacecraft *sat,DiscretizedSensor *sensor);
	
	// Pixel center projection onto earth
	std::vector<AnglePair> checkIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	std::vector<AnglePair> checkIntersection();
	
	// Pole projection onto earth for each FPA row/col
	std::vector<Rvector3> checkPoleIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	std::vector<Rvector3> checkPoleIntersection();
	
	// Pixel corner projection onto earth
	std::vector<AnglePair> checkCornerIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	std::vector<AnglePair> checkCornerIntersection();
	
	// Core projection algorithm for a single heading
	AnglePair projectionAlg(Real clock,Real cone,const Rvector3 &sphericalPos);
	
	// Coordinate conversion
	Rmatrix33 getNadirToSpacecraftAccessMatrix(const Rvector6 &state_ECF);
	std::vector<AnglePair> unitVectorToClockCone(const std::vector<Rvector3> &cartesianHeadings);
	Rvector6 getEarthFixedState(Real jd,const Rvector6 &state_I);

protected:

	Spacecraft *sc;
   	Earth *centralBody;
   	DiscretizedSensor *sensor;
};
#endif // DiscreteCoverageChecker_hpp
