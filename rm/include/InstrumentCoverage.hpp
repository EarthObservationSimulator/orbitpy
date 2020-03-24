/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   InstrumentCoverage.h
 * Author: gabeapaza
 *
 * Created on October 27, 2018, 12:25 PM
 */

#ifndef INSTRUMENTCOVERAGE_H
#define INSTRUMENTCOVERAGE_H

//Standard Library
#include <string>
#include <vector>
#include <iostream>
#include <math.h>
#include <ctime>
#include <array>
#include <fstream>

//Boost
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/tokenizer.hpp>

//Json Parser
#include <json/json.h>

//GMAT Includes
#include "gmatdefs.hpp"
#include "Rmatrix.hpp"
#include "Rvector6.hpp"
#include "Rvector3.hpp"


using namespace std;







//!  This class contains Payload specific information
/*!
    This class reads from <architecture>.json file under the "payload" section and builds a coverage for a Satellite.  <br>
    This coverage will be used to create a Sensor object.

    <b>Note</b> <br>
    This class is currently hard coded to model an instrument from Landsat-8. View the readme on gitlab for more information

*/
class InstrumentCoverage {
public:


    //!  InstrumentCoverage Constructor
    /*!
        \param cov - Json::Value object containing information from the "Payload" field in <architecture>.json
        \param semiMajorAxis - double containing the host Satellite's Semi-Major Axis

        --The Semi-Major Axis is required for the grid size calculation
    */
    InstrumentCoverage(Json::Value cov, double gs, double semi_MajorAxis);



    //!  InstrumentCoverage Copy Constructor
    /*!
        Copies an InstrumentCoverage object
    */
    InstrumentCoverage(const InstrumentCoverage& orig);



    //!  InstrumentCoverage Destructor
    /*!
        Destroys an InstrumentCoverage object
    */
    virtual ~InstrumentCoverage();



    //!  Calls the instrument module to get the payload's instrument specifications
    /*!
     *  \param payload --> Json::Value containing payload fields in <arch>.json
        \return Json::Value containing specifications
    */
    Json::Value getInstrumentSpecs(Json::Value payload);




    //!  Returns true if the coverage specified is for a rectangular sensor, false otherwise
    /*!
        \return bool
    */
    bool isRectangular();


    //! Writes the satX_accessInfo.json file containing sensor information
    void writeJson(Json::Value instrumentToWrite, string writeFiles, int satelliteNum);






    //!  Finds a Nyquist sampled timestep for propagation
    /*!
        \param SMA - Host satellite's Semi-Major Axis
        \return Integer - Timestep
    */
    Integer findNyqTimestep(double SMA);




    //!  Finds a timestep based on the SMA and along track values (conical and rectangular)
    /*!
        \return Integer
    */
    Real findInterpolationStep();


    //!  Finds a timestep such that there are 100 propagation calculations per orbit
    /*!
        \return Integer
    */
    Integer findPropagationStep();


    //!  Finds either a conical or rectangular proxy sensor based on the min interpolation step size passed in
    /*!
        \return Rvector
    */
    Rvector findProxySensor(Real tInpQ_OCmin);

    //!  Returns the sensor angles for either a conical or rectangular sensor
    /*!
        \return Rvector
    */
    Rvector getSensorAngles();



    Rvector getEulerParameters();




    
    
    
    
    
    
    // ---------- CONICAL SENSOR ----------

    //!  The single cone angle of a Conical Sensor
    //Real coneAngle;

    //!  The half field of view of a Conical Sensor
    //Real halfFOV;


    //!  The full field of view of a Conical Sensor
    //Real fullFOV;
    
    
    
    
    // ---------- RECTANGULAR SENSOR ----------

    //!  The four clock angles of a Rectangular Sensor
    /*!
        <b>Issue</b>: <br>
        In the new architecture we need to be provided 4 clock angles if Rectangular
    */
    Rvector clockAngles;

    //!  The four cone angles of a Rectangular Sensor
    /*!
        <b>Issue</b>: <br>
        In the new architecture we need to be provided 4 cone angles if Rectangular
    */
    Rvector coneAngles;

    
    
    
    // ---------- ELEMENTS FOR EITHER RECTANGULAR OR CONICAL ----------

    //!  A sensor's cross track field of view (Rectangular / Conical) full / half
    Real crossTrackFOV_rad;
    Real crossTrackFOV_deg;

    Real crossTrackFOV_half_rad;
    Real crossTrackFOV_half_deg;

    //!  A sensor's along track field of view (Rectangular / Conical) full / half
    Real alongTrackFOV_rad;
    Real alongTrackFOV_deg;

    Real alongTrackFOV_half_rad;
    Real alongTrackFOV_half_deg;






    //!  The sensor's first euler angle
    Real eulerAngle1;
    //!  The sensor's second euler angle
    Real eulerAngle2;
    //!  The sensor's third euler angle
    Real eulerAngle3;
    //!  The sensor's first euler sequence
    Integer eulerSeq1;
    //!  The sensor's second euler sequence
    Integer eulerSeq2;
    //!  The sensor's third euler sequence
    Integer eulerSeq3;





    //!  The grid size calculated for this Coverage considering the host satellite's Semi-Major Axis
    double gridSize;



    //!  The sensor type can either be CONICAL or RECTANGULAR
    string sensorType;


    //!  Json::Value object containing information from the "Payload" field in <architecture>.json after calling instrument module
    Json::Value instrumentSpecs;

    //!  Json::Value object containing information from the "Payload" field in <architecture>.json before calling instrument module
    Json::Value originalSpecs;

    //!  Json::Value object containing information on the "Proxy" sensor if corrections are needed
    Json::Value proxySpecs;


    //! Gets along track earch centric angle from payload
    Real get_atECA();


    //! Finds size of the along-track footprint of the sensor
    Real get_atfp_dim();

    //! Get sensor AT-fov from Along-track footprint
    Real get_atfov_dim(Real AT_FP_len);

    //! Returns a path to the instrument module for calling purposes
    string getInstrumentModulePath();


    Real semiMajorAxis;

    Real alt_min;

    
private:


    Real sind(Real val);
    Real cosd(Real val);
    Real asind(Real val);
    Real acosd(Real val);



};

#endif /* INSTRUMENTCOVERAGE_H */

