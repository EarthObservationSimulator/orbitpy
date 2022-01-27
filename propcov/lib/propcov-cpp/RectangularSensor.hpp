//------------------------------------------------------------------------------
//                           RectangularSensor
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
// Created: 2016.05.03
// Modified: 2021.00.00 Ryan
// Modifed: 2022.02.26 Vinay
//
/**
 * Definition of the RectangularSensor class.  This class models a rectangular FOV.
 * This is a subclass of the Sensor class. 
 * It can be used to evaluate the presence/absence of a point-location in a sensor FOV (conical shape). 
 * The target location must be expressed in the Sensor frame.
 * 
 * The class evaluates the dot product between the target point and the normal of the hemispherical-planes
 * formed by the 4 edges of the rectangle shape. The corners of the rectangle are arranged in 
 * anti-clockwise manner about the center on the spherical surface,
 * if the target -point is in the Northern hemisphere corresponding to 4 hemispherical planes formed by 
 * the edges of the rectangle, then the target falls within the sensor FOV.  
 */
//------------------------------------------------------------------------------
#ifndef RectangularSensor_hpp
#define RectangularSensor_hpp

#include "gmatdefs.hpp"
#include "Sensor.hpp"

class RectangularSensor : public Sensor
{
public:
   
   /// class construction/destruction
   RectangularSensor(Real angleWidthIn, Real angleHeightIn);
   RectangularSensor( const RectangularSensor &copy);
   RectangularSensor& operator=(const RectangularSensor &copy);
   
   virtual ~RectangularSensor();
   
   /// Check the target visibility given the input cone and clock angles:
   /// determines whether or not the point is in the sensor FOV.
   virtual bool  CheckTargetVisibility(Real viewConeAngle,
                                       Real viewClockAngle);
   
   /// Set/Get angle width
   virtual void  SetAngleWidth(Real angleWidthIn);
   virtual Real  GetAngleWidth();
   
   /// Set/Get angle height
   virtual void  SetAngleHeight(Real angleHeightIn);
   virtual Real  GetAngleHeight();
   
   /// New Functions
   std::vector<Real> getClockAngles();
   std::vector<Rvector3> getCornerHeadings(std::vector<Real> &clocks);
   std::vector<Rvector3> getPoleHeadings(std::vector<Rvector3> &corners);

protected:
   
   ///  Angle width
   Real    angleWidth;
   /// Angle height
   Real    angleHeight;
   
   std::vector<Rvector3> poles;
};
#endif // RectangularSensor_hpp
