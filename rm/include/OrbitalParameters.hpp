/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   OrbitalParameters.h
 * Author: gabeapaza
 *
 * Created on October 23, 2018, 3:20 PM
 */

#ifndef ORBITALPARAMETERS_H
#define ORBITALPARAMETERS_H


#include <json/json.h>
#include <vector>
#include <string>

//GMAT defs
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"

using namespace std;





//!  This class contains Satellite specific information
/*!
    This class reads from <architecture>.json file under the "satellite" section  <br>
    These orbital parameters will be used to propagate the satellite
*/
class OrbitalParameters {
public:

    //!  OrbitalParameters Constructor
    /*!
        \param cov - Json::Value object containing information from the "satellite" field in <architecture>.json
    */
    OrbitalParameters(Json::Value satellite);



    //!  OrbitalParameters Copy Constructor
    /*!
        Copies an OrbitalParameters object
    */
    OrbitalParameters(const OrbitalParameters& orig);



    //!  OrbitalParameters Destructor
    /*!
        Destroys an OrbitalParameters object
    */
    virtual ~OrbitalParameters();




    //!  Returns the Satellite's Semi-Major Axis
    /*!
        This is useful for calculating grid size for each of the Payloads
    */
    double getSMA();


    //!  Returns a vector of size 6 containing this Satellite's Keplerian Elements
    vector<Real> getKeplarianElements();


    //! Contains the comm bands for the satellite
    vector<string> commBands;



    //! Value holding the volume of the Spacecraft
    Real volume;


    //! Value holding the mass of the Spacecraft
    Real mass;


    //! Value holding the power of the Spacecraft
    Real power;

    //! The drag coefficient of the Spacecraft
    Real dragCoeff;


    //! Value holding the name of the Spacecraft
    string name;

    //Ephemeris data

    //! Value holding the orbit type of this spacecraft
    string orbitType;


    //! Satellite starting eccentricity
    Real startEcc;

    //! Satellite starting inclination
    Real startIncl;

    //! Satellite starting argument of periapsis
    Real startPer;


    //! Satellite starting right ascension of the ascending node
    Real startRAAN;

    //! Satellite starting Semi-Major Axis
    Real startSMA;


    //! Satellite starting true anomaly
    Real startTrueA;

    //! The starting date of the satellite
    string orbitEpoch;


    //! -- Testing function that prints out all the elements of this class
    void printElements();

    
private:

};

#endif /* ORBITALPARAMETERS_H */

