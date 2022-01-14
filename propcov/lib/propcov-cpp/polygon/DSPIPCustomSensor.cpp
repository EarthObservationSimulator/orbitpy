#include "DSPIPCustomSensor.hpp"

//------------------------------------------------------------------------------
// public methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// DSPIPCustomSensor(const Rvector& coneAngleVecIn, const Rvector& clockAngleVecIn, AnglePair contained)
//------------------------------------------------------------------------------
/**
 * Constructor
 *
 * coneAngleVec and clockAngleVec contain pairs of angles that describe the 
 * sensor FOV.  coneAngleVec[0] is paired with clockAngleVec[0], 
 * 
 * @param coneAngleVec array of cone angles measured from +Z sensor axis (radians)
 *        if xP,yP,zP is a UNIT vector describing a FOV point, then the 
 *        cone angle for the point is pi/2 - asin(zP);
 * @param clockAngleVec array of clock angles (right ascensions) (radians)
 *        measured clockwise from the + X-axis.  if xP,yP,zP is a UNIT vector
 *        describing a FOV point, then the clock angle for the point
 *        is atan2(yP,xP);
 * @param contained (cone, clock) angle of a point (radians, expressed in Sensor frame) 
 *        known to be contained in the sensor FOV.
 */
//------------------------------------------------------------------------------
DSPIPCustomSensor::DSPIPCustomSensor(const Rvector &coneAngleVecIn, const Rvector &clockAngleVecIn, AnglePair contained) :
Sensor()
{
    std::vector<AnglePair> vertices(coneAngleVecIn.GetSize());
    for (int i = 0; i < coneAngleVecIn.GetSize(); i++)
    {
        vertices[i][0] = coneAngleVecIn[i];
        vertices[i][1] = clockAngleVecIn[i];
    }

    poly = new SlicedPolygon(vertices,contained);
    Preprocessor* prep = new SliceArray(poly->getLonArray(),poly->getEdgeArray());
    prep->preprocess();
    poly->addPreprocessor(prep);
}

DSPIPCustomSensor::~DSPIPCustomSensor()
{
    delete(poly);
}

bool DSPIPCustomSensor::CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle)
{
    AnglePair query = {viewConeAngle,viewClockAngle};
    return poly->contains(query);
}