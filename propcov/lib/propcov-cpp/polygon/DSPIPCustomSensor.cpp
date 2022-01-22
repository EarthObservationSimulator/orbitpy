#include "DSPIPCustomSensor.hpp"

//#define DEBUG_DSPIP

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
 * sensor FOV.  coneAngleVec[0] is paired with clockAngleVec[0], and so on.
 * 
 * 
 * @param coneAngleVec array of cone angles measured from +Z sensor axis (radians, expressed in Sensor frame)
 *        if xP,yP,zP is a UNIT vector describing a FOV point, then the 
 *        cone angle for the point is pi/2 - asin(zP);
 * @param clockAngleVec array of clock angles (right ascensions) (radians, expressed in Sensor frame)
 *        measured clockwise from the + X-axis.  if xP,yP,zP is a UNIT vector
 *        describing a FOV point, then the clock angle for the point
 *        is atan2(yP,xP);
 * @param interiorIn (cone, clock) angle of a point (radians, expressed in Sensor frame) 
 *        known to be contained in the sensor FOV.
 */
//------------------------------------------------------------------------------
DSPIPCustomSensor::DSPIPCustomSensor(const Rvector &coneAngleVecIn, const Rvector &clockAngleVecIn, AnglePair interiorIn) :
Sensor()
{
    std::vector<AnglePair> verticesIn(coneAngleVecIn.GetSize());
    for (int i = 0; i < coneAngleVecIn.GetSize(); i++)
    {        
        verticesIn[i][0] = coneAngleVecIn[i];
        verticesIn[i][1] = clockAngleVecIn[i];
    }
    
    // initialize the poly object with the vertices, interior point in the Inital (Sensor Body) frame
    poly = new SlicedPolygon(verticesIn, interiorIn);

    Preprocessor* prep = new SliceArray(poly->getLonArray(),poly->getEdgeArray());
    prep->preprocess();
    poly->addPreprocessor(prep);

    /// TODO: Move the below snippet into a Max() function in the Sensor class. It is also available in the GMATCustomSensor class.
    Real maxval = coneAngleVecIn[0];
    Integer N = coneAngleVecIn.GetSize();
    for (int i = 0; i < N; i++)
        if (coneAngleVecIn[i] > maxval)
            maxval = coneAngleVecIn[i];
    maxExcursionAngle = maxval;

    // Make the rotation matrix from spacecraft body to Sensor Query frame
    QI = poly->getQI();
    Rot_ScBody2SensorQuery = QI*R_SB; 

}

DSPIPCustomSensor::~DSPIPCustomSensor()
{
    delete(poly);
}

//------------------------------------------------------------------------------
// bool CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle)
//------------------------------------------------------------------------------
/*
 * determines if point represented by a cone angle and a clock angle (in Query frame) is in the
 * sensor's field of view, returns true if this is so
 *
 * @param   viewConeAngle     cone angle for point being tested (rad) (Should be in the Query frame)
 * @param   viewClockAngle    clock angle for point being tested (rad) (Should be in the Query frame)
 * @return  returns true if point is within sensor field of view
 *
 */
//------------------------------------------------------------------------------
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
        return poly->contains(query, "Query");
   }
}

//------------------------------------------------------------------------------
//  void SetSensorBodyOffsetAngles(Real angle1, Real angle2, Real angle3,
//                                 Integer seq1, Integer seq2, Integer seq3)
//------------------------------------------------------------------------------
/**
 * Sets the euler angles and sequence for the sensor
 *
 * @param angle1 The euler angle 1 (degrees)
 * @param angle2 The euler angle 2 (degrees)
 * @param angle3 The euler angle 3 (degrees)
 * @param seq1   Euler sequence 1
 * @param seq2   Euler sequence 2
 * @param seq3   Euler sequence 3
 */
//------------------------------------------------------------------------------
void DSPIPCustomSensor::SetSensorBodyOffsetAngles(
             Real angle1, Real angle2, Real angle3,
             Integer seq1, Integer seq2, Integer seq3)
{
   offsetAngle1  = angle1;
   offsetAngle2  = angle2;
   offsetAngle3  = angle3;
   eulerSeq1     = seq1;
   eulerSeq2     = seq2;
   eulerSeq3     = seq3;
   
   ComputeBodyToSensorMatrix(); // sets the R_SB instance variable in the parent Sensor class
   Rot_ScBody2SensorQuery = QI*R_SB; // sets the rotation matrix from spacecraft body to sensor Query frame
}

//------------------------------------------------------------------------------
/**
 * Returns the rotation matrix from the spacecraft-body frame to the sensor frame.
 * Function has been overloaded to return the spacecraft-body to sensor query frame.
 *
 * @param forTime  time at which to get the body-to-sensor matrix <unused>
 */
//------------------------------------------------------------------------------
Rmatrix33 DSPIPCustomSensor::GetBodyToSensorMatrix(Real forTime)
{
    return Rot_ScBody2SensorQuery;
}

// Returns transformation matrix from initial to query frame
Rmatrix33 DSPIPCustomSensor::getQI()
{
	return QI;
}