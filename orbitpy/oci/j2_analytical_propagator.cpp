//------------------------------------------------------------------------------
//                         TATC J2 analytical propagator
//------------------------------------------------------------------------------
//
// Author: Vinay Ravindra
// Created: 2020.09.22
//
/**
 * Run a single satellite mission and calculate satellite states 
 * (position, velocity) according to J2 analytical model.
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
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include "TimeTypes.hpp"

#include "oci_utils.h"

#define DEBUG_CONSISE
//#define DEBUG_CHK_INPS

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;

/**
 * @param epoch mission epoch in UTCGregorian 
 * @param sma semi-major axis in kilometers
 * @param ecc eccentricity
 * @param inc inclination in degrees
 * @param raan right ascension of the ascending node in degrees
 * @param aop argument of perigee in degrees
 * @param ta true anomaly in degrees
 * @param duration mission duration in days
 * @param stepSize propagation step size
 * @param satStateFp Filename, path to write the satellite ECI states
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
  Real stepSize; 
  string satStateFp;

  if(argc==11){            
      _epoch = argv[1];
      sma = Real(stod(argv[2]));
      ecc = Real(stod(argv[3]));
      inc = Real(stod(argv[4]));
      raan = Real(stod(argv[5]));
      aop = Real(stod(argv[6]));
      ta = Real(stod(argv[7]));
      duration = Real(stod(argv[8]));
      stepSize = Real(stod(argv[9]));
      satStateFp = argv[10];
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
      MessageInterface::ShowMessage("\n");
      MessageInterface::ShowMessage("Step size is %16.9f \n", stepSize);
      MessageInterface::ShowMessage("Satellite states file path, name is: %s \n", satStateFp.c_str());
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
	   Earth                    *earth;
      NadirPointingAttitude    *attitude;
      LagrangeInterpolator     *interp = new LagrangeInterpolator( // Not used really.
                                             "TATCLagrangeInterpolator", 6, 7);   
      
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
      IntegerArray   loopPoints;
      IntegerArray   loopPoints_yaw180;

      /** Write satellite states and access files **/
      const int prc = std::numeric_limits<double>::digits10 + 1; // set to maximum precision

      // Satellite state file initialization
      ofstream satOut; 
      satOut.open((satStateFp).c_str(),ios::binary | ios::out);
      satOut << "Satellite states are in Earth-Centered-Inertial equatorial-plane frame.\n";
      satOut << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satOut << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satOut << "Mission Duration [Days] is "<< duration << "\n";
      satOut << "TimeIndex,X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]\n";

      // Keplerian elements as state output
      ofstream satOutKep; 
      satOutKep.open((satStateFp+"_Keplerian").c_str(),ios::binary | ios::out);
      satOutKep << "Satellite states as Keplerian elements.\n";
      satOutKep << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satOutKep << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satOutKep << "Mission Duration [Days] is "<< duration << "\n";
      satOutKep << "TimeIndex,SMA[km],ECC,INC[deg],RAAN[deg],AOP[deg],TA[deg]\n";                     

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
        
         // Write satellite ECI cartesian states to file
         satOut << std::setprecision(prc) << nSteps<< "," ;
         satOut << std::setprecision(prc) << cartState[0] << "," ;
         satOut << std::setprecision(prc) << cartState[1] << "," ;
         satOut << std::setprecision(prc) << cartState[2] << "," ;
         satOut << std::setprecision(prc) << cartState[3] << "," ;
         satOut << std::setprecision(prc) << cartState[4] << "," ;
         satOut << std::setprecision(prc) << cartState[5] << "\n" ; 

         Rvector6 kepState;
         kepState = sat1->GetKeplerianState();      
         // Write satellite Keplerian states to file
         satOutKep << std::setprecision(prc) << nSteps<< "," ;
         satOutKep << std::setprecision(prc) << kepState[0] << "," ;
         satOutKep << std::setprecision(prc) << kepState[1] << "," ;
         satOutKep << std::setprecision(prc) << kepState[2]*GmatMathConstants::DEG_PER_RAD << "," ;
         satOutKep << std::setprecision(prc) << kepState[3]*GmatMathConstants::DEG_PER_RAD << "," ;
         satOutKep << std::setprecision(prc) << kepState[4]*GmatMathConstants::DEG_PER_RAD << "," ;
         satOutKep << std::setprecision(prc) << kepState[5]*GmatMathConstants::DEG_PER_RAD << "\n" ;

         nSteps++; 

         // Propagate
         date->Advance(stepSize);
         prop->Propagate(*date); 
      
      }
      satOut.close();
      satOutKep.close();

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- propagation completed\n");
      #endif      
      
      //Delete objects
      delete    prop;
      delete    date;
      delete    state;
      delete    attitude;           
      delete    earth;
      // delete    sat1; ??

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
