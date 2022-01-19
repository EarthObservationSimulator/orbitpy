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

    //maxExcursionAngle = Max(coneAngleVecIn); // in superclass Sensor
    Real maxval = coneAngleVecIn[0];
    Integer N = coneAngleVecIn.GetSize();
    for (int i = 0; i < N; i++)
        if (coneAngleVecIn[i] > maxval)
            maxval = coneAngleVecIn[i];
    maxExcursionAngle = maxval;
}

DSPIPCustomSensor::~DSPIPCustomSensor()
{
    delete(poly);
}

bool DSPIPCustomSensor::CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle)
{
   bool possiblyInView = true;
   // first check if in view cone, if so check stereographic box
   if (!CheckTargetMaxExcursionAngle(viewConeAngle))
        possiblyInView = false;
   
   // we've executed the quick tests, if point is possibly in the FOV
   // then run a line intersection test to determine if it is or not
   if (!possiblyInView)
        return false;
   else
   {    
        AnglePair query = {viewConeAngle,viewClockAngle};
        return poly->contains(query);
   }
}