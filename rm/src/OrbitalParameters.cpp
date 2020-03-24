/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   OrbitalParameters.cpp
 * Author: gabeapaza
 * 
 * Created on October 23, 2018, 3:20 PM
 */

#include "OrbitalParameters.hpp"
#include <iostream>

using namespace std;
using namespace GmatMathConstants; //contains RAD_PER_DEG

OrbitalParameters::OrbitalParameters(Json::Value satellite)
{


    commBands.push_back("X");


    //Get other satellite specific data
    volume = satellite["volume"].asDouble();
    mass = satellite["mass"].asDouble();
    power = satellite["power"].asDouble();
    name = satellite["name"].asString();
    orbitType = satellite["orbit"]["orbitType"].asString();
    startIncl = satellite["orbit"]["inclination"].asDouble();
    startSMA = satellite["orbit"]["semimajorAxis"].asDouble();
    startEcc = satellite["orbit"]["eccentricity"].asDouble();
    startPer = satellite["orbit"]["periapsisArgument"].asDouble();
    startRAAN = satellite["orbit"]["rightAscensionAscendingNode"].asDouble();
    startTrueA = satellite["orbit"]["trueAnomaly"].asDouble();
    orbitEpoch = satellite["orbit"]["epoch"].asString();

    //Currently we aren't being supplied a drag coefficient --> it will not be used until we are given one
    dragCoeff = 0;
}

OrbitalParameters::OrbitalParameters(const OrbitalParameters& orig)
{

}

OrbitalParameters::~OrbitalParameters()
{
    
}



// ------------- Testing Functions --------------
void OrbitalParameters::printElements()
{
    cout <<  "Volume " << volume << endl;
    cout <<  "Ecc " << startEcc << endl;
    cout <<  "Incl " << startIncl << endl;
    cout <<  "Per " << startPer << endl;
    cout <<  "RAAN " << startRAAN << endl;
    cout <<  "SMA " << startSMA << endl;
    cout <<  "TrueA " << startTrueA << endl;
}



// ------------- Access Functions --------------
double OrbitalParameters::getSMA()
{
    return startSMA;
}

vector<Real> OrbitalParameters::getKeplarianElements()
{
    vector<Real> ephemerisData;

    //Push all ephemerisData onto vector
    ephemerisData.push_back(startSMA);                //Dist from sat to earth's center (Km)
    ephemerisData.push_back(startEcc);                //Value between 0 and 1
    ephemerisData.push_back(startIncl * RAD_PER_DEG); //Angle
    ephemerisData.push_back(startRAAN * RAD_PER_DEG); //Angle
    ephemerisData.push_back(startPer * RAD_PER_DEG);  //Angle
    ephemerisData.push_back(startTrueA * RAD_PER_DEG);//Angle

//    ephemerisData.push_back(startSMA);
//    ephemerisData.push_back(startEcc);
//    ephemerisData.push_back(startIncl);
//    ephemerisData.push_back(startRAAN);
//    ephemerisData.push_back(startPer);
//    ephemerisData.push_back(startTrueA);

    //Return data
    return ephemerisData;
}


















