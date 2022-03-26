#ifndef Grid_hpp
#define Grid_hpp

#include "gmatdefs.hpp"
#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "OrbitState.hpp"
#include "Rvector6.hpp"

class Grid
{
public:
   /// Get point position for given index
   virtual Rvector3* GetPointPositionVector(Integer idx) = 0;
   /// Get the latitude and longitude for the given index
   virtual void      GetLatAndLon(Integer idx, Real &theLat, Real &theLon) = 0;
   virtual std::pair<Real, Real> GetLatAndLon(Integer idx) = 0;
   /// Get the number of points
   virtual Integer   GetNumPoints() = 0;
   /// Get the latitude and longitude vectors
   virtual void      GetLatLonVectors(RealArray &lats, RealArray &lons) = 0;
   virtual std::pair<RealArray, RealArray> GetLatLonVectors() = 0;

protected:
   
   /// num of points
   Integer                numPoints;
   /// Number of points requested in the point algorithm
   Integer                numRequestedPoints;  // WHERE/WHY is this used?
   
};
#endif // Grid_hpp
