//------------------------------------------------------------------------------
//                               Mission
//------------------------------------------------------------------------------
//
// Author: Vinay Ravindra
// Created: 2020.02.12
//
/**
 * Run a single satellite mission.
 * 
 * There are two types of coverage calculations possible using OC:
 * (1) accumulate coverage as we propagate.
 * (2) propagate first with large time-step, and later accumulate using interpolation with smaller time steps.
 * Method (1) is implemented.
 * 
 * The pointing of the satellite is fixed to be Nadir-pointing.
 * Lat must be in the range -pi/2 to pi/2, while lon must be in the range -pi to pi
 * 
 * Log file is written in the bin directory
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



int readCovGridFile(const string &covGridFp, RealArray &lats, RealArray &lons)
{
    ifstream in(covGridFp.c_str());

    if(!in){
  		std::cerr << "Cannot open the Coverage Grid File : "<<covGridFp.c_str()<<std::endl;
		return -1;
    }

    string line;
    while (getline(in,line))
    {
      stringstream ss(line);
      vector<string> vecStrOut;

      while(ss.good()){
         string substr;
         std::getline( ss, substr, ',' );
         vecStrOut.push_back( substr );
      }
     
      if(vecStrOut[0] == "" or vecStrOut[0] == "regi"){
         continue;
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

/**
 * @param epoch mission epoch in UTCGregorian 
 * @param sma semi-major axis in kilometers
 * @param ecc eccentricity
 * @param inc inclination in degrees
 * @param raan right ascension of the ascending node in degrees
 * @param aop argument of perigee in degrees
 * @param ta true anomaly in degrees
 * @param duration mission duration in days
 * @param covGridFp coverage grid file path and name
 * @param senType sensor type
 * @param senOrien sensor orientation (euler angles and sequence)
 * @param senClock sensor clock angles in degrees
 * @param senCone sensor cone angles in degrees
 * @param stepSize propagation step size
 * @param satFn Filename, path to write the satellite ECI states
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
  MessageInterface::SetLogFile(outPath + "OClog.txt");
  MessageInterface::SetLogEnable(true);
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
  string covGridFp; 
  string senType; 
  string _senOrien; 
  string _senClock; 
  string _senCone; 
  Real stepSize; 
  string satFn;
  string satAccFn;

  if(argc==17){            
      _epoch = argv[1];
      sma = Real(stod(argv[2]));
      ecc = Real(stod(argv[3]));
      inc = Real(stod(argv[4]));
      raan = Real(stod(argv[5]));
      aop = Real(stod(argv[6]));
      ta = Real(stod(argv[7]));
      duration = Real(stod(argv[8]));
      covGridFp = argv[9];
      senType = argv[10];
      _senOrien = argv[11];
      _senClock = argv[12];
      _senCone = argv[13];
      stepSize = Real(stod(argv[14]));
      satFn = argv[15];
      satAccFn = argv[16];
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

   RealArray senOrien(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_senOrien, ',')));
   if(senOrien.size()!=6){
      MessageInterface::ShowMessage("Sensor orientation must be specified in a set of euler angles and sequence.\n");
      exit(1);
   }

   RealArray senClock(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_senClock, ',')));
   RealArray senCone(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_senCone, ',')));
   if(senCone.size()==0){
      MessageInterface::ShowMessage("Atleast one sensor cone angle must be present.\n");
      exit(1);
   }
   if(senType!="Conical" && senCone.size()!=senClock.size()){ 
      MessageInterface::ShowMessage("The number of sensor cone and clock angles must be the same for non-conical sensor.\n");
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
      MessageInterface::ShowMessage("Coverage grid file path is %s \n", covGridFp.c_str());
      MessageInterface::ShowMessage("Sensor type is %s \n", senType.c_str());
      MessageInterface::ShowMessage("Sensor Orientation is %16.9f, %16.9f, %16.9f,%16.9f, %16.9f, %16.9f \n", senOrien[0], senOrien[1], senOrien[2], senOrien[3], senOrien[4], senOrien[5]);
      MessageInterface::ShowMessage("Sensor cone angle vector is: ");
      for(int i =0; i<senCone.size(); i++){
         MessageInterface::ShowMessage(" %16.9f ", senCone[i]);
      }
      MessageInterface::ShowMessage("\n");
      MessageInterface::ShowMessage("Sensor clock angle vector is: ");
      for(int i =0; i<senClock.size(); i++){
         MessageInterface::ShowMessage(" %16.9f ", senClock[i]);
      }
      MessageInterface::ShowMessage("\n");
      MessageInterface::ShowMessage("Step size is %16.9f \n", stepSize);
      MessageInterface::ShowMessage("Satellite states file path, name is: %s \n", satFn.c_str());
      MessageInterface::ShowMessage("Satellite access file path, name is: %s \n", satAccFn.c_str());
   #endif
   
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** About to read in Coverage grid ******\n");
   #endif
   /** Read in the coverage grid **/
   RealArray lats, lons;
   readCovGridFile(covGridFp, lats, lons);  
   PointGroup               *pGroup = new PointGroup();
   pGroup->AddUserDefinedPoints(lats, lons);
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** Finished reading in Coverage grid ******\n");
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
      ConicalSensor            *conicalSensor;
      Spacecraft               *sat1;
      Propagator               *prop;
      CoverageChecker          *covChecker;
	   Earth                    *earth;
      CustomSensor             *customSensor;
      NadirPointingAttitude    *attitude;
      LagrangeInterpolator     *interp = new LagrangeInterpolator( // Not used really.
                                             "TATCLagrangeInterpolator", 6, 7);


      // Create the container to hold the coverage events
      std::vector<IntervalEventReport> coverageEvents;
      
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
      sat1     = new Spacecraft(date, state, attitude, interp); //,0.0, 0.0,
                                                                  // 180.0);
         
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** DONE creating Spacecraft!!!!\n");
         MessageInterface::ShowMessage("**** attitude and sat1 OK "
                                       "**************\n");
      #endif

   
      // Add sensor to satellite
      if(senType == "CONICAL"){
         conicalSensor = new ConicalSensor(senCone[0]*RAD_PER_DEG);
         conicalSensor->SetSensorBodyOffsetAngles(senOrien[3]*RAD_PER_DEG, senOrien[4]*RAD_PER_DEG, senOrien[5]*RAD_PER_DEG, senOrien[0], senOrien[1], senOrien[2]);
         sat1->AddSensor(conicalSensor);

      }else if(senType == "CUSTOM"){

         std::vector<double> senCone_r(senCone.size()); 
         std::transform(senCone.begin(), senCone.end(), senCone_r.begin(),[](double i){ return i * RAD_PER_DEG; });
         std::vector<double> senClock_r(senClock.size()); 
         std::transform(senClock.begin(), senClock.end(), senClock_r.begin(),[](double i){ return i * RAD_PER_DEG; });

         customSensor =  new CustomSensor(senCone_r, senClock_r);
         customSensor->SetSensorBodyOffsetAngles(senOrien[3]*RAD_PER_DEG, senOrien[4]*RAD_PER_DEG, senOrien[5]*RAD_PER_DEG, senOrien[0], senOrien[1], senOrien[2]);
         sat1->AddSensor(customSensor);
      }

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** Creating and adding sensors OK **************\n");
      #endif
      
      // Create the propagator
      prop = new Propagator(sat1);
      
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** DONE creating Propagator!!!!\n");
      #endif      
      
     
      // Initialize the coverage checker
      covChecker = new CoverageChecker(pGroup,sat1);
      covChecker->SetComputePOIGeometryData(true);
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** Coverage Checker created!!!!\n");
      #endif
      
      // Propagate for a duration and collect data
      Real           startDate   = date->GetJulianDate();
      IntegerArray   loopPoints;

      /** Write satellite access files **/
      const int prc = std::numeric_limits<double>::digits10 + 1; // set to maximum precision

      ofstream satOut; 
      satOut.open(satFn.c_str(),ios::binary | ios::out);
      satOut << "Satellite states are in Earth-Centered-Inertial equatorial plane.\n";
      satOut << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satOut << "All time is referenced to the Epoch.\n";
      satOut << "Mission Duration [Days] is "<< duration << "\n";
      satOut << "Time[s],X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]\n";
      
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** About to Propagate!!!!\n");
      #endif
      int nSteps = 0;
      // Propagate to the initial time first
      prop->Propagate(*date);
      while (date->GetJulianDate() < ((Real)startDate +
                                       duration))
      {
         loopPoints = covChecker->AccumulateCoverageData();

         // Propagate
         date->Advance(stepSize);
         prop->Propagate(*date);
         
         Rvector6 cartState;
         cartState = sat1->GetCartesianState();

         // Write satellite states to file
         satOut << std::setprecision(prc) << nSteps * stepSize << "," ;
         satOut << std::setprecision(prc) << cartState[0] << "," ;
         satOut << std::setprecision(prc) << cartState[1] << "," ;
         satOut << std::setprecision(prc) << cartState[2] << "," ;
         satOut << std::setprecision(prc) << cartState[0] << "," ;
         satOut << std::setprecision(prc) << cartState[1] << "," ;
         satOut << std::setprecision(prc) << cartState[2] << "\n" ; 
         
         nSteps++;
      
      }
      satOut.close();
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- propagation completed\n");
      #endif
      
      // Compute coverage data
      coverageEvents = covChecker->ProcessCoverageData();
      MessageInterface::ShowMessage(" --- ProcessCoverageData completed \n");
      if (coverageEvents.empty())
      {
         MessageInterface::ShowMessage("--- !! No events !!\n");
         exit(0);
      }
      
      //Delete un-needed objects
      delete    covChecker;
      delete    prop;
      // delete    sat1;  // deletes date, state, attitude, interp - so DON'T
      delete    date;
      delete    state;
      delete    attitude;
      
      if(senType == "Conical"){
         delete    conicalSensor;
      }else if(senType == "Custom"){
         delete    customSensor;
      }      
      delete    earth;

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- Done deleting old pointers\n");
      #endif


      // check timing
      Real timeSpent = ((Real) (clock() - t0)) / CLOCKS_PER_SEC;
      MessageInterface::ShowMessage("TIME SPENT is %12.10f seconds\n",timeSpent);

      
      #ifdef DEBUG_CONSISE
      MessageInterface::ShowMessage("Writing results\n");
      #endif

      /** Write satellite access files **/
      ofstream satAcc; 
      satAcc.open(satAccFn.c_str(),ios::binary | ios::out);
      satAcc << "Satellite states are in Earth-Centered-Inertial equatorial plane.\n";
      satAcc << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satAcc << "All time is referenced to the Epoch.\n";
      satAcc << "Mission Duration [Days] is "<< duration << "\n";
      satAcc << "eventNum,gpi,accessFrom[Days],duration[s],time[Days],x[km],y[km],z[km],vx[km/s],vy[km/s],vz[km/s]\n";

      for (UnsignedInt eventIdx = 0; eventIdx < coverageEvents.size(); eventIdx++)
      {
            IntervalEventReport currEvent = coverageEvents.at(eventIdx);
            Integer          poiIndex       = currEvent.GetPOIIndex();
            std::vector<VisiblePOIReport> discreteEvents = currEvent.GetPOIEvents();
            Real             eventDuration  = (currEvent.GetEndDate().GetJulianDate() -
                                             currEvent.GetStartDate().GetJulianDate()) * GmatTimeConstants::SECS_PER_DAY;
            VisiblePOIReport ev = discreteEvents[int(discreteEvents.size()/2)]; // The 1/2 factor allows to access the middle of the access period.
     
            satAcc << eventIdx << "," ;
            satAcc << poiIndex << "," ;
            satAcc << std::setprecision(prc) << currEvent.GetStartDate().GetJulianDate() - startDate << "," ;
            satAcc << std::setprecision(prc) << eventDuration << "," ;
            satAcc << std::setprecision(prc) << (ev.GetStartDate().GetJulianDate() - startDate) << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsPosInertial()[0] << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsPosInertial()[1] << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsPosInertial()[2] << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsVelInertial()[0] << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsVelInertial()[1] << "," ;
            satAcc << std::setprecision(prc) << ev.GetObsVelInertial()[2] << "\n" ;     
      }
      satAcc.close();  
      
      
      
      MessageInterface::ShowMessage("*** END ***\n");
   
   
   }
   catch (BaseException &be)
   {
      MessageInterface::ShowMessage("Exception caught: %s\n",
                                    be.GetFullMessage().c_str());
   }
   
}