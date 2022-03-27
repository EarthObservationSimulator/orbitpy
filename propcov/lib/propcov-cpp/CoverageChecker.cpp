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
//  CoverageChecker(Grid *ptGroup, Spacecraft *sat)
//------------------------------------------------------------------------------
/**
 * Constructor
 *
 * @param ptGroup  pointer to the Grid object to use
 * @param sat      pointer to the Spacecraft object to use
 */
//------------------------------------------------------------------------------
CoverageChecker::CoverageChecker(Grid *ptGroup, Spacecraft *sat, GridFilter* filter) :
   pointGroup        (ptGroup),
   sc                (sat),
   filter            (filter),
   centralBody       (NULL)
{
   centralBody    = new Earth();
   centralBodyRadius = centralBody->GetRadius();
}

//------------------------------------------------------------------------------
//  CoverageChecker(const CoverageChecker &copy)
//------------------------------------------------------------------------------
/**
 * Copy constructor
 *
 * @param copy  the object to copy
 * 
 * @todo: Cloning required of the pointGroup, sc, centralBody, pointArray objects? 
 * 
 */
//------------------------------------------------------------------------------
CoverageChecker::CoverageChecker(const CoverageChecker &copy) :
   pointGroup        (copy.pointGroup),
   sc                (copy.sc),
   centralBody       (copy.centralBody),
   filter            (copy.filter)
{}

//------------------------------------------------------------------------------
//  CoverageChecker& operator=(const CoverageChecker &copy)
//------------------------------------------------------------------------------
/**
 * The operator= for the CoverageChecker object
 *
 * @param copy  the object to copy
 * 
 * @todo: Cloning required of the pointGroup, sc, centralBody, pointArray objects? 
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
   filter            = copy.filter;

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
}

//------------------------------------------------------------------------------
// IntegerArray CheckPointCoverage()
//------------------------------------------------------------------------------
/**
 * Check point coverage for all points in the pointGroup object, at the current date and spacecraft state.
 *
 * @return  array of indexes
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage()
{
   const Integer numPts = pointGroup->GetNumPoints();
   IntegerArray PointIndices;
   for(int i=0; i < numPts; i++) // Coverage calculation done for all points in pointGroup object
   {
      PointIndices.push_back(i);
   }
   return CoverageChecker::CheckPointCoverage(PointIndices);
}

//------------------------------------------------------------------------------
// IntegerArray CheckPointCoverage(IntegerArray PointIndices)
//------------------------------------------------------------------------------
/**
 * Check point coverage at the current date and spacecraft state.
 *
 * @param PointIndices: Indices of the points (of the respective Grid object)
 *                      to be considered for coverage.
 * 
 * @return  array of indexes
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(IntegerArray PointIndices)
{
   // Get the state and date here
   Real     theDate   = sc->GetJulianDate();
   Rvector6 scCartState = sc->GetCartesianState();
   Rvector6 bodyFixedState  = GetCentralBodyFixedState(theDate, scCartState);
   return CheckPointCoverage(bodyFixedState, theDate, scCartState, PointIndices);

}

//------------------------------------------------------------------------------
//  IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &theState,
//                                                   Real           theTime, 
//                                                   const Rvector6 &cartState) 
//------------------------------------------------------------------------------
/**
 * Coverage calculation done for all points in Grid object
 * 
 * @param   bodyFixedState    central body fixed state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s]))
 * @param   theTime     time corresponding to the state of spacecraft (JDUT1)
 * @param   scCartState   inertial state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s])) (UNUSED)
 *
 * @return  Array of point-indices (starting from 0) which are in-view of sensor/spacecraft
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &bodyFixedState,
                                                 Real           theTime, 
                                                 const Rvector6 &scCartState)   
{
   const Integer numPts = pointGroup->GetNumPoints();
   IntegerArray PointIndices;
   for(int i=0; i < numPts; i++) // Coverage calculation done for all points in Grid object
   {
      PointIndices.push_back(i);
   }
   return CoverageChecker::CheckPointCoverage(bodyFixedState, theTime, scCartState, PointIndices);
}
//------------------------------------------------------------------------------
//  IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &theState,
//                                                   Real           theTime, 
//                                                   const Rvector6 &cartState) 
//------------------------------------------------------------------------------
/**
 * Coverage calculation done for select points in Grid object
 * 
 * @param   bodyFixedState      central body fixed state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s]))
 * @param   theTime                    time corresponding to the state of spacecraft (JDUT1)
 * @param   scCartState   inertial state of spacecraft (Cartesian (x[km], y[km], z[km], vx[km/s], vy[km/s], vz[km/s])) (UNUSED)
 * @param   PointIndices               indices of points which are to be checked for coverage
 *
 * @return  Array of point-indices (starting from 0) which are in-view of sensor/spacecraft
 *
 */
//------------------------------------------------------------------------------
IntegerArray CoverageChecker::CheckPointCoverage(const Rvector6 &bodyFixedState,
                                                 Real           theTime, 
                                                 const Rvector6 &scCartState,
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
   Rvector3      centralBodyFixedPos(bodyFixedState[0],
                                     bodyFixedState[1],
                                     bodyFixedState[2]);
   Rvector3      centralBodyFixedVel(bodyFixedState[3],
                                     bodyFixedState[4],
                                     bodyFixedState[5]);

   Rvector3 rangeVector;
   Integer  numPts = PointIndices.size();
    
   #ifdef DEBUG_COV_CHECK
      MessageInterface::ShowMessage(" --- numPoints from pointGroup = %d\n",
                                     numPts);
      MessageInterface::ShowMessage(" --- Checking Feasibility ...\n");
   #endif
   
   std::vector<bool> feasibilityTest = filter->FilterGrid(); // line of sight followed by horizon test for each point, the `feasibilityTest` instance variable is updated 
   
   // no performance difference
   //const std::vector<Rvector3*> gridpts = pointGroup->GetPointPositionVectors();
   for ( Integer k = 0; k < numPts; k++)
   {
      if (feasibilityTest.at(PointIndices[k]))
      {
         #ifdef DEBUG_COV_CHECK
            MessageInterface::ShowMessage(
                              " --- feasibility at point %d is TRUE!\n",
                              PointIndices[k]);
         #endif

         Integer  sensorNum = 0; // 1; // Currently only works for one sensor, hence hardcoded!!

         bool     inView    = false;         

         if (sc->HasSensors())
         {
            // The CheckTargetVisibility function first expresses the satToTargetVec in sensor frame and then 
            // evaluates its presence/absence in sensor FOV
            Rvector3 pointLocation = *(pointGroup->GetPointPositionVector(PointIndices[k]));
            Rvector3 satToTargetVec = pointLocation - centralBodyFixedPos;
            inView = sc->CheckTargetVisibility(bodyFixedState, satToTargetVec,
                                               theTime,  sensorNum);                 
         }
         else
         {
            // No sensor, just report the results of the horizon test (done in the CheckGridFeasibility(.) function)
            inView = true;
         }
         if(inView)
         {
            result.push_back(PointIndices[k]);   // covCount'th entry
            covCount++;
         }

         #ifdef DEBUG_COV_CHECK
            MessageInterface::ShowMessage(
                            " --- In CheckPointCoverage, bodyFixedState = %s\n",
                            bodyFixedState.ToString(12).c_str());
         #endif

      }
   }

   return result;
}

//------------------------------------------------------------------------------
// Rvector6 GetCentralBodyFixedState(Real jd, const Rvector6& scCartState)
//------------------------------------------------------------------------------
/**
 * Returns the central body-fixed state at the specified time
 * 
 * @param jd  Julian date 
 *
 * @return  body-fixed state at the input time
 * 
 */
//------------------------------------------------------------------------------
Rvector6 CoverageChecker::GetCentralBodyFixedState(Real jd,
                                                const Rvector6& scCartState)
{
   // Converts state from inertial to body-fixed
   Rvector3 inertialPos   = scCartState.GetR();
   Rvector3 inertialVel   = scCartState.GetV();
   // TODO.  Handle differences in units of points and states.
   // TODO.  This ignores omega cross r term in velocity, which is ok and 
   // perhaps desired for current use cases but is not always desired.
   Rvector3 centralBodyFixedPos  = centralBody->GetBodyFixedState(inertialPos,
                                                                  jd);
   Rvector3 centralBodyFixedVel  = centralBody->GetBodyFixedState(inertialVel,
                                                                  jd);
   Rvector6 bodyFixedState(centralBodyFixedPos(0), centralBodyFixedPos(1),
                            centralBodyFixedPos(2),
                            centralBodyFixedVel(0), centralBodyFixedVel(1),
                            centralBodyFixedVel(2));
   return bodyFixedState;
}