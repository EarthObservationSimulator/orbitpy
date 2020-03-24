//
// Created by Gabriel Apaza on 2019-02-07.
//

#ifndef ORBIT_METRICS_H
#define ORBIT_METRICS_H


#include <algorithm>
#include <vector>
#include <iterator>
#include <utility>
#include <iostream>
#include <fstream>
#include <sys/param.h>
#include <utility>
#include <unistd.h>
#include <stack>

#include "VisiblePOIReport.hpp"
#include "IntervalEventReport.hpp" //src includes
#include "PointGroup.hpp"


// Orbit Includes
#include "CacheInterface.hpp"

//Json Parser
#include <json/json.h>

using namespace std;




//!  This class computes access metrics on one or multiple Satellites
/*!
    The Metrics class is capable of computing access history metrics for one or multiple Satellites. <br>
    Both Ground Network and Area of Interest access metrics can be computed

*/
class Metrics {
public:



    //!  Metrics Constructor
    /*!
        \param points - int value specifying how many points are in the Area of Interest PointGroup
        \param startD - Real value with the start date of the mission
        \param gsNum - Integer value specifying how many ground stations are in the Ground Network

        \Issue:
        This is if there is only one ground network being evaluated in the architecture. Could we ever evaluate more than one?
    */
    Metrics(Json::Value ms, int points, Real startD, Integer gsNum, Real mD, string path_writeFiles, string path_cache, vector< pair< Real, Real > > pointCoordsVec);



    //!  Metrics Copy Constructor
    /*!
        Copies a Metrics object
    */
    Metrics(const Metrics& orig);




    //!  Metrics Destructor
    /*!
        Destroys a Metrics object
    */
    virtual ~Metrics();



    //!  Recalculates metrics based on new access history data (Area of Interest)
    /*!
        \param coverageEvents - Represents all the access data for one Satellite

        Each vector of VisiblePOIReports represents the total access history for one of the Satellite's payloads <br>
            --Ex.  If the satellite has 2 payloads, there would be 2 vectors of VisiblePOIReports <br>

        <b>Calculates</b>: <br>
            The max amount of times a point was passed                                  --Global Metric <br>
            The min amount of times a point was passed                                  --Global Metric <br>
            The total amount of times all the points were passed                        --Global Metric <br>
            The min amount of time elapsed before any point was seen for the first time --Global Metric <br>
            The max amount of time elapsed before any point was seen for the first time --Global Metric <br>
            The total amount of time elapsed before all the points were seen            --Global Metric <br>

            Total amount of time each point was seen     --Local Metric <br>
            Total amount of times each point was passed  --Local Metric <br>
            The Julian Time when the point was first seen by the   --Local Metric <br>
    */
    void addPOIData(vector<IntervalEventReport> coverageEvents);





    //!  Recalculates revisit and access time metrics (Area of Interest)
    /*!
        This calculation is costly, so it has the option to be called separately

        <b>Calculates</b>: <br>
            Max revisit time over all the points of interest        --Global Metric <br>
            Min revisit time over all the points of interest        --Global Metric <br>
            Summation of the average revisit time for each point    --Global Metric <br>

            Max access time over all the points of interest         --Global Metric <br>
            Min access time over all the points of interest         --Global Metric <br>
            Summation of the average access time for each point     --Global Metric <br>

            Average revisit time for each point of interest         --Local Metric <br>
            Min revisit time for each point of interest             --Local Metric <br>
            Max revisit time for each point of interest             --Local Metric <br>

            Average access time for each point of interest          --Local Metric <br>
            Min access time for each point of interest              --Local Metric <br>
            Max access time for each point of interest              --Local Metric <br>
    */
    void calc_Revisit_Access_POI();



    void calculateMetrics_POI();


    void calculateMetrics_GS();






    //!  Recalculates metrics based on new access history data (Ground Network)
    /*!
        \param gsEvents - Represents all the access data for one Satellite

        Each vector of VisiblePOIReports represents the total access history for one of the Satellite's payloads <br>
            --Ex.  If the satellite has 2 payloads, there would be 2 vectors of VisiblePOIReports

        <b>Calculates</b>: <br>
            The total amount of times all the Ground Stations were passed   --Global Metric <br>

            Total amount of time each Ground Station was seen      --Local Metric <br>
            Total amount of times each Ground Station was passed   --Local Metric
    */
    void addGSData(vector<IntervalEventReport> gsEvents);



    //!  Recalculates revisit and access time metrics (Ground Network)
    /*!
        This calculation is costly, so it has the option to be called separately

        <b>Calculates</b>: <br>
            Max revisit time over all the Ground Stations                    --Global Metric <br>
            Min revisit time over all the Ground Stations                    --Global Metric <br>
            Summation of the average revisit time for each Ground Station    --Global Metric <br>

            Max access time over all the Ground Stations                     --Global Metric <br>
            Min access time over all the Ground Stations                     --Global Metric <br>
            Summation of the average access time for each Ground Station     --Global Metric <br>

            Total down-link time                                             --Global Metric <br>

            Average revisit time for each Ground Station        --Local Metric <br>
            Min revisit time for each Ground Station            --Local Metric <br>
            Max revisit time for each Ground Station            --Local Metric <br>

            Average access time for each Ground Station         --Local Metric <br>
            Min access time for each Ground Station             --Local Metric <br>
            Max access time for each Ground Station             --Local Metric <br>
    */
    void calc_Revisit_Access_GS();



    //!  This function writes the gbl.csv file for the GUI to visualize
    void writeGlobals();

    //! This function writes the lvl.csv file for the GUI to visualize
    void writeLocals();

    //! This funciton writes the access.csv file
    void writeAccess();

    //! This function writes the poi.csv file
    void writePOI();



    //! CacheInterface object allowing the Metrics obj to write to the cache
    CacheInterface* cache;


    //!  Smooth continuation of access events for each point of interest
    /*!
        Due to having multiple Satellites in an architecture, access events for a specific POI might overlap  <br>
        This structure combines any overlapping events into one event, creating a smooth continuation of events
    */
    vector< vector< pair<Real, Real> > > pointWhenCombined;




    //!  Smooth continuation of access events for each Ground Network
    /*!
        Due to having multiple Satellites in an architecture, access events for a specific GS might overlap  <br>
        This structure combines any overlapping events into one event, creating a smooth continuation of events
    */
    vector< vector< pair<Real, Real> > > gsWhenCombined;


    //!  Total number of Ground Stations in the architecture
    Integer numGS;

    //!  Total number of points of interest in the architecture
    Integer numPoints;

    //!  Beginning of performance period
    Real startDate;

    //! Holds the mission.json file
    Json::Value tsr;


    // ---------- Points of Interest Metrics ---------- Event: a point of interest being seen

    //ACCESS --> how long a point was seen during an event
    //ACCESS - Local

    //!  Average access time for each point of interest          --Local Metric
    RealArray pointAverageAccess;  //The average event time for this specific point

    //!  Min access time for each point of interest              --Local Metric
    RealArray pointMinAccess;      //The event for this specific point with the longest length

    //!  Max access time for each point of interest              --Local Metric
    RealArray pointMaxAccess;      //The event for this specific point with the shortest length

    //!  Total amount of times each point was passed    --Local Metric
    RealArray pointPasses;         //How many times this point was seen in total

    //!  Total amount of time each point was seen     --Local Metric
    RealArray pointDuration;       //How long this specific point was seen in total

    //!  The Julian Time when the point was first seen by the   --Local Metric
    RealArray pointFirst;          //The JulianTime when the point was first seen by the DSM

    //!  Average revisit time for each point of interest         --Local Metric
    RealArray pointAverageRevisit; //Average revisit time calculated for each point of interest

    //!  Min revisit time for each point of interest             --Local Metric
    RealArray pointMinRevisit;     //Minimum revisit time for each point of interest

    //!  Max revisit time for each point of interest             --Local Metric
    RealArray pointMaxRevisit;     //Maximum revisit time for each point of interest

    //!  Holds the mean response times for each point of interest
    RealArray pointMeanResponse;


    //! Minimum average response time for a point of interest
    Real minResponse;

    //! Maximum average response time for a point of interest
    Real maxResponse;

    //! Average response time over all the points of interest
    Real sumResponse;

    //!  Min access time over all the points of interest         --Global Metric
    Real minAccess;                //The event over all the points with the shortest length

    //!  Max access time over all the points of interest         --Global Metric
    Real maxAccess;                //The event over all the points with the longest length

    //!  Summation of the average revisit time for each point    --Global Metric
    Real sumAccess;                //The summation of the average event length for each point

    //Global - max/min/sum all points passed

    //!  The max amount of times a point was passed                                  --Global Metric
    double maxPAS;                 //The maximum amount of times a point was passed

    //!  The min amount of times a point was passed                                  --Global Metric
    double minPAS;                 //The minimum amount of times a point was passed

    //!  The total amount of times all the points were passed                        --Global Metric
    double sumPAS;                 //The total number of times all the points were passed

    //!  Min revisit time over all the points of interest        --Global Metric
    Real minRevisit; //Min revisit time over all points of interest

    //!  Max revisit time over all the points of interest        --Global Metric
    Real maxRevisit; //Max revisit time over all points of interest

    //!  Summation of the average revisit time for each point    --Global Metric
    Real sumRevisit; //Sum revisit time over all points of interest

    //When point of interest was first seen - Global

    //!  How long until the very last point was seen --Global Metric
    Real maxTime2Coverage;         //Max amount of time elapsed before any point was seen for the first time

    //!  How long until the very first point was seen --Global Metric
    Real minTime2Coverage;         //Min amount of time elapsed before any point was seen for the first time

    //!  The total amount of time elapsed before all the points were seen ()           --Global Metric
    Real sumTime2Coverage;         //Total amount of time elapsed before all the points of interest were seen

    // ---------- Points of Interest Metrics ----------











    //Access Time: duration between when a point was seen and lost

    // ---------- Ground Station Metrics ----------

    //Local Metrics

    //!  Total amount of time each ground station was seen      --Local Metric
    RealArray gsDuration;           //How long this specific point was seen in total

    //!  Total amount of times each ground station was passed   --Local Metric
    RealArray gsPassesDSM;             //How many times this ground station was seen in total

    //!  Average revisit time for each Ground Station        --Local Metric
    RealArray gsAverageRevisit;     //Average revisit time calculated for each ground station

    //!  Min revisit time for each Ground Station            --Local Metric
    RealArray gsMinRevisit;         //Min revisit time calculated for each ground station

    //!  Max revisit time for each Ground Station            --Local Metric
    RealArray gsMaxRevisit;         //Max revisit time calculated for each ground station

    //!  Average access time for each Ground Station         --Local Metric
    RealArray gsAverageAccess;      //Average access time calculated for each ground station

    //!  Min access time for each Ground Station             --Local Metric
    RealArray gsMinAccess;          //Min access time calculated for each ground station

    //!  Max access time for each Ground Station             --Local Metric
    RealArray gsMaxAccess;          //Max access time calculated for each ground station



    //Global Metrics

    //!  Max revisit time over all the Ground Stations                    --Global Metric
    Real algsMaxRevisit;

    //!  Min revisit time over all the Ground Stations                    --Global Metric
    Real algsMinRevisit;

    //!  Summation of the average revisit time for each Ground Station    --Global Metric
    Real algsSumRevisit;

    //!  Max access time over all the Ground Stations                     --Global Metric
    Real algsMaxAccess;

    //!  Min access time over all the Ground Stations                     --Global Metric
    Real algsMinAccess;

    //!  Summation of the average access time for each Ground Station     --Global Metric
    Real algsSumAccess;

    //!  The total amount of times all the Ground Stations were passed   --Global Metric
    Real algsPassesDSM;

    //!  The total down-link time
    Real totalDLtimeDSM;



    Real numGS_Seen;
    Real numGS_Revisit;

    Real interpTime;
    void setInterpTime(Real time);

    // ---------- Ground Station Metrics ----------



    //This is a vector of durations from the beginning of the mission to the first sighting of a point of interest

    //!  The time elapsed until a specific point of interest was seen     --Local Metric
    vector<Real> timeToCovDSM;

    //! The number of days the mission ran
    Real missionDays;

    //! The number of seconds the mission ran
    Real missionSeconds;

    //! The directory to write the output files
    string writeFiles;

    //! The directory where the cache exists
    string writeCache;

    //! The number of points of interest seen
    Real pointsSeen;

    //! The number of points that meet revisit criteria
    Real pointsRevisited;


    //! Latitudes of points of interest
    vector< pair< Real, Real > > lat_lon_vector;


    //! Prints point access for testing
    void printPointAccess(vector< pair<Real, Real> > toPrint, int pNum);




    vector< pair<Real, Real> > combineEvents(vector< pair<Real, Real> > events);












};


#endif //ORBIT_METRICS_H
