//------------------------------------------------------------------------------
//                    Coverage Calcs with Pointing Options
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
 * The pointing of the satellite is fixed to be Nadir-pointing nominally. When the 'yaw180_flag' is set,
 * the satellite is rotated about 180 deg about yaw axis and additional coverage is calculated.
 * 
 * Latitudes must be in the range -pi/2 to pi/2, while longitudes must be in the range -pi to pi.
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
//#define COMPUTE_AND_STORE_POI_GEOMETRY

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
 * @param covGridFp coverage grid file path and name
 * @param fovGeom sensor FOV geometry type
 * @param senOrien sensor orientation (sequence and euler angles in degrees, eg: "1,2,3,20,10,30")
 * @param fovClock sensor clock angles in degrees
 * @param fovCone sensor cone angles in degrees
 * @param yaw180_flag 
 * @param stepSize propagation step size
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
  string _epoch; 
  Real sma; 
  Real ecc; 
  Real inc; 
  Real raan; 
  Real aop; 
  Real ta; 
  Real duration; 
  string covGridFp; 
  string fovGeom; 
  string _senOrien; 
  string _fovClock; 
  string _fovCone;
  bool yaw180_flag; 
  Real stepSize; 
  string satStateFp;
  string satAccFp;

  if(argc==18){            
      _epoch = argv[1];
      sma = Real(stod(argv[2]));
      ecc = Real(stod(argv[3]));
      inc = Real(stod(argv[4]));
      raan = Real(stod(argv[5]));
      aop = Real(stod(argv[6]));
      ta = Real(stod(argv[7]));
      duration = Real(stod(argv[8]));
      covGridFp = argv[9];
      fovGeom = argv[10];
      _senOrien = argv[11];
      _fovClock = argv[12];
      _fovCone = argv[13];
      yaw180_flag = bool(stoi(argv[14]));
      stepSize = Real(stod(argv[15]));
      satStateFp = argv[16];
      satAccFp = argv[17];
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

   RealArray fovClock(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_fovClock, ',')));
   RealArray fovCone(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_fovCone, ',')));
   if(fovCone.size()==0){
      MessageInterface::ShowMessage("Atleast one sensor cone angle must be present.\n");
      exit(1);
   }
   if(fovCone.size()!=fovClock.size()){ 
      MessageInterface::ShowMessage("The number of sensor cone and clock angles must be the same.\n");
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
      MessageInterface::ShowMessage("Sensor type is %s \n", fovGeom.c_str());
      MessageInterface::ShowMessage("Sensor Orientation is %16.9f, %16.9f, %16.9f,%16.9f, %16.9f, %16.9f \n", senOrien[0], senOrien[1], senOrien[2], senOrien[3], senOrien[4], senOrien[5]);
      MessageInterface::ShowMessage("Sensor cone angle vector is: ");
      for(int i =0; i<fovCone.size(); i++){
         MessageInterface::ShowMessage(" %16.9f ", fovCone[i]);
      }
      MessageInterface::ShowMessage("\n");
      MessageInterface::ShowMessage("Sensor clock angle vector is: ");
      for(int i =0; i<fovClock.size(); i++){
         MessageInterface::ShowMessage(" %16.9f ", fovClock[i]);
      }
      MessageInterface::ShowMessage("\n");
      MessageInterface::ShowMessage("yaw180_flag is %d \n", yaw180_flag);
      MessageInterface::ShowMessage("Step size is %16.9f \n", stepSize);
      MessageInterface::ShowMessage("Satellite states file path, name is: %s \n", satStateFp.c_str());
      MessageInterface::ShowMessage("Satellite access file path, name is: %s \n", satAccFp.c_str());
   #endif
   
   #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("**** About to read in Coverage grid ******\n");
   #endif
   /** Read in the coverage grid **/
   RealArray lats, lons;
   oci_utils::readCovGridFile(covGridFp, lats, lons);  
   PointGroup               *pGroup = new PointGroup();
   pGroup->AddUserDefinedPoints(lats, lons);
   Integer numGridPoints = lats.size();
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
   
      MessageInterface::ShowMessage("*** About to add Sensors!!!!\n");
      // Add sensor to satellite
      if(fovGeom == "CONICAL"){
         conicalSensor = new ConicalSensor(fovCone[0]*RAD_PER_DEG);
         conicalSensor->SetSensorBodyOffsetAngles(senOrien[3], senOrien[4], senOrien[5], senOrien[0], senOrien[1], senOrien[2]); // careful: angle in degrees
         sat1->AddSensor(conicalSensor);
         #ifdef DEBUG_CONSISE
            MessageInterface::ShowMessage("*** CONICAL Sensor added.\n");
         #endif
      }else if(fovGeom == "RECTANGULAR" || fovGeom == "CUSTOM"){

         std::vector<double> senCone_r(fovCone.size()); 
         std::transform(fovCone.begin(), fovCone.end(), senCone_r.begin(),[](double i){ return i * RAD_PER_DEG; });
         std::vector<double> senClock_r(fovClock.size()); 
         std::transform(fovClock.begin(), fovClock.end(), senClock_r.begin(),[](double i){ return i * RAD_PER_DEG; });
         customSensor =  new CustomSensor(senCone_r, senClock_r);
         customSensor->SetSensorBodyOffsetAngles(senOrien[3], senOrien[4], senOrien[5], senOrien[0], senOrien[1], senOrien[2]); // careful: angle in degrees
         sat1->AddSensor(customSensor);
         #ifdef DEBUG_CONSISE
            MessageInterface::ShowMessage("*** RECTANGULAR/ CUSTOM Sensor added.\n");
         #endif
      }else{
         MessageInterface::ShowMessage("**** Warning no Sensor defined!! ****\n");
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
      
      #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
         covChecker->SetComputePOIGeometryData(true); 
      #else
         covChecker->SetComputePOIGeometryData(false); 
      #endif    
      
      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage("*** Coverage Checker created!!!!\n");
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

      // Write the access file in matrix format with rows as the time and columns as ground-points. 
      // Each entry in a cell of the matrix corresponds to 0 (No Access) or 1 (Access).
      ofstream satAcc; 
      satAcc.open(satAccFp.c_str(),ios::binary | ios::out);
      satAcc << "Satellite states are in Earth-Centered-Inertial equatorial-plane frame.\n";
      satAcc << "Epoch[JDUT1] is "<< std::fixed << std::setprecision(prc) << startDate <<"\n";
      satAcc << "Step size [s] is "<< std::fixed << std::setprecision(prc) << stepSize <<"\n";
      satAcc << "Mission Duration [Days] is "<< duration << ".\n";
      satAcc << "TimeIndex,";
      for(int i=0;i<numGridPoints;i++){
         satAcc<<"GP"<<i;
         if(i<numGridPoints-1){
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
         #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
            loopPoints = covChecker->AccumulateCoverageData();
         #else
            loopPoints = covChecker->CheckPointCoverage();
         #endif

         if(yaw180_flag == true){
            // Rotate satellite around z-axis by 180 deg and calculate coverage
            sat1->SetBodyNadirOffsetAngles(0,0,180,1,2,3);
            #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
               loopPoints_yaw180 = covChecker->AccumulateCoverageDataAtPreviousTimeIndex();
            #else
               loopPoints_yaw180 = covChecker->CheckPointCoverage();
            #endif

            sat1->SetBodyNadirOffsetAngles(0,0,0,1,2,3); // Reset the satellite attitude to Nadir-pointing
            // Add the points to the list of points seen. Sort and remove possible duplicates (in case of overlap)
            loopPoints.insert( loopPoints.end(), loopPoints_yaw180.begin(), loopPoints_yaw180.end() );
            // remove duplicates
            sort( loopPoints.begin(), loopPoints.end() );
            loopPoints.erase( unique( loopPoints.begin(), loopPoints.end() ), loopPoints.end() );
         }
        
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

         // Write access data         
         // Make array with '1' (Access) in the cells corresponding to indices of gp's accessed
         // and nothing with there is no access.
         if(loopPoints.size()>0){
            // If no ground-points are accessed at this time, skip writing the row altogether.
            IntegerArray accessRow(numGridPoints,0);
            for(int j = 0; j<loopPoints.size();j++){
               accessRow[loopPoints[j]] = 1;
            }
            satAcc << std::setprecision(prc) << nSteps;
            for(int k=0; k<numGridPoints; k++){
               if(accessRow[k] == 1){
                  satAcc<< ",1";
               }else{
                  satAcc<< ",";
               }
               
            }
            satAcc << "\n";
            }        
         nSteps++; 

         // Propagate
         date->Advance(stepSize);
         prop->Propagate(*date); 
      
      }
      satOut.close();
      satOutKep.close();
      satAcc.close(); 

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- propagation completed\n");
      #endif
      
      #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
      // Compute coverage data
      coverageEvents = covChecker->ProcessCoverageData();
      MessageInterface::ShowMessage(" --- ProcessCoverageData completed \n");
      if (coverageEvents.empty())
      {
         MessageInterface::ShowMessage("--- !! No events !!\n");
         //exit(0);
      }
      #endif
      
      //Delete un-needed objects
      delete    covChecker;
      delete    prop;
      // delete    sat1;  // deletes date, state, attitude, interp - so DON'T
      delete    date;
      delete    state;
      delete    attitude;
      
      if(fovGeom == "Conical"){
         delete    conicalSensor;
      }else if(fovGeom == "Custom" || fovGeom=="Rectangular"){
         delete    customSensor;
      }      
      delete    earth;

      #ifdef DEBUG_CONSISE
         MessageInterface::ShowMessage(" --- Done deleting old pointers\n");
      #endif


      // check timing
      Real timeSpent = ((Real) (clock() - t0)) / CLOCKS_PER_SEC;
      MessageInterface::ShowMessage("TIME SPENT is %12.10f seconds\n",timeSpent);

            
      #ifdef COMPUTE_AND_STORE_POI_GEOMETRY
      // TODO: Need to reqrite since accumulation of coverage is not performed previously.
      MessageInterface::ShowMessage("       =======================================================================\n");
      MessageInterface::ShowMessage("       ==================== Brief POI Geometry Report ========================\n");
      MessageInterface::ShowMessage("       POI index: Ground point index                               \n");
      MessageInterface::ShowMessage("       lat: Latitude of point in degrees                     \n");
      MessageInterface::ShowMessage("       lon: Longitude of point in degrees                    \n");
      MessageInterface::ShowMessage("       Mid access date: Date of the middle of the access (Julian Day UT1) \n");
      MessageInterface::ShowMessage("       Access duration: Access duration in seconds                 \n");
      MessageInterface::ShowMessage("       obsZenith: Satellite zenith in degrees                      \n");
      MessageInterface::ShowMessage("       obsAzimuth : Satellite azimuth in degrees                   \n");
      MessageInterface::ShowMessage("       obsRange   : Satellite range in kilometers                  \n");
      MessageInterface::ShowMessage("       sunZenith   : Satellite zenith in degrees                   \n");
      MessageInterface::ShowMessage("       sunAzimuth   : Satellite azimuth in degrees                 \n");
      MessageInterface::ShowMessage("       =======================================================================\n");
      MessageInterface::ShowMessage("       =======================================================================\n");
      MessageInterface::ShowMessage("  ");
      satAcc << "    POI index    lat      lon      obsZenith      obsAzimuth     obsRange    SunZenith      SunAzimuth\n";

      for (UnsignedInt eventIdx = 0; eventIdx < coverageEvents.size(); eventIdx++)
      {
            IntervalEventReport currEvent = coverageEvents.at(eventIdx);
            Integer          poiIndex       = currEvent.GetPOIIndex();
            std::vector<VisiblePOIReport> discreteEvents = currEvent.GetPOIEvents();
            Real             eventDuration  = (currEvent.GetEndDate().GetJulianDate() -
                                             currEvent.GetStartDate().GetJulianDate()) * GmatTimeConstants::SECS_PER_DAY;
            VisiblePOIReport ev = discreteEvents[int(discreteEvents.size()/2)]; // The 1/2 factor allows to access the middle of the access period.
     
            Rvector3 *vec = pGroup->GetPointPositionVector(poiIndex);
            Real lon = (ATan(vec->GetElement(1),vec->GetElement(0))
                           *DEG_PER_RAD);
            Real lat = (ASin(vec->GetElement(2)/vec->GetMagnitude())
                           *DEG_PER_RAD);

            MessageInterface::ShowMessage(
                           "     %d    %le      %le      %le      %le      %le      %le      %le      %le     %le \n",
                           poiIndex,
                           lat,
                           lon,
                           ev.GetStartDate().GetJulianDate(),
                           eventDuration,
                           ev.GetObsZenith()*DEG_PER_RAD,
                           ev.GetObsAzimuth()*DEG_PER_RAD,
                           ev.GetObsRange(),
                           ev.GetSunZenith()*DEG_PER_RAD,
                           ev.GetSunAzimuth()*DEG_PER_RAD);
      }

      #endif       
      
      MessageInterface::ShowMessage("*** END ***\n");
   
   
   }
   catch (BaseException &be)
   {
      MessageInterface::ShowMessage("Exception caught: %s\n",
                                    be.GetFullMessage().c_str());
   }
   
}
