//------------------------------------------------------------------------------
//                           Sensor
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
// Created: 2017.03.21
//
/**
 * Definition of the base Sensor class. This class models a sensor.
 * The Sensor class maintains knowledge of the sensors orientation relative to the spacecraft body, 
 * and has a virtual-function (which must be defined in the child classes) to determines if a point is within the sensor field of view. 
 * It also defines a max-excursion angle which is the maximum cone angle corresponding to the sensor FOV (FOV could be of any shape).
 * 
 * There are three subclasses of Sensor. A conical sensor’s FOV is defined by a constant cone angle; 
 * <a rectangular sensor’s FOV is defined by angular width and angular height - INACTIVE>, both of which are symmetric around the boresight; 
 * and a custom sensor’s FOV is defined by an arbitrary set of points that are defined by cone and clock angle around the sensor frame’s +z axis. 
 * 
 * For nadir pointing instruments the boresight axis is aligned with the spacecraft +z axis, 
 * and the body to sensor rotation is generally defined as the 3x3 identity matrix or an 
 * equivalent representation (e.g., quaternion or Euler angles). 
 * The rotation is to be specified by means of Euler angles and sequence.
 * The rotation matrix rotates the coordinate system (See https://mathworld.wolfram.com/RotationMatrix.html). I.e. by performing
 * R_SB * vec_ScBody, the representation of the vector in the sensor body frame is found. (R_SB is the rotation matrix from the spacecraft-body
 * frame to the sensor frame and vec_ScBody is the vector in the spacecraft-body frame.)
 * 
 * The Sensor class provides a CheckTargetVisibility() method which is implemented by each of the subclasses. 
 * This function determines if a vector (which must be rotated into the sensor frame to make this test valid) 
 * is inside the field of view or not. For cone <and rectangular INACTIVE> sensors these involve simple inequality tests, 
 * for the custom sensor a sophisticated line crossing algorithm is used.
 * 
 * The class also includes utilities to convert coordinates between different coordinate-representations 
 * (cone/clock, right-ascension/ declination, unit-vector, stereographic).
 *
 */
//------------------------------------------------------------------------------
#ifndef Sensor_hpp
#define Sensor_hpp

#include "gmatdefs.hpp"
#include "Rmatrix33.hpp"
#include "Rvector.hpp"
#include "Rvector3.hpp"

class Sensor
{
public:
   
   /// class construction/destruction
   Sensor(Real angle1 = 0.0, Real angle2 = 0.0, Real angle3 = 0.0,
          Integer seq1 = 1, Integer seq2 = 2, Integer seq3 = 3);
   Sensor( const Sensor &copy);
   Sensor& operator=(const Sensor &copy);
   
   virtual ~Sensor();
   
   /// Set the sensor-to-body offset angles (in degrees)
   virtual void  SetSensorBodyOffsetAngles(
                        Real angle1 = 0.0, Real angle2 = 0.0, Real angle3 = 0.0,
                        Integer seq1 = 1, Integer seq2 = 2,   Integer seq3 = 3);
   /// Get the body-to-sensor matrix
   virtual Rmatrix33 GetBodyToSensorMatrix(Real forTime);
   
   //------------------------------------------------------------------------------
   // bool CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle = 0.0)
   //------------------------------------------------------------------------------
   /**
    * Check the target visibility given the input cone and clock angles:
    * determines whether or not the point is in the sensor FOV.
    *
    * @param viewConeAngle  cone angle (rad)
    * @param viewClockAngle clock angle (rad)
    *
    * @return true if point is in the sensor FOV; false otherwise
    *
    * @note This method is pure virtual and MUST be implemented in child
    *       classes
    */
   //---------------------------------------------------------------------------
   virtual bool  CheckTargetVisibility(Real viewConeAngle,
                                       Real viewClockAngle = 0.0) = 0;
   
protected:
   
   /// The maximum excursion angle
   Real          maxExcursionAngle;
   
   /// Offset angles and the euler sequence both define the rotation with respect to spacecraft body-frame. 
   /// Offset angles (degrees)
   Real          offsetAngle1;
   Real          offsetAngle2;
   Real          offsetAngle3;
   
   /// Euler sequence
   Integer       eulerSeq1;
   Integer       eulerSeq2;
   Integer       eulerSeq3;
   
   /// The rotation matrix from the spacecraft body frame to the sensor frame
   Rmatrix33     R_SB;
   
   /// Check the target maximum excursion angle
   virtual bool  CheckTargetMaxExcursionAngle(Real viewConeAngle);
   /// Compute the body-to-sensor matrix
   virtual void  ComputeBodyToSensorMatrix();
   
   /// Coordinate conversion utilities
   void ConeClocktoRADEC(Real coneAngle, Real clockAngle,
                         Real &RA, Real &dec);
   Rvector3 RADECtoUnitVec(Real RA, Real dec);
   void UnitVecToStereographic(const Rvector3 &u,
                               Real &xCoord, Real &yCoord);
   void ConeClockToStereographic(Real coneAngle, Real clockAngle,
                                 Real &xCoord, Real &yCoord);
   void ConeClockArraysToStereographic(const Rvector &coneAngleVec,
                                       const Rvector &clockAngleVec,
                                       Rvector &xArray, Rvector &yArray);

};
#endif // Sensor_hpp
