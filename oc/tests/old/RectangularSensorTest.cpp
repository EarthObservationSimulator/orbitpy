#include <iostream>
#include <string>
#include <ctime>
#include <cmath>
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

//------------------------------------------------------------------------------
// int main(int argc, char *argv[])
//------------------------------------------------------------------------------
int main(int argc, char *argv[])
{
  
  /******************** Initialization of auxillary items ***************************/
  
  std::string outFormat = "%16.9f ";
  

  // Set up the message receiver and log file
  ConsoleMessageReceiver *consoleMsg = ConsoleMessageReceiver::Instance();
  MessageInterface::SetMessageReceiver(consoleMsg);
  std::string outPath = "./";
  MessageInterface::SetLogFile(outPath + "GmatLog.txt");
  MessageInterface::SetLogEnable(true);
  MessageInterface::ShowMessage("%s\n",GmatTimeUtil::FormatCurrentTime().c_str());
 
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
  
  /******************** Initialize objects with user values * ************************************/

  AbsoluteDate             *date;
  OrbitState               *state;
  RectangularSensor        *rectSensor;
  Spacecraft               *sat1;
  Propagator               *prop;
  PointGroup               *pGroup;
  Earth                    *earth;
  NadirPointingAttitude    *attitude;
  LagrangeInterpolator     *interp;
  std::vector<IntervalEventReport> coverageEvents; // container to hold the coverage events

  pGroup = new PointGroup();
  earth = new Earth();
  date = new AbsoluteDate();
  state = new OrbitState();
  rectSensor = new RectangularSensor(7.5*PI/180.0, 7.5*PI/180.0); // 15 deg, 15 deg FOV?
 
  interp = new LagrangeInterpolator("TATCLagrangeInterpolator", 6, 7);
  attitude = new NadirPointingAttitude();
  

  // Set Landsat-8 orbit, TA~MA due to nearly circular orbit.
  date->SetGregorianDate(2019, 3, 19, 20, 16, 26.000);
  /* (Real SMA, Real ECC, Real INC, Real RAAN, Real AOP, Real TA) */
  state->SetKeplerianState(6378.137+703, 0.0001323, 98.1949*RAD_PER_DEG,
             150.0865*RAD_PER_DEG, 76.7198*RAD_PER_DEG, 283.4074*RAD_PER_DEG);

  sat1     = new Spacecraft(date, state, attitude, interp); 
  sat1->AddSensor(rectSensor); 

  prop = new Propagator(sat1);

  // Create the point group and initialize the coverage checker
  pGroup->AddHelicalPointsByNumPoints(200);
  CoverageChecker *covChecker = new CoverageChecker(pGroup,sat1);
  covChecker->SetComputePOIGeometryData(true);

  
  /**************************Start Propagation and Coverage accumulation********************************/
  
  /* whichTest 1 = accumulate as we propagate;
     whichTest 2 = propagate first, then interpolate for coverage 
  */
  Integer whichTest = 2;
  Real stepSize = 60; // Set step size depending on Sensor fov
  Real interpolationStepSize = 1;

  MessageInterface::ShowMessage("*** TEST*** Rectangular sensor !!!!\n");
  clock_t t0 = clock(); // for timing

  Real           epoch   = date->GetJulianDate();
  MessageInterface::ShowMessage(" epoch %.9f \n", epoch);
  IntegerArray   loopPoints;
  Integer numOfDays = 1;
         
  if (whichTest == 1)
  {
    // TEST 1: accumulate coverage data as we go, no interpolation here
    MessageInterface::ShowMessage("*** About to Propagate!!!!\n");
    // Propagate to the initial time first
    prop->Propagate(*date);
    while (date->GetJulianDate() < ((Real)epoch + numOfDays))
    {
        // Compute points in view
        loopPoints = covChecker->AccumulateCoverageData();

        // Propagate
        date->Advance(stepSize);
        prop->Propagate(*date);
    
        // Compute lat., lon., and height of s/c w/r/t the ellipsoid
        Real     jDate        = sat1->GetJulianDate();
        Rvector6 cartState    = sat1->GetCartesianState();
        Rvector3 inertialPosVec(cartState(0), cartState(1), cartState(2));
        Rvector3 latLonHeight = earth->InertialToBodyFixed(inertialPosVec,
                                                          jDate, "Spherical");
    }
    MessageInterface::ShowMessage(" --- propagation completed\n");
    // END TEST 1: accumulate coverage data as we go
  }
  else // whichTest = 2
  {
    Real           interpTime = epoch;
    Real           midRange   = 0.0;
    Real           propTime   = date->GetJulianDate();
    // TEST 2: propagate first, then accumulate coverage data:
    //         interpolate data when needed (number of points is
    //         sufficient and we are not about to fall off the
    //         time range
    // Propagate to the initial time first
    prop->Propagate(*date);
    while (date->GetJulianDate() < ((Real) epoch + numOfDays)) 
    {
        date->Advance(stepSize);
        prop->Propagate(*date);
        propTime = date->GetJulianDate();
        // Interpolate when and if needed
        if (sat1->TimeToInterpolate(propTime, midRange))
        {
          while (interpTime < (propTime - midRange))
          {
              loopPoints = covChecker->
                          AccumulateCoverageData(interpTime);
              interpTime += interpolationStepSize/
                            GmatTimeConstants::SECS_PER_DAY;
          }
        }
    }
    MessageInterface::ShowMessage(" --- propagation completed\n");

    // Interpolate to the end, if necessary
    propTime = date->GetJulianDate();
    while (interpTime <= propTime)
    {
        loopPoints = covChecker->
                    AccumulateCoverageData(interpTime);
        interpTime += interpolationStepSize/
                      GmatTimeConstants::SECS_PER_DAY;
    }
    
    MessageInterface::ShowMessage(" --- interpolation completed\n");
    // END TEST 2: propagate first, then accumulate coverage data
  }

  coverageEvents = covChecker->ProcessCoverageData();

  // check timing
  Real timeSpent = ((Real) (clock() - t0)) / CLOCKS_PER_SEC;
  MessageInterface::ShowMessage("TIME SPENT is %.9f seconds\n",timeSpent);
  
  /**************************Process Coverage data ********************************/
  // Compute access data.
  MessageInterface::ShowMessage("EventNum,POI,AccessFrom[Days],Duration[s]\n");
  // Compute total coverage statistics from all coverage events;
  for (UnsignedInt eventIdx = 0; eventIdx < coverageEvents.size(); eventIdx++)
  {
      IntervalEventReport currEvent = coverageEvents.at(eventIdx);
      Integer          poiIndex       = currEvent.GetPOIIndex();
      std::vector<VisiblePOIReport> discreteEvents = currEvent.GetPOIEvents();
      Real             eventDuration  = (currEvent.GetEndDate().GetJulianDate() -
                                        currEvent.GetStartDate().GetJulianDate()) * GmatTimeConstants::SECS_PER_DAY;

      MessageInterface::ShowMessage(
                           "%d,%d,%.9f,%.9f\n",
                           eventIdx,
                           poiIndex,
                           currEvent.GetStartDate().GetJulianDate() - epoch,
                           eventDuration);      
  }

  MessageInterface::ShowMessage(" END OF TEST \n");
  MessageInterface::ShowMessage("\n");

}


