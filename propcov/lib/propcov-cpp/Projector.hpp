#ifndef Projector_hpp
#define Projector_hpp

#include "gmatdefs.hpp"
#include "DiscretizedSensor.hpp"
#include "Spacecraft.hpp"
#include "Earth.hpp"
#include <math.h>
#include "BodyFixedStateConverter.hpp"

class Projector
{
public:

	// Class construction and destruction
	Projector(Spacecraft *sat,DiscretizedSensor *sensor);
	
	// Pixel center projection onto earth
	std::vector<AnglePair> checkIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	std::vector<AnglePair> checkIntersection();
	
	// Pole projection onto earth for each FPA row/col
	virtual std::vector<Rvector3> checkPoleIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	virtual std::vector<Rvector3> checkPoleIntersection();
	
	// Pixel corner projection onto earth
	std::vector<AnglePair> checkCornerIntersection(const Rvector6 &stateECF);
	// Uses state vector stored in the Spacecraft class member
	std::vector<AnglePair> checkCornerIntersection();
	
	// Core projection algorithm for a single heading
	AnglePair projectionAlg(Real clock,Real cone,const Rvector3 &sphericalPos);
	
	// Coordinate conversion
	std::vector<AnglePair> unitVectorToClockCone(const std::vector<Rvector3> &cartesianHeadings);
	Rvector6 getEarthFixedState(Real jd,const Rvector6 &state_I);
	
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
