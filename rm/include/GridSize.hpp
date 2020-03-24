//
// Created by Gabriel Apaza on 2019-02-09.
//

#ifndef ORBIT_GRIDSIZE_H
#define ORBIT_GRIDSIZE_H

#include <string>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <array>

#include <boost/algorithm/string.hpp>


#include "gmatdefs.hpp"
#include "Rmatrix.hpp"
#include "Rvector6.hpp"
#include "Rvector3.hpp"

//Boost
#include <boost/foreach.hpp>
#include <boost/tokenizer.hpp>


#include <json/json.h>

/*
 * The purpose of this class is to create a homogeneous grid size considering all the potential satellites
 * -- The potential satellites are limited to the satellites listed in the Architecture
 */




using namespace std;




//!  This class is used to calculate the grid size for an Area of Interest
/*!
 * <b>Functionalities</b> <br>
    Calculates a homogeneous grid size if given an <architecture<.json file
    Calculates a specific grid size if given an alongtrack, crosstrack, and SMA
*/
class GridSize {
public:

    GridSize();
    GridSize(const GridSize& orig);
    virtual ~GridSize();

    //! This calculates a grid size for each of the satellites in an architecture based on their along track FOV and semi-major axis. The smallest grid size will be returned and used
    /*!
      \param archJson - A Json::Value object containing information about the <architecture>.json file
      \return Homogeneous grid size
    */
    Real findHomogeneousGrid(Json::Value mission_json);


    //! Finds the minimum altitude possible for any satellite in the mission.json file
    Real FindMinAltitude(Json::Value mission_json);

    //! Finds the minimum sensor cross track possible for any satellite in the mission.json file
    Real FindMinCrossTrack(Json::Value mission_json);



    //! This function calls the Instrument module to calculate the cross track FOV of a given sensor
    /*!
      \param archJson - A Json::Value object containing information about the spacecraft's payload
      \return the cross track FOV
    */
    Json::Value getCoverageSpecs(Json::Value payload);




    //! This returns a grid size based on a sensor's cross track field of view and a Satellite's Semi-Major Axis
    /*!
      \param crossTrack - A Sensor's cross track field of view
      \param SMA - The Semi-Major Axis of a Satellite
      \return grid size
    */
    Real findGridSize(Real crossTrack, double SMA);


private:


    //! This funciton finds a lambda value based on a Sensor's field of view and a Satellite's Semi-Major Axis
    /*!
      \param FOC - A Sensor's along or cross track FOV
      \param SMA - The Semi-Major Axis of a Satellite
      \return Homogeneous grid size
    */
    Real get_ctECA(Real FOV, double SMA); //This is a helper function for GridSize


    //! Matlab function cosd()
    Real cosd(Real val);

    //! Matlab function sind()
    Real sind(Real val);

    //! Matlab function asind()
    Real asind(Real val);

    //! Matlab function acosd()
    Real acosd(Real val);

    //! Returns a path to the instrument module
    string getInstrumentModulePath();

};


#endif //ORBIT_GRIDSIZE_H
