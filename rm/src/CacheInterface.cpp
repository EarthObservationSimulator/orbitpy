//
// Created by Gabriel Apaza on 2019-06-24.
//



#include "CacheInterface.hpp"





using namespace std;
using namespace GmatMathConstants; //contains RAD_PER_DEG




/*
 * The constructor will check to see if the cache has been created yet. If it hasn't, create it
 * cache_directory = /....../sli-2/cache
 */
CacheInterface::CacheInterface(string cache_directory)
{
    path_cache_directory  = cache_directory;
    path_cache_poi_file   = path_cache_directory + "/poi.csv";
    path_cache_queue_file = path_cache_directory + "/queue.json";
    bool cache_exists    = DoesDirectoryExist(path_cache_directory);
    if(!cache_exists)
    {
        cout << "--> Creating cache directory" << endl;
        int     success               = mkdir(path_cache_directory.c_str(), 0777);
        if(success == -1)
        {
            if(errno == EEXIST)
            {
                cout << "--> Cache already exists" << endl;
            }
        }

        //Create queue.json -- Commented out due to concurrency issues
        // Json::Value        queueObj;
        // Json::StyledWriter styledWriter;
        // ofstream           outputQueue;
        // queueObj["queue"] = Json::Value(Json::arrayValue);
        // outputQueue.open(path_cache_queue_file);
        // outputQueue << styledWriter.write(queueObj);
        // outputQueue.close();
    }





}

CacheInterface::CacheInterface(const CacheInterface& orig)
{

}

CacheInterface::~CacheInterface()
{

}









void CacheInterface::WritePoiFile(vector< pair< Real, Real > >* lat_lon_vector, double numPoints)
{
    //First check to see if POI.csv file exists in cache
    ifstream f(path_cache_poi_file.c_str());
    bool fileExists = f.good();

    if(!fileExists)
    {
        //Create File Headers
        vector<string> poiHeader;
        poiHeader.push_back("POI");
        poiHeader.push_back("lat[deg]");
        poiHeader.push_back("lon[deg]");

        ofstream poifile;
        poifile.open(path_cache_poi_file.c_str(),ios::binary | ios::out);

        //Write Headers
        for (Integer ii=0;ii<poiHeader.size()-1;ii++)
        {
            poifile << poiHeader[ii] << ",";
        }
        poifile << poiHeader[poiHeader.size()-1] << endl;


        for (Integer num = 0; num < numPoints; num++)
        {
            poifile << num << ",";
            poifile << (*lat_lon_vector)[num].first << ",";
            poifile << (*lat_lon_vector)[num].second << endl;

        }
    }






}


void CacheInterface::WritePoiAccessFile(string link_to_sat_directory, vector<IntervalEventReport>* poi_access, double missionEpoch, double missionDays)
{
    string satAccessFileNameT       = link_to_sat_directory + "/sat_accessInfo.csv";
    ofstream satelliteStateFileT;
    satelliteStateFileT.precision(20);
    satelliteStateFileT.open(satAccessFileNameT.c_str(),ios::binary | ios::out);

    //First 5 header lines for the sat_accessInfo.csv file
    string headerLineOneT   = "Satellite states are in Earth-Centered-Inertial equatorial plane.";
    string headerLineTwoT   = "Epoch[JDUT1] is " + to_string(missionEpoch);
    string headerLineThreeT = "All time is referenced to the Epoch.";
    string headerLineFourT  = "Mission Duration [Days] is " + to_string(missionDays);
    satelliteStateFileT << headerLineOneT   << "," << endl;
    satelliteStateFileT << headerLineTwoT   << "," << endl;
    satelliteStateFileT << headerLineThreeT << "," << endl;
    satelliteStateFileT << headerLineFourT  << "," << endl;
    satelliteStateFileT << "EventNum" << ",";
    satelliteStateFileT << "POI" << ",";
    satelliteStateFileT << "AccessFrom[Days]" << ",";
    satelliteStateFileT << "Duration[s]" << ",";
    satelliteStateFileT << "Time[Days]" << ",";
    satelliteStateFileT << "X[km]" << ",";
    satelliteStateFileT << "Y[km]" << ",";
    satelliteStateFileT << "Z[km]" << ",";
    satelliteStateFileT << "VX[km/s]" << ",";
    satelliteStateFileT << "VY[km/s]" << ",";
    satelliteStateFileT << "VZ[km/s]" << endl;


    int eventID = 0;
    vector<IntervalEventReport>::iterator report;
    for(report = poi_access->begin(); report != poi_access->end(); report++) //Loop through all the reports for this propagation step
    {
        Integer poiNum = report->GetPOIIndex();

        Real accessFrom = (report->GetStartDate().GetJulianDate() - missionEpoch); //Days
        //Real accessFromSeconds = accessFrom * 24 * 60 * 60;

        Real eventDuration = ((report->GetEndDate().GetJulianDate()) - (report->GetStartDate().GetJulianDate())); //Days
        Real eventDurationSeconds = eventDuration * 24.0 * 60.0 * 60.0; //Seconds

        //Get all the VisiblePOIReports and determine the middle one
        vector<VisiblePOIReport> discreteEvents = report->GetPOIEvents();
        VisiblePOIReport ev = discreteEvents[int(discreteEvents.size()/2)];

        Real midJulianDate = ev.GetStartDate().GetJulianDate() - missionEpoch;

        satelliteStateFileT << eventID << ",";
        satelliteStateFileT << poiNum << ",";
        satelliteStateFileT << accessFrom << ",";
        satelliteStateFileT << (eventDurationSeconds) << ",";
        satelliteStateFileT << midJulianDate << ",";

        satelliteStateFileT << ev.GetObsPosInertial()[0] << ",";
        satelliteStateFileT << ev.GetObsPosInertial()[1] << ",";
        satelliteStateFileT << ev.GetObsPosInertial()[2] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[0] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[1] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[2] << endl;

        eventID++;
    }

}

void CacheInterface::WriteGsAccessFile(string link_to_sat_directory,  vector<IntervalEventReport>* gs_access)
{
    string satAccessFileNameT_GS    = link_to_sat_directory + "/sat_accessInfo_GS.csv";
    ofstream satelliteStateFileT_GS;
    satelliteStateFileT_GS.precision(20);
    satelliteStateFileT_GS.open(satAccessFileNameT_GS.c_str(),ios::binary | ios::out);

    //Create headers for sat_accessInfo_GS.csv file
    satelliteStateFileT_GS << "gsIndex"   << ",";
    satelliteStateFileT_GS << "startDate" << ",";
    satelliteStateFileT_GS << "endDate"   << endl;

    vector<IntervalEventReport>::iterator report;
    for(report = gs_access->begin(); report != gs_access->end(); report++)
    {
        Integer poiIndex = report->GetPOIIndex(); //This tells us which point of interest the report is referring to
        Real startDate   = report->GetStartDate().GetJulianDate();
        Real endDate     = report->GetEndDate().GetJulianDate();

        std::ostringstream tempStream1;
        std::ostringstream tempStream2;
        std::ostringstream tempStream3;

        tempStream1 << setprecision(20);
        tempStream2 << setprecision(20);
        tempStream3 << setprecision(20);

        tempStream1 << poiIndex;
        tempStream2 << startDate;
        tempStream3 << endDate;

        satelliteStateFileT_GS << tempStream1.str() << ",";
        satelliteStateFileT_GS << tempStream2.str() << ",";
        satelliteStateFileT_GS << tempStream3.str() << endl;
    }


}

vector<IntervalEventReport> CacheInterface::GetPoiReports(string link_to_sat_directory)
{
    string path_record_file = link_to_sat_directory + "/record.json";
    string path_access_file = link_to_sat_directory + "/sat_accessInfo.csv";
    string access_line;
    double missionEpoch = GetSatRecordAttribute(link_to_sat_directory, "missionEpoch");

    vector<IntervalEventReport> parsed_events_poi;
    ifstream                    access_file_poi(path_access_file);


    int header_counter = 0;
    while(getline(access_file_poi, access_line))
    {
        if(header_counter < 5)
        {
            header_counter++;
            continue;
        }

        vector<string>                                access_tokens;
        boost::char_separator<char>                   sep(",");
        boost::tokenizer<boost::char_separator<char>> tokens(access_line, sep);
        for (const auto& t : tokens)
        {
            access_tokens.push_back(t);
        }

        IntervalEventReport    temp;
        AbsoluteDate           temp_start;
        AbsoluteDate           temp_end;

        temp_start.SetJulianDate( (stod(access_tokens[2]) + missionEpoch)  );
        temp_end.SetJulianDate  ( (stod(access_tokens[2]) + missionEpoch) + (stod(access_tokens[3]) /60.0/60.0/24.0) );

        temp.SetPOIIndex       ( stoi(access_tokens[1]) );
        temp.SetStartDate      ( temp_start );
        temp.SetEndDate        ( temp_end );
        parsed_events_poi.push_back(temp);
        header_counter++;

    }
    return parsed_events_poi;
}

vector<IntervalEventReport> CacheInterface::GetGsReports(string link_to_sat_directory)
{
    string path_record_file = link_to_sat_directory + "/record.json";
    string path_access_file = link_to_sat_directory + "/sat_accessInfo_GS.csv";
    string access_line;

    vector<IntervalEventReport> parsed_events_gs;
    ifstream                    access_file_gs(path_access_file);


    int header_counter = 0;
    while(getline(access_file_gs, access_line))
    {
        if(header_counter < 1)
        {
            header_counter++;
            continue;
        }

        vector<string>                                access_tokens;
        boost::char_separator<char>                   sep(",");
        boost::tokenizer<boost::char_separator<char>> tokens(access_line, sep);
        for (const auto& t : tokens)
        {
            access_tokens.push_back(t);
        }

        IntervalEventReport    temp;
        AbsoluteDate           temp_start;
        AbsoluteDate           temp_end;

        temp_start.SetJulianDate(stod(access_tokens[1]));
        temp_end.SetJulianDate  (stod(access_tokens[2]));
        temp.SetPOIIndex        ( stoi(access_tokens[0]) );
        temp.SetStartDate       ( temp_start );
        temp.SetEndDate         ( temp_end );

        parsed_events_gs.push_back(temp);

        header_counter++;
    }
    return parsed_events_gs;
}

double CacheInterface::GetSatRecordAttribute(string link_to_sat_directory, string attribute)
{
    string path_record_file = link_to_sat_directory + "/record.json";
    Json::Value  satRecord;
    Json::Reader satReader;
    ifstream     recordFile(path_record_file, std::ifstream::binary);
    bool parsingSuccessful = satReader.parse(recordFile,satRecord);
    if (!parsingSuccessful)
    {
        cout << "Failed to load record.json file in cache" << endl;
        //Use __LINE__ and __FILE__ preprocessors macros to alert user exactly where the error is
        //----------------------------------Return error to user here through GUI socket connection----------------------------------
        exit(1);
    }


    if(attribute == "interp-timestep")
    {
        return satRecord["propagationParameters"]["interp-timestep"].asDouble();
    }
    else if(attribute == "missionEpoch")
    {
        return satRecord["propagationParameters"]["missionEpoch"].asDouble();
    }
    else if(attribute == "missionDays")
    {
        return satRecord["propagationParameters"]["missionDays"].asDouble();
    }
    else if(attribute == "numPOIs")
    {
        return satRecord["propagationParameters"]["numPOIs"].asDouble();
    }
    else
    {
        cout << "--> " << attribute << " is not an attribute specified in the record file" << endl;
    }


    return 0;
}

void CacheInterface::CreateSatelliteEntry(string satellite_directory_path, string satellite_file_name)
{
    int success = mkdir(satellite_directory_path.c_str(), 0777);
    if(success == -1)
    {
        cout << "--> ERROR: Failed to create cache satellite directory" << endl;
    }

    // This line causes concurrency issues
    //AddDirectoryToQueue(satellite_file_name);
}


// This is currently not being called due to concurrency issues
void CacheInterface::AddDirectoryToQueue(string satellite_file_name)
{
    Json::Value  queueObj;
    Json::Reader queueReader;
    ifstream     queueFile(path_cache_queue_file, std::ifstream::binary);
    bool parsingSuccessful = queueReader.parse(queueFile,queueObj);
    if (!parsingSuccessful)
    {
        cout << "Failed to load queue.json in Cache" << endl;
        exit(1);
    }

    queueObj["queue"].append(satellite_file_name.c_str());


    Json::StyledWriter styledWriter;
    ofstream           outputQueue;

    outputQueue.open(path_cache_queue_file);
    outputQueue << styledWriter.write(queueObj);
    outputQueue.close();
}

void CacheInterface::ClearCache(int max_size)
{
    Json::Value  queueObj;
    Json::Reader queueReader;
    ifstream     queueFile(path_cache_queue_file, std::ifstream::binary);
    bool parsingSuccessful = queueReader.parse(queueFile,queueObj);
    if (!parsingSuccessful)
    {
        cout << "Failed to load queue.json in Cache" << endl;
        exit(1);
    }

    int currentSize = queueObj["queue"].size();
    int remove_num  = max_size / 10;

    if(currentSize > max_size)
    {
        for(int x = 0; x < remove_num; x++)
        {
            string to_remove = queueObj["queue"][x].asString();
            RemoveElement(to_remove);
        }
    }
}

void CacheInterface::RemoveElement(string element)
{
    string full_removal_path = path_cache_directory + "/" + element;
    //Now we have to remove this whole directory
}






void CacheInterface::CreateHardLink(string file_in_cache, string link_to_file)
{
    if (link(file_in_cache.c_str(), link_to_file.c_str()) != 0)
    {
        if(errno == EEXIST){
            cout << "--> Link Already Exists: " << link_to_file << endl;
        }
        else if(errno == EACCES){
            cout << "--> Write access / premissions denied for directory containing link or file" << endl;
            cout << link_to_file << endl;
            cout << file_in_cache << endl << endl;
        }
        else if(errno == EMLINK){
            cout << "--> File referred to has max number of links (limit 65,000): " << file_in_cache << endl;
        }
        else if(errno == EROFS){
            cout << "--> The file is on a read only file system" << file_in_cache << endl;
        }
        else
        {
            cout << endl << "--> WARNING: Hard Link Failed <--" << endl;
            cout << link_to_file << endl;
            cout << file_in_cache << endl << endl;
        }
    }
}







void CacheInterface::LinkPoiFile(string link_to_poi)
{
    if (link(path_cache_poi_file.c_str(), link_to_poi.c_str()) != 0)
    {
        cout << "-- POI.csv link failed" << endl;
        cout << link_to_poi << endl;
        cout << "      -->      " << endl;
        cout << path_cache_poi_file << endl;
    }
}

void CacheInterface::LinkObsFile(string link_to_obs, string cache_to_obs)
{
    if (link(cache_to_obs.c_str(), link_to_obs.c_str()) != 0)
    {
        cout << "-- POI.csv link failed" << endl;
        cout << link_to_obs << endl;
        cout << "      -->      " << endl;
        cout << cache_to_obs << endl;
    }
}

void CacheInterface::LinkAccessInfoFile(string link_to_access, string cache_to_access)
{
    if (link(cache_to_access.c_str(), link_to_access.c_str()) != 0)
    {
        cout << "--> POI.csv link failed" << endl;
        cout << link_to_access << endl;
        cout << "      -->      " << endl;
        cout << cache_to_access << endl;
    }
}

bool CacheInterface::DoesDirectoryExist(string path_directory)
{
    struct stat info;

    if ( stat( path_directory.c_str(), &info ) != 0 )
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
