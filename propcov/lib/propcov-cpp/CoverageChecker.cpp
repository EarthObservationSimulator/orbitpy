//------------------------------------------------------------------------------
//                           CoverageChecker
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
// Created: 2016.05.10
//
/**
 * Implementation of the CoverageChecker class
 */
//------------------------------------------------------------------------------
#include "gmatdefs.hpp"
#include "CoverageChecker.hpp"
#include "RealUtilities.hpp"
#include "GmatConstants.hpp"
#include "Rmatrix33.hpp"
#include "TATCException.hpp"
#include "MessageInterface.hpp"
#include <iostream>

//#define DEBUG_COV_CHECK
//#define DEBUG_COV_CHECK_FOV
//#define DEBUG_GRID

//------------------------------------------------------------------------------
// static data
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// public methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
//  CoverageChecker(PointGroup *ptGroup, Spacecraft *sat)
//------------------------------------------------------------------------------
/**
 * Constructor
 *
 * @param ptGroup  pointer to the PointGroup object to use
 * @param sat      pointer to the Spacecraft object to use
 */
//------------------------------------------------------------------------------
CoverageChecker::CoverageChecker(PointGroup *ptGroup, Spacecraft *sat) :
   pointGroup        (ptGroup),
   sc                (sat),
   centralBody       (NULL)
{
   pointArray.clear();
   feasibilityTest.clear();

   centralBody    = new Earth();
   centralBodyRadius = centralBody->GetRadius();

   Integer numPts = pointGroup->GetNumPoints();
   for (Integer ii = 0; ii < numPts; ii++)
   {     
      /// @TODO This should not be set here - we should store both
      /// positions and unitized positions in the PointGroup and
      /// then access those arrays when needed <<<<<<<<<<<<<<
      Rvector3 *ptPos1  = pointGroup->GetPointPositionVector(ii);
      Rvector3 *posUnit = new Rvector3(ptPos1->GetUnitVector());
      #ifdef DEBUG_GRID
         MessageInterface::ShowMessage("CovCheck: posUnit = %s\n",
                                       posUnit->ToString(12).c_str());
      #endif
      pointArray.push_back(posUnit);
      feasibilityTest.push_back(false);
   }
}

//------------------------------------------------------------------------------
//  CoverageChecker(const CoverageChecker &copy)
//------------------------------------------------------------------------------
/**
 * Copy constructor
 *
 * @param copy  the object to copy
 * 
 * @todo: Cloning required of the pointGroup, sc, centralBody objects? 
 * 
 */
//------------------------------------------------------------------------------
CoverageChecker::CoverageChecker(const CoverageChecker &copy) :
   pointGroup        (copy.pointGroup),
   sc                (copy.sc),
   centralBody       (copy.centralBody)
{  
   for (Integer ii = 0; ii < pointArray.size(); ii++)
      delete pointArray.at(ii);
   pointArray.clear();
   for (Integer ii = 0; ii < copy.pointArray.size(); ii++)
   {
      // these Rvector3s are coordinates (x,y,z)
      Rvector3 *rv = new Rvector3(*copy.pointArray.at(ii));
      pointArray.push_back(rv);
   }
   feasibilityTest.clear();
   for (Integer ff = 0; ff < copy.feasibilityTest.size(); ff++)
      feasibilityTest.push_back(copy.feasibilityTest.at(ff));
}

//------------------------------------------------------------------------------
//  CoverageChecker& operator=(const CoverageChecker &copy)
//------------------------------------------------------------------------------
/**
 * The operator= for the CoverageChecker object
 *
 * @param copy  the object to copy
 * 
 * @todo: Cloning required of the pointGroup, sc, centralBody objects? 
 * 
 */
//------------------------------------------------------------------------------
CoverageChecker& CoverageChecker::operator=(const CoverageChecker &copy)
{
   if (&copy == this)
      return *this;
   
   pointGroup        = copy.pointGroup;
   sc                = copy.sc;
   centralBody       = copy.centralBody;

   for (Integer ii = 0; ii < pointArray.size(); ii++)
      delete pointArray.at(ii);
   pointArray.clear();
   for (Integer ii = 0; ii < copy.pointArray.size(); ii++)
   {
      // these Rvector3s are coordinates (x,y,z)
      Rvector3 *rv = new Rvector3(*copy.pointArray.at(ii));
      pointArray.push_back(rv);
   }
   feasibilityTest.clear();
   for (Integer ff = 0; ff < copy.feasibilityTest.size(); ff++)
      feasibilityTest.push_back(copy.feasibilityTest.at(ff));

   return *this;
}

//------------------------------------------------------------------------------
//  ~CoverageChecker()
//------------------------------------------------------------------------------
/**
 * Destructor
 * 
 */
//------------------------------------------------------------------------------
CoverageChecker::~CoverageChecker()
{
   delete centralBody;
   for(int x = 0; x < pointArray.size(); x++)
   {
      delete pointArray[x];
   }
}

//------------------------------------------------------------------------------
//  IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &theState,
//                                                   Real           theTime, 
//                                                   const Rvector6 &cartState) 
//------------------------------------------------------------------------------
/**
 * Coverage calculation done for all points in PointGroup object
 * 
 * @param   centralBodyFixedState    central body fixed state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s]))
 * @param   theTime     time corresponding to the state of spacecraft (JDUT1)
 * @param   centralBodyInertialState   inertial state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s])) (UNUSED)
 *
 * @return  Array of point-indices (starting from 0) which are in-view of sensor/spacecraft
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &centralBodyFixedState,
                                                 Real           theTime, 
                                                 const Rvector6 &centralBodyInertialState)   
{
   const Integer numPts = pointGroup->GetNumPoints();
   IntegerArray PointIndices;
   for(int i=0; i < numPts; i++) // Coverage calculation done for all points in PointGroup object
   {
      PointIndices.push_back(i);
   }
   return CoverageChecker::CheckPointCoverage(centralBodyFixedState, theTime, centralBodyInertialState, PointIndices);
}
//------------------------------------------------------------------------------
//  IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &theState,
//                                                   Real           theTime, 
//                                                   const Rvector6 &cartState) 
//------------------------------------------------------------------------------
/**
 * Coverage calculation done select points in PointGroup object
 * 
 * @param   centralBodyFixedState  central body fixed state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s]))
 * @param   theTime                time corresponding to the state of spacecraft (JDUT1)
 * @param   centralBodyInertialState              inertial state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s])) (UNUSED)
 * @param   PointIndices           indices of points which are to be checked for coverage
 *
 * @return  Array of point-indices (starting from 0) which are in-view of sensor/spacecraft
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &centralBodyFixedState,
                                                 Real           theTime, 
                                                 const Rvector6 &centralBodyInertialState,
                                                 const IntegerArray &PointIndices)   
{
   #ifdef DEBUG_COV_CHECK
      MessageInterface::ShowMessage("In CoverageChecker::CheckPointCoverage\n");
      MessageInterface::ShowMessage("  theState = %s\n",
                                    theState.ToString(12).c_str());
   #endif
   // Check coverage given a spacecraft location in body fixed coordinates
   IntegerArray  result;
   AbsoluteDate  aDate;
   aDate.SetJulianDate(theTime);
   
   Integer       covCount              = 0;
   Rvector3      centralBodyFixedPos(centralBodyFixedState[0],
                                     centralBodyFixedState[1],
                                     centralBodyFixedState[2]);
   Rvector3      centralBodyFixedVel(centralBodyFixedState[3],
                                     centralBodyFixedState[4],
                                     centralBodyFixedState[5]);

   Rvector3 rangeVector;
   Integer  numPts = PointIndices.size();
    
   #ifdef DEBUG_COV_CHECK
      MessageInterface::ShowMessage(" --- numPoints from pointGroup = %d\n",
                                     numPts);
      MessageInterface::ShowMessage(" --- Checking Feasibility ...\n");
   #endif
   
   CheckGridFeasibility(centralBodyFixedPos); // line of sight test for each point, the `feasibilityTest` instance variable is updated 
   for ( Integer k = 0; k < numPts; k++)
   {
      // Simple line of sight test for each point
      // if (CheckGridFeasibility(pointIdx, centralBodyFixedPos)) // this is slower
      if (feasibilityTest.at(PointIndices[k])) //  > 0)
      {
         #ifdef DEBUG_COV_CHECK
            MessageInterface::ShowMessage(
                              " --- feasibility at point %d is TRUE!\n",
                              PointIndices[k]);
         #endif

         Integer  sensorNum = 0; // 1; // Currently only works for one sensor, hence hardcoded!!

         bool     inView    = false;
         Rvector3 pointLocation = (*pointArray.at(PointIndices[k])) *
                                   centralBodyRadius;
         Rvector3 satToTargetVec = pointLocation - centralBodyFixedPos;

//         Rmatrix33 R_fixed_to_nadir =
//                   sc->GetBodyToInertialMatrix(centralBodyFixedState);
//         Rvector3  viewVector = R_fixed_to_nadir * satToTargetVec;

         if (sc->HasSensors())
         {
            // NOTE - should be sc->ChTV(satToTargetVec, state, sensorNum);
            // Then the sc computes the R_NI, R_BN, and calls the sensor for
            // the R_SB to detmine the visibility
//            inView = sc->CheckTargetVisibility(viewVector, sensorNum);
            inView = sc->CheckTargetVisibility(centralBodyFixedState, satToTargetVec,
                                               theTime,  sensorNum);                 
         }
         else
         {
            // No sensor, just perform horizon test
            // Vinay: Doubtful of the below code. 
            rangeVector              = -satToTargetVec;
            Real rangeMag            = rangeVector.GetMagnitude();
            Real bodyFixedMag        = centralBodyFixedPos.GetMagnitude(); // Vinay: previously => centralBodyFixedState.GetMagnitude();
            Real cosineOffNadirAngle = rangeVector * centralBodyFixedPos /
                                       rangeMag / bodyFixedMag;
            Real offNadirAngle       = GmatMathUtil::ACos(cosineOffNadirAngle);
            if ((offNadirAngle < (GmatMathConstants::PI_OVER_TWO -
                                  GmatMathUtil::ACos(centralBodyRadius/bodyFixedMag)))
                                  && rangeVector(2) > 0.0)
               inView = true;
            else
               inView = false;
         }

         #ifdef DEBUG_COV_CHECK
            MessageInterface::ShowMessage(
                            " --- In CheckPointCoverage, centralBodyFixedState = %s\n",
                            centralBodyFixedState.ToString(12).c_str());
         #endif
         
         if (inView)
         {
            result.push_back(PointIndices[k]);   // covCount'th entry
            covCount++;
         }
      }
   }

   return result;
}



//------------------------------------------------------------------------------
// IntegerArray AccumulateCoverageData()
//------------------------------------------------------------------------------
/**
 * Check point coverage at the current date and spacecraft state. Author: Vinay
 *
 * @param PointIndices: Indices of the points (of the respective PointGroup object)
 *                      to be considered for coverage.
 * 
 * @return  array of indexes
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(IntegerArray PointIndices)
{
   // Accumulates coverage data after propagation update
   // Get the state and date here
   Real     theDate   = sc->GetJulianDate();
   Rvector6 cartState = sc->GetCartesianState();
   Rvector6 theState  = GetEarthFixedSatState(theDate, cartState);
   return CheckPointCoverage(theState, theDate, cartState, PointIndices);

}

//------------------------------------------------------------------------------
// IntegerArray AccumulateCoverageData()
//------------------------------------------------------------------------------
/**
 * Check point coverage at the current date and spacecraft state.
 *
 * @return  array of indexes
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage()
{
   const Integer numPts = pointGroup->GetNumPoints();
   IntegerArray PointIndices;
   for(int i=0; i < numPts; i++) // Coverage calculation done for all points in PointGroup object
   {
      PointIndices.push_back(i);
   }
   return CoverageChecker::CheckPointCoverage(PointIndices);
}


//------------------------------------------------------------------------------
// Rvector6 GetEarthFixedSatState(Real jd, const Rvector6& scCartState)
//------------------------------------------------------------------------------
/**
 * Returns the Earth-Fixed state at the specified time
 * 
 * @param jd  Julian date 
 *
 * @return  earth-fixed state at the input time
 * 
 */
//------------------------------------------------------------------------------
Rvector6 CoverageChecker::GetEarthFixedSatState(Real jd,
                                                const Rvector6& scCartState)
{
   // Converts state from Earth interial to Earth fixed
   Rvector3 inertialPos   = scCartState.GetR();
   Rvector3 inertialVel   = scCartState.GetV();
   // TODO.  Handle differences in units of points and states.
   // TODO.  This ignores omega cross r term in velocity, which is ok and 
   // perhaps desired for current use cases but is not always desired.
   Rvector3 centralBodyFixedPos  = centralBody->GetBodyFixedState(inertialPos,
                                                                  jd);
   Rvector3 centralBodyFixedVel  = centralBody->GetBodyFixedState(inertialVel,
                                                                  jd);
   Rvector6 earthFixedState(centralBodyFixedPos(0), centralBodyFixedPos(1),
                            centralBodyFixedPos(2),
                            centralBodyFixedVel(0), centralBodyFixedVel(1),
                            centralBodyFixedVel(2));
   return earthFixedState;
}

//------------------------------------------------------------------------------
// protected methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// bool CheckGridFeasibility(Integer         ptIdx,,
//                           const Rvector3& bodyFixedState)
//------------------------------------------------------------------------------
/**
 * Checks the grid feasibility
 *
 * @param   ptIdx             point index
 * @param   bodyFixedState    input body fixed state
 *
 * @return   output feasibility flag
 *
 */
//------------------------------------------------------------------------------
bool CoverageChecker::CheckGridFeasibility(Integer         ptIdx,
                                           const Rvector3& bodyFixedState)
{
#ifdef DEBUG_GRID
   MessageInterface::ShowMessage(
                     "CheckGridFeasibility: ptIDx = %d, bodyFixedState = %s\n",
                     ptIdx, bodyFixedState.ToString(12).c_str());
#endif
   bool     isFeasible = false;
//   Rvector3 rangeVec;  // defaults to all zeroes
   
   bfState  = bodyFixedState/centralBodyRadius;
   bodyUnit = bfState.GetUnitVector();

   ptPos    = *(pointArray.at(ptIdx));
   Real  feasibilityReal = ptPos * bodyUnit;
   
   if (feasibilityReal > 0.0)
   {
      rangeVec  = bfState - ptPos;
      Real dot  = rangeVec * ptPos;
      if (dot > 0.0)
         isFeasible = true;
   }
   return isFeasible;
}

//------------------------------------------------------------------------------
// void CheckGridFeasibility(const Rvector3& bodyFixedState)
//------------------------------------------------------------------------------
/**
 * Checks the grid feasibility
 *
 * @param   bodyFixedState    input body fixed state
 *
 */
//------------------------------------------------------------------------------
void CoverageChecker::CheckGridFeasibility(const Rvector3& bodyFixedState)
{
#ifdef DEBUG_GRID
   MessageInterface::ShowMessage("CheckGridFeasibility: bodyFixedState = %s\n",
                                 bodyFixedState.ToString(12).c_str());
#endif
   bfState  = bodyFixedState/centralBodyRadius;
   bodyUnit = bfState.GetUnitVector();
   
   for (Integer ii = 0; ii < pointArray.size(); ii++)
   {
      ptPos = *(pointArray.at(ii));
      if ((ptPos * bodyUnit) > 0.0)
      {
         rangeVec = bfState - ptPos;
         Real     dot   = rangeVec * ptPos;
         if (dot > 0.0)
            feasibilityTest.at(ii) = true;
         else
            feasibilityTest.at(ii) = false;
      }
   }
}


