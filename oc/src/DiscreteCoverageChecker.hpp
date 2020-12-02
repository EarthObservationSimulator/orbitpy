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
	
	// Intersect with Earth
	std::vector<AnglePair> checkIntersection(const Rvector6 &stateECF);
	std::vector<AnglePair> checkIntersection();
	
	std::vector<Rvector3> checkPoleIntersection(const Rvector6 &stateECF);
	std::vector<AnglePair> checkCornerIntersection(const Rvector6 &stateECF);
	
	// Core projection algorithm for a single heading
	AnglePair projectionAlg(Real clock,Real cone,const Rvector3 &sphericalPos);
	
	// Projection for Poles
	//std::array<Real,3> poleProjectionAlg(Real clock,Real cone,const Rvector3 &sphericalPos);
	
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
