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
// Created: 2016.05.02
//
/**
 * Implementation of the Sensor class
 */
//------------------------------------------------------------------------------
#include <iostream>
#include "gmatdefs.hpp"
#include "Sensor.hpp"
#include "GmatConstants.hpp"
#include "AttitudeConversionUtility.hpp"
#include "GmatConstants.hpp"

//#define DEBUG_SENSOR
//------------------------------------------------------------------------------
// static data
//------------------------------------------------------------------------------
// None

//------------------------------------------------------------------------------
// public methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// Sensor(Real angle1, Real angle2, Real angle3,
//        Integer seq1, Integer seq2, Integer seq3)
//------------------------------------------------------------------------------
/**
 * Constructor
 * 
 * @param angle1 The euler angle 1 (degrees)
 * @param angle2 The euler angle 2 (degrees)
 * @param angle3 The euler angle 3 (degrees)
 * @param seq1   Euler sequence 1
 * @param seq2   Euler sequence 2
 * @param seq3   Euler sequence 3
 */
//------------------------------------------------------------------------------
Sensor::Sensor(Real angle1, Real angle2, Real angle3,
               Integer seq1, Integer seq2, Integer seq3) :
   maxExcursionAngle (0.0),
   offsetAngle1      (angle1),
   offsetAngle2      (angle2),
   offsetAngle3      (angle3),
   eulerSeq1         (seq1),
   eulerSeq2         (seq2),
   eulerSeq3         (seq3)
{
   ComputeBodyToSensorMatrix();
}

//------------------------------------------------------------------------------
// Sensor(const Sensor &copy)
//------------------------------------------------------------------------------
/**
 * Copy constructor
 * 
 * @param copy object to copy
 */
//------------------------------------------------------------------------------
Sensor::Sensor(const Sensor &copy) :
   maxExcursionAngle (copy.maxExcursionAngle),
   offsetAngle1      (copy.offsetAngle1),
   offsetAngle2      (copy.offsetAngle2),
   offsetAngle3      (copy.offsetAngle3),
   eulerSeq1         (copy.eulerSeq1),
   eulerSeq2         (copy.eulerSeq2),
   eulerSeq3         (copy.eulerSeq3),
   R_SB              (copy.R_SB)
{
}

//------------------------------------------------------------------------------
// Sensor& operator=(const Sensor &copy)
//------------------------------------------------------------------------------
/**
 * The operator= for the Sensor
 * 
 * @param copy object to copy
 */
//------------------------------------------------------------------------------
Sensor& Sensor::operator=(const Sensor &copy)
{
   if (&copy == this)
      return *this;
   
   maxExcursionAngle    = copy.maxExcursionAngle;
   offsetAngle1         = copy.offsetAngle1;
   offsetAngle2         = copy.offsetAngle2;
   offsetAngle3         = copy.offsetAngle3;
   eulerSeq1            = copy.eulerSeq1;
   eulerSeq2            = copy.eulerSeq2;
   eulerSeq3            = copy.eulerSeq3;
   R_SB                 = copy.R_SB;
   
   return *this;
}

//------------------------------------------------------------------------------
// ~Sensor()
//------------------------------------------------------------------------------
/**
 * Destructor
 * 
 */
//------------------------------------------------------------------------------
Sensor::~Sensor()
{
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
void Sensor::SetSensorBodyOffsetAngles(
             Real angle1, Real angle2, Real angle3,
             Integer seq1, Integer seq2, Integer seq3)
{
   offsetAngle1  = angle1;
   offsetAngle2  = angle2;
   offsetAngle3  = angle3;
   eulerSeq1     = seq1;
   eulerSeq2     = seq2;
   eulerSeq3     = seq3;
   
   ComputeBodyToSensorMatrix(); // sets the R_SB instance variable
}


//------------------------------------------------------------------------------
//  Rmatrix33 GetBodyToSensorMatrix(Real forTime)
//------------------------------------------------------------------------------
/**
 * Returns the rotation matrix from the body frame to the sensor frame.
 *
 * @param forTime  time at which to get the body-to-sensor matrix <unused>
 */
//------------------------------------------------------------------------------
Rmatrix33 Sensor::GetBodyToSensorMatrix(Real forTime)
{
   #ifdef DEBUG_SENSOR
      std::cout<<"Sensor::GetBodyToSensorMatrix function has been called \n";
   #endif
   return R_SB;
}

//------------------------------------------------------------------------------
// protected methods
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
//  bool CheckTargetMaxExcursionAngle(Real viewConeAngle)
//------------------------------------------------------------------------------
/**
 * Checks if the target lies inside the max excursion angle
 * TODO: Check that the range of the entered angle makes sense.
 *
 * @param viewConeAngle  the view cone angle (rad)
 *
 * @return true if the point lies inside the max excursion angle; 
 *         false otherwise
 */
//------------------------------------------------------------------------------
bool Sensor::CheckTargetMaxExcursionAngle(Real viewConeAngle)
{
   // Check if the target lies inside the max excursion angle
   if (viewConeAngle < maxExcursionAngle)
      return true;
   return false;
}

//------------------------------------------------------------------------------
//  void ComputeBodyToSensorMatrix()
//------------------------------------------------------------------------------
/**
 * Computes the rotation matrix from the body frame to the sensor frame.
 */
//------------------------------------------------------------------------------
void Sensor::ComputeBodyToSensorMatrix()
{
   Rvector3 angles(offsetAngle1 * GmatMathConstants::RAD_PER_DEG,
                   offsetAngle2 * GmatMathConstants::RAD_PER_DEG,
                   offsetAngle3 * GmatMathConstants::RAD_PER_DEG);
   R_SB = AttitudeConversionUtility::ToCosineMatrix(angles, eulerSeq1,
                                                    eulerSeq2, eulerSeq3);
}

// coordinate conversion utilities

//------------------------------------------------------------------------------
// void ConeClocktoRADEC(Real coneAngle, Real clockAngle, Real &RA, Real &dec);
//------------------------------------------------------------------------------
/* converts cone and clock angles to right ascension and declination.
 * Cone angle is defined about the z-axis (boresight).
 *
 * @param coneAngle  [in] (rad) cone angle to be converted
 * @param clockAngle [in] (rad) clock angle to be converted
 * @param RA         [out] (rad) computed right ascension
 * @param dec        [out] (rad) computed declination
 */
//------------------------------------------------------------------------------
void Sensor::ConeClocktoRADEC(Real coneAngle, Real clockAngle,
                              Real &RA, Real &dec)
{
   RA = clockAngle;
   dec = GmatMathConstants::PI/2 - coneAngle;
}

//------------------------------------------------------------------------------
// Rvector3 RADECtoUnitVec(Real RA, Real dec)
//------------------------------------------------------------------------------
/*
 * converts right ascension and declination angles to a unit vector
 *
 * @param   right ascension (rad)
 * @param   declination (rad)
 *
 * @return  unit vector for point represented by (RA,dec)
 *
 */
//------------------------------------------------------------------------------
Rvector3 Sensor::RADECtoUnitVec(Real RA, Real dec)
{
   Rvector3 u;
   Real cosDec = cos(dec);
   u[0] = cosDec * cos(RA);
   u[1] = cosDec * sin(RA);
   u[2] = sin(dec);
   return u;
}
//------------------------------------------------------------------------------
// void UnitVecToStereographic(const Rvector3 &U, Real &xCoord, Real &yCoord)
//------------------------------------------------------------------------------
/*
 * converts a 3-d unit vector to a 2-d stereographic projection
 *
 * @param u        [in] unit vector to be converted into stereographic 
 *                 projection
 * @param xCoord   [out] x coordinate of resulting stereographic projection
 * @param yCoord   [out] y coordinate of resulting stereographic projection
 *
 */
//------------------------------------------------------------------------------
void Sensor::UnitVecToStereographic(const Rvector3 &u,
                                    Real &xCoord, Real &yCoord)
{
   xCoord = u[0] / (1+u[2]);
   yCoord = u[1] / (1+u[2]);
}

//------------------------------------------------------------------------------
// ConeClocktoStereographic(Real coneAngle, Real clockAngle,
//                          Real &xCoord, Real &yCoord);
//------------------------------------------------------------------------------
/*
 * converts a (coneAngle, clockAngle) pair into stereographic projection
 * yielding an x and a y coordinate in that projection.
 *
 * @param coneAngle      [in] cone angle to be converted (rad)
 * @param clockAngle     [in] clock angle to be converted (rad)
 * @param xCoord         [out] x coordinate of resulting projection
 * @param yCoord         [out] y coordinate of resulting projection
 *
 */
//------------------------------------------------------------------------------
void Sensor::ConeClockToStereographic(Real coneAngle, Real clockAngle,
                                      Real &xCoord, Real &yCoord)
{
   Real RA, dec;
   ConeClocktoRADEC(coneAngle,clockAngle,RA,dec);
   Rvector3 unitVec = RADECtoUnitVec(RA,dec);
   UnitVecToStereographic(unitVec,xCoord,yCoord);
}

//------------------------------------------------------------------------------
// coneClockArraysToStereographic(const Rvector &coneAngleVec,
//                                const Rvector &clockAngleVec,
//                                Rvector &xArray, Rvector &yArray)
/*
 * converts the cone and clock angles in their respective Rectors
 * to stereographic projection coordinates in their respective Rvectors. Each
 * pair of vectors represents a set of points that when connnected by line
 * segments enclose a region.
 *
 * @param coneAngleVec  [in] vector of cone angles (rad)
 * @param clockAngleVec [in] vector of clock angles (rad)
 * @param xArray        [out] resulting vector of x values 
 *                      (stereographic projection)
 * @param yArray        [out] resulting vector of y values 
 *                      (stereographic projection)
 *
 */
//------------------------------------------------------------------------------
void Sensor::ConeClockArraysToStereographic(const Rvector &coneAngleVec,
                                            const Rvector &clockAngleVec,
                                            Rvector &xArray,
                                            Rvector &yArray)
{
   Real x,y;
   for (int i=0; i < coneAngleVec.GetSize(); i++)
   {
      ConeClockToStereographic(coneAngleVec.GetElement(i),
                               clockAngleVec.GetElement(i),x,y);
      xArray.SetElement(i,x);
      yArray.SetElement(i,y);
   }
   
}

// internal utilities for Rvector and coordinate conversion

// Rvector utilities

//------------------------------------------------------------------------------
// void Sort(Rvector &v, bool ascending = true)
//------------------------------------------------------------------------------
/*
 * sorts an rVector into ascending or descending order, in place
 * NOTE: THIS COULD BE MOVED INTO RVECTOR ITSELF AS A MEMBER FUNCTION
 *
 * @param   v  vector to be sorted
 * @param   Ascending indicates ascending sort if true, descending if false
 *
 */
//------------------------------------------------------------------------------
void Sensor::Sort(Rvector &v, bool ascending)
{
   // load list with Rvector & sort it
   Integer size = v.GetSize();
   std::list<Real> rList;
   for (int i = 0; i < size; i++)
      rList.push_back(v[i]);
   rList.sort();
   
   // move back to Rvector in either ascending or descending order
   if (ascending)
      for (int i = 0; i < size; i++)
      {
         v[i] = rList.front();
         rList.pop_front();
      }
   else // descending
      for (int i = 0; i < size; i++)
      {
         v[i] = rList.back();
         rList.pop_back();
      }
}


//------------------------------------------------------------------------------
// void Sort(Rvector &v, IntegerArray &indices, bool ascending = true)
//------------------------------------------------------------------------------
/*
 * sorts an rVector into ascending or descending order, in place
 * NOTE: THIS COULD BE MOVED INTO RVECTOR ITSELF AS A MEMBER FUNCTION
 *
 * @param   v  vector to be sorted
 * @param   indices  array of pre-sort indices of sorted vector
 * @param   Ascending indicates ascending sort if true, descending if false
 *
 */
//------------------------------------------------------------------------------
void Sensor::Sort(Rvector &v, IntegerArray &indices, bool ascending)
{
   Integer size = v.GetSize();
   indices.resize(size);
   SensorElement e;
   std::list<SensorElement> eList;
   eList.clear();
   
   // load list with elements - real value from Rvector and corresponding index
   for (int i = 0; i<size; i++)
   {
      e.value = v[i];
      e.index = i;
      eList.push_back(e);
   }

   // sort with std::list sort function; providing necessary compare function
   eList.sort(CompareSensorElements);
   
   // eList now is ascending order, pull data off appropriate end of the list
   if (ascending)
   {
      for (int i = 0; i < size; i++)
      {
         e = eList.front();
         v[i] = e.value;
         indices[i] = e.index;
         eList.pop_front();
      }
   }
   else // descending, pull highest values off of back to load v
   {
      for (int i = 0; i < size; i++)
      {
         e = eList.back();
         v[i] = e.value;
         indices[i] = e.index;
         eList.pop_back();
      }
   }
}

//------------------------------------------------------------------------------
// Real Max(const Rvector &v)
//------------------------------------------------------------------------------
/**
 * returns maximum value from an Rvector
 *
 * @param v vector containing real values to select maximum from
 * @return  maximum value contained in vector
 */
//------------------------------------------------------------------------------
Real Sensor::Max(const Rvector &v)
{
   Real maxval = v[0];
   Integer N = v.GetSize();
   for (int i = 0; i < N; i++)
      if (v[i] > maxval)
         maxval = v[i];
   return maxval;
}

//------------------------------------------------------------------------------
// Real Min(const Rvector &v)
//------------------------------------------------------------------------------
/**
 * returns minimum value from an Rvector
 *
 * @param v vector containing real values to select minimum from
 * @return  minimum value contained in vector
 */
//------------------------------------------------------------------------------
Real Sensor::Min(const Rvector &v)
{
   Real minval = v[0];
   Integer N = v.GetSize();
   for (int i = 0; i < N; i++)
      if (v[i] < minval)
         minval = v[i];
   return minval;
}

//------------------------------------------------------------------------------
// bool CompareSensorElements(SensorElement e1, SensorElement e2)
//------------------------------------------------------------------------------
/**
 * compares 2 elements using ordering of values
 *
 * @param e1   first element in comparison
 * @param e2   second element in comparison
 * @return     true if value of e1 is less than value of e2, false otherwise
 *
 */
//------------------------------------------------------------------------------
bool CompareSensorElements(const SensorElement &e1, const SensorElement &e2)
{
   return e1.value < e2.value;
}
