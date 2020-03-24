//------------------------------------------------------------------------------
//                               ReductionAndMetrics
//------------------------------------------------------------------------------
// TAT-C: Tradespace Analysis Tools for Constellations
//
// File:    orbitModule.cpp
//
// Author:  Gabriel Apaza
// Created: October 6, 2018, 6:43 PM
// PI:      Jon Verville and Paul Grogan
//
/**
 * Main CPP file for the Orbits module. It will be called by the
 * orbits_proxy.py file.
 *
 */
//------------------------------------------------------------------------------


//Class Includes
#include "Metrics.hpp"
#include "OrbitPropagator.hpp"
#include "GridSize.hpp"
#include "MessageHandler.hpp"
#include "AreaOfInterest.hpp"
#include "GroundNetwork.hpp"
#include "CacheInterface.hpp"

//Socket Includes
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <unistd.h>
#include <time.h>

//Standard Library
#include <utility>
#include <fstream>
#include <algorithm>
#include <cstdlib>
#include <string>
#include <iostream>
#include <iterator>
#include <thread>
#include <queue>
#include <vector>
#include <future>

//GMAT includes
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"
#include "Rvector6.hpp"
#include "Rvector3.hpp"
#include "Rmatrix.hpp"
#include "RealUtilities.hpp"
#include "AbsoluteDate.hpp"
#include "IntervalEventReport.hpp"

//Global Variables
#include "source.hpp"

//Json Parser
#include <json/json.h>

//Stardard TCP socket port
//#define PORT 80

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;


//Forward Declarations
vector< vector<Json::Value> >getConstellations(Json::Value mission, Json::Value architecture);
void                        connectToGUI       ();
string                      getTATC_Path       ();
string                      getCachePath       (string architecture_path);
Json::Value                 getJsonObj         (string filePath);
Real                        getMissionEpoch    (string date);
Real                        getMissionDuration (string dur);
string                      getMissionDirectory(string missionJSON);
bool                        doesCacheExist     (string pathToCache);
void                        satThread          (Json::Value ms,
                                                Json::Value sat,
                                                double      gs,
                                                string      path_writeFiles,
                                                PointGroup*  poiGroup,
                                                PointGroup*  gsGroup,
                                                int         satNum,
                                                int         constNum,
                                                string      path_cache,
                                                bool        use_cache,
                                                int         satCounter,
                                                vector<IntervalEventReport> &poi_report,
                                                vector<IntervalEventReport> &gs_report,
                                                Real &metricsIT);



/*
 * Command line arguments
 * 1. Path to <mission_name>.json (including mission file extension)
 * 2. Path to <architecture>.json (directory only)
 */
int main(int argc, char** argv) {
    time_t start = time(0);


    bool status = false;

    //Read in the first two command line arguments
    string path_binary               (argv[0]);
    string path_missionJson          (argv[1]);                                                        //  /...../Landsat8/landsat8.json
    string path_architectureDirectory(argv[2]);                                                        //  /...../Landsat8/arch-0
    string path_missionDirectory      = getMissionDirectory(path_missionJson);                         //  /...../Landsat8
    string path_cacheDirectory        = getCachePath(path_architectureDirectory)  + "/cache";          //  /...../Landsat8/cache
    string path_cacheDirectoryPOI     = path_cacheDirectory      + "/poi.csv";                         //  /...../Landsat8/cache/poi.csv
    string path_architectureJson      = path_architectureDirectory + "/arch.json";                     //  /...../Landsat8/arch-0/arch.json
    string path_tatc                  = getTATC_Path();
    Json::Value archJson              = getJsonObj(path_architectureJson);
    Json::Value tsrJson               = getJsonObj(path_missionJson);
    Json::Value groundNetworkJson     = archJson["groundSegment"];

    int         position              = path_architectureDirectory.find_last_of("/");
    string      archFileName          = path_architectureDirectory.substr( (position+1) , string::npos);
    Real        missionDuration       = getMissionDuration(tsrJson["mission"]["duration"].asString()); //Days
    Real        missionEpoch          = getMissionEpoch   (tsrJson["mission"]["start"].asString());    //Seconds








    // -------- CACHE INTERFACE --------
    CacheInterface* cache = new CacheInterface(path_cacheDirectory);




    // -------- RETRIEVE ALL CONSTELLATIONS --------
    vector< vector<Json::Value> >       all_constellations              = getConstellations(tsrJson, archJson);
    int                                 all_constellations_num          = all_constellations.size();
    int                                 total_sats                      = 0;
    int                                 total_constellations            = 0;
    for(int x = 0; x < all_constellations.size(); x++)
    {
        total_constellations++;
        vector<Json::Value> temp = all_constellations[x];
        for(int y = 0; y < temp.size(); y++)
        {
            cout << "Constellation: " << x << " Satellite: " << y << endl;
            total_sats++;
        }
    }
    cout << endl << endl;
    cout << "+--- Total Constellations: " << total_constellations << endl;
    cout << "+--------Total Satellites: " << total_sats << endl;





    // -------- OUTPUT SETTINGS --------
    bool outputGlobal     = true;
    bool outputLocal      = true;
    bool outputAccess     = false;
    bool outputInstrument = true;
    bool use_cache        = true;
    bool use_threads      = false;
    if(tsrJson["settings"]["outputs"].isMember("orbits.global")){
        outputGlobal      = tsrJson["settings"]["outputs"]["orbits.global"].asBool();
    }
    if(tsrJson["settings"]["outputs"].isMember("orbits.local")){
        outputLocal       = tsrJson["settings"]["outputs"]["orbits.local"].asBool();
    }
    if(tsrJson["settings"]["outputs"].isMember("orbits.access")){
        outputAccess      = tsrJson["settings"]["outputs"]["orbits.access"].asBool();
    }
    if(tsrJson["settings"]["outputs"].isMember("orbits.instrumentAccess")){
        outputInstrument  = tsrJson["settings"]["outputs"]["orbits.instrumentAccess"].asBool();
    }
    if(tsrJson["settings"].isMember("useCache")){
        use_cache         = tsrJson["settings"]["useCache"].asBool();
    }
    if(tsrJson["settings"].isMember("useThreading")){
        use_threads       = tsrJson["settings"]["useThreading"].asBool();
    }



    // ------- GRID SIZE --------
    GridSize*       gridCalc  = new GridSize();
    Real            gridSize  = gridCalc->findHomogeneousGrid(tsrJson);

    // ------- AREA OF INTEREST --------
    AreaOfInterest* poiArea   = new AreaOfInterest(tsrJson, gridSize);
    GroundNetwork*  gnArea    = new GroundNetwork(groundNetworkJson);

    // ------- METRICS -------
    Metrics*        output    = new Metrics(tsrJson,
                                            poiArea->getNumPoints(),
                                            missionEpoch,
                                            gnArea->getNumStations(),
                                            missionDuration,
                                            path_architectureDirectory,
                                            path_cacheDirectory,
                                            poiArea->getCoordVec());



    if(!use_threads)
    {
        int satellite_counter = 0;
        for(int constellation = 0; constellation < all_constellations_num; constellation++)//-----------Iterate over constellations
        {
            vector<Json::Value> sats_in_constellation = all_constellations[constellation];
            for(int sat = 0; sat < sats_in_constellation.size(); sat++)//-------------------------------Iterate over sats in constellation
            {
                //Colorful Output
                string cont_sat_alert = string("\033[1;31mConstellation: ") + to_string(constellation+1) + string(" Satellite: ") + to_string(sat+1) + string("\033[0m");
                cout << endl << endl << endl << "--------------------------> " + cont_sat_alert + " <--------------------------" << endl;

                Json::Value      satellite = sats_in_constellation[sat];
                OrbitPropagator* sim       = new OrbitPropagator(tsrJson,
                                                                 satellite,
                                                                 poiArea->getPointGroup(),
                                                                 gnArea->getPointGroup(),
                                                                 path_cacheDirectory,
                                                                 path_architectureDirectory,
                                                                 gridSize,
                                                                 sat,
                                                                 constellation,
                                                                 satellite_counter,
                                                                 true);
                sim->useCache(use_cache);
                sim->setOrbitalParameters();
                sim->setInstrumentCoverage();
                status = sim->propagateOrbit();

                //Add data to metrics object -- outside threads
                output->setInterpTime(sim->metricsInterpTime);
                output->addPOIData(sim->getCoverageEvents());
                output->addGSData(sim->getGsEvents());
                delete sim;

                satellite_counter++;
            }
        }
    }




    // ------------------------------------------------------------------- THREAD TESTING START -------------------------------------------------------------------
    if(use_threads)
    {
        int satellite_counter = 0;
        // Create pointers for vector<IntervalEventReport> for threads
        vector< vector< IntervalEventReport > > poi_reports;
        vector< vector< IntervalEventReport > > gs_reports;
        vector<Real>        interpTimes;
        vector<std::thread> threads;
        int                 satCounter = 0;
        for(int x = 0; x < total_sats; x++)
        {
            vector<IntervalEventReport> temp_poi;
            vector<IntervalEventReport> temp_gs;
            poi_reports.push_back       (temp_poi);
            gs_reports.push_back        (temp_gs);
            interpTimes.push_back       (0);
        }
        cout << endl << "-- Number of Threads: " << total_sats << endl;
        // NEW STUFF
        for(int constellation = 0; constellation < all_constellations_num; constellation++)//------------Iterate over the constellations
        {
            vector<Json::Value> sats_in_constellation = all_constellations[constellation];

            for(int sat = 0; sat < sats_in_constellation.size(); sat++)//--------------------------------Iterate over the satellites in a constellation
            {
                cout << "-- Thread " << (satCounter+1) << " started" << endl;
                Json::Value      satellite = sats_in_constellation[sat];

                std::thread temp_thread (&satThread,
                                         tsrJson,
                                         satellite,
                                         gridSize,
                                         path_architectureDirectory,
                                         poiArea->getPointGroup(),
                                         gnArea->getPointGroup(),
                                         sat,
                                         constellation,
                                         path_cacheDirectory,
                                         use_cache,
                                         satCounter,
                                         std::ref(poi_reports[satCounter]),
                                         std::ref(gs_reports[satCounter]),
                                         std::ref(interpTimes[satCounter]));

                threads.push_back(std::move(temp_thread));
                satCounter++;
            }
        }
        for(auto& one_thread : threads)
        {
            one_thread.join();
        }
        for(int x = 0; x < poi_reports.size(); x++)
        {
            output->setInterpTime(interpTimes[x]);
            output->addPOIData(poi_reports[x]);
            output->addGSData(gs_reports[x]);
        }
    }
    // ------------------------------------------------------------------- THREAD TESTING END -------------------------------------------------------------------




    status = true;
    if(status)
    {
        output->calculateMetrics_POI();
        output->calculateMetrics_GS();

        if(outputGlobal)
        {
            output->writeGlobals();
        }
        if(outputLocal)
        {
            output->writeLocals();
        }
        if(outputAccess)
        {
            output->writeAccess();
        }
        if(outputInstrument)
        {
            output->writePOI();
        }
    }

    delete gridCalc;
    delete output;
    delete poiArea;
    delete gnArea;
    delete cache;


    double seconds_since_start = difftime( time(0), start);

    cout << endl << "-- RUNTIME: " << seconds_since_start << " sec" << endl;


    return 0;
}





// ------------------------------------------------------------ THREAD CLASS ------------------------------------------------------------
void satThread(Json::Value ms,
               Json::Value sat,
               double      gs,
               string      path_writeFiles,
               PointGroup*  poiGroup,
               PointGroup*  gsGroup,
               int satNum,
               int constNum,
               string path_cache,
               bool use_cache,
               int satCounter,
               vector<IntervalEventReport> &poi_report,
               vector<IntervalEventReport> &gs_report,
               Real &metricsIT)
{
    OrbitPropagator* sim       = new OrbitPropagator(ms,
                                                     sat,
                                                     poiGroup,
                                                     gsGroup,
                                                     path_cache,
                                                     path_writeFiles,
                                                     gs,
                                                     satNum,
                                                     constNum,
                                                     satCounter,
                                                     false);
    sim->useCache(use_cache);
    sim->setOrbitalParameters();
    sim->setInstrumentCoverage();

    bool status = sim->propagateOrbit();



    metricsIT   = sim->metricsInterpTime;
    poi_report  = sim->getCoverageEvents();
    gs_report   = sim->getGsEvents();
    delete sim;
    cout << "-- Thread Finished" << endl;
}



vector< vector<Json::Value> > getConstellations(Json::Value mission, Json::Value architecture)
{
    vector< vector<Json::Value> > all_constellations;

    //First, check the mission file for constellations
    Json::Value design_space   = mission["designSpace"];
    Json::Value constellations = mission["designSpace"]["spaceSegment"];
    int         num_consts     = constellations.size();

    for(int x = 0; x < num_consts; x++)//----------------------------------------Iterates over constellaitons in mission file
    {
        Json::Value constellation = constellations[x];
        if(constellation["constellationType"].asString() == "EXISTING")//--------If constellation is EXISTING
        {
            vector<Json::Value> temp_constellation;
            int num_sats = constellation["numberSatellites"].asInt();
            for(int y = 0; y < num_sats; y++)//----------------------------------Iterate over satellites in existing constellation
            {
                Json::Value temp_satellite = constellation["satellites"][y];
                temp_constellation.push_back(temp_satellite);
            }
            all_constellations.push_back(temp_constellation);
        }
    }

    //Second, check the architecture file for constellations
    constellations = architecture["spaceSegment"];
    num_consts     = constellations.size();

    for(int x = 0; x < num_consts; x++)//------------------------------------------Iterate over all the constellations in arch file
    {
        Json::Value constellation = constellations[x];
        int         num_sats      = constellation["numberSatellites"].asInt();
        vector<Json::Value>         temp_constellation;

        for(int y = 0; y < num_sats; y++)//----------------------------------------Iterate over all the sats in a constellation obj
        {
            Json::Value temp_satellite = constellation["satellites"][y];
            temp_constellation.push_back(temp_satellite);
        }
        all_constellations.push_back(temp_constellation);
    }

    return all_constellations;
}





//Parse a Json file into a Json object
Json::Value getJsonObj(string filePath)
{
    Json::Value toReturn;
    Json::Reader reader;
    ifstream test(filePath, std::ifstream::binary);
    bool parsingSuccessful = reader.parse(test,toReturn);
    if (!parsingSuccessful)
    {
        cout << "Failed to load json file" << endl;
        //Use __LINE__ and __FILE__ preprocessors macros to alert user exactly where the error is
        //----------------------------------Return error to user here through GUI socket connection----------------------------------
        exit(1);
    }
    return toReturn;
}

Real getMissionDuration(string dur)
{
    Real days = 0;

    string year;
    string month;
    string day;

    size_t pos_t;
    int pos;

    int strLength = dur.length();
    string parsed = dur.substr(1, (strLength-1) ); //Take out the first "P" in the duration field

    //Get the years
    pos_t = parsed.find("Y");
    pos = pos_t;
    year = parsed.substr(0, pos);
    parsed = parsed.substr( (pos+1) , (parsed.length() - (pos+1)) );


    //Get the months
    pos_t = parsed.find("M");
    pos = pos_t;
    month = parsed.substr(0, pos);
    parsed = parsed.substr( (pos+1) , (parsed.length() - (pos+1)) );




    //Get the days
    pos_t = parsed.find("D");
    pos = pos_t;
    day = parsed.substr(0, pos);


    int y = stoi(year);
    int m = stoi(month);
    int d = stoi(day);

    days = (y * 365) + (m * 30) + (d);

    return days;
}

Real getMissionEpoch(string date)
{
    vector<Integer> dateParams;
    Integer year = stoi(date.substr(0,4));
    Integer month = stoi(date.substr(5,2));
    Integer day = stoi(date.substr(8,2));
    Integer hour = stoi(date.substr(11,2));
    Integer minute = stoi(date.substr(14,2));
    Integer second = stoi(date.substr(17,2));

    dateParams.push_back(year);
    dateParams.push_back(month);
    dateParams.push_back(day);
    dateParams.push_back(hour);
    dateParams.push_back(minute);
    dateParams.push_back(second);

    AbsoluteDate* dateConverter = new AbsoluteDate();
    AbsoluteDate* orbitDate = new AbsoluteDate();

    Real seconds = dateParams[5];

    dateConverter->SetGregorianDate(dateParams[0],dateParams[1],dateParams[2],dateParams[3],dateParams[4],seconds);
    Real epoch = dateConverter->GetJulianDate();
    orbitDate->SetJulianDate(epoch);

    Real toReturn = orbitDate->GetJulianDate();


    delete dateConverter;
    delete orbitDate;
    return toReturn;
}

//Return the path to the tatc directory
string getTATC_Path()
{
    char buffer[1024]; // Or optionally PATH_MAX
    char *result = getcwd(buffer, 1024);
    if (result == NULL)
    {
        return "Error changing to directory containing tests";
    }
    string pathL(buffer);
    vector<string> directories;

    boost::char_separator<char> sep("/");
    boost::tokenizer<boost::char_separator<char>> tokens(pathL, sep);
    for (const auto& t : tokens) {
        directories.push_back(t);
    }

    string path = "/";
    for(int x = 0; x < directories.size(); x++)
    {
        if(directories[x] == "tat-c")
        {
            path = path + directories[x];
            break;
        }
        path = path + directories[x] + "/";
    }

    return path;
}

string getCachePath(string architecture_path)
{
    vector<string> directories;
    boost::char_separator<char> sep("/");
    boost::tokenizer<boost::char_separator<char>> tokens(architecture_path, sep);
    for (const auto& t : tokens) {
        directories.push_back(t);
    }

    string path = "";
    for(int x = 0; x < directories.size(); x++)
    {
        if( (directories[x]).substr(0,4) == "arch")
        {
            break;
        }
        path = path + "/" + directories[x];
    }

    return path;
}


string getMissionDirectory(string missionJSON)
{
    std::size_t position = missionJSON.find_last_of("/");
    string toReturn = missionJSON.substr(0, position);
    return toReturn;
}

bool doesCacheExist(string pathToCache)
{
    struct stat info;

    if ( stat( pathToCache.c_str(), &info ) != 0 )
    {
        return false;
    }
    else if(info.st_mode & S_IFDIR)
    {
        return true;
    }
    else
    {
        return false;
    }

}


// -------------------- Socket thread commented out for now --------------------
/*
void connectToGUI()
{


    //Instantiate variables for socket connection

    //Address of socket server
    struct sockaddr_in serv_addr;
    int sock = 0, valread;

    //Timeout socket structure for LINUX
    struct timeval tv;
    tv.tv_sec = 2; //Timeout value in seconds
    tv.tv_usec = 0;

    //Socket Buffer
    char buffer[32] = {0};

    //Create a socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        cout << "Error creating the socket" << endl;
    }

    //Set the timout for the socket
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof tv);

    //Set the server address
    memset(&serv_addr, '0', sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0)
    {
        cout << "Invalid socket address / address not supported" << endl;
    }


    //Connect the socket to the GUI server socket
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        cout << "Client socket failed to connect to server socket" << endl;
    }



    //Continuously look for incoming/outgoing messages to the GUI
    while(!closeConnection)
    {

        //Set to timeout after 2 seconds
        valread = read( sock , buffer, 32);

        // valread should contain the number of bytes read on success    ---    we always send messages of size 32 bytes
        if(valread == 32)
        {
            //This is if a message was received    ---    Use semaphores here for reading shared queue
            string received(buffer);

            criticalSection.lock();
            messagesIN.push(received);
            criticalSection.unlock();
        }




        //If we have a message to send to the GUI    ---    Use semaphores here for reading shared queue
        if(!(messagesOUT.empty()))
        {

            criticalSection.lock();
            char* toSend = messagesOUT.front();
            messagesOUT.pop();
            criticalSection.unlock();

            send( sock , toSend , strlen(toSend) , 0 );
        }

    }



}
*/

// -------------------- Doxygen Documentation --------------------

/*! \mainpage <b>Orbit Module</b> --- TAT-C Version 2.0
 *
 *
 * \section userGuide User Guide
 *

 * <b>Compilation</b> - make all <br>
 * <b>Cleaning</b> - make bare <br>
 * <b>Running</b> - ./bin/reductionMetrics <b>param1</b> <b>param2</b> <br>
 * <br>
 * <br>
 *
 *  <b>param1</b> - Path to <mission_name>.json (including mission file extension) <br>
 *  <b>param2</b> - Path to <architecture>.json (directory only) <br>
 *
 *
 *
 * \section Introduction
    The Orbit module's main purpose is to simulate a mission architecture (DSM) and calculate metrics on that architecture. These metrics <br>
    are then visualized by the front-end, helping the user assign value to different architectures. <br>
    <br>
    Previously (TAT-C version 1.0), the Orbit module was broken up into two separate modules:
    1. Reduction and Metrics <br>
    2. Orbit and Coverage <br>
    <br>
    Because these two modules are so closly related, they have been merged into one Orbit module for TAT-C 2.0. <br>
    These two modules must be understood separately to show how the Orbit module works. I will briefly <br>
    review each of the modules's functionality, painting a picture of how the Orbit module works. Keep in mind, the functionality mentioned will <br>
    only be relavent to TAT-C Version 2.0
    <br>
    <br>
    From this point on, the Orbit and Coverage module will be referred to as the "OC" module and the <br>
    Reduction and Metrics module will be referred to as the "RM" module.

    \section orbit_coverage Orbit and Coverage (OC)

    The OC module is a library of classes that can be built/combined to model a Satellite, model Instruments on a satellite, propagate that Satellite's orbit, <br>
    and calculate earth point coverage for that Satellite. These capibilities can be broken down into two main functionalities: <br>
    1. <b>Orbit Calculation</b> <br>
    2. <b>Coverage Calculation</b> <br>
    <br>


    \subsection orb_calc Orbit Calculation
    The Orbit Calculations require a "Satellite" object and a "Propagator" object. The "Satellite" object models one satellite including any Instruments in its payload. <br>
    The "Propagator" object simulates a satellite object's orbit about an orbit. The satellite's position is calculated and stored for later use during each propagation step. <br>
    The time duration between each propagation calculation is determined by a "timestep" provided by the user. <br>



    \subsection cov_calc Coverage Calculation
    Typically, after each propagation step (orbit calculation), earth point coverage is calculated for each Instrument on the satellite. How is this done? <br>
    In order to calculate earth point coverage, we first need a set of points to be analyzing on the earth. A "PointGroup" object models this just. <br>
    There are two classifications of PointGroups: <br>

    1. <b>Area of Interest</b> <br>
    Before tat-c runs, the user will specify an Area of Interest defining what part of the earth they want to analyze during their mission. <br>
    A PointGroup is created containing evenly distributed lat/lon points modeling this Area of Interest. <br>


    2. <b>Ground Network</b>  <br>
    For every architecture, a network of Ground Stations is provided. <br>
    Each Ground Station is modeled as one lat/lon point in a PointGroup and all those points model a Ground Network. <br>
    <br>

    But how are we looking at these PointGroup objects? Each satellite has a payload that can contain multiple instruments. Each of these on-board instruments has a coverage <br>
    that is used to determine if a point in a PointGroup is visible or not. Because the OC module knows the satellite's position/orientation (due to the Orbit Calculation), the OC module <br>
    can now calculate which points out of all the PointGroups are visible. For each point seen, a VisiblePOIReport is returned stating at what time that point was seen.



    \section reduction_metrics Reduction and Metrics (RM)
    The RM module can be thought of as the layer above the OC module. Similar to OC, RM has two main functionalities:
    1. <b>Reduction</b> <br>
    2. <b>Metrics</b> <br>
    <br>


    \subsection reduction Reduction
    RM first acts as "wrapper" for the OC module. It will read in an architecture (DSM) from a JSON document and build the appropriate OC classes (see Orbit and Coverage section) to simulate this architecture. <br>
    But why is this functoinality called "Reduction"? An example will best explain this. <br>
    <br>

    Let's say two separate architectures (arch A and arch B) both contain a Satellite (sat S) with an identical orbit. <br>
    Arch A will be evaluated first. During its evaluation, sat S will be propagated around the earth and all of its positions/orientations will be recorded and stored.
    <br>
    Now, Arch B will be evaluated. During its evaluation, RM will see that sat S was already propagated around the earth during Arch A's evaluation. <br>
    Because propagation is a costly calculation, RM will used sat S's stored positions/orientations (from Arch A's evaluation) to calculate coverage instead of propagating sat S a second time. <br>
    This allows us to reuse satellite propagation, even if the same satellite S has different Instruments across Arch A and B. <br>

    <b>Note</b>: the propagation time step and mission start/end date will be the same across all architectures. <br>

    As stated above, the OC module will return a vector of VisiblePOIReports to RM. These are used in RM's second functionality.



    \subsection metrics Metrics
    After the OC module has been called and all earth point access history has been retrieved, metrics will be calculated on the data. <br>
    Local and Global metrics will be calculated for the architecture being evaluated. Local metrics pertain to a specific point of interest while Global metrics <br>
    describe all the points of interest. <br>
    <br>
    It should be noted that some Global and Local metrics are calculated after each Satellite in the architecture is simulated (opposed to after all the Satellites have been simulated). <br>
    This may seem reudandant, as the metrics calculations could be done only once after all the Satellites have been propagated. <br>
    But running this calculation only once would mean the access history computed for all the Satellites in the architecture would have to be presant at the same time. <br>
    This takes up a huge amount of memory and leads to memory issues. <br>
    Calculating the metrics iteravely (after the coverage calculations for each Satellite) allows us to free the memory containing this satellite's access history in <br>
    preparation for the next Satellite's propagation. This drastically reduces the memory used in a single run of the Orbit module.<br>
    <br>



    \section everything Putting it all together

    It is important to note that the Orbit module processes one architecture per call. Here is a high-level list of steps that the Orbit module <br>
    takes when evaluating an architecture: <br>
    (Steps 2 - 7 will loop for each of the satellites in an architecture) <br>
    1. Read in an architecture
    <br>
    2. Build the satellite and instrument objects for the current Satellite
    3. Create the Ground Network and Area of Interest PointGroups to be analyzed
    4. Propagate the satellite's orbit
    5. Store the access history data for this satellite's orbit
    6. Calculate metrics incorporating this satellite's access history data
    7. Free memory containing access history
    <br>
    8. Write Global and Local metrics to appropriate files to be used in visualizations

    So what else is new in version 2.0? <br>
    The Orbit Module has a Cache System that records satellite access info as they are processed. This access info is written to "satX_accessInfo.csv" files, where the X denotes the
    satellite's ID. If the orbit module encounters a satellite that has been processed by a previous architecture, it will load that satellite's access info from the cache instead of
    re-propagating the satellite. The cache system was also created to use system disc memory as efficiently as possible. Below, I will go over the different output files and how the cache
    minimizes memory usage.
    <br>
    <br>
    \subsection outputs Outputs
    The files outputted by the Orbit Module fall into three different categories <br>
    1. Satellite Specific Files    - files that contain information on a specific satellite
    2. Architecture Specific Files - files that contain information pertaining to a specific architecture
    3. Mission Specific Files      - files that contain informattion pertaining to the whole mission
    <br>
    In TAT-C's current architecture, there is one large mission directory containing many architecture directories. It would make sense to place the mission specific files (poi.csv)
    in the root mission directory, but other modules need this file to be in the architecture directories to function. This means that mission specific files will be duplicated in
    architecture directories (thus wasting memory). Similarly, satellite specific files need to be placed in the architecture directories so that other modules can extract
    information from them. In many cases, two different architectures will have a common satellite, so these satellite specific files will be duplicated in these directories.
    <br>
    The solution to this memory management issue is to place satellite specific files in the "/...../cache/satellite" directory and the mission specific files in the
    "/...../cache' directory. From here, we will create hard links from the cache to the desired architecure directories. This way, there will be no duplicate files and
    all the modules can still access the files they need.
    <br>
    <br>






 */
