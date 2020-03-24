/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   InstrumentCoverage.cpp
 * Author: gabeapaza
 * 
 * Created on October 27, 2018, 12:25 PM
 */

#include "InstrumentCoverage.hpp"





#define RE 6378.0 // in km
#define GM 3.986004418e14 //in m and s
#define PI 3.14159265358979323846


using namespace GmatMathConstants;


//Non-Rectangular
//Conical instruments only get provided one cone angle -- no clock angle
//Conical sensors get passed a fov!! This is simply the given coneAngle!!



//Rectangular
//Rectangular instruments get provided multiple cone angles and clock angles
//We will create a CustomSensor in OC using the vector of cone angles and vector of clock angles


//Here we have the constructor for InstrumentCoverage object
InstrumentCoverage::InstrumentCoverage(Json::Value cov, double gs, double semi_MajorAxis)
{
    originalSpecs = cov;
    proxySpecs = cov;
    instrumentSpecs = getInstrumentSpecs(cov);
    //cout << instrumentSpecs << endl;
    gridSize = gs;

    semiMajorAxis = semi_MajorAxis;
    alt_min = semi_MajorAxis - RE;




    sensorType        = instrumentSpecs["fieldOfView"]["geometry"].asString();
    crossTrackFOV_deg = instrumentSpecs["fieldOfView"]["CrossTrackFov"].asDouble();
    crossTrackFOV_rad = crossTrackFOV_deg * RAD_PER_DEG;
    alongTrackFOV_deg = instrumentSpecs["fieldOfView"]["AlongTrackFov"].asDouble();
    alongTrackFOV_rad = alongTrackFOV_deg * RAD_PER_DEG;
    eulerAngle1       = instrumentSpecs["Orientation"]["eulerAngle1"].asDouble();
    eulerAngle2       = instrumentSpecs["Orientation"]["eulerAngle2"].asDouble();
    eulerAngle3       = instrumentSpecs["Orientation"]["eulerAngle3"].asDouble();
    eulerSeq1         = instrumentSpecs["Orientation"]["eulerSeq1"].asDouble();
    eulerSeq2         = instrumentSpecs["Orientation"]["eulerSeq2"].asDouble();
    eulerSeq3         = instrumentSpecs["Orientation"]["eulerSeq3"].asDouble();

    crossTrackFOV_half_rad = crossTrackFOV_rad/2.0;
    crossTrackFOV_half_deg = crossTrackFOV_deg/2.0;
    alongTrackFOV_half_rad = alongTrackFOV_rad/2.0;
    alongTrackFOV_half_deg = alongTrackFOV_deg/2.0;



    //Save cone and clock angles in RADIANS
    if(sensorType == "CONICAL")
    {
        coneAngles.SetSize(1);
        coneAngles[0]  = instrumentSpecs["fieldOfView"]["coneAnglesVector"][0].asDouble() * RAD_PER_DEG;
    }
    else
    {
        clockAngles.SetSize(4);
        clockAngles[0] = instrumentSpecs["fieldOfView"]["clockAnglesVector"][0].asDouble() * RAD_PER_DEG;
        clockAngles[1] = instrumentSpecs["fieldOfView"]["clockAnglesVector"][1].asDouble() * RAD_PER_DEG;
        clockAngles[2] = instrumentSpecs["fieldOfView"]["clockAnglesVector"][2].asDouble() * RAD_PER_DEG;
        clockAngles[3] = instrumentSpecs["fieldOfView"]["clockAnglesVector"][3].asDouble() * RAD_PER_DEG;

        coneAngles.SetSize(4);
        coneAngles[0]  = instrumentSpecs["fieldOfView"]["coneAnglesVector"][0].asDouble() * RAD_PER_DEG;
        coneAngles[1]  = instrumentSpecs["fieldOfView"]["coneAnglesVector"][1].asDouble() * RAD_PER_DEG;
        coneAngles[2]  = instrumentSpecs["fieldOfView"]["coneAnglesVector"][2].asDouble() * RAD_PER_DEG;
        coneAngles[3]  = instrumentSpecs["fieldOfView"]["coneAnglesVector"][3].asDouble() * RAD_PER_DEG;
    }


    cout << endl << "------> Original Instrument Specifications <------" << endl;
    cout         << "+-------- Sensor Type: " << sensorType << endl;
    cout         << "+--- Full Cross Track: " << crossTrackFOV_deg << endl;
    cout         << "+--- Full Along Track: " << alongTrackFOV_deg << endl;
    cout         << "--------------------------------------------------" << endl << endl;




}


//Dont for get to build the copy constructor --> this could be useful for saving the orbit on failure
InstrumentCoverage::InstrumentCoverage(const InstrumentCoverage& orig) 
{
    
}


//Destructor
InstrumentCoverage::~InstrumentCoverage() 
{
    
}


// ------------------- Propagation / Interpolation Timestep Functions -------------------
Integer InstrumentCoverage::findPropagationStep()
{
    Real    orbitPeriod;
    Real    flightVelocity;
    Integer propStepSize;

    flightVelocity = sqrt( (GM * 100000.0) / semiMajorAxis );
    orbitPeriod    = 2*PI*sqrt(pow( semiMajorAxis * 1e3, 3) / GM ); //Seconds
    propStepSize   = floor(orbitPeriod / 100);

    return propStepSize; //There will be 100 propagations per-orbit
}


Real InstrumentCoverage::findInterpolationStep()
{
    Real tInp_minreq;
    Real AT_FP_len;
    Real t_AT_FP;         // Time taken by satellite to go over the along-track length
    Real orbitPeriod;
    Real earthCircumference;
    Real sat_Gvel;


    // ---------- Ground Velocity Calculation ----------
    orbitPeriod        = 2.0*PI*sqrt(pow( semiMajorAxis * 1e3, 3) / GM ); // Seconds
    earthCircumference = 2.0*PI*RE;
    sat_Gvel           = (Real) earthCircumference / (Real) orbitPeriod;  // Km/s
    AT_FP_len          = get_atfp_dim();                                  // Full along track FOV
    t_AT_FP            = AT_FP_len / sat_Gvel;

    if(sensorType == "CONICAL")
    {
        tInp_minreq = 0.1 * t_AT_FP;
    }
    else if(sensorType == "RECTANGULAR")
    {
        tInp_minreq = 0.20 * t_AT_FP;
    }
    else
    {
        tInp_minreq = 1.0;
    }

    return tInp_minreq;
}

Real InstrumentCoverage::get_atfp_dim()
{
    Real AT_FP_len;
    Real eca_deg;

    eca_deg   = get_atECA();                  //Get earth centric angle
    AT_FP_len = RE * (eca_deg * RAD_PER_DEG); //Now in radians

    return AT_FP_len;
}


Real InstrumentCoverage::get_atECA()
{
    double sinRho;
    double lambda_deg;
    double elev_deg;
    double hfov_deg;
    double eca_deg;

    sinRho     = RE / semiMajorAxis;             //sinRho = RE/(RE+H); % RE is radius of Earth, H is altitude of satellite
    hfov_deg   = alongTrackFOV_deg/2;            //hfov_deg = CT_fov_deg/2;
    elev_deg   = acosd(sind(hfov_deg) / sinRho);
    lambda_deg = 90 - hfov_deg - elev_deg;       //half earth centric angle (deg)
    eca_deg    = lambda_deg * 2;                 //full earth centric angle (deg)

    return eca_deg;
}
// ------------------- Propagation / Interpolation Timestep Functions -------------------
















// ------------------- Proxy Sensor Functions -------------------
Rvector InstrumentCoverage::findProxySensor(Real tInpQ_OCmin)
{
    cout << "-----> ORIGINAL INSTRUMENT <-----" << endl;
    Rvector angles;
    if(sensorType == "CONICAL")
    {
        cout << "Conical Cone Angle: " << to_string(coneAngles[0]) << endl << "------------------------------" << endl;
    }
    else
    {
        cout << "Rectangular Cone Angles: " << to_string(coneAngles[0]) << " " << to_string(coneAngles[1]) << " " << to_string(coneAngles[2]) << " " << to_string(coneAngles[3]) << endl;
        cout << "Rectangular Clock Angles: " << to_string(clockAngles[0]) << " " << to_string(clockAngles[1]) << " " << to_string(clockAngles[2]) << " " << to_string(clockAngles[3]) << endl;
        cout << "------------------------------" << endl;
    }
    cout << endl << "-----> PROXY INSTRUMENT <-----" << endl;




    Rvector proxy;
    Real    t_AT_FP;
    Real    AT_FP_len;
    Real    orbitPeriod;
    Real    sat_Gvel;    //Satellite Ground Velocity


    orbitPeriod = 2.0*PI*sqrt(pow( semiMajorAxis * 1e3, 3.0) / GM );
    sat_Gvel    = 2.0*PI*RE / orbitPeriod;


    if(sensorType == "CONICAL")
    {
        Real sensor_Conical_fov;
        proxy.SetSize(1);

        t_AT_FP            = tInpQ_OCmin / 0.1;
        AT_FP_len          = t_AT_FP * sat_Gvel;
        sensor_Conical_fov = get_atfov_dim(AT_FP_len);
        proxy[0]           = (sensor_Conical_fov * RAD_PER_DEG) / 2;

        //Debugging
        cout << "+------- FOV (full): " << (Real) sensor_Conical_fov << endl;

        return proxy;
    }
    else if(sensorType == "RECTANGULAR")
    {
        Json::Value proxySpecsConverted;
        Real        sensor_AT_fov;       //Proxy full along track angle (deg)


        t_AT_FP                                            = tInpQ_OCmin / 0.20;       // previously 0.25 -- tInpQ_OCmin = 1.0
        AT_FP_len                                          = t_AT_FP * sat_Gvel;
        sensor_AT_fov                                      = get_atfov_dim(AT_FP_len);
        //sensor_AT_fov                                      = sensor_AT_fov + (sensor_AT_fov * 0.5); // Added to correct quick step
        proxySpecs["fieldOfView"]["alongTrackFieldOfView"] = sensor_AT_fov; //Call instrument module with new along track FOV to get cone and clock angles

        if(sensor_AT_fov > crossTrackFOV_deg)
        {
            proxySpecs["fieldOfView"]["crossTrackFieldOfView"] = sensor_AT_fov;
        }


        //Debugging
        cout << "+- Full Cross Track: " << proxySpecs["fieldOfView"]["crossTrackFieldOfView"].asString() << endl;
        cout << "+- Full Along Track: " << proxySpecs["fieldOfView"]["alongTrackFieldOfView"].asString() << endl;



        proxy.SetSize(8);
        proxySpecsConverted = getInstrumentSpecs(proxySpecs);
        proxy[0]            = proxySpecsConverted["fieldOfView"]["coneAnglesVector"][0].asDouble() * RAD_PER_DEG;
        proxy[1]            = proxySpecsConverted["fieldOfView"]["coneAnglesVector"][1].asDouble() * RAD_PER_DEG;
        proxy[2]            = proxySpecsConverted["fieldOfView"]["coneAnglesVector"][2].asDouble() * RAD_PER_DEG;
        proxy[3]            = proxySpecsConverted["fieldOfView"]["coneAnglesVector"][3].asDouble() * RAD_PER_DEG;
        proxy[4]            = proxySpecsConverted["fieldOfView"]["clockAnglesVector"][0].asDouble() * RAD_PER_DEG;
        proxy[5]            = proxySpecsConverted["fieldOfView"]["clockAnglesVector"][1].asDouble() * RAD_PER_DEG;
        proxy[6]            = proxySpecsConverted["fieldOfView"]["clockAnglesVector"][2].asDouble() * RAD_PER_DEG;
        proxy[7]            = proxySpecsConverted["fieldOfView"]["clockAnglesVector"][3].asDouble() * RAD_PER_DEG;




        return proxy;
    }
}


Real InstrumentCoverage::get_atfov_dim(Real AT_FP_len)
{
    Real AT_fov_deg;
    Real f;
    Real eca;

    f          = RE / semiMajorAxis;
    eca        = (AT_FP_len/ RE);
    AT_fov_deg = 2.0 * atan(  f*sin(eca/2.0)  /  (1.0 - f*cos(eca/2.0))  )  * DEG_PER_RAD;

    return AT_fov_deg;
}
// ------------------- Proxy Sensor Functions -------------------





//Takes a value in degrees and returns the sin
Real InstrumentCoverage::sind(Real val)
{
    Real   answer = sin(val*RAD_PER_DEG);
    return answer;
}

//Takes a value in degrees and returns the cos
Real InstrumentCoverage::cosd(Real val)
{
    Real   answer = cos(val*RAD_PER_DEG);
    return answer;
}

//Takes a value in the range [-1,1], returns a degree in range [-90,90]
Real InstrumentCoverage::asind(Real val)
{
    Real   answer = asin(val) * DEG_PER_RAD;
    return answer;
}

//Takes a value in the range [-1,1], returns a degree in range [0,180]
Real InstrumentCoverage::acosd(Real val)
{
    Real   answer = acos(val) * DEG_PER_RAD;
    return answer;
}






//Returns vector --> first 3 = euler angles --> last 3 = euler sequences
Rvector InstrumentCoverage::getEulerParameters()
{
    Rvector eulerParameters;
    eulerParameters.SetSize(6);

    eulerParameters[0] = eulerAngle1;
    eulerParameters[1] = eulerAngle2;
    eulerParameters[2] = eulerAngle3;
    eulerParameters[3] = eulerSeq1;
    eulerParameters[4] = eulerSeq2;
    eulerParameters[5] = eulerSeq3;

    return eulerParameters;
}

//Returns vector --> first 4 = cone angles --> last 4 = clock sequences
Rvector InstrumentCoverage::getSensorAngles()
{
    Rvector angles;
    if(sensorType == "CONICAL")
    {
        angles.SetSize(1);
        angles[0] = coneAngles[0];
    }
    else
    {
        //This will change when we move to the OC rectangular sensor class
        angles.SetSize(8);
        angles[0] = coneAngles[0];
        angles[1] = coneAngles[1];
        angles[2] = coneAngles[2];
        angles[3] = coneAngles[3];
        angles[4] = clockAngles[0];
        angles[5] = clockAngles[1];
        angles[6] = clockAngles[2];
        angles[7] = clockAngles[3];
    }

    return angles;
}

Integer InstrumentCoverage::findNyqTimestep(double SMA)
{
    Real orbP, groundVel;
    Integer tStep;

    orbP      = 2*PI*sqrt(pow( SMA * 1e3, 3) / GM ); //in seconds
    groundVel = 2*PI*RE/orbP; // km per second Vinay: Need to change for elliptical orbits
    tStep     = floor(gridSize*RAD_PER_DEG*RE/groundVel); // Vinay: Why use floor function? Is the minimum step time strictly 1 sec?
    if (tStep == 0)
    {
        tStep = 1;
    }

    return tStep;
}

Json::Value InstrumentCoverage::getInstrumentSpecs(Json::Value payload)
{

    //Turn the payload into a string
    Json::StyledWriter    writer;
    Json::Value           root;
    Json::Reader          reader;
    std::array<char, 128> buffer;  //Holds returned data from Instrument Module
    string                toWrite;
    string                path;
    string                instCall;
    string                command;
    string                result;
    bool                  parsingSuccessful;


    toWrite  = writer.write(payload);
    path     = getInstrumentModulePath();
    instCall = "python3 " + path;
    boost::replace_all(toWrite, "\"", "\\\"");
    toWrite  = "\"" + toWrite + "\"";
    command  = instCall + " " + toWrite;
    FILE* in = popen(command.c_str(), "r");

    while (fgets(buffer.data(), 128, in) != NULL)
    {
        result += buffer.data();
    }

    pclose(in);

    //Parse string from instrument module into Json::Value object
    parsingSuccessful = reader.parse( result, root );
    if ( !parsingSuccessful )
    {
        cout << "Error parsing the string" << endl;
    }

    //Return the json object
    return root;
}



string InstrumentCoverage::getInstrumentModulePath()
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

    path = path + "/modules/instrument/bin/InstruPy_get_coverage_specs.py";

    return path;
}



bool InstrumentCoverage::isRectangular()
{
    if(sensorType == "CONICAL"){return false;}
    else{return true;}
}



void InstrumentCoverage::writeJson(Json::Value instrumentToWrite, string writeFiles, int satelliteNum)
{
    string outputPath = writeFiles + "/sat" + to_string(satelliteNum) + "_accessInfo.json";
    Json::StyledWriter styledWriter;

    ofstream instrumentJson;
    instrumentJson.open(outputPath);

    instrumentJson << styledWriter.write(instrumentToWrite);
    instrumentJson.close();

}

























