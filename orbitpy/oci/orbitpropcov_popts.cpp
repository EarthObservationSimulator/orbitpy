//------------------------------------------------------------------------------
//         Orbit Propagation and Coverage Calcs with Pointing Options
//------------------------------------------------------------------------------
//
// Author: Vinay Ravindra
// Created: 2020.05.14
//
/**
 * Run a single satellite mission.
 * 
 * Coverage involves calculation of the seen locations on spherical Earth surface (lat, lon) for various poiting options. * 
 * 
 */
//------------------------------------------------------------------------------

#include <iostream>
#include <string>
#include <sstream>
#include <iomanip> 
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

#include "oci_utils.h"

#define DEBUG_CONSISE
//#define DEBUG_CHK_INPS

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;

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


/**
 * @param epoch mission epoch in UTCGregorian 
 * @param sma semi-major axis in kilometers
 * @param ecc eccentricity
 * @param inc inclination in degrees
 * @param raan right ascension of the ascending node in degrees
 * @param aop argument of perigee in degrees
 * @param ta true anomaly in degrees
 * @param duration mission duration in days
 * @param popts_fl pointing options file path and name
 * @param stepSize propagation step size
 * @param satStateFn Filename, path to write the satellite ECI states
 * @param satAccFn Filename, path to write the computed satellite access data
 *
 */
int main(int argc, char *argv[])
{
  /** Set up the messaging and output **/
  std::string outFormat = "%16.9f";

  /** Set up the message receiver and log file **/
  //Uncomment to set up receving debug messages on console 
  ConsoleMessageReceiver *consoleMsg = ConsoleMessageReceiver::Instance();
  MessageInterface::SetMessageReceiver(consoleMsg);
  
  std::string outPath = "./";
  //MessageInterface::SetLogFile(outPath + "OClog.txt");
  //MessageInterface::SetLogEnable(true);
  MessageInterface::ShowMessage("%s\n",
                                GmatTimeUtil::FormatCurrentTime().c_str());
  /** Parse input arguments **/
  string _epoch; 
  Real sma; 
  Real ecc; 
  Real inc; 
  Real raan; 
  Real aop; 
  Real ta; 
  Real duration; 
  string popts_fl; 
  Real stepSize; 
  string satStateFn;
  string satAccFn;

  if(argc==13){            
      _epoch = argv[1];
      sma = Real(stod(argv[2]));
      ecc = Real(stod(argv[3]));
      inc = Real(stod(argv[4]));
      raan = Real(stod(argv[5]));
      aop = Real(stod(argv[6]));
      ta = Real(stod(argv[7]));
      duration = Real(stod(argv[8]));
      popts_fl = argv[9];
      stepSize = Real(stod(argv[10]));
      satStateFn = argv[11];
      satAccFn = argv[12];
   }else{
      MessageInterface::ShowMessage("Please input right number of arguments.\n");
      exit(1);
   }  

   // Extract values from string comma separated string arguments
   RealArray epoch(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_epoch, ',')));
   if(epoch.size()!=6){
      MessageInterface::ShowMessage("Please enter epoch in the format of \"year,month,day,hour, minute, second\".\n");
      exit(1);
   }


   #ifdef DEBUG_CHK_INPS
      MessageInterface::ShowMessage("epoch is %16.9f year, %16.9f month, %16.9f day, %16.9f hour, %16.9f min, %16.9f second \n", 
      epoch[0], epoch[1], epoch[2], epoch[3], epoch[4], epoch[5]);
      MessageInterface::ShowMessage("SMA is %16.9f \n", sma);
      MessageInterface::ShowMessage("ECC is %16.9f \n", ecc);
      MessageInterface::ShowMessage("INC is %16.9f \n", inc);
      MessageInterface::ShowMessage("RAAN is %16.9f \n", raan);
      MessageInterface::ShowMessage("AOP is %16.9f \n", aop);
      MessageInterface::ShowMessage("TA is %16.9f \n", ta);
      MessageInterface::ShowMessage("Mission Duration is %16.9f \n", duration);
      MessageInterface::ShowMessage("Pointing options file path is %s \n", popts_fl.c_str());
      MessageInterface::ShowMessage("Step size is %16.9f \n", stepSize);
      MessageInterface::ShowMessage("Satellite states file path, name is: %s \n", satStateFn.c_str());
      MessageInterface::ShowMessage("Satellite access file path, name is: %s \n", satAccFn.c_str());
   #endif
   
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** About to read in pointing options ******\n");
   #endif
   /** Read in the coverage grid **/
   RealArray euler_angle1, euler_angle2, euler_angle3;
   readPntOptsFile(popts_fl, euler_angle1, euler_angle2, euler_angle3);  
   Integer numPntOpts = euler_angle1.size();
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** Finished reading in pointing options  ******\n");
   #endif
   
   // Set the global format setting
   GmatGlobal *global = GmatGlobal::Instance();
   global->SetActualFormat(false, false, 16, 1, false);
   
   // Check the OS (note that this does not work correctly for Mac)
   char *buffer = NULL;
   buffer = getenv("OS");
   if (buffer  != NULL)
   {
      MessageInterface::ShowMessage("Current OS is %s\n", buffer);
   }
   else
   {
      MessageInterface::ShowMessage("Buffer is NULL\n");
   }
   
   /// ******** Begin setting up the test
   MessageInterface::ShowMessage("*** START TEST ***\n");
  
   try
   {      
      // These are the objects needed
      AbsoluteDate             *date;
      OrbitState               *state;
      Spacecraft               *sat1;
      Propagator               *prop;
      CoverageChecker          *covChecker;
	   Earth                    *earth;
      NadirPointingAttitude    *attitude;
      LagrangeInterpolator     *interp = new LagrangeInterpolator( // Not used really.
                                             "TATCLagrangeInterpolator", 6, 7);

      #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
         // Create the container to hold the coverage events
         std::vector<IntervalEventReport> coverageEvents;
      #endif      
      
      clock_t t0 = clock(); // for timing

      // Create an Earth model
      earth = new Earth();
      
      // Create the epoch object and set the initial epoch
      date = new AbsoluteDate();
      date->SetGregorianDate(epoch[0], epoch[1], epoch[2], epoch[3], epoch[4], epoch[5]);
      
      // Create the spacecraft state object and set Keplerian elements
      state = new OrbitState();
      state->SetKeplerianState( sma, ecc, inc*RAD_PER_DEG, raan*RAD_PER_DEG, 
                                 aop*RAD_PER_DEG, ta*RAD_PER_DEG );
      
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** date and state OK "
                                       "**************\n");
      #endif            
               
      // Create a spacecraft giving it a state and epoch
      attitude = new NadirPointingAttitude();

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(
                           "*** About to create Spacecraft!!!!\n");
      #endif
      sat1     = new Spacecraft(date, state, attitude, interp); //,0.0, 0.0, 180.0);
         
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** DONE creating Spacecraft!!!!\n");
         MessageInterface::ShowMessage("**** attitude and sat1 OK "
                                       "**************\n");
      #endif
        
      // Create the propagator
      prop = new Propagator(sat1);
      
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** DONE creating Propagator!!!!\n");
      #endif            
      
      // Propagate for a duration and collect data
      Real           startDate   = date->GetJulianDate();

      /** Write satellite states and access files **/
      const int prc = std::numeric_limits<double>::digits10 + 1; // set to maximum precision

      // Satellite state file initialization
      ofstream satOut; 
      satOut.open(satStateFn.c_str(),ios::binary | ios::out);
      satOut << "Satellite states are in Earth-Centered-Inertial equatorial-plane frame.\n";
      satOut << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satOut << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satOut << "Mission Duration [Days] is "<< duration << "\n";
      satOut << "TimeIndex,X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]\n";

      // Write the access file in matrix format with rows as the time and columns as ground-points. 
      // Each entry in a cell of the matrix corresponds to 0 (No Access) or 1 (Access).
      ofstream satAcc; 
      satAcc.open(satAccFn.c_str(),ios::binary | ios::out);
      satAcc << "Satellite states are in Earth-Centered-Inertial equatorial-plane frame.\n";
      satAcc << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satAcc << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satAcc << "Mission Duration [Days] is "<< duration << ".\n";
      satAcc << "TimeIndex,";
      for(int i=0;i<numPntOpts;i++){
         satAcc<<"PntOpt"<<i;
         if(i<numPntOpts-1){
            satAcc<<",";
         }
      }
      satAcc << "\n";

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** About to Propagate!!!!\n");
      #endif
      int nSteps = 0;
      // Propagate to the initial time first
      prop->Propagate(*date);
      while (date->GetJulianDate() < ((Real)startDate +
                                       duration))
      {        
         Rvector6 cartState;
         cartState = sat1->GetCartesianState();
         Real jd = sat1->GetJulianDate();

         // Write satellite states to file
         satOut << std::setprecision(prc) << nSteps<< "," ;
         satOut << std::setprecision(prc) << cartState[0] << "," ;
         satOut << std::setprecision(prc) << cartState[1] << "," ;
         satOut << std::setprecision(prc) << cartState[2] << "," ;
         satOut << std::setprecision(prc) << cartState[3] << "," ;
         satOut << std::setprecision(prc) << cartState[4] << "," ;
         satOut << std::setprecision(prc) << cartState[5] << "\n" ; 

         satAcc << std::setprecision(4) << nSteps;
         /** Iterate over all pointing options **/
         for(int j=0;j<numPntOpts;j++){
            sat1->SetBodyNadirOffsetAngles(euler_angle1[j],euler_angle2[j],euler_angle3[j],1,2,3); 
            Rmatrix33 R_N2B = sat1->GetNadirTOBodyMatrix();

            Rvector6 earthFixedState  = earth->GetBodyFixedState(cartState, jd);
            Rmatrix33 R_EF2N = sat1->GetBodyFixedToReference(earthFixedState); // Earth fixed to Nadir
            
            Rmatrix33 R_EF2B = R_N2B * R_EF2N;
            // find the direction of the pointing axis (z-axis of the satellite body) in the Earth-Fixed frame
            Rvector3 pnt_axis = R_EF2B.Transpose() * Rvector3(0,0,1);
            Rvector3 earthFixedPos(earthFixedState[0], earthFixedState[1], earthFixedState[2]);
            Rvector3 intersect_point;         
            bool result = oci_utils::intersect_vector_sphere(earth->GetRadius(), earthFixedPos, pnt_axis,intersect_point);
            if(result== true){
               Rvector3 geoCoords = earth->Convert(intersect_point, "Cartesian", "Spherical");
               satAcc<< ",(" << geoCoords[0]*DEG_PER_RAD <<" "<< geoCoords[1]*DEG_PER_RAD <<")";
            }
            else{
               satAcc<< ",";
            }

         }
         
         satAcc << "\n";
                
         nSteps++; 

         // Propagate
         date->Advance(stepSize);
         prop->Propagate(*date);     
      
      }
      satOut.close();

      satAcc.close(); 

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- propagation completed\n");
      #endif
      

      //Delete un-needed objects
      delete    covChecker;
      delete    prop;
      // delete    sat1;  // deletes date, state, attitude, interp - so DON'T
      delete    date;
      delete    state;
      delete    attitude; 
      delete    earth;

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- Done deleting old pointers\n");
      #endif


      // check timing
      Real timeSpent = ((Real) (clock() - t0)) / CLOCKS_PER_SEC;
      MessageInterface::ShowMessage("TIME SPENT is %12.10f seconds\n",timeSpent);

            
     
      
      MessageInterface::ShowMessage("*** END ***\n");
   
   
   }
   catch (BaseException &be)
   {
      MessageInterface::ShowMessage("Exception caught: %s\n",
                                    be.GetFullMessage().c_str());
   }
   
}
