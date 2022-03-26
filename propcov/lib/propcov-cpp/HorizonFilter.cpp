#include "HorizonFilter.hpp"

HorizonFilter::HorizonFilter(Spacecraft *spacecraft, Grid *grid) :
   grid        (grid),
   spacecraft                (spacecraft),
   centralBody       (NULL)
{
   pointArray.clear();
   feasibilityTest.clear();

   centralBody    = new Earth();
   centralBodyRadius = centralBody->GetRadius();

   Integer numPts = grid->GetNumPoints();
   for (Integer ii = 0; ii < numPts; ii++)
   {     
      /// @TODO This should not be set here - we should store both
      /// positions and unitized positions in the grid and
      /// then access those arrays when needed <<<<<<<<<<<<<<
      Rvector3 *ptPos1  = grid->GetPointPositionVector(ii);
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
//  HorizonFilter(const HorizonFilter &copy)
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
HorizonFilter::HorizonFilter(const HorizonFilter &copy) :
   grid        (copy.grid),
   spacecraft                (copy.spacecraft),
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
//  HorizonFilter& operator=(const HorizonFilter &copy)
//------------------------------------------------------------------------------
/**
 * The operator= for the HorizonFilter object
 *
 * @param copy  the object to copy
 * 
 * @todo: Cloning required of the pointGroup, sc, centralBody, pointArray objects? 
 * 
 */
//------------------------------------------------------------------------------
HorizonFilter& HorizonFilter::operator=(const HorizonFilter &copy)
{
   if (&copy == this)
      return *this;
   
   grid        = copy.grid;
   spacecraft                = copy.spacecraft;
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
// std::vector<bool> FilterGrid()
//------------------------------------------------------------------------------
/**
 * Returns an array of grid indices to be examined for FOV inclusion
 *
 * @return  IntegerArray of grid indices
 * 
 */
//------------------------------------------------------------------------------
std::vector<bool> HorizonFilter::FilterGrid()
{
   // Get the state and date here
    Real     theDate   = spacecraft->GetJulianDate();
    Rvector6 scCartState = spacecraft->GetCartesianState();
    Rvector6 bodyFixedState  = GetCentralBodyFixedState(theDate, scCartState);
    Rvector3 centralBodyFixedPos(bodyFixedState[0],
                                 bodyFixedState[1],
                                 bodyFixedState[2]);
    CheckGridFeasibility(centralBodyFixedPos);

    return feasibilityTest;
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
Rvector6 HorizonFilter::GetCentralBodyFixedState(Real jd,
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

//------------------------------------------------------------------------------
// protected methods
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// bool CheckGridFeasibility(Integer         ptIdx,,
//                           const Rvector3& bodyFixedState)
//------------------------------------------------------------------------------
/**
 * Checks the grid feasibility for a (single) select point.
 * First it is checked if the spacecraft and the ground-point are on the same hemispheres
 * (where the hemisphere is formed by the plane defined by the unit-normal along the ground-point position-vector).
 * If so, a horizon test is performed, i.e. to check if the ground-point is within the horizon seen by the spacecraft.
 *
 * @param   ptIdx             point index
 * @param   bodyFixedState    central body fixed state (position) of spacecraft
 *
 * @return   output feasibility flag
 *
 */
//------------------------------------------------------------------------------
bool HorizonFilter::CheckGridFeasibility(Integer         ptIdx,
                                           const Rvector3& bodyFixedState)
{
   #ifdef DEBUG_GRID
      MessageInterface::ShowMessage(
                        "CheckGridFeasibility: ptIDx = %d, bodyFixedState = %s\n",
                        ptIdx, bodyFixedState.ToString(12).c_str());
   #endif

   bool     isFeasible = false;   
   bodyUnit = bodyFixedState.GetUnitVector();

   unitPtPos    = *(pointArray.at(ptIdx)); // is normalized
   Real  feasibilityReal = unitPtPos * bodyUnit; // gives the cosine of the angle b/w the spacecraft and point
   
   if (feasibilityReal > 0.0) // i.e. check if the point and satellite are on the same hemisphere
   {
      // do horizon test           
      /* This code is  slower. Next snippet is the faster.
      ptPos  = unitPtPos*centralBodyRadius;
      rangeVec  = bodyFixedState - ptPos;
      unitRangeVec   = rangeVec.GetUnitVector(); 
      Real dot  = unitRangeVec * unitPtPos;
      if (dot > 0.0)
         isFeasible = true;
      */
      rangeVec  = bodyFixedState/centralBodyRadius - unitPtPos; // scaled version of the actual range vector
      Real dot  = rangeVec * unitPtPos;
      if (dot > 0.0)
         isFeasible = true;    
      
   }
   return isFeasible;
}

//------------------------------------------------------------------------------
// void CheckGridFeasibility(const Rvector3& bodyFixedState)
//------------------------------------------------------------------------------
/**
 * Checks the grid feasibility for all the points. The `feasibilityTest` instance variable is updated.
 * First it is checked if the spacecraft and the ground-point are on the same hemispheres
 * (where the hemisphere is formed by the plane defined by the unit-normal along the ground-point position-vector).
 * If so, a horizon test is performed, i.e. to check if the ground-point is within the horizon seen by the spacecraft.
 *
 * @param   bodyFixedState    central body fixed state of spacecraft
 *
 */
//------------------------------------------------------------------------------
void HorizonFilter::CheckGridFeasibility(const Rvector3& bodyFixedState)
{
   #ifdef DEBUG_GRID
      MessageInterface::ShowMessage("CheckGridFeasibility: bodyFixedState = %s\n",
                                    bodyFixedState.ToString(12).c_str());
   #endif

   bodyUnit = bodyFixedState.GetUnitVector();   
   
   for (Integer ptIdx = 0; ptIdx < pointArray.size(); ptIdx++)
   {
      feasibilityTest.at(ptIdx) = false; //initialize
      
      // feasibilityTest.at(ptIdx) = CheckGridFeasibility(ptIdx, bodyFixedState); // this makes it slow because unit body vector is calculated repeatedly

      unitPtPos    = *(pointArray.at(ptIdx)); // is normalized
      //Real  feasibilityReal = unitPtPos * bodyUnit; // gives the cosine of the angle b/w the spacecraft and point
      
      if ((unitPtPos * bodyUnit) > 0.0) // i.e. check if the point and satellite are on the same hemisphere
      {
         // do horizon test           
         /* This code is  slower. Next snippet is the faster.
         ptPos  = unitPtPos*centralBodyRadius;
         rangeVec  = bodyFixedState - ptPos;
         unitRangeVec   = rangeVec.GetUnitVector(); 
         Real dot  = unitRangeVec * unitPtPos;
         if (dot > 0.0)
            isFeasible = true;
         */      
         rangeVec  = bodyFixedState/centralBodyRadius - unitPtPos; // scaled version of the actual range vector
         if ((rangeVec * unitPtPos) > 0.0)
            feasibilityTest.at(ptIdx) = true;         
      }

   }
}