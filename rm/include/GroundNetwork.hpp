//
// Created by Gabriel Apaza on 2019-03-27.
//

#ifndef ORBITS_GROUNDNETWORK_HPP
#define ORBITS_GROUNDNETWORK_HPP



//Json Parser
#include <json/json.h>

//Std
#include <iostream>
#include <vector>
#include <fstream>


//OC Includes
#include "PointGroup.hpp"


//Boost
#include <boost/tokenizer.hpp>



//GMAT Defs
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"






using namespace std;


//!  Builds a point group based on all the ground networks in the <atchitecture>.json file
class GroundNetwork {
public:

    GroundNetwork(Json::Value gN);


    GroundNetwork(const GroundNetwork& orig);


    virtual ~GroundNetwork();




    // ---------- Functions ----------

    //! Returns a shifted longitude from (-180,180) range to (0,360) range
    Real shiftLongitude(Real lon);

    //! Returns the number of ground stations in all the networks
    Real getNumStations();

    //! Returns the number of ground networks
    Real getNumNetworks();

    //! Returns a vector of pairs containing the coordinates for each point of interest
    vector< pair< Real, Real > > getCoordVec();

    //! Returns the PointGroup object for the OrbitSimulator
    PointGroup* getPointGroup();


    void parseGroundStations(string path);



    // ---------- Public Variables ----------

    //!  Poing Group modeling the Area of Interest
    PointGroup* groundNetworkPoints;









private:



    // ---------- Private Variables ----------

    //!  Contains parsed <mission>.json file
    Json::Value groundNetworkJson;

    //!  The number of points in the area of interest
    Integer numPoints;

    //! The number of ground networks in this architecture
    Integer numNetworks;

    //! The number of ground stations in all the ground networks
    Integer numStations;





};


#endif //ORBITS_GROUNDNETWORK_HPP
