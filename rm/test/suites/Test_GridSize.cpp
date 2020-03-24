//
// Created by Gabriel Apaza on 2019-04-13.
//
#define BOOST_TEST_MODULE "C++ Unit Tests for GridSize.cpp"
#include <unit_test.hpp>

//File being tested
#include "GridSize.hpp"
#include "gmatdefs.hpp"

//Std
#include <iostream>
#include <math.h>
#include <iostream>
#include <json/json.h>
#include <unistd.h>
#include <string>

//#include <boost/filesystem.hpp>


using namespace GmatMathConstants;
using namespace std;


const int RADIUS_EARTH = 6378;
const string rmSrcDir = "../../src";

std::string testingDirectory();
std::string testingDirectoryArch();
Json::Value getJsonObj(std::string filePath);






BOOST_AUTO_TEST_SUITE (gridsize_test)


BOOST_AUTO_TEST_CASE (conical1)
        {

            double altitude = 700 + RADIUS_EARTH;
            double crossTrackFOV = 15;
            GridSize grid;
            Real gSize = grid.findGridSize(crossTrackFOV, altitude);

            double EPSILON = .01;
            BOOST_TEST( (fabs(gSize - (1.657*.9)) < EPSILON) );

        }

BOOST_AUTO_TEST_CASE (conical2)
        {

                double altitude = 500 + RADIUS_EARTH;
                double crossTrackFOV = 15;
                GridSize grid;
                Real gSize = grid.findGridSize(crossTrackFOV, altitude);

                double EPSILON = .01;
                BOOST_TEST( (fabs(gSize - (1.18*.9)) < EPSILON) );
        }

BOOST_AUTO_TEST_CASE (conical3)
        {

                double altitude = 500 + RADIUS_EARTH;
                double crossTrackFOV = 55.24;
                GridSize grid;
                Real gSize = grid.findGridSize(crossTrackFOV, altitude);

                double EPSILON = .01;
                BOOST_TEST( (fabs(gSize - (4.76*.9)) < EPSILON) );

        }



BOOST_AUTO_TEST_CASE (instrumentModuleCall1)
        {
                string dir = testingDirectory();
                string testFile = dir + "oneSat.json";

                Json::Value arch = getJsonObj(testFile);
                Json::Value payload = arch["spaceSegment"][0]["satellites"][0]["payload"];

                GridSize grid;
                Json::Value specs = grid.getCoverageSpecs(payload);

                Real crossTrackFOV = specs["fieldOfView"]["CrossTrackFov"].asDouble();

                BOOST_TEST( crossTrackFOV == 30 );

        }


BOOST_AUTO_TEST_CASE (instrumentModuleCall2)
        {
                string dir = testingDirectory();
                string testFile = dir + "payload_1.json";

                Json::Value payload = getJsonObj(testFile);
                payload = payload["payload"];

                GridSize grid;
                Json::Value specs = grid.getCoverageSpecs(payload);

                Real crossTrackFOV = specs["fieldOfView"]["CrossTrackFov"].asDouble();
                BOOST_TEST( crossTrackFOV == 90 );

        }




BOOST_AUTO_TEST_SUITE_END()




std::string testingDirectory()
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

    path = path + "/modules/orbits/rm/test/testing-files/";
    return path;
}

std::string testingDirectoryArch()
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

    path = path + "/modules/orbits/rm/test/testing-architectures/";
    return path;
}




Json::Value getJsonObj(std::string filePath)
{
    Json::Value toReturn;

    Json::Reader reader;
    std::ifstream test(filePath, std::ifstream::binary);
    bool parsingSuccessful = reader.parse(test,toReturn);
    if (!parsingSuccessful)
    {
        std::cout << "Failed to load json file" << std::endl;
        //Use __LINE__ and __FILE__ preprocessors macros to alert user exactly where the error is
        //----------------------------------Return error to user here through GUI socket connection----------------------------------
        exit(1);
    }
    return toReturn;
}