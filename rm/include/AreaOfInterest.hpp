//
// Created by Gabriel Apaza on 2019-03-27.
//

#ifndef ORBITS_AREAOFINTEREST_HPP
#define ORBITS_AREAOFINTEREST_HPP


//Json Parser
#include <json/json.h>
#include <boost/tokenizer.hpp>

//Std
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <math.h>


//OC Includes
#include "PointGroup.hpp"



//GMAT Defs
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"





using namespace std;



//!  Builds a point group based on the Area of Interest provided in the <mission>.json
class AreaOfInterest {
public:


    AreaOfInterest(Json::Value tsr, Real gs);


    AreaOfInterest(const AreaOfInterest& orig);


    virtual ~AreaOfInterest();




    // ---------- Functions ----------

    vector< pair<Real, Real> > shiftBounds(Real lonLow, Real lonHigh);

    //! Returns a shifted longitude from (-180,180) range to (0,360) range
    Real shiftLongitude(Real lon);

    //! Returns the number of points in the Area of Interest
    Real getNumPoints();

    //! Returns a vector of pairs containing the coordinates for each point of interest (ordered)
    vector< pair< Real, Real > > getCoordVec();

    //! Returns a reference to the PointGroup object modeling the AreaOfInterest
    PointGroup* getPointGroup();

    //! Prints out the area of interest bounds 0 - 360 deg
    void printBounds(Real latLow, Real latHigh, Real lonLow, Real lonHigh);


    //! Determines the number of points to put on the whole globe in order to get "num_points" points in the region of interest
    int getGlobalPoints(double latmin, double latmax, double lonmin, double lonmax, double num_points);






    // ---------- Public Variables ----------

    //!  PointGroup modeling the Area of Interest
    PointGroup* area;

    //! True if there is only one target area defined by lat/lon bounds
    bool singleTargetAreaBounded;

    //! True if there are multiple target areas defined by lat/lon bounds
    bool multipleTargetAreaBounded;





private:




    // ---------- Private Variables ----------

    //!  Contains parsed <mission>.json file
    Json::Value tsrJson;

    //!  The homogeneous grid size calculated for this architecture
    Real gridSize;

    //!  The number of points in the area of interest
    Integer numPoints;

    //!  The number of global points spanning the whole grid
    int numMaxGlobalPoints;

    //! The number of local points for one region of interest
    int numMaxLocalPoints;


    // ---------- For Tropics ----------
    //! Parses a poi.csv file into a GMAT PointGroup. poi.csv file convention can be found in the Orbit Module's README
    void parsePOIs();

    //! Custom array adding function for GMAT RealArrays
    RealArray addRealArrays(RealArray a1, RealArray a2);

    //! If we have multiple areas of interest defined by lat/lon bounds AND a restriction on the number of POIs, we need to assign a size ratio to each of the regions to determine how many POIs to place in that region
    double areaRatioFinder(int region_num, Json::Value regions);






};


#endif //ORBITS_AREAOFINTEREST_HPP
