//
// Created by Gabriel Apaza on 2019-04-17.
//
#define BOOST_TEST_MODULE "C++ Unit Tests for AreaOfInterest.cpp"
#include <unit_test.hpp>

//File being tested
#include "AreaOfInterest.hpp"
#include "gmatdefs.hpp"

//Std
#include <iostream>
#include <math.h>
#include <iostream>
#include <json/json.h>
#include <unistd.h>
#include <string>



using namespace GmatMathConstants;
using namespace std;

const string rmSrcDir = "../../src";

std::string testingDirectory();
Json::Value getJsonObj(std::string filePath);



BOOST_AUTO_TEST_SUITE (areaofinterest_test)

//One test for the constructor
//two tests for the longitude shift



//A test needs to be added for creating a point group from a set of points


BOOST_AUTO_TEST_CASE (pointgroup)
        {
                string dir = testingDirectory();
                string testFile = dir + "AOI_1.json";

                double gridSize = 1.65; //Landsat

                Json::Value file = getJsonObj(testFile);
                AreaOfInterest aoi(file, gridSize);


                double numPts = aoi.getNumPoints();

                //BOOST_TEST( numPts == 44 );
                BOOST_TEST( numPts == 44 );

                chdir(dir.c_str());
        }


BOOST_AUTO_TEST_CASE (pointgroup2)
        {
                string dir = testingDirectory();
                string testFile = dir + "AOI_2.json";

                double gridSize = 1.65; //Landsat

                Json::Value file = getJsonObj(testFile);
                AreaOfInterest aoi(file, gridSize);


                double numPts = aoi.getNumPoints();

                //BOOST_TEST( numPts == 15152 );
                BOOST_TEST( numPts == 15152 );

                chdir(dir.c_str());
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