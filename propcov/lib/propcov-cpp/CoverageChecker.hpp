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
// Created: 2016.05.09
// Modified: 2022.01.05 by Vinay
//
/**
 * Definition of the CoverageChecker class.  This class checks for point
 * coverage. The class is a reduced version of 'CoverageCheckerLegacy'. While the
 * legacy version includes functionality to generate reports, this class only checks for 
 * point-coverage.
 * 
 * The CoverageChecker is instantiated with pointers to PointGroup object and a Spacecraft object.
 * The point-group contains list of points which are to be checked for coverage calculations. 
 * The spacecraft may contain sensor, in which case coverage is evaluated for the sensor FOV or if no sensor
 * the coverage is evaluated for the spacecraft (complete horizon is considered). There is room to expand to multiple sensors
 * per spacecraft, but currently only 1 sensor per spacecraft is allowed.
 * 
 * THe primary functions utilized are the overloaded functions CheckPointCoverage(.). 
 * 
 */
//------------------------------------------------------------------------------
#ifndef CoverageChecker_hpp
#define CoverageChecker_hpp

#include "gmatdefs.hpp"
#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "PointGroup.hpp"
#include "Earth.hpp"
#include "Rvector.hpp"
#include "Rvector3.hpp"

class CoverageChecker
{
public:
   
   /// class construction/destruction
   CoverageChecker(PointGroup *ptGroup, Spacecraft *sat);
   CoverageChecker( const CoverageChecker &copy);
   CoverageChecker& operator=(const CoverageChecker &copy);
   
   virtual ~CoverageChecker();
   
   /// Check the point coverage and return the resulting index array
   virtual IntegerArray      CheckPointCoverage(IntegerArray PointIndices);
   virtual IntegerArray      CheckPointCoverage();
   virtual IntegerArray      CheckPointCoverage(const Rvector6 &bodyFixedState,
                                                Real           theTime,
                                                const Rvector6 &scCartState,
                                                const IntegerArray &PointIndices);
   virtual IntegerArray      CheckPointCoverage(const Rvector6 &bodyFixedState,
                                                Real           theTime,
                                                const Rvector6 &scCartState);

   
protected:
   
   /// the points to use for coverage
   PointGroup                 *pointGroup;
   /// The spacecraft object @todo Should this be an array of spacecraft?
   Spacecraft                 *sc;
   /// the central body; the model of Earth's properties & rotation
   Earth                      *centralBody;
   /// central body radius
   Real centralBodyRadius;

   /// array of all points (unit-vectors) @todo: Move this to the PointGroup class.
   std::vector<Rvector3*>     pointArray;
   /// feasibility values for each point
   std::vector<bool>          feasibilityTest;
   
   /// Get the central body fixed state at the input time for the input cartesian state
   virtual Rvector6          GetCentralBodyFixedState(Real jd, const Rvector6& scCartState);
   /// Check the grid feasibility for the input point with the input body fixed state
   virtual bool              CheckGridFeasibility(Integer ptIdx,
                                  const Rvector3& bodyFixedState);
   /// Check the grid feasibility for all points for the input body fixed state
   virtual void              CheckGridFeasibility(
                                  const Rvector3& bodyFixedState);

   
   /// local Rvectors used for Grid Feasibility calculations
   /// (for performance)
   Rvector3 rangeVec;   
   Rvector3 bfState;
   Rvector3 bodyUnit;
   Rvector3 ptPos;
};
#endif // CoverageChecker_hpp







