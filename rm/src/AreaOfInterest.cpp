//
// Created by Gabriel Apaza on 2019-03-27.
//

#include "AreaOfInterest.hpp"



#define PI 3.14159265358979323846
#define MAX_GRID_POINTS 10000
#define POI_FROM_FILE false
#define POI_FILE "/Users/gapaza/Documents/Validation/OrbitsValidation/poi.csv"



using namespace std;
using namespace GmatMathConstants; //contains RAD_PER_DEG
using namespace boost;


AreaOfInterest::AreaOfInterest(Json::Value tsr, Real gs)
{
    cout << "CREATE AREA" << endl;
    area       = new PointGroup();

    // Get the Tradespace Search Request file
    tsrJson           = tsr;
    gridSize          = gs;

    // Get the max number of local points if set
    if(tsrJson["settings"]["maxGridSize"].isNumeric())
        numMaxLocalPoints = tsrJson["settings"]["maxGridSize"].asDouble();
    else
        numMaxLocalPoints = MAX_GRID_POINTS;

    // If Array
    // 1. True  --> multiple regions of interest or a list of POIs
    // 2. False --> one region of interest
    singleTargetAreaBounded = !(tsrJson["mission"]["target"].isArray());
    if(!singleTargetAreaBounded)
    {
        multipleTargetAreaBounded = tsrJson["mission"]["target"][0]["latitude"]["minValue"].isNumeric();
    }
    else
    {
        multipleTargetAreaBounded = false;
    }



    // The user will specify either
    // 1. A file containing a list of points of interest (poi.csv)
    // 2. One Region of Interest
    // 3. Multiple Regions of Interest
    // 4. A List of latitudes / longitudes

    if (POI_FROM_FILE)  //---------------------------------------------------------------------------------------
    {
        parsePOIs();
        numPoints = area->GetNumPoints();
        cout << "--> Points: " << numPoints << endl;
    }

    else if(singleTargetAreaBounded) //--------------------------------------------------------------------------
    {
        RealArray latB;
        RealArray lonB;
        latB.push_back(tsrJson["mission"]["target"]["latitude"]["minValue"].asDouble());
        latB.push_back(tsrJson["mission"]["target"]["latitude"]["maxValue"].asDouble());
        lonB.push_back(tsrJson["mission"]["target"]["longitude"]["minValue"].asDouble());
        lonB.push_back(tsrJson["mission"]["target"]["longitude"]["maxValue"].asDouble());
        area->SetLatLonBounds(latB[1]*RAD_PER_DEG,latB[0]*RAD_PER_DEG,lonB[1]*RAD_PER_DEG,lonB[0]*RAD_PER_DEG);
        area->AddHelicalPointsByAngle(gridSize*RAD_PER_DEG);
        numPoints = area->GetNumPoints();
        cout << "Points Created vs Allowed: " << to_string(numPoints) << " / " << to_string(numMaxLocalPoints) << endl;
        if(numPoints > numMaxLocalPoints)
        {
            cout << "Recalculating POIs for one region" << endl;
            delete area;
            area   = new PointGroup();
            numMaxGlobalPoints = getGlobalPoints(latB[0],latB[1],lonB[0],lonB[1],numMaxLocalPoints);
            area->SetLatLonBounds(latB[1]*RAD_PER_DEG,latB[0]*RAD_PER_DEG,lonB[1]*RAD_PER_DEG,lonB[0]*RAD_PER_DEG);
            area->AddHelicalPointsByNumPoints(numMaxGlobalPoints);
            numPoints = area->GetNumPoints();
            printBounds(latB[0], latB[1], lonB[0], lonB[1]);
        }
        else
        {
            printBounds(latB[0], latB[1], lonB[0], lonB[1]);
        }
    }

    else if(multipleTargetAreaBounded) //--------------------------------------------------------------------------
    {
        //For each target region, we will have a PointGroup object
        RealArray all_lats; all_lats.resize(0);
        RealArray all_lons; all_lons.resize(0);
        Integer current_size = 0;
        Json::Value regions = tsrJson["mission"]["target"];
        int num_regions     = regions.size();
        for(int x = 0; x < num_regions; x++)
        {
            Json::Value region = regions[x];
            PointGroup* temp   = new PointGroup();
            RealArray          latB, lats;
            RealArray          lonB, lons;
            latB.push_back(region["latitude"]["minValue"].asDouble());
            latB.push_back(region["latitude"]["maxValue"].asDouble());
            lonB.push_back(region["longitude"]["minValue"].asDouble());
            lonB.push_back(region["longitude"]["maxValue"].asDouble());
            temp->SetLatLonBounds(latB[1]*RAD_PER_DEG,latB[0]*RAD_PER_DEG,lonB[1]*RAD_PER_DEG,lonB[0]*RAD_PER_DEG);
            temp->AddHelicalPointsByAngle(gridSize*RAD_PER_DEG);
            temp->GetLatLonVectors(lats, lons);
            all_lats = addRealArrays(all_lats, lats);
            all_lons = addRealArrays(all_lons, lons);
            delete temp;
        }

        cout << "Points Created vs Allowed: " << to_string(all_lats.size()) << " / " << to_string(numMaxLocalPoints) << endl;

        // Recalculate points of interest if there are more than the allowed amount
        if(all_lats.size() > numMaxLocalPoints)
        {
            cout << "Recalculating POIs for multiple regions" << endl;
            all_lats.clear();
            all_lons.clear();
            double regionGlobalPoints = 0;
            for(int x = 0; x < num_regions; x++)
            {
                double region_ratio  = areaRatioFinder(x,regions);
                double region_points = region_ratio * numMaxLocalPoints;
                Json::Value region   = regions[x];
                PointGroup* temp     = new PointGroup();
                RealArray            latB, lats;
                RealArray            lonB, lons;
                latB.push_back(region["latitude"]["minValue"].asDouble());
                latB.push_back(region["latitude"]["maxValue"].asDouble());
                lonB.push_back(region["longitude"]["minValue"].asDouble());
                lonB.push_back(region["longitude"]["maxValue"].asDouble());
                regionGlobalPoints = getGlobalPoints(latB[0],latB[1],lonB[0],lonB[1],region_points);
                temp->SetLatLonBounds(latB[1]*RAD_PER_DEG,latB[0]*RAD_PER_DEG,lonB[1]*RAD_PER_DEG,lonB[0]*RAD_PER_DEG);
                temp->AddHelicalPointsByNumPoints(regionGlobalPoints);
                temp->GetLatLonVectors(lats, lons);
                all_lats = addRealArrays(all_lats, lats);
                all_lons = addRealArrays(all_lons, lons);
                delete temp;
            }
        }
        area->AddUserDefinedPoints(all_lats, all_lons);
        numPoints = area->GetNumPoints();
        cout << "--> Points: " << numPoints << endl;
    }

    else //-------------------------------------------------------------------------------------------------------
    {
        RealArray lats;
        RealArray lons;
        numPoints = tsrJson["mission"]["target"].size();
        for(int x = 0; x < numPoints; x++)
        {
            Real lat = tsrJson["mission"]["target"][x]["latitude"].asDouble();
            Real lon = tsrJson["mission"]["target"][x]["longitude"].asDouble();
            lats.push_back( lat*RAD_PER_DEG );
            lons.push_back( lon*RAD_PER_DEG );
        }
        area->AddUserDefinedPoints(lats, lons);
        numPoints = area->GetNumPoints();
        cout << "--> Points: " << numPoints << endl;
    }











}

AreaOfInterest::AreaOfInterest(const AreaOfInterest& orig)
{

}

AreaOfInterest::~AreaOfInterest()
{
    delete area;
}



double AreaOfInterest::areaRatioFinder(int region_num, Json::Value regions)
{
    double total_area = 0;
    double region_of_interest_area = 0;
    for(int x = 0; x < regions.size(); x++)
    {
        Json::Value region   = regions[x];
        double length        = abs(region["latitude"]["maxValue"].asDouble() - region["latitude"]["minValue"].asDouble());
        double height        = abs(region["longitude"]["maxValue"].asDouble() - region["longitude"]["minValue"].asDouble());
        double region_area   = length * height;
        total_area           = total_area + region_area;
        if(x == region_num)
            region_of_interest_area = region_area;
    }
    double region_fraction = region_of_interest_area / total_area;
    return region_fraction;
}




RealArray AreaOfInterest::addRealArrays(RealArray a1, RealArray a2)
{
    RealArray        combined;
    int size_a1    = a1.size();
    int size_a2    = a2.size();
    int final_size = size_a1 + size_a2;
    combined.resize(final_size);
    for(int x = 0; x < size_a1; x++)
    {
        combined[x] = a1[x];
    }
    for(int x = 0; x < size_a2; x++)
    {
        combined[(x+size_a1)] = a2[x];
    }
    return combined;
}


void AreaOfInterest::parsePOIs()
{
    RealArray lats;
    RealArray lons;

    string POIs = POI_FILE;
    ifstream in(POIs.c_str());

    typedef tokenizer< escaped_list_separator<char> > Tokenizer;

    vector< string > objs;
    string line;

    while (getline(in,line))
    {
        Tokenizer tok(line);
        objs.assign(tok.begin(),tok.end());

        if(objs[0] == "" or objs[0] == "POI")
        {
            continue;
        }

        Real lat = stod(objs[1]);
        Real lon = stod(objs[2]);

        lats.push_back( lat*RAD_PER_DEG );
        lons.push_back( lon*RAD_PER_DEG );

    }
    area->AddUserDefinedPoints(lats, lons);

}




// ------------------- Get Functions ------------------
Real AreaOfInterest::getNumPoints()
{
    return numPoints;
}

vector< pair< Real, Real > > AreaOfInterest::getCoordVec()
{
    vector< pair< Real, Real > > toReturn;
    toReturn.resize(numPoints);

    double lat, lon;
    for(int x = 0; x < numPoints; x++)
    {
        Rvector3 *vec = area->GetPointPositionVector(x);
        lat = GmatMathUtil::ASin(vec->GetElement(2)/vec->GetMagnitude())*DEG_PER_RAD;
        lon = GmatMathUtil::ATan(vec->GetElement(1),vec->GetElement(0))*DEG_PER_RAD;
        pair<Real, Real> temp(lat, lon);
        toReturn[x] = temp;
    }

    return toReturn;
}

PointGroup* AreaOfInterest::getPointGroup()
{
    return area;
}





// ------------------- Helper Functions ------------------
vector< pair<Real, Real> > AreaOfInterest::shiftBounds(Real lonLow, Real lonHigh)
{
    vector< pair<Real, Real> > bounds;
    bool lonNegative = (lonLow < 0);
    Real low = shiftLongitude(lonLow);
    Real high = shiftLongitude(lonHigh);


    //Only in this case will we need two bounds
    if(low > high)
    {
        pair<Real, Real> bound1(low, 360);
        pair<Real, Real> bound2(0, high);
        bounds.push_back(bound1);
        bounds.push_back(bound2);
        return bounds;
    }
    else
    {
        pair<Real, Real> bound1(low, high);
        bounds.push_back(bound1);
        return bounds;
    }
}




//Takes a longitude in bounds (-180, 180) and converts to bounds (0, 360)
Real AreaOfInterest::shiftLongitude(Real lon)
{
    int upperBound = 360;

    int counter = 0;
    int lower = floor(lon);
    while( (lon - lower) != 0 )
    {
        lon = lon * 10.0;
        lower = floor(lon);
        counter++;
    }

    for(int x = 0; x < counter; x++)
    {
        upperBound = upperBound * 10;
    }


    int longitude = lon;


    Real toReturn = (((longitude % upperBound) + upperBound) % upperBound);

    for(int x = 0; x < counter; x++)
    {
        toReturn = toReturn / 10;
    }

    return toReturn;
}


//Lon Bounds (0,360) -- Lat Bounds (-90,90)
int AreaOfInterest::getGlobalPoints(double latmin, double latmax, double lonmin, double lonmax, double num_points)
{
    double lat1;
    double lat2;
    double lon1;
    double lon2;
    double londiff;
    double surfaceAreaCoeff;
    int    numGlobalPoints;

    lat1 = latmin * RAD_PER_DEG;
    lat2 = latmax * RAD_PER_DEG;
    lon1 = lonmin * RAD_PER_DEG;
    lon2 = lonmax * RAD_PER_DEG;

    if(lon1 <= lon2)
    {
        londiff = lon2 - lon1;
    }
    else
    {
        londiff =  (2*PI - lon1) + lon2;
    }

    surfaceAreaCoeff = londiff * abs( sin(lat1) - sin(lat2) ) / (4 * PI);
    numGlobalPoints = num_points / surfaceAreaCoeff;

    return numGlobalPoints;
}



void AreaOfInterest::printBounds(Real latLow, Real latHigh, Real lonLow, Real lonHigh)
{

    cout << endl << "----- Area of Interest (" << numPoints << " points) -----" << endl << endl;
    cout << "                   North: " << latHigh << endl << endl << endl << endl;
    cout << "          West: " << lonLow << "           East: " << lonHigh << endl << endl << endl << endl;
    cout << "                   South: " << latLow << endl << endl;
    cout << "-------------------------------------------" << endl << endl;
}