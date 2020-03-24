//
// Created by Gabriel Apaza on 2019-06-24.
//

#ifndef CACHEINTERFACE
#define CACHEINTERFACE



//GMAT src
#include "IntervalEventReport.hpp"
#include "AbsoluteDate.hpp"

//GMAT defs
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"


//BOOST
#include <boost/tokenizer.hpp>


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
#include <cerrno>

//Json Parser
#include <json/json.h>




using namespace std;


//! This class interacts with the cache system! Creating files and getting information from past runs.
class CacheInterface {
public:

    //! Constructor - takes a string telling it where to create the cache directory
    CacheInterface(string cache_directory);
    CacheInterface(const CacheInterface& orig);
    virtual ~CacheInterface();



    // ---------------- FUNCTIONS ----------------

    //! Takes a string (path) and returns if that path exists or not
    bool DoesDirectoryExist(string directory_path);

    //Create hard links to files in the cache
    void LinkPoiFile(string link_to_poi);

    void LinkObsFile(string link_to_obs, string cache_to_obs);

    void LinkAccessInfoFile(string link_to_access, string cache_to_access);

    //! Creates a hard link from parameter A to parameter B
    void CreateHardLink(string file_in_cache, string link_to_file);

    //! Create a new satellite directory in the cache
    void CreateSatelliteEntry(string satellite_directory_path, string satellite_file_name);

    //! Retrieves all POI reports from past satellite propagation
    vector<IntervalEventReport> GetPoiReports(string link_to_sat_directory);

    //! Retrieves all GS reports from past satellite propagation
    vector<IntervalEventReport> GetGsReports(string link_to_sat_directory);

    //! Writes POI access file "satX_accessInfo.csv" in cache
    void WritePoiAccessFile(string link_to_sat_directory, vector<IntervalEventReport>* poi_access, double missionEpoch, double missionDays);

    //! Writes GS access file "satX_accessInfo_GS.csv" in cache
    void WriteGsAccessFile(string link_to_sat_directory,  vector<IntervalEventReport>* gs_access);

    //! Writes poi.csv file in cache
    void WritePoiFile(vector< pair< Real, Real > >* points, double numPoints);

    //! Adds a satellite directory to the queue
    void AddDirectoryToQueue(string satellite_file_name);

    //! Clears the cache if needed "not implemented yet"
    void ClearCache(int max_size);
    void RemoveElement(string element);

    //! Gets a satellite attribute from the record.json file in the cache
    double GetSatRecordAttribute(string link_to_sat_directory, string attribute);




    // ---------------- VARIABLES ----------------
    //! Path to the cache directory
    string path_cache_directory;

    //! Path to the poi.csv file in the cache directory
    string path_cache_poi_file;

    //! Path to the queue.json file in the cache directory
    string path_cache_queue_file;




private:

    // ---------------- FUNCTIONS ----------------


    // ---------------- VARIABLES ----------------











};








































#endif //CACHEINTERFACE


