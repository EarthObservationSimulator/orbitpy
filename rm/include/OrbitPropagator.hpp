/*
 * File:   OrbitPropagator.h
 * Author: Gabriel Apaza
 *
 * Created on October 23, 2018, 1:48 PM
 */

#ifndef ORBITPROPAGATOR
#define ORBITPROPAGATOR



//Global Variables
#include "source.hpp"



//GMAT util includes
#include "LagrangeInterpolator.hpp"
#include "GmatConstants.hpp"
#include "Rmatrix.hpp"
#include "Rvector3.hpp"
#include "Rvector6.hpp"
#include "RealUtilities.hpp"



//GMAT src includes
#include "IntervalEventReport.hpp"
#include "CoverageChecker.hpp"
#include "Propagator.hpp"
#include "NadirPointingAttitude.hpp"
#include "CustomSensor.hpp"
#include "ConicalSensor.hpp"
#include "RectangularSensor.hpp"
#include "Spacecraft.hpp"
#include "OrbitState.hpp"
#include "PointGroup.hpp"
#include "Propagator.hpp"
#include "Earth.hpp"
#include "VisiblePOIReport.hpp"
#include "AbsoluteDate.hpp"


//GMAT defs
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"



//RM includes
#include "MessageHandler.hpp"
#include "InstrumentCoverage.hpp" //Coverage class and Orbital Parameter classes
#include "OrbitalParameters.hpp"
#include "CacheInterface.hpp"

//Json Parser
#include <json/json.h>



//Standard Library
#include <string>
#include <map>
#include <vector>
#include <utility>
#include <unistd.h>
#include <ctime>
#include <stdlib.h>
#include <fstream>
#include <iostream>
#include <sys/param.h>
#include <sys/stat.h>
#include <algorithm>
#include <sstream>
#include <iomanip>





using namespace std;



//!  This class simulates a Satellite's orbit and calculates access history for ground stations and points of interest
/*!
    This class reads from <architecture>.json file and simulates one of the Satellites specified in that file.  <br>
    As the Satellite's orbit is propagated, access history is calculated for both the Ground Stations and Points of Interest. <br>
    This access data can be retrieved for further analysis.
*/
class OrbitPropagator {
public:


    //!  OrbitPropagator Constructor
    /*!
        \param ms - Json::Value object containing information from the "mission" field in <mission_name>.json
        \param sat - Json::Value object containing information from the "satellite" field in <architecture>.json
        \param gN - Json::Value object containing information from the "groundNetwork" field in <architecture>.json
        \param gs - A homogeneous grid size used to calculate the Points of Interest
        \param handler - A pointer to a MessageHandler used to read messages from the GUI
    */
    OrbitPropagator(Json::Value ms,
                    Json::Value sat,
                    PointGroup *  poiGroup,
                    PointGroup *  gsGroup,
                    string      path_cache,
                    string      path_writeFiles,
                    double      gs,
                    int         satNum,
                    int         constNum,
                    int         total_sat_number,
                    bool        printOutput);



    //!  OrbitPropagator Copy Constructor
    /*!
        Copies a OrbitPropagator object
    */
    OrbitPropagator(const OrbitPropagator& orig);




    //!  OrbitPropagator Destructor
    /*!
        Destroys a OrbitPropagator object
    */
    virtual ~OrbitPropagator();




    //! Creates an OrbitalParameter object based on the Satellite being simulated
    /*!
      \return void
    */
    void setOrbitalParameters(); // TESTED



    //! Creates InstrumentCoverage object for each of the Payloads specified for this Satellite
    /*!
      \return void
    */
    void setInstrumentCoverage();



    //! Propagates a Satellite's orbit and calculates access history based on the Area of Interest and the Ground Networks in this architecture
    /*!
      Writes access.csv <br>
      Writes obs.csv <br>
      Writes SatelliteStateDuringAccess.csv <br>
      <b>Needs to be updated for new architecture</b> <br> <br>
      This is the only method where we are checking for contact with the GUI <br>
      \return if the user aborts the run, this will return false and the whole program will terminate
      <b>Issue - if we are only evaluating one architecture per run, how will the other architecture know not to be ran on the "abort" signal?
    */
    bool propagateOrbit();




    //! Returns the number of points in the Area of Interest's PointGroup object
    /*!
      \return int
    */
    int getNumPoints();



    //! Returns the number of Ground Stations in the architecture
    /*!
      \return int
    */
    int getNumGS();



    //! Testing Function
    /*!
      Prints the Satellite's orbital parameters
    */
    void printOrbitalParameters();


    Real round(Real temp);




    //! Returns a reference to an object containing all the Ground Network access history
    /*!
      \return vector<IntervalEventReport>&
    */
    vector<IntervalEventReport> getGsEvents();



    //! Returns a reference to an object containing all the Area of Interest access history
    /*!
      \return vector< vector<IntervalEventReport> >&
    */
    vector<IntervalEventReport> getCoverageEvents();



    //! Returns the start date of the mission
    /*!
      \return Real - mission start date
    */
    Real getMissionStartDate();



    //! Returns the number of days the mission ran
    Real getMissionDays();

    //! Returns a vector of pairs containing the coordinates for each point of interest
    vector< pair< Real, Real > > getCoordVec();


    //! This is the object checking the messages sent from the GUI
    MessageHandler* messages;


    //! A pointer to an OrbitalParameters object
    /*!
      This objects holds the ephemeris data for the Satellite being propagated  <br>

      It is used to get the Satellite's start date and return ephemeris data
    */
    OrbitalParameters* orbitParams;


    //! Holds the coverage data for the Spacecraft's payload
    /*!
     * This object calls the instrument module to get all the coverage information for a specific instrument.
     * Curretnly, the instrument coverage specifications are hard coded
     *
     */
    InstrumentCoverage* coverage;
    //vector<InstrumentCoverage*> instrumentCoverages;

    CacheInterface* cache;



    // -------- These paths let us interface with the cache --------
    string satellite_file_name;
    string satellite_directory_path;
    string cache_accessFile_POI;
    string cache_accessFile_GS;
    string cache_obsPath;
    string link_obsPath;
    string cache_satAccessJSON;
    string link_satAccessJSON;
    string cache_satAccessCSV;
    string link_satAccessCSV;
    string cache_POI;
    string link_POI;
    string cache_recordFile;







    //! The number of days the mission ran
    Real missionDays;


    //! All the coverage events for this satellite (POI)
    vector<IntervalEventReport> coverageEvents;

    //! All the coverage events for this satellite (GS)
    vector<IntervalEventReport> gsEvents;


    //! Specifies the mission duration
    string missionDuration;

    string path_cacheDirectory;


    //! Determines if the obs.csv file is outputted
    bool outputStates;

    //! Determines if the satellite to be propagated is already in the cache or not
    bool sat_in_cache;

    //! Determines if the cache system is to be used or not
    bool use_cache;

    //! Checks to see if the directory specified exists
    bool does_directory_exist(string directoryPath);

    //! Creates the access files in the cache
    bool create_access_txt(string write_path_poi, string write_path_gs);

    //! Tells the Orbit Propagator if the cache is to be used or not
    void useCache(bool cacheValue);


    //! Determines if the instrument files are outputted
    bool outputInstrument;

    //! If true, print debugging output
    bool print_output;





    //! Contains a homogeneous grid size for calculating Points of Interest
    double gridSize;


    Real metricsInterpTime;

    //! This function will take the parameters for an IntervalEventReport and re-propagate the interval with a smaller interpolation step
    /*!
      \param MissionEpoch - when the event started
      \param tPropC - the propagation timestep of the correct step
      \param tInpC - the interpolation timestep of the correct step
      \param currEvent - the current event that is being propagated over
      \param eventNum - a counter for which event is currently being processed
      \param totalEvents - the total number of events found
      \param numSuccess - the number of correction steps that found access
      \param numFail - the number of correction steps that didn't find access
      \return - a vector of Interval Event Reports (should be of length 1)
    */
    vector<IntervalEventReport> intervalCorrection(Real missionEpoch,
                                                   Real tPropC,
                                                   Real tInpC,
                                                   Real tInpQ,
                                                   IntervalEventReport currEvent,
                                                   int& eventNum,
                                                   int totalEvents, int& numSuccess, int& numFail);



private:

    //! Takes a message from the message handler and deals with it accordingly
    /*!
      \param memo - the message passed by the message handler
      Based on the memo, this function will either call abort, pause, or neither

      \return if there is an abort signal we return false
    */
    bool handleMessage(string memo);


    //! This function takes a longitued bound in range (-180,180) and shifts it to the range (0,360)
    Real shiftLongitude(Real lon);


    //!Contains the path to write the access and satellite state files
    string writeFiles;

    //! Safely aborts the program -- in the future will save the satellite propagation data
    void abort();


    //! Pauses the module until the user hits the play button again
    void pause();




    //! Contains information on the from the <mission_name>.json file
    Json::Value tsr;

    //! Contains information from the "satellite" field in <architecture>.json
    Json::Value satellite;





    //! Contains the start date of the mission
    Real startDate;


    //! Contains which satellite in the architecture is being processed
    int satelliteNum;

    //! Contains the total amount of satellites that have been processed
    int total_sat_num;

    //! Contains which constellation in the architecture is being processed
    int constellationNum;


    //! This contains all the points of interest making up the Area of Interest
    PointGroup* pointsOfInterest;


    //! This contains all the ground stations of interest specified in the <architecture>.json
    PointGroup* gsOfInterest;





    //! Boolean value specifying if the Satellite has propulsion or not
    /*!
      If the Satellite has propulsion, no drag needs to be accounted for in the propagation
    */
    bool propulse;


    //! Specifies when the mission starts
    string missionStart;


    //! When the mission starts "Julian Date"
    Real missionEpoch;

    //! The starting date of the satellite
    Real satelliteEpoch;


    //The cone and clock IP are members of this class
    Rvector coneIP;
    Rvector clockIP;






    //! This parses the mission start date in <mission>.json
    vector<Integer> parseDate(string date);

    //! This parses the mission duration in <mission>.json
    Real parseDuration(string dur);



    void writeAccessIntervals(string write_path);





};

#endif /* ORBITPROPAGATOR */
