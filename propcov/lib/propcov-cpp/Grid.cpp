#include "Grid.hpp"

//------------------------------------------------------------------------------
// Rvector3* GetPointPositionVector(Integer idx)
//------------------------------------------------------------------------------
/**
 * Returns the coordinates of the specified point.
 * 
 * @param idx  index of point whose coordinates to return
 * 
 * @return  a 3-vector representing the coordinates of the specifed point
 *
 */
//------------------------------------------------------------------------------
inline Rvector3* Grid::GetPointPositionVector(Integer idx)
{
   // Returns body fixed location of point given point index
   // Inputs. int poiIndex
   // Outputs. Rvector 3x1 containing the position.
   
   // Make sure there are points
   CheckHasPoints();
   
   #ifdef DEBUG_POINTS
      MessageInterface::ShowMessage(
                 "In PG::GetPointPositionVector, returning coords "
                 "(%p) at idx = %d\n",
                 coords.at(idx), idx);
   #endif
  return coords.at(idx);
}

//------------------------------------------------------------------------------
// bool CheckHasPoints()
//------------------------------------------------------------------------------
/**
 * Checks to see if there are any ponts set or computed
 * 
 * @return   true if there are points; false otherwise
 *
 */
//------------------------------------------------------------------------------
bool Grid::CheckHasPoints()
{
   if (numPoints <= 0)
      throw TATCException("The point group does not have any points\n");
   return true;
}