//------------------------------------------------------------------------------
//                           NadirPointingAttitude
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
// Updated by Vinay, 2019
//
/**
 * Definition of the NadirPointingAttitude class. NadirPointingAttitude is a subclass of Attitude 
 * that models the Nadir-pointing coordinate frame. 
 * The main responsibility of this class is to compute the rotation from an inertial/body-fixed frame 
 * to the nadir pointing coordinate frame using the input (spacecraft) state-vector (position and velocity).
 */
//------------------------------------------------------------------------------
#ifndef NadirPointingAttitude_hpp
#define NadirPointingAttitude_hpp

#include "gmatdefs.hpp"
#include "Attitude.hpp"
#include "Rmatrix33.hpp"

class NadirPointingAttitude : public Attitude
{
public:
   
   /// class construction/destruction
   NadirPointingAttitude();
   NadirPointingAttitude( const NadirPointingAttitude &copy);
   NadirPointingAttitude& operator=(const NadirPointingAttitude &copy);
   
   virtual ~NadirPointingAttitude();

   /// Clone the Attitude
   virtual Attitude* Clone() const;
   
   /// Produces the inertial-to-reference rotation matrix
   virtual Rmatrix33   InertialToReference(const Rvector6& centralBodyState);

   /// Produces the body-fixed-to-reference rotation matrix 
   virtual Rmatrix33   BodyFixedToReference(const Rvector6& centralBodyState);
   
   
protected:
   
   /// Local class data for performance
   Rvector3      centralBodyFixedPos;
   Rvector3      centralBodyFixedVel;
   Rmatrix33     R_fixed_to_nadir;
   Rmatrix33     R_fixed_to_nadir_transposed;

   Rvector3      centralInertialPos;
   Rvector3      centralInertialVel;
   Rmatrix33     R_inertial_to_nadir;
   Rmatrix33     R_inertial_to_nadir_transposed;  
   
};
#endif // NadirPointingAttitude_hpp
