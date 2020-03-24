//
// Created by Gabriel Apaza on 2019-02-09.
//

#include "GridSize.hpp"
#include <string>
#include <json/json.h>
#include <math.h>
#include <vector>
#include <ctime>






#define RE 6378 // in km
#define GM 3.986004418e14 //in m and s
#define PI 3.14159265358979323846
#define GRID_RESOLUTION_COEFF 0.9


using namespace GmatMathConstants;
using namespace boost;
using namespace std;



GridSize::GridSize()
{

}




GridSize::GridSize(const GridSize& orig)
{

}



GridSize::~GridSize()
{

}





Real GridSize::findHomogeneousGrid(Json::Value mission_json) //mission_json
{
    cout << endl << "------> Grid Resolution Calculation <------" << endl;
    Real min_altitude    = FindMinAltitude(mission_json);
    Real min_sma         = min_altitude + RE;
    Real min_cross_track = FindMinCrossTrack(mission_json);
    Real grid_size       = findGridSize(min_cross_track, min_sma);
    Real grid_return     = 0;

    if(grid_size < 1.0)
    {
        grid_return = 1.0;
        //grid_return = grid_size;
    }
    else
    {
        grid_return = grid_size;
    }

    cout << "+-- Final Grid Resolution: " << grid_return << endl;
    cout << "-------------------------------------------" << endl << endl;
    return grid_return;
}




// 1. Find the minimum altitude
//    Look through the designSpace --> constellations[x] EXISTING --> satellites[x] --> orbit --> semimajorAxis
//    Look through the designSpace --> constellations[x] NOT EXISTING --> orbit --> altitude (could be list, range, or single value)
Real GridSize::FindMinAltitude(Json::Value mission_json)
{
    Json::Value design_space       = mission_json["designSpace"];
    Json::Value constellations     = design_space["spaceSegment"];
    int         num_constellations = constellations.size();
    Real        min_altitude       = 100000000000;

    for(int x = 0; x < num_constellations; x++)
    {
        Json::Value constellation = constellations[x];


        if(constellation["constellationType"].asString() == "EXISTING")
        {
            for(int y = 0; y < (constellation["numberSatellites"].asDouble()); y++)
            {
                Json::Value satellite = constellation["satellites"][y];
                Real temp_altitude = (satellite["orbit"]["semimajorAxis"].asDouble() - RE);
                if(temp_altitude < min_altitude){min_altitude = temp_altitude;}
            }
        }
        else
        {
            Json::Value non_existing_orbit = constellation["orbit"];
            if(non_existing_orbit["altitude"].isArray())                //List
            {
                for(int y = 0; y < (non_existing_orbit["altitude"].size()); y++)
                {
                    Real temp_altitude = non_existing_orbit["altitude"][y].asDouble();
                    if(temp_altitude < min_altitude){min_altitude = temp_altitude;}
                }
            }
            else if(non_existing_orbit["altitude"].isNumeric()) //Single Value
            {
                Real temp_altitude = non_existing_orbit["altitude"].asDouble();
                if(temp_altitude < min_altitude){min_altitude = temp_altitude;}

            }
            else //Range
            {
                Real temp_altitude = non_existing_orbit["altitude"]["minValue"].asDouble();
                if(temp_altitude < min_altitude){min_altitude = temp_altitude;}
            }
        }
    }
    cout << "+----------- Min Altitude: " << min_altitude << endl;
    return min_altitude;
}

// 1. Find the sensor with the smallest cross track FOV
//    Look through the designSpace --> spaceSegment[x] EXISTING --> satellites[x] --> payload[x] --> fieldOfView --> crossTrackFieldOfView
//    Look through the designSpace --> satellites[x] --> payload[x] --> fieldOfView --> crossTrackFieldOfView
Real GridSize::FindMinCrossTrack(Json::Value mission_json)
{
    Json::Value design_space       = mission_json["designSpace"];
    Json::Value constellations     = design_space["spaceSegment"];
    Json::Value satellites         = design_space["satellites"];
    int         num_constellations = constellations.size();
    int         num_satellites     = satellites.size();
    Real        min_cross_track       = 100000000000;

    for(int x = 0; x < num_constellations; x++)//--------------------------------------------------Iterate over constellations
    {
        Json::Value constellation      = constellations[x];
        string const_type = constellation["constellationType"].asString();
        if(const_type == "EXISTING" || const_type == "DELTA_HOMOGENEOUS" || const_type == "DELTA_HETEROGENEOUS" || const_type == "TRAIN" || const_type == "AD_HOC")
        {
            for(int y = 0; y < (constellation["satellites"].size()); y++)//--------------Iterate over sats in constellation
            {
                Json::Value satellite = constellation["satellites"][y];

                for(int z = 0; z < (satellite["payload"].size()); z++)//---------------------------Iterate over payloads of sat
                {
                    Json::Value payload = satellite["payload"][z];
                    Real temp_cross_track = payload["fieldOfView"]["crossTrackFieldOfView"].asDouble();//-----For each payload get the cross track FOV
                    if(min_cross_track > temp_cross_track){min_cross_track = temp_cross_track;}
                }
            }
        }
    }
    for(int x = 0; x < num_satellites; x++)//---------------------------Iterate over the satellites
    {
        Json::Value satellite = satellites[x];
        for(int y = 0; y < (satellite["payload"].size()); y++)//--------Iterate over the payloads of each sat
        {
            Json::Value payload = satellite["payload"][y];
            Real temp_cross_track = payload["fieldOfView"]["crossTrackFieldOfView"].asDouble();
            if(min_cross_track > temp_cross_track){min_cross_track = temp_cross_track;}
        }
    }
    cout << "+--------- Min CrossTrack: " << min_cross_track << endl;
    return min_cross_track;
}















//This finds the homogeneous grid size
Real GridSize::findGridSize(Real crossTrack, double SMA)
{
    double crossTrack_ECA, gridres_minreq;

    //We are only using cross track now!! The along track is going to be dealt with in the new propagation method
    crossTrack_ECA = get_ctECA(crossTrack, SMA); // CT
    gridres_minreq = crossTrack_ECA * GRID_RESOLUTION_COEFF;

    cout << "+--------- CrossTrack ECA: " << crossTrack_ECA << endl;
    cout << "+-------- Calculated Grid: (" << crossTrack_ECA << ") * "<< GRID_RESOLUTION_COEFF <<" = " << gridres_minreq << endl;
    return gridres_minreq;
}

//Takes FOV in degrees!!
Real GridSize::get_ctECA(Real FOV, double SMA)
{
    double sinRho, lambda_deg, elev_deg, hfov_deg, eca_deg;

    sinRho = RE / SMA;                                          //sinRho = RE/(RE+H); % RE is radius of Earth, H is altitude of satellite
    hfov_deg = FOV/2;                                           //hfov_deg = CT_fov_deg/2;
    elev_deg = acosd(sind(hfov_deg) / sinRho);
    lambda_deg = 90 - hfov_deg - elev_deg;                      //half-earth centric angle
    eca_deg = lambda_deg * 2;

    return eca_deg;
}


Json::Value GridSize::getCoverageSpecs(Json::Value payload)
{
    //Calling popen working from the current directory.
    //We need to find the path of this executing program then derive the path of the instrument module
    string path = getInstrumentModulePath();
    string instCall = "python3 " + path;




    //Turn the payload into a string
    Json::StyledWriter writer;
    string toWrite = writer.write(payload);

    //Add escape characters that will be present at the command line level
    boost::replace_all(toWrite, "\"", "\\\"");
    toWrite = "\"" + toWrite + "\"";

    //Create a buffer to hold the returned data --> put the returned data into the string result
    std::array<char, 128> buffer;
    string result;




    string command = instCall + " " + toWrite;
    FILE* in = popen(command.c_str(), "r");

    while (fgets(buffer.data(), 128, in) != NULL) {
        result += buffer.data();
    }

    pclose(in);

    //Parse the result string into another json object
    Json::Value root;
    Json::Reader reader;

    bool parsingSuccessful = reader.parse( result, root );
    if ( !parsingSuccessful )
    {
        cout << "Error parsing the string" << endl;
    }

    //Return the json object
    return root;
}



//Takes a value in degrees and returns the sin
Real GridSize::sind(Real val)
{
    Real answer = sin(val*RAD_PER_DEG);
    return answer;
}

//Takes a value in degrees and returns the cos
Real GridSize::cosd(Real val)
{
    Real answer = cos(val*RAD_PER_DEG);
    return answer;
}

//Takes a value in the range [-1,1], returns a degree in range [-90,90]
Real GridSize::asind(Real val)
{
    Real answer = asin(val) * DEG_PER_RAD;
    return answer;
}

//Takes a value in the range [-1,1], returns a degree in range [0,180]
Real GridSize::acosd(Real val)
{
    Real answer = acos(val) * DEG_PER_RAD;
    return answer;
}




string GridSize::getInstrumentModulePath()
{
    char buffer[1024]; // Or optionally PATH_MAX
    char *result = getcwd(buffer, 1024);
    if (result == NULL)
    {
        return "Error changing to directory containing tests";
    }
    string pathL(buffer);
    vector<string> directories;

    char_separator<char> sep("/");
    tokenizer<char_separator<char>> tokens(pathL, sep);
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

    path = path + "/modules/instrument/bin/InstruPy_get_coverage_specs.py";

    return path;
}
