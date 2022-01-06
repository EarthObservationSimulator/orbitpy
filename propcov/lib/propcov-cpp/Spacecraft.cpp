//------------------------------------------------------------------------------
//                           Spacecraft
//------------------------------------------------------------------------------
// GMAT: General Mission Analysis Tool.
//
// Copyright (c) 2002 - 2017 United States Government as represented by the
// Administrator of the National Aeronautics and Space Administration.
// All Other Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// You may not use this file except in compliance with the License.
// You may obtain a copy of the License at:
// http://www.apache.org/licenses/LICENSE-2.0.
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied.   See the License for the specific language
// governing permissions and limitations under the License.
//
// Author: Wendy Shoan, NASA/GSFC
// Created: 2016.05.02
//
/**
 * Implementation of the Spacecraft class.
 */
//------------------------------------------------------------------------------

#include "gmatdefs.hpp"
#include "Spacecraft.hpp"
#include "TATCException.hpp"
#include "MessageInterface.hpp"
#include "AttitudeConversionUtility.hpp"
#include "GmatConstants.hpp"

#include <iostream>

//#define DEBUG_STATES
//#define DEBUG_CAN_INTERPOLATE

//------------------------------------------------------------------------------
// static data
//------------------------------------------------------------------------------
// None

//------------------------------------------------------------------------------
// public methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
//  Spacecraft(AbsoluteDate *epoch, OrbitState *state, Attitude *att,
//             LagrangeInterpolator *interp,
//             Real    angle1, Real angle2,  Real angle3,
//             Integer seq1,   Integer seq2, Integer seq3)
//------------------------------------------------------------------------------
/**
 * Default constructor for Spacecraft.
 *
 * @param epoch  The orbit epoch object
 * @param state  The orbit state object
 * @param att    The attitude object
 * @param interp The LagrangeInterpolator
 * @param angle1 The euler angle 1 (degrees)
 * @param angle2 The euler angle 2 (degrees)
 * @param angle3 The euler angle 3 (degrees)
 * @param seq1   Euler sequence 1
 * @param seq2   Euler sequence 2
 * @param seq3   Euler sequence 3
 *
 */
//------------------------------------------------------------------------------
Spacecraft::Spacecraft(AbsoluteDate *epoch, OrbitState *state, Attitude *att,
                       LagrangeInterpolator *interp,
                       Real angle1, Real angle2, Real angle3,
                       Integer seq1, Integer seq2, Integer seq3) :
   dragCoefficient  (2.0),
   dragArea         (2.0),
   totalMass        (200.0),
   orbitState       (state),
   orbitEpoch       (epoch),
   numSensors       (0),
   attitude         (att),
   interpolator     (interp)
{
   // sensorList is empty at start
   // R_Nadir2ScBody is identity if default angles are used
   
   offsetAngle1 = angle1;
   offsetAngle2 = angle2;
   offsetAngle3 = angle3;
   
   eulerSeq1    = seq1;
   eulerSeq2    = seq2;
   eulerSeq3    = seq3;
   
   ComputeNadirToBodyMatrix();
}


//------------------------------------------------------------------------------
//  Spacecraft(const Spacecraft &copy)
//------------------------------------------------------------------------------
/**
 * Copy constructor for Spacecraft.
 *
 * @param copy The spacecraft of which to create a copy
 * 
 */
//------------------------------------------------------------------------------
Spacecraft::Spacecraft(const Spacecraft &copy) :
   dragCoefficient  (copy.dragCoefficient),
   dragArea         (copy.dragArea),
   totalMass        (copy.totalMass),
   orbitState       ((copy.orbitState)->Clone()), // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   orbitEpoch       ((copy.orbitEpoch)->Clone()), // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   numSensors       (copy.numSensors),
   offsetAngle1     (copy.offsetAngle1),
   offsetAngle2     (copy.offsetAngle2),
   offsetAngle3     (copy.offsetAngle3),
   eulerSeq1        (copy.eulerSeq1),
   eulerSeq2        (copy.eulerSeq2),
   eulerSeq3        (copy.eulerSeq3),
   R_Nadir2ScBody   (copy.R_Nadir2ScBody)
{
   if (copy.numSensors > 0)
   {
      sensorList.clear();
      for (Integer ii = 0; ii < copy.numSensors; ii++)
         sensorList.push_back(copy.sensorList.at(ii)); 
   }
   if (copy.interpolator)
   {
      interpolator = (LagrangeInterpolator*) (copy.interpolator)->Clone(); // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   }
   if (copy.attitude)
   {
      attitude = (Attitude*) (copy.attitude)->Clone(); // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   }
}

//------------------------------------------------------------------------------
//  Spacecraft& operator=(const Spacecraft &copy)
//------------------------------------------------------------------------------
/**
 * operator= for Spacecraft.
 *
 * @param copy The spacecraft whose values to copy
 * 
 */
//------------------------------------------------------------------------------
Spacecraft& Spacecraft::operator=(const Spacecraft &copy)
{
   if (&copy == this)
      return *this;
   
   dragCoefficient  = copy.dragCoefficient;
   dragArea         = copy.dragArea;
   totalMass        = copy.totalMass;
   orbitState       = (copy.orbitState)->Clone();  // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   orbitEpoch       = (copy.orbitEpoch)->Clone();  // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   numSensors       = copy.numSensors;

   offsetAngle1     = copy.offsetAngle1;
   offsetAngle2     = copy.offsetAngle2;
   offsetAngle3     = copy.offsetAngle3;
   eulerSeq1        = copy.eulerSeq1;
   eulerSeq2        = copy.eulerSeq2;
   eulerSeq3        = copy.eulerSeq3;
   R_Nadir2ScBody   = copy.R_Nadir2ScBody;
   
   sensorList.clear();
   for (Integer ii = 0; ii < copy.numSensors; ii++)
      sensorList.push_back(copy.sensorList.at(ii));
   
   if (copy.interpolator)
   {
      interpolator = (LagrangeInterpolator*) (copy.interpolator)->Clone(); // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   }
   if (copy.attitude)
   {
      attitude = (Attitude*) (copy.attitude)->Clone(); // TODO: Clone this? Probably yes because the object can be changed by the Spacecraft class.
   }

   return *this;
}

//------------------------------------------------------------------------------
//  ~Spacecraft()
//------------------------------------------------------------------------------
/**
 * destructor for Spacecraft.
 *
 */
//------------------------------------------------------------------------------
Spacecraft::~Spacecraft()
{
   /** @todo: Vinay - I think that objects should be deleted outside and not by this class (since this class doesn't create the objects).
      Hence am commenting the originally written delete operations. Also having the delete operations creates problems with pybind11.    

      However when the copy operation is used, the objects are created by the Spacecraft class itself, in which case the deletion becomes 
      the responsibility of the Spacecraft class.            
   
   if (orbitState)
      delete orbitState;
   if (orbitEpoch)
      delete orbitEpoch;

   if (interpolator)
      delete interpolator;
   if (attitude)
      delete attitude;
   */   
}

//------------------------------------------------------------------------------
//  OrbitState* GetOrbitState()
//------------------------------------------------------------------------------
/**
 * Returns a pointer to the Spacecraft's OrbitState object.
 *
 * @return  pointer to the spacecraft's OrbitState
 * 
 */
//------------------------------------------------------------------------------
OrbitState* Spacecraft::GetOrbitState()
{
   return orbitState;
}

//------------------------------------------------------------------------------
//  AbsoluteDate* GetOrbitEpoch()
//------------------------------------------------------------------------------
/**
 * Returns a pointer to the Spacecraft's AbsoluteDate object.
 *
 * @return  pointer to the spacecraft's AbsoluteDate
 * 
 */
//------------------------------------------------------------------------------
AbsoluteDate* Spacecraft::GetOrbitEpoch()
{
   return orbitEpoch;
}

//------------------------------------------------------------------------------
//  Real GetJulianDate()
//------------------------------------------------------------------------------
/**
 * Returns the Spacecraft's Julian Date at Epoch.
 *
 * @return  Spacecraft's JulianDate
 * 
 */
//------------------------------------------------------------------------------
Real Spacecraft::GetJulianDate()
{
   return orbitEpoch->GetJulianDate();
}

//------------------------------------------------------------------------------
//  Attitude GetAttitude()
//------------------------------------------------------------------------------
/**
 * Returns the Spacecraft's attitude.
 *
 * @return  Spacecraft's attitude
 * 
 */
//------------------------------------------------------------------------------
Attitude* Spacecraft::GetAttitude()
{
   return attitude;
}


//------------------------------------------------------------------------------
//  Rvector6 GetCartesianState()
//------------------------------------------------------------------------------
/**
 * Returns the Spacecraft's cartesian state.
 *
 * @return  Spacecraft's cartesian state
 * 
 */
//------------------------------------------------------------------------------
Rvector6 Spacecraft::GetCartesianState()
{
   return orbitState->GetCartesianState();
}

//------------------------------------------------------------------------------
//  Rvector6 GetKeplerianState()
//------------------------------------------------------------------------------
/**
 * Returns the Spacecraft's Keplerian state.
 * @return  Spacecraft's Keplerian state
 * 
 */
//------------------------------------------------------------------------------
Rvector6 Spacecraft::GetKeplerianState()
{
   return orbitState->GetKeplerianState();
}


//------------------------------------------------------------------------------
//  void AddSensor(Sensor* sensor)
//------------------------------------------------------------------------------
/**
 * Adds the input sensor to the Spacecraft's sensor list.
 *
 * @param  sensor Sensor to add to the list
 * 
 */
//------------------------------------------------------------------------------
void Spacecraft::AddSensor(Sensor* sensor)
{
   /// @todo - check for sensor already on list!!
   sensorList.push_back(sensor);
   numSensors++;
}

//------------------------------------------------------------------------------
//  bool HasSensors()
//------------------------------------------------------------------------------
/**
 * Returns a flag indicating whether or not the spacecraft has sensors.
 *
 * @return  flag indicating whether or not the spacecraft has sensors.
 * 
 */
//------------------------------------------------------------------------------
bool Spacecraft::HasSensors()
{
   return (numSensors > 0);
}

//------------------------------------------------------------------------------
//  void SetDragArea(Real area)
//------------------------------------------------------------------------------
/**
* Sets the Spacecraft's drag area.
*
* @param  the drag area in m^2
*
*/
//------------------------------------------------------------------------------
void Spacecraft::SetDragArea(Real area)
{
	dragArea = area;
}

//------------------------------------------------------------------------------
//  void SetDragCoefficient(Real Cr)
//------------------------------------------------------------------------------
/**
* Sets the Spacecraft's drag coefficient.
*
* @param  the drag coefficient
*
*/
//------------------------------------------------------------------------------
void Spacecraft::SetDragCoefficient(Real Cd)
{
	dragCoefficient = Cd;
}

//------------------------------------------------------------------------------
//  void SetTotalMass(Real mass);
//------------------------------------------------------------------------------
/**
* Sets the Spacecraft's total mass.
*
* @param the total mass
*
*/
//------------------------------------------------------------------------------
void Spacecraft::SetTotalMass(Real mass)
{
	totalMass = mass;
}

//------------------------------------------------------------------------------
//  void SetAttitude(Attitude *att)
//------------------------------------------------------------------------------
/**
 * Sets the Spacecraft's attitude object
 *
 * @param att  the attitude object
 *
 */
//------------------------------------------------------------------------------
void Spacecraft::SetAttitude(Attitude *att)
{
   attitude = att;
}


//------------------------------------------------------------------------------
//  Real GetDragArea()
//------------------------------------------------------------------------------
/**
* Gets the Spacecraft's drag area.
*
* @return  the drag area in m^2
*
*/
//------------------------------------------------------------------------------
Real Spacecraft::GetDragArea()
{
	return dragArea;
}

//------------------------------------------------------------------------------
//  Real GetDragCoefficient()
//------------------------------------------------------------------------------
/**
* Gets the Spacecraft's drag coefficient.
*
* @return  the drag coefficient
*
*/
//------------------------------------------------------------------------------
Real Spacecraft::GetDragCoefficient()
{
	return dragCoefficient;
}

//------------------------------------------------------------------------------
//  Real GetTotalMass();
//------------------------------------------------------------------------------
/**
* Gets the Spacecraft's total mass.
*
* @return the total mass
*
*/
//------------------------------------------------------------------------------
Real Spacecraft::GetTotalMass()
{
	return totalMass;
}

//------------------------------------------------------------------------------
//  Rvector6 GetCartesianStateAtEpoch(const AbsoluteDate &atDate)
//------------------------------------------------------------------------------
/**
 * Gets the Spacecraft's cartesian state (Inertial) at the input time
 *
 * @param atDate  the date for which to get the cartesian state
 *
 * @return state
 *
 */
//------------------------------------------------------------------------------
Rvector6 Spacecraft::GetCartesianStateAtEpoch(const AbsoluteDate &atDate)
{
   return Interpolate(atDate.GetJulianDate());
}


//------------------------------------------------------------------------------
//  bool CheckTargetVisibility(Real    targetConeAngle,
//                             Real    targetClockAngle,
//                             Integer sensorNumber)
//------------------------------------------------------------------------------
/**
 * Returns a flag indicating whether or not the point is within the sensor FOV.
 * 
 * @param   targetConeAngle  the cone angle (evaluated in the Sensor frame)
 * @param   targetClockAngle the clock angle (evaluated in the Sensor frame)
 * @param   sensorNumber     sensor for which to check target visibility
 *
 * @return  true if point is visible, false otherwise
 *
 */
//------------------------------------------------------------------------------
bool Spacecraft::CheckTargetVisibility(Real    targetConeAngle,
                                       Real    targetClockAngle,
                                       Integer sensorNumber)
{
   if (numSensors == 0)
   {
      throw TATCException("ERROR - Spacecraft has no sensors\n");
   }

   if ((sensorNumber < 0) || (sensorNumber >= numSensors))
      throw TATCException(
            "ERROR - sensor number out-of-bounds in Spacecraft\n");

   return sensorList.at(sensorNumber)->CheckTargetVisibility(targetConeAngle,
                                                             targetClockAngle);
}


//------------------------------------------------------------------------------
//  bool CheckTargetVisibility(const Rvector6 &bodyFixedState,
//                             const Rvector3 &satToTargetVec,
//                             Real            atTime,
//                             Integer         sensorNumber)
//------------------------------------------------------------------------------
/**
 * Returns a flag indicating whether or not the point is within the
 * sensor FOV at the given time, given the satToTargetVec. THe function first expresses the satellite-to-target
 * vector in the Sensor frame and then invokes the function to evaluate the targets presence/absence in sensor FOV.
 *
 * @param   bodyFixedState  input body fixed state
 * @param   satToTargetVec  spacecraft-to-target vector (vector expressed in body(Earth)-fixed frame)
 * @param   atTime          time for which to check the target visibility
 * @param   sensorNumber    sensor for which to check target visibility
 *
 * @return  true if point is visible, false otherwise
 *
 */
//------------------------------------------------------------------------------
bool Spacecraft::CheckTargetVisibility(const Rvector6 &bodyFixedState,
                                       const Rvector3 &satToTargetVec,
                                       Real            atTime,
                                       Integer         sensorNumber)
{

   Rmatrix33 R_EF2Nadir = GetBodyFixedToReference(bodyFixedState); 
   Rvector3  satToTarget_Sensor = // satToTarget_Sensor is vector expressed in Sensor frame
             sensorList.at(sensorNumber)->GetBodyToSensorMatrix(atTime) *
             (R_Nadir2ScBody * (R_EF2Nadir * satToTargetVec));
   Real cone, clock;
   VectorToConeClock(satToTarget_Sensor, cone, clock);
   return CheckTargetVisibility(cone, clock, sensorNumber);
}

//------------------------------------------------------------------------------
//  Rmatrix33 GetBodyFixedToReference(const Rvector6 &bfState)
//------------------------------------------------------------------------------
/**
 * Returns the body-fixed-to-reference (Earth-fixed to Nadir) rotation matrix, given the input state in body(Earth)-fixed frame.
 *
 * @param bfState  body-fixed state
 *
 * @return  bodyfixed-to-reference matrix
 *
 */
Rmatrix33 Spacecraft::GetBodyFixedToReference(const Rvector6 &bfState) 
{
   return attitude->BodyFixedToReference(bfState);
}

//------------------------------------------------------------------------------
//  bool SetOrbitEpochOrbitStateKeplerian(const AbsoluteDate &t,
//                     const Rvector6     &kepl)
//------------------------------------------------------------------------------
/*
 * Sets the orbit state and corresponding epoch on the Spacecraft.
 *
 * @param t      input time
 * @param kepl   input keplerian elements (SMA[km], ECC, INC[rad], RAAN[rad], AOP[rad], TA[rad])
 *
 * @return  true if set; false otherwise
 *
 */
//------------------------------------------------------------------------------ @TODO: Vinay: Set date also?
bool Spacecraft::SetOrbitEpochOrbitStateKeplerian(const AbsoluteDate &t,
                               const Rvector6     &kepl)
{
   if (!interpolator)
      throw TATCException(
            "Cannot interpolate - no interpolator set on spacecraft\n");
   // Set the Spacecraft's orbitEpoch and orbitState parameters
   orbitEpoch->SetJulianDate(t.GetJulianDate()); 
   orbitState->SetKeplerianVectorState(kepl);
   
   // pass data to the interpolator, in Cartesian state
   Rvector6 cart = orbitState->GetCartesianState();
   #ifdef DEBUG_STATES
      MessageInterface::ShowMessage(
                        "About to set date and state on the interpolator:\n");
      MessageInterface::ShowMessage("date: %12.10f\n", t.GetJulianDate());
      for (Integer ii = 0; ii < 6; ii++)
         MessageInterface::ShowMessage("  %12.10f\n", cart[ii]);
   #endif
   Real     cartReal[6];
   for (Integer ii = 0; ii < 6; ii++)
      cartReal[ii] = cart[ii];
   interpolator->AddPoint(t.GetJulianDate(), cartReal);
   
   return true;
}


//------------------------------------------------------------------------------
//  bool SetOrbitEpochOrbitStateCartesian(const AbsoluteDate &t,
//                     const Rvector6     &kepl)
//------------------------------------------------------------------------------
/**
 * Sets the orbit state (along with corresponding epoch) on the Spacecraft
 *
 * @param t      input time
 * @param kepl   input Cartesian (Inertial frame) elements (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s])
 *
 * @return  true if set; false otherwise
 *
 */
bool  Spacecraft::SetOrbitEpochOrbitStateCartesian(const AbsoluteDate &t,
                                         const Rvector6 &cart)
{
   if (!interpolator)
      throw TATCException(
            "Cannot interpolate - no interpolator set on spacecraft\n");
   // Set the Spacecraft's orbitEpoch and orbitState parameters
   orbitEpoch->SetJulianDate(t.GetJulianDate()); 
   orbitState->SetCartesianState(cart);
   
   #ifdef DEBUG_STATES
      MessageInterface::ShowMessage(
                        "About to set date and state on the interpolator:\n");
      MessageInterface::ShowMessage("date: %12.10f\n", t.GetJulianDate());
      for (Integer ii = 0; ii < 6; ii++)
         MessageInterface::ShowMessage("  %12.10f\n", cart[ii]);
   #endif
   Real     cartReal[6];
   for (Integer ii = 0; ii < 6; ii++)
      cartReal[ii] = cart[ii];
   interpolator->AddPoint(t.GetJulianDate(), cartReal);
   
   return true;

} 


//------------------------------------------------------------------------------
//  void SetBodyNadirOffsetAngles(Real angle1, Real angle2, Real angle3,
//                                Integer seq1, Integer seq2,
//                                Integer seq3)
//------------------------------------------------------------------------------
/**
 * Sets the body nadir offset angles
 *
 * @param angle1      euler angle 1 (degrees)
 * @param angle2      euler angle 2 (degrees)
 * @param angle3      euler angle 3 (degrees)
 * @param seq1        euler sequence 1
 * @param seq2        euler sequence 2
 * @param seq3        euler sequence 3
 *
 */
//------------------------------------------------------------------------------
void Spacecraft::SetBodyNadirOffsetAngles(Real angle1, Real angle2, Real angle3,
                                          Integer seq1, Integer seq2,
                                          Integer seq3)
{
   offsetAngle1  = angle1;
   offsetAngle2  = angle2;
   offsetAngle3  = angle3;
   eulerSeq1     = seq1;
   eulerSeq2     = seq2;
   eulerSeq3     = seq3;
   
   ComputeNadirToBodyMatrix();
}

//------------------------------------------------------------------------------
//  bool CanInterpolate(Real atTime)
//------------------------------------------------------------------------------
/**
 * Can the orbit be interpolated (is it feasible given the number of points,
 * etc.?)
 *
 * @param atTime      input time
 * @param checkRange  check the range to see if we need to interpolate
 *
 * @return  true if interpolation is feasible;  false otherwise
 *
 */
//------------------------------------------------------------------------------
bool Spacecraft::CanInterpolate(Real atTime)
{
   if (!interpolator)
      return false;
   
   Integer canInterp = interpolator->IsInterpolationFeasible(atTime);
   
   #ifdef DEBUG_CAN_INTERPOLATE
      MessageInterface::ShowMessage(" ----- canInterp = %d\n",
                                    canInterp);
      Real lower, upper;
      interpolator->GetRange(lower, upper);
      MessageInterface::ShowMessage("   lower, upper = %12.10f  %12.10f\n",
                                    lower, upper);
   #endif
   
   if (canInterp != 1)
      return false;
   
   return true;
}

//------------------------------------------------------------------------------
//  bool TimeToInterpolate(Real atTime, Real &midRange)
//------------------------------------------------------------------------------
/**
 * Get the midpoint time to interpolate to, if
 *
 * @param atTime      [in]  input time
 * @param midRange    [out] middle of the interpolation range size
 *
 * @return  true if interpolation should be performed at the input time;
 *          false otherwise
 */
//------------------------------------------------------------------------------
bool Spacecraft::TimeToInterpolate(Real atTime, Real &midRange)
{
   if (!CanInterpolate(atTime))
      return false;
   
   Real lower, upper;
   interpolator->GetRange(lower, upper);
   
   midRange = (upper - lower) / 2.0;
   #ifdef DEBUG_CAN_INTERPOLATE
      MessageInterface::ShowMessage(" ----- midRange = %12.10f\n",
                                    midRange);
   #endif
   return true;
}

//------------------------------------------------------------------------------
//  Rvector6 Interpolate(Real toTime)
//------------------------------------------------------------------------------
/**
 * Interpolate the orbit data at the input time
 *
 * @param atTime      input time
 *
 * @return  interpolated state data
 *
 */
//------------------------------------------------------------------------------
Rvector6 Spacecraft::Interpolate(Real toTime)
{
   Rvector6 theResults;
   
   Real     interpResults[6];
   for (Integer ii = 0; ii < 6; ii++)
      interpResults[ii] = 0.0;

   if (!interpolator)
      throw TATCException(
            "Cannot interpolate - no GMAT interpolator set on spacecraft\n");
   if (!CanInterpolate(toTime))
      throw TATCException(
            "Cannot interpolate - interpolator does not have enough data\n");
   bool isInterpolated = interpolator->Interpolate(toTime, interpResults);
   #ifdef DEBUG_STATES
      if (!isInterpolated)
         MessageInterface::ShowMessage(" ---- did not interpolate!!!!!!!\n");
   #endif
   theResults.Set(interpResults);

   #ifdef DEBUG_STATES
      MessageInterface::ShowMessage("Results:\n"); // ***
      for (Integer ii = 0; ii < 6; ii++)
         MessageInterface::ShowMessage("   %12.10f\n", theResults[ii]);
   #endif
   
   return theResults;
}



//------------------------------------------------------------------------------
// protected methods
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
//  void VectorToConeClock(const Rvector3 &viewVec,
//                           Real &cone, Real &clock)
//------------------------------------------------------------------------------
/**
 * Computes the cone, clock angles of a given input vector.
 *
 * @param viewVec      [in]  input view vector
 * @param cone         [out] cone angle
 * @param clock        [out] clock angle
 *
 */
//------------------------------------------------------------------------------
void Spacecraft::VectorToConeClock(const Rvector3 &viewVec,
                                     Real &cone,
                                     Real &clock)
{
   Real targetDEC = GmatMathUtil::ASin(viewVec(2) / viewVec.GetMagnitude());
   cone   = GmatMathConstants::PI_OVER_TWO - targetDEC;
   clock  = GmatMathUtil::ATan2(viewVec(1), viewVec(0));
}


//------------------------------------------------------------------------------
//  void ComputeNadirToBodyMatrix()
//------------------------------------------------------------------------------
/**
 * Computes the rotation matrix from the Nadir pointing frame to Spacecraft body frame.
 */
//---------------------------------------------------------------------------
void Spacecraft::ComputeNadirToBodyMatrix()
{
   Rvector3 angles(offsetAngle1 * GmatMathConstants::RAD_PER_DEG,
                   offsetAngle2 * GmatMathConstants::RAD_PER_DEG,
                   offsetAngle3 * GmatMathConstants::RAD_PER_DEG);
   R_Nadir2ScBody = AttitudeConversionUtility::ToCosineMatrix(angles, eulerSeq1,
                                                    eulerSeq2, eulerSeq3);
}

Rmatrix33 Spacecraft::GetNadirToBodyMatrix(){
   return R_Nadir2ScBody;
}
