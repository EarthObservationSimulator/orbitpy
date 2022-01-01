//------------------------------------------------------------------------------
//                           Propagator
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
// Created: 2016.05.05
//
/**
 * Propagates spacecraft state to a requested time using a J2 Analytical propagator. 
 * The default physical constants are set to that of spacecraft orbiting Earth. 
 * A Propagator object is to be initialized with a pointer to a spacecraft, from which the orbit-state is read & modified. 
 * 
 * @todo Drag effects can be optionally considered by setting a flag, but this part is erroneous and needs revision. 
 *       (See the Propagator::Propagate(const AbsoluteDate &toDate) function.)
 */
//------------------------------------------------------------------------------
#ifndef Propagator_hpp
#define Propagator_hpp

#include "gmatdefs.hpp"
#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "OrbitState.hpp"
#include "Rvector6.hpp"
#include "ExponentialAtmosphere.hpp"

class Propagator
{
public:
   
   /// class construction/destruction
   Propagator(Spacecraft *sat);
   Propagator( const Propagator &copy);
   Propagator& operator=(const Propagator &copy);
   
   virtual ~Propagator();
   
   /// Set the body physical constants on the propagator
   virtual void      SetPhysicalConstants(Real bodyMu, Real bodyJ2,
                                          Real bodyRadius);
   /// Propagate the spacecraft
   virtual Rvector6  Propagate(const AbsoluteDate &toDate);
   
   /// Get the propagation start and end times
   virtual void      GetPropStartEnd(AbsoluteDate &pStart, AbsoluteDate &pEnd);

   /// Set the flag indicating whether or not to apply drag
   void              SetApplyDrag(bool applyDrag);
   /// Get the flag indicating whether or not to apply drag
   bool              GetApplyDrag();
   
protected:
   
   /// The spacecraft to be propagated @todo should this be an array of sc?
   Spacecraft   *sc;
   /// Density model used in computing effects of atmospheric drag
   ExponentialAtmosphere *densityModel;
   /// J2 term for Earth
   Real         J2;
   /// Gravitational parameter of the Earth
   Real         mu;
   /// Equatorial radius of the Earth
   Real         eqRadius;
   /// Flag to turn on/off drag modeling.
   bool         applyDrag;
   
   /** Julian date of the reference orbital elements. The `refJd` instance variable stores the last date until 
    *  which the drag-effects have been considered.
    *  Note that when the drag is disabled, the refJd term is not updated and remains at the initial epoch at 
    *  which the propagator was initialized.
   */
   Real         refJd;
   /// The epoch at which the propagation started
   AbsoluteDate propStart;
   /// The epoch at which the propagation ended (so far, i.e. the last
   /// propagation time)
   AbsoluteDate propEnd;
   /// Epoch of last update to orbit to account for drag effects
   Real         lastDragUpdateEpoch;
   /// The orbital period
   Real         orbitPeriod;

   /// The below orbital-elements at any point in time are at sync with the spacecraft orbit-state
   /// Orbital semi-major axis
   Real         SMA;
   /// Orbital eccentricity
   Real         ECC;
   /// Orbital inclination
   Real         INC;
   /// Orbital right ascention of the ascending node
   Real         RAAN;
   /// Orbital argument of periapsis
   Real         AOP;
   /// Orbital true anomaly
   Real         TA;
   /// Orbital true anomaly
   Real         MA;
   
   /// The drift in mean motion caused by J2
   Real         meanMotionRate;
   /// The drift in argument of periapsis caused by J2
   Real         argPeriapsisRate;
   /// The drift in right ascention of the ascending node caused by J2
   Real         rightAscensionNodeRate;
   /// The orbital semi-latus rectum
   Real         semiLatusRectum;
   /// The orbital mean motion
   Real         meanMotion;
   
   /// <static const> Mu for the Earth
   static const Real MU_FOR_EARTH;
   
   /// Set the orbit state
   void         SetOrbitState(OrbitState *orbState);
   /// Compute the periapsis altitude
   Real         ComputePeriapsisAltitude(Rvector6 orbElem, Real julianDate);
   /// Propagate the orbital elements
   Rvector6     PropagateOrbitalElements(Real propDuration);
   /// Compute the drag effects
   void         ComputeDragEffects(Real sma, Real ecc, Real altitude,
	                                Real &deltaSMAperRev, Real &deltaECCperRev);
   /// Compute the orbital mean motion
   Real         MeanMotion();
   /// Compute the semi parameter
   Real         SemiParameter();
   /// Compute the orbit rates
   void         ComputeOrbitRates();
   /// Compute the mean motion rate
   void         ComputeMeanMotionRate();
   /// Compute the argument of periapsis
   void         ComputeArgumentOfPeriapsisRate();
   /// Compute the right ascension of the ascending node rate
   void         ComputeRightAscensionNodeRate();
   
};
#endif // Propagator_hpp
