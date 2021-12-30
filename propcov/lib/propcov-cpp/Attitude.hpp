//------------------------------------------------------------------------------
//                           Attitude
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
// Created: 2018.07.30
// Updated by Vinay, 2021.12.31
//
/**
 * Definition of the Attitude class. This base class is used to model the spacecraft attitude state. 
 * It relies on the child-classes to implement the calculation of rotation matrices to rotate coordinate systems.
 */
//------------------------------------------------------------------------------
#ifndef Attitude_hpp
#define Attitude_hpp

#include "gmatdefs.hpp"
#include "Rmatrix33.hpp"
#include "Rvector6.hpp"

class Attitude
{
public:
   
   /// class construction/destruction
   Attitude();
   Attitude( const Attitude &copy);
   Attitude& operator=(const Attitude &copy);
   
   /// Clone the Attitude
   virtual Attitude* Clone() const = 0;
   
   virtual ~Attitude();
   
   /// Produces the inertial-to-reference rotation matrix
   //  @note This method is pure virtual and MUST be implemented in child classes
   virtual Rmatrix33   InertialToReference(const Rvector6& centralBodyState) = 0;

   /// Produces the body-fixed-to-reference rotation matrix
   //  @note This method is pure virtual and MUST be implemented in child classes
   virtual Rmatrix33 BodyFixedToReference(const Rvector6& centralBodyState) = 0;
   
   
protected:
      
};
#endif // Attitude_hpp
