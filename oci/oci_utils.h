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

//#define DEBUG_OCI_UTILS_READSATSTATEFLEHEADER

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

int readSatStateFileHeader(const string &satStateFp, Real &epoch, Real &stepSize, Real &duration, Rvector6 &state0)
{  /**Read header of the satellite state files and extract the epoch and duration.**/
   ifstream in(satStateFp.c_str());
   if(!in){
       std::cerr << "Cannot open the Satellite State File : "<<satStateFp.c_str()<<std::endl;
       return -1;
   }
   string line;
   std::getline(in,line); 
   std::getline(in,line); // second line in the satellite state file contains the epoch
   stringstream ss1(line);
   vector<string> epoch_line;
   while(ss1.good()){
       string substr;
       std::getline( ss1, substr, ' ' );
       epoch_line.push_back( substr );
   }
   epoch = stod(epoch_line[2]); // epoch in JDUT1
   #ifdef DEBUG_OCI_UTILS_READSATSTATEFLEHEADER
      MessageInterface::ShowMessage("*** epoch is %f \n", epoch);
   #endif

   std::getline(in,line); // third line in the satellite state file contains the step-size
   vector<string> step_size_line;
   stringstream ss2(line);
   while(ss2.good()){
       string substr;
       std::getline( ss2, substr, ' ' );
       step_size_line.push_back( substr );
   }
   stepSize = stod(step_size_line[4]); // step size in seconds
   #ifdef DEBUG_OCI_UTILS_READSATSTATEFLEHEADER
      MessageInterface::ShowMessage("*** stepSize is %f \n", stepSize);
   #endif

   std::getline(in,line); // fourth line in the satellite state file contains the duration in days
   vector<string> duration_line;
   stringstream ss3(line);
   while(ss3.good()){
       string substr;
       std::getline( ss3, substr, ' ' );
       duration_line.push_back( substr );
   }
   duration = stod(duration_line[4]); // duration size in days
   #ifdef DEBUG_OCI_UTILS_READSATSTATEFLEHEADER
      MessageInterface::ShowMessage("*** duration is %f \n", duration);
   #endif

   std::getline(in,line);
   std::getline(in,line);  // sixth line in the satellite state file contains the state at the epoch
   RealArray e;
   int i=0;
   stringstream ss4(line);
   while(ss4.good()){
       string substr;
       std::getline(ss4, substr, ',');
       if(i==0){
        epoch = epoch + stoi(substr)*stepSize*GmatTimeConstants::DAYS_PER_SEC;
        #ifdef DEBUG_OCI_UTILS_READSATSTATEFLEHEADER
            MessageInterface::ShowMessage("*** state0 date is %f \n", epoch);
        #endif
       }
       else{
        e.push_back(stod(substr));               
       }
       i++;
   }
   
   state0.Set(e[0], e[1], e[2], e[3], e[4], e[5]);
   #ifdef DEBUG_OCI_UTILS_READSATSTATEFLEHEADER
      MessageInterface::ShowMessage("*** state0 is %f, %f, %f, %f, %f, %f \n", state0(0), state0(1), state0(2), state0(3), state0(4), state0(5));
   #endif
   return 0;
}

int readCovGridFile(const string &covGridFp, RealArray &lats, RealArray &lons)
{/**Read coverage grid data file onto double arrays.**/

    ifstream in(covGridFp.c_str());

    if(!in){
  		std::cerr << "Cannot open the Coverage Grid File : "<<covGridFp.c_str()<<std::endl;
		return -1;
    }

    string line;
    getline(in,line); // skip header
    while (getline(in,line))
    {
      stringstream ss(line);
      vector<string> vecStrOut;

      while(ss.good()){
         string substr;
         std::getline( ss, substr, ',' );
         vecStrOut.push_back( substr );
      }
      // The first two entries in the file are the region index and grid point index
      Real lat = stod(vecStrOut[2]);
      Real lon = stod(vecStrOut[3]);

      lats.push_back( lat*RAD_PER_DEG );
      lons.push_back( lon*RAD_PER_DEG );

    }
    in.close();

    return 0;

}

int readPntOptsFile(const string &pOptsFl, RealArray &euler_angle1, RealArray &euler_angle2, RealArray &euler_angle3)
{/**Read pointing options data file onto double arrays.**/

    ifstream in(pOptsFl.c_str());

    if(!in){
  		std::cerr << "Cannot open the Pointing Options File : "<<pOptsFl.c_str()<<std::endl;
		return -1;
    }

    string line;
    getline(in,line); // skip header
    getline(in,line); // skip header
    while (getline(in,line))
    {
      stringstream ss(line);
      vector<string> vecStrOut;

      while(ss.good()){
         string substr;
         std::getline( ss, substr, ',' );
         vecStrOut.push_back( substr );
      }
      // The first entry is the index
      Real eu1 = stod(vecStrOut[1]);
      Real eu2 = stod(vecStrOut[2]);
      Real eu3 = stod(vecStrOut[3]);

      // retain the angles in degrees!
      euler_angle1.push_back( eu1 );
      euler_angle2.push_back( eu2 );
      euler_angle3.push_back( eu3 );

    }
    in.close();

    return 0;

}



bool is_in_lineOfSight(const Rvector3* object1_pos, const Rvector3* object2_pos, const Real obstacle_radius){
      
      Rvector3 obj1_unitVec = object1_pos->GetUnitVector();
      Rvector3 obj2_unitVec = object2_pos->GetUnitVector();  

      // This condition tends to give a numerical error, so solve for it independently.
      Real eps = 1e-9;
      Real x = obj1_unitVec * obj2_unitVec; // Dot product
      Real theta, theta1, theta2;

      if((x > -1-eps) && (x < -1+eps)){
         return false;
      }         
      else{
         if(x>1){
             x=1;
         }            
         theta  = GmatMathUtil::ACos(x);
      }
                        
      Real obj1_r = object1_pos->GetMagnitude();      
      if(obj1_r - obstacle_radius > 1e-5){
         theta1 = GmatMathUtil::ACos(obstacle_radius/obj1_r);
      }
      else if(abs(obj1_r - obstacle_radius) < 1e-5){
         theta1 =  0.0;
      }         
      else{
         return false; // object1 is inside the obstacle
      }
         
      Real obj2_r = object2_pos->GetMagnitude();
      if(obj2_r - obstacle_radius > 1e-5){
         theta2 = GmatMathUtil::ACos(obstacle_radius/obj2_r);
      }         
      else if(abs(obj2_r - obstacle_radius) < 1e-5){
         theta2 =  0.0;
      }         
      else{
         return false; // object2 is inside the obstacle
      }        
               
      if(theta1 + theta2 < theta)
         return false;
      else
         return true;
}

void get_points_in_lineOfSight(const Rvector3 sat_pos_EF_km, PointGroup *pointGroupIn, IntegerArray& inViewPntInd){
   /* 
      Perform horizon test on the list of points
   */
   // @todo DON'T hard-code body radius
   const Real BODY_RADIUS = 6378.1363;
   Integer numPts = pointGroupIn->GetNumPoints();   
   for (Integer pointIdx = 0; pointIdx < numPts; pointIdx++)
   {
 
      Rvector3 *ptPos1  = pointGroupIn->GetPointPositionVector(pointIdx);

      if (oci_utils::is_in_lineOfSight(ptPos1, &sat_pos_EF_km, BODY_RADIUS)){
         inViewPntInd.push_back(pointIdx); 
      }
   
   }
}
}
#endif /* OCI_UTILS_H */
