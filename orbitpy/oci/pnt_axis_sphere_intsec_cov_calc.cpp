//------------------------------------------------------------------------------
//                         Coverage Calcs with Pointing Options
//------------------------------------------------------------------------------
//
// Author: Vinay Ravindra
// Created: 2020.09.23
//
/** 
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
#define DEBUG_CHK_INPS

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;

/**
 * @param popts_fl pointing options file path and name
 * @param satStateFp Filename, path to write the satellite ECI states
 * @param satAccFp Filename, path to write the computed satellite access data
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
  string popts_fl; 
  string satStateFp;
  string satAccFp;

  if(argc==4){            
      popts_fl = argv[1];
      satStateFp = argv[2];
      satAccFp = argv[3];
   }else{
      MessageInterface::ShowMessage("Please input right number of arguments.\n");
      exit(1);
   }  

   #ifdef DEBUG_CHK_INPS
      MessageInterface::ShowMessage("Pointing options file path is %s \n", popts_fl.c_str());
      MessageInterface::ShowMessage("Satellite states file path, name is: %s \n", satStateFp.c_str());
      MessageInterface::ShowMessage("Satellite access file path, name is: %s \n", satAccFp.c_str());
   #endif
   
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** About to read in pointing options ******\n");
   #endif
   RealArray euler_angle1, euler_angle2, euler_angle3; // The pointing-options are defined with respect to the Nadir-frame
   oci_utils::readPntOptsFile(popts_fl, euler_angle1, euler_angle2, euler_angle3);  
   Integer numPntOpts = euler_angle1.size();
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** Finished reading in pointing options  ******\n");
   #endif

   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** About to read satellite state file header ******\n");
   #endif
   // Read the epoch and satellite state at the epoch from input satellite state file
   Real epoch, duration, stepSize;
   Rvector6 state0;
   oci_utils::readSatStateFileHeader(satStateFp,  epoch,  stepSize, duration, state0);
   #ifdef DEBUG_CHK_INPS
      MessageInterface::ShowMessage("Epoch is %f \n", epoch);
      MessageInterface::ShowMessage("stepSize is: %f \n", stepSize);
      MessageInterface::ShowMessage("duration is: %f \n", duration);
      MessageInterface::ShowMessage("*** state0 is %f, %f, %f, %f, %f, %f \n", state0(0), state0(1), state0(2), state0(3), state0(4), state0(5));
   #endif
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** Finished reading satellite state file header ******\n");
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

      #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
         // Create the container to hold the coverage events
         std::vector<IntervalEventReport> coverageEvents;
      #endif      
      
      clock_t t0 = clock(); // for timing

      // Create an Earth model
      earth = new Earth();
      
       // Create the epoch object and set the initial epoch
      date = new AbsoluteDate();
      date->SetJulianDate(epoch);
      
      // Create the spacecraft state object and set Keplerian elements
      state = new OrbitState();
      state->SetCartesianState(state0);
      
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

      // Write the access file in matrix format with rows as the time and columns as ground-points. 
      // Each entry in a cell of the matrix corresponds to 0 (No Access) or 1 (Access).
      ofstream satAcc; 
      satAcc.open(satAccFp.c_str(),ios::binary | ios::out);
      satAcc << "Satellite states are in Earth-Centered-Inertial equatorial-plane frame.\n";
      satAcc << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satAcc << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satAcc << "Mission Duration [Days] is "<< duration << ".\n";
      satAcc << "TimeIndex,";
      for(int i=0;i<numPntOpts;i++){
         satAcc<<"pntopt"<<i;
         if(i<numPntOpts-1){
            satAcc<<",";
         }
      }
      satAcc << "\n";

      ifstream satState(satStateFp.c_str());

      if(!satState){
          std::cerr << "Cannot open the Satellite State File : "<<satStateFp.c_str()<<std::endl;
          return -1;
      }

      string line;
      std::getline(satState,line); 
      std::getline(satState,line); 
      std::getline(satState,line);
      std::getline(satState,line);
      std::getline(satState,line);

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("Start looping through the states.\n");
      #endif
      int nSteps = 0;

      while (std::getline(satState,line))
      {        
        Rvector6 _state;
        Real _date;
        RealArray e;
        int i=0;
        stringstream ss(line);
        while(ss.good()){
            string substr;
            std::getline(ss, substr, ',');
            if(i==0){
                _date = epoch + stepSize*stoi(substr)*GmatTimeConstants::DAYS_PER_SEC;
            }
            else{
                e.push_back(stod(substr));               
            }
            i++;
        }        
        _state.Set(e[0], e[1], e[2], e[3], e[4], e[5]);

        date->SetJulianDate(_date);
        state->SetCartesianState(_state);

        satAcc << std::setprecision(4) << nSteps;
        
        /** Iterate over all pointing options **/
        for(int j=0;j<numPntOpts;j++){
        sat1->SetBodyNadirOffsetAngles(euler_angle1[j],euler_angle2[j],euler_angle3[j],1,2,3); 
        Rmatrix33 R_N2B = sat1->GetNadirTOBodyMatrix();

        Rvector6 earthFixedState  = earth->GetBodyFixedState(_state, _date);
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
      
      }
      satAcc.close(); 
      satState.close();

      //Delete un-needed objects
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
