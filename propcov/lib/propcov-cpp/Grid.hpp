#ifndef Grid_hpp
#define Grid_hpp

#include "gmatdefs.hpp"
#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "OrbitState.hpp"
#include "Rvector6.hpp"
#include "TATCException.hpp"
#include <string>

class Grid
{
public:
   /// Get point position for given index
   Rvector3* GetPointPositionVector(Integer idx);

   /// Get the latitude and longitude for the given index
   virtual void      GetLatAndLon(Integer idx, Real &theLat, Real &theLon) = 0;
   virtual std::pair<Real, Real> GetLatAndLon(Integer idx) = 0;
   /// Get the number of points
   virtual Integer   GetNumPoints() = 0;
   /// Get the latitude and longitude vectors
   virtual void      GetLatLonVectors(RealArray &lats, RealArray &lons) = 0;
   virtual std::pair<RealArray, RealArray> GetLatLonVectors() = 0;

   // Get point representations for output file
   virtual std::vector<std::string> GetPointHeader() = 0;
   virtual std::vector<Real> GetPoint(Integer idx) = 0;
   virtual std::vector<RealArray> GetPoints() = 0;
   
   // Todo
   // virtual std::vector<RealArray> GetPoints(Integer idx) = 0;
protected:

   /// Protected methods for managing points
   bool CheckHasPoints();

   std::vector<Rvector3*> coords;
   /// num of points
   Integer                numPoints;
   
};
#endif // Grid_hpp
