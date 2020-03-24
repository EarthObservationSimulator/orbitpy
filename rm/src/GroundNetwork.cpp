//
// Created by Gabriel Apaza on 2019-03-27.
//

#include "GroundNetwork.hpp"



using namespace std;
using namespace GmatMathConstants; //contains RAD_PER_DEG
using namespace boost;





GroundNetwork::GroundNetwork(Json::Value gN)
{
    //cout << endl << "----- Ground Network Object -----" << endl;

    groundNetworkJson = gN;
    groundNetworkPoints = new PointGroup();
    numNetworks = 0;
    numStations = 0;



    bool gsFile = false;
    if(gsFile)
    {
        parseGroundStations("/Users/gapaza/Documents/TAT-C/landsat8-architecture/NENgov.txt");
    }
    else
    {
        RealArray latArray;
        RealArray lonArray;

        numNetworks = groundNetworkJson.size();

        Json::Value network;
        for(int x = 0; x < numNetworks; x++)
        {
            network = groundNetworkJson[x];
            int numberStations = network["numberStations"].asInt();

            for(int station = 0; station < numberStations; station++)
            {

                Real lat = 0;
                Real lon = 0;

                lat = network["groundStations"][station]["latitude"].asDouble();
                lon = network["groundStations"][station]["longitude"].asDouble();

                //Fill latArray and lonArray with all the ground stations
                latArray.push_back(lat*RAD_PER_DEG);
                lonArray.push_back(lon*RAD_PER_DEG);
                numStations++;
            }

        }

        groundNetworkPoints->AddUserDefinedPoints(latArray, lonArray);
    }


    numStations = groundNetworkPoints->GetNumPoints();
    //cout << "Num Ground Stations: " << numStations << endl;


}

GroundNetwork::GroundNetwork(const GroundNetwork& orig)
{

}

GroundNetwork::~GroundNetwork()
{
    delete groundNetworkPoints;
}


void GroundNetwork::parseGroundStations(string path)
{
    RealArray lats;
    RealArray lons;
    numNetworks = 1;

    ifstream in(path.c_str());

    typedef tokenizer< char_separator<char> > Tokenizer;
    char_separator<char> sep(" ");

    vector< string > objs;
    string line;

    while (getline(in,line))
    {
        Tokenizer tok(line, sep);
        objs.assign(tok.begin(),tok.end());

        Real lat = stod(objs[0]);
        Real lon = shiftLongitude(stod(objs[1]));


        lats.push_back( lat*RAD_PER_DEG );
        lons.push_back( lon*RAD_PER_DEG );

        numStations++;
    }
    groundNetworkPoints->AddUserDefinedPoints(lats, lons);






}




// ------------------- Get Functions ------------------
Real GroundNetwork::getNumStations()
{
    return numStations;
}

Real GroundNetwork::getNumNetworks()
{
    return numNetworks;
}

vector< pair< Real, Real > > GroundNetwork::getCoordVec()
{
    vector< pair< Real, Real > > toReturn;
    toReturn.resize(numPoints);

    double lat, lon;
    for(int x = 0; x < numPoints; x++)
    {
        Rvector3 *vec = groundNetworkPoints->GetPointPositionVector(x);
        lat = GmatMathUtil::ASin(vec->GetElement(2)/vec->GetMagnitude())*DEG_PER_RAD;
        lon = GmatMathUtil::ATan(vec->GetElement(1),vec->GetElement(0))*DEG_PER_RAD;
        pair<Real, Real> temp(lat, lon);
        toReturn[x] = temp;
    }

    return toReturn;
}

PointGroup* GroundNetwork::getPointGroup()
{
    return groundNetworkPoints;
}












// ------------------- Helper Functions ------------------
Real GroundNetwork::shiftLongitude(Real lon)
{
    Real longitude = lon;

    if(longitude < 0)
    {
        longitude += 360;
    }

    return longitude;
}