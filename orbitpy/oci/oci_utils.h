#ifndef OCI_UTILS_H // include guard
#define OCI_UTILS_H


#include <iostream>
#include <string>
#include <sstream>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <fstream>
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"
#include "Rvector6.hpp"
#include "Rvector3.hpp"
#include "Rmatrix.hpp"
#include "RealUtilities.hpp"
#include "MessageInterface.hpp"
#include "ConsoleMessageReceiver.hpp"
#include "AbsoluteDate.hpp"
#include "Spacecraft.hpp"
#include "Earth.hpp"
#include "KeyValueStatistics.hpp"
#include "VisiblePOIReport.hpp"
#include "OrbitState.hpp"
#include "PointGroup.hpp"
#include "Propagator.hpp"
#include "ConicalSensor.hpp"
#include "RectangularSensor.hpp"
#include "CustomSensor.hpp"
#include "CoverageChecker.hpp"
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include "TimeTypes.hpp"


using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;

namespace oci_utils {

vector<string> extract_dlim_str(string strinp, char dlim){
/** Extract substrings from comma seprated string **/
   stringstream ss(strinp.c_str());
   vector<string> vecStrOut;

   while( ss.good() )
   {
      string substr;
      std::getline( ss, substr, dlim );
      vecStrOut.push_back( substr );
   }

   return vecStrOut;
}

RealArray convertStringVectortoRealVector(const std::vector<std::string>& stringVector){
/** Convert string vector to RealArray**/
   RealArray realVector(stringVector.size());
   std::transform(stringVector.begin(), stringVector.end(), realVector.begin(), [](const std::string& val)
   {
      return Real(stod(val));
   });
   return realVector;
}

/** Find intersection of a vector with a sphere.  
 *  The origin of the reference-frame (in which the vector is expressed) 
 *  is assumed to be at the center of the sphere.  
 * https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection
 * 
 * @param r radius of sphere
 * 
 * @param o start position of vector
 * 
 * @param vecDirec direction of vector
 * 
 * @param intersect_point Coordinates of the the first intersection point on the sphere
 * 
 * @return true if point is found, false if no intersection  
 * 
 * **/
bool intersect_vector_sphere(const Real r, const Rvector3 &o, const Rvector3 &vecDirec, Rvector3 &intersect_point){
   // center of sphere is c = (0,0,0)
   const Rvector3 l = vecDirec.GetUnitVector();

   Real under_root = (l*o)*(l*o) - (o*o - r*r);
   if(under_root > 0){
      Real d1 = -1*(l*o) - std::sqrt(under_root);
      Real d2 = -1*(l*o) + std::sqrt(under_root);
      if(abs(d1) < abs(d2)){ // find the point closest to the sphere wrt the vector origin
         intersect_point = o + l*d1;
      }else{
         intersect_point = o + l*d2;
      }      
      return true;
   }
   else if(under_root == 0){
      Real d = -1*(l*o);
      intersect_point = o + l*d;
      return true;
   }else{
      return false; // no point of intersection
   }

}
}

#endif /* OCI_UTILS_H */
