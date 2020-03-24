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


/** Extract substrings from comma seprated string **/
vector<string> extract_dlim_str(string strinp, char dlim){
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

/** Convert string vector to RealArray**/
RealArray convertStringVectortoRealVector(const std::vector<std::string>& stringVector){
   RealArray realVector(stringVector.size());
   std::transform(stringVector.begin(), stringVector.end(), realVector.begin(), [](const std::string& val)
   {
      return Real(stod(val));
   });
   return realVector;
}

}


#endif /* OCI_UTILS_H */
