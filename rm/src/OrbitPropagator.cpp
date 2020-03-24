/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/*
 * File:   OrbitPropagator.cpp
 * Author: gabeapaza
 *
 * Created on October 23, 2018, 1:48 PM
 */


//Header
#include "OrbitPropagator.hpp"


using namespace std;
using namespace GmatMathConstants; //contains RAD_PER_DEG


OrbitPropagator::OrbitPropagator(Json::Value ms,
                                 Json::Value sat,
                                 PointGroup *  poiGroup,
                                 PointGroup *  gsGroup,
                                 string      path_cache,
                                 string      path_writeFiles,
                                 double      gs,
                                 int         satNum,
                                 int         constNum,
                                 int         total_sat_number,
                                 bool        printOutput)
{

    //Initialize member variables
    total_sat_num       = total_sat_number;
    satelliteNum        = satNum;
    constellationNum    = constNum;
    writeFiles          = path_writeFiles;
    tsr                 = ms;
    satellite           = sat;
    gridSize            = gs;
    startDate           = 0;
    metricsInterpTime   = 0;
    propulse            = tsr["settings"]["includePropulsion"].asBool();
    missionStart        = tsr["mission"]["start"].asString();
    missionDuration     = tsr["mission"]["duration"].asString();
    path_cacheDirectory = path_cache;
    sat_in_cache        = false;
    use_cache           = true;
    outputStates        = true;
    outputInstrument    = true;
    print_output        = printOutput;

    if(tsr["settings"]["outputs"].isMember("orbits.states"))
    {
        outputStates = tsr["settings"]["outputs"]["orbits.states"].asBool();
    }
    if(tsr["settings"]["outputs"].isMember("orbits.instrumentAccess"))
    {
        outputInstrument = tsr["settings"]["outputs"]["orbits.instrumentAccess"].asBool();
    }


    coneIP.SetSize(4);
    clockIP.SetSize(4);


    pointsOfInterest    = new PointGroup();
    (*pointsOfInterest) = (*poiGroup);

    gsOfInterest        = new PointGroup();
    (*gsOfInterest)     = (*gsGroup);

    cache = new CacheInterface(path_cacheDirectory);
}

OrbitPropagator::OrbitPropagator(const OrbitPropagator& orig)
{

}

OrbitPropagator::~OrbitPropagator()
{
    delete orbitParams;
    delete coverage;
    delete cache;
    delete pointsOfInterest;
    delete gsOfInterest;
}

//Sets satellite cache directory name
void OrbitPropagator::setOrbitalParameters()
{
    orbitParams                = new OrbitalParameters(satellite);
    vector<Real> fn_params     = orbitParams->getKeplarianElements();


    satellite_file_name = to_string(fn_params[0]) + "_" +
                                 to_string(fn_params[1]) + "_" +
                                 to_string(fn_params[2]) + "_" +
                                 to_string(fn_params[3]) + "_" +
                                 to_string(fn_params[4]) + "_" +
                                 to_string(fn_params[5]) + "_SAT";
    satellite_directory_path = path_cacheDirectory + "/" + satellite_file_name;

    sat_in_cache = cache->DoesDirectoryExist(satellite_directory_path);

    cache_accessFile_POI = satellite_directory_path + "/sat_accessInfo.csv";
    cache_accessFile_GS  = satellite_directory_path + "/sat_accessInfo_GS.csv";
    cache_obsPath        = satellite_directory_path + "/obs.csv";
    link_obsPath         = writeFiles               + "/obs_" + to_string(total_sat_num) + ".csv";
    cache_satAccessJSON  = satellite_directory_path + "/sat_accessInfo.json";
    link_satAccessJSON   = writeFiles               + "/sat" + to_string(total_sat_num) + "_accessInfo.json";
    cache_satAccessCSV   = satellite_directory_path + "/sat_accessInfo.csv";
    link_satAccessCSV    = writeFiles               + "/sat" + to_string(total_sat_num) + "_accessInfo.csv";
    cache_POI            = path_cacheDirectory      + "/poi.csv";
    link_POI             = writeFiles               + "/poi.csv";
    cache_recordFile     = satellite_directory_path + "/record.json";



}

void OrbitPropagator::setInstrumentCoverage()
{
    Json::Value covJson = satellite["payload"][0];
    coverage = new InstrumentCoverage(covJson, gridSize, orbitParams->getSMA());
    if(outputInstrument)
    {
        coverage->writeJson(covJson, writeFiles, total_sat_num);
    }
}


/*
 * Purpose: Propagate an orbit for a single set of starting ephemeris data - get access data for points of interest and ground stations
 * Produces: IntervalEventReports with access data for different coverages
 */
bool OrbitPropagator::propagateOrbit()
{


    // Check if the satellite is in the Cache
    if(sat_in_cache)
    {
        if(print_output)
        {
            cout << "-- Sat: " << (total_sat_num + 1) << " found in cache!!" << endl;
        }
        if(outputStates)
        {
            cache->CreateHardLink(cache_obsPath, link_obsPath);
        }
        if(outputInstrument)
        {
            cache->CreateHardLink(cache_satAccessCSV, link_satAccessCSV);
        }

        if(use_cache)
        {
            metricsInterpTime = cache->GetSatRecordAttribute(satellite_directory_path, "interp-timestep");
            missionEpoch      = cache->GetSatRecordAttribute(satellite_directory_path, "missionEpoch");
            coverageEvents    = cache->GetPoiReports(satellite_directory_path);
            gsEvents          = cache->GetGsReports(satellite_directory_path);
            return true;
        }
    }
    else
    {
        // Create a directory for the satellite in the cache system
        cache->CreateSatelliteEntry(satellite_directory_path, satellite_file_name);
    }




    // --------------- Propagation Steps ---------------
    //1. Quick Search
    //2. Correction Step --If fov is small


    // --------------- Propagation Recipe ---------------
    //1. Create one date object (orbitDate) using two separate date objects
    //2. Create one Orbit State object, all of the coverages will use this one object
    //3. Make a Spacecraft Object for each coverage in this Orb, using the one date created, the Orbit State, and then add sensors
    //4. Create all the coverage checkers for the Area of Interest and Ground Networks
    //5. Create a propagator using only one of the spacecraft -- propagate the orbit
    //6. Calculate coverage metrics based on the Coverage Checkers
    //7. Check to see if correction step is needed. If yes, do correction step
    //8. Delete dynamically allocated memory


    // ----- 0.1 -----
    Earth* earth = new Earth();
    // ----- 0.1 -----


    // ----- 1 -----
    vector<Integer> dateParams;
    Real            seconds;

    AbsoluteDate* dateConverter = new AbsoluteDate();

    //These hold the mission epoch
    AbsoluteDate* orbitDate     = new AbsoluteDate();
    AbsoluteDate* orbitDateGS   = new AbsoluteDate();

    //These hold the satellite epoch
    AbsoluteDate* satelliteDate     = new AbsoluteDate();
    AbsoluteDate* satelliteDateGS   = new AbsoluteDate();


    // Set the mission epoch
    dateParams  = parseDate(missionStart);
    seconds     = dateParams[5];
    dateConverter->SetGregorianDate(dateParams[0],dateParams[1],dateParams[2],dateParams[3],dateParams[4],seconds);
    missionEpoch = dateConverter->GetJulianDate();

    // Parse satellite epoch,
    dateParams  = parseDate(orbitParams->orbitEpoch);
    seconds     = dateParams[5];
    dateConverter->SetGregorianDate(dateParams[0],dateParams[1],dateParams[2],dateParams[3],dateParams[4],seconds);
    satelliteEpoch = dateConverter->GetJulianDate();



    //Mission absolute date
    orbitDate->SetJulianDate(missionEpoch);
    orbitDateGS->SetJulianDate(missionEpoch);

    //Satellite absolute date
    satelliteDate->SetJulianDate(satelliteEpoch);
    satelliteDateGS->SetJulianDate(satelliteEpoch);

    missionDays = parseDuration(missionDuration);

    // ----- 1 -----






    // ----- 2 -----
    vector<Real> ephemerisData;

    OrbitState* state   = new OrbitState();
    OrbitState* stateGS = new OrbitState();

    ephemerisData = orbitParams->getKeplarianElements();

    state->SetKeplerianState(ephemerisData[0],ephemerisData[1],
                             ephemerisData[2],ephemerisData[3],
                             ephemerisData[4],ephemerisData[5]);
    stateGS->SetKeplerianState(ephemerisData[0],ephemerisData[1],
                             ephemerisData[2],ephemerisData[3],
                             ephemerisData[4],ephemerisData[5]);
    // ----- 2 -----





    // ----- 3 -----    Create Spacecraft
    bool runCorrections = true;
    Real    tInp_minreq;
    Real    tInpQ_OCmin = 1;
    Real    tPropQ;         //Propagation step-size in Quick-Search step
    Real    tInpQ;          //Interpolation step-size in Quick-Search step
    Real    tPropC;   //Propagation step-size in Correction step
    Real    tInpC = 0.001;  //Interpolation step-size in Correction step
    Rvector instSpecs;
    Rvector eulerParams;


    LagrangeInterpolator*  interp     = new LagrangeInterpolator("TATCLagrangeInterpolator", 6, 7);
    LagrangeInterpolator*  interpGS   = new LagrangeInterpolator("TATCLagrangeInterpolator", 6, 7);
    NadirPointingAttitude* attitude   = new NadirPointingAttitude();
    NadirPointingAttitude* attitudeGS = new NadirPointingAttitude();
    Spacecraft*            sat        = new Spacecraft(satelliteDate,state,attitude,interp);
    Spacecraft*            satGS      = new Spacecraft(satelliteDateGS,stateGS,attitudeGS,interpGS);
    CustomSensor*          rectangular;
    ConicalSensor*         conical;



    //If we don't have propulsion we need to account for drag ---> currently we have not drag coefficient, so we don't account for drag
    //if(!propulse)
    //{
        //sat->SetDragArea(pow(pow(orbitParams->volume,1/3),2));
        //sat->SetDragCoefficient(orbitParams->dragCoeff);        //Ask vinay where the drag coefficiend is in the file
        //sat->SetTotalMass(orbitParams->mass);
    //}



    eulerParams = coverage->getEulerParameters();
    tPropQ      = coverage->findPropagationStep();  //(100 steps per-orbit)
    tInp_minreq = coverage->findInterpolationStep();



    if(tInp_minreq < tInpQ_OCmin){
        instSpecs      = coverage->findProxySensor(tInpQ_OCmin); //Calculate proxy sensor based on minimum interpolation time-step
        cout         << "------------------------------" << endl << endl;
        tInpQ          = 1.0;
        runCorrections = true;
    }
    else{
        instSpecs      = coverage->getSensorAngles();
        tInpQ          = tInp_minreq;
        runCorrections = false;
    }



    bool isRectangular = coverage->isRectangular();
    if(isRectangular) // ------ Rectangular ------
    {
        coneIP[0]  = (Real) instSpecs[0];
        coneIP[1]  = (Real) instSpecs[1];
        coneIP[2]  = (Real) instSpecs[2];
        coneIP[3]  = (Real) instSpecs[3];
        clockIP[0] = (Real) instSpecs[4];
        clockIP[1] = (Real) instSpecs[5];
        clockIP[2] = (Real) instSpecs[6];
        clockIP[3] = (Real) instSpecs[7];

        rectangular = new CustomSensor(coneIP,clockIP);
        rectangular->SetSensorBodyOffsetAngles(eulerParams[0], eulerParams[1], eulerParams[2], eulerParams[3], eulerParams[4], eulerParams[5]);
        sat->AddSensor(rectangular);
    }
    else             // ----- Conical -----
    {
        conical = new ConicalSensor(instSpecs[0]);
        conical->SetSensorBodyOffsetAngles(eulerParams[0], eulerParams[1], eulerParams[2], eulerParams[3], eulerParams[4], eulerParams[5]);
        sat->AddSensor(conical);
    }

    // ----- 3 -----




    // ----- 4 -----
    CoverageChecker* poiChecker = new CoverageChecker(pointsOfInterest, sat);
    CoverageChecker* gsChecker  = new CoverageChecker(gsOfInterest, satGS);

    poiChecker->SetComputePOIGeometryData(true);
    gsChecker->SetComputePOIGeometryData(true);
    // ----- 4 -----






    // ----- 5 -----
    vector<string>     obsHeader;
    ofstream           obsfile;
    Propagator* prop   = new Propagator(sat);
    Propagator* propGS = new Propagator(satGS);

    if(!propulse)
    {
        //prop->SetApplyDrag(true);
    }

    if(outputStates)
    {
        obsHeader.push_back("Time[s]");
        obsHeader.push_back("Ecc[deg]");
        obsHeader.push_back("Inc[deg]");
        obsHeader.push_back("SMA[km]");
        obsHeader.push_back("AOP[deg]");
        obsHeader.push_back("RAAN[deg]");
        obsHeader.push_back("MA[deg]");
        obsHeader.push_back("Lat[deg]");
        obsHeader.push_back("Lon[deg]");
        obsHeader.push_back("Alt[km]");
        obsHeader.push_back("x[km]");
        obsHeader.push_back("y[km]");
        obsHeader.push_back("z[km]");
        obsHeader.push_back("vx[km/s]");
        obsHeader.push_back("vy[km/s]");
        obsHeader.push_back("vz[km/s]");
        obsfile.open(cache_obsPath.c_str(),ios::binary | ios::out);        //    /...../cache/SMA_ECC_INCLINATION_RAAN_PER_TRUEA_SAT/obs.csv
        for (Integer header = 0; header < obsHeader.size() - 1; header++)
        {
            obsfile << obsHeader[header] << ",";
        }
        obsfile << obsHeader[obsHeader.size()-1] << endl;
    }


    startDate       = orbitDate->GetJulianDate();
    Real interpTime = startDate;
    Real midRange   = 0.0;
    Real propTime   = orbitDate->GetJulianDate();
    Real simSecs    = 0.0;
    int  propStep   = 0;
    int  interpStep = 0;


    //Propagate to the satellite orbit epoch
    prop->Propagate(*satelliteDate);
    propGS->Propagate(*satelliteDateGS);

    //Propagate to the mission epoch
    prop->Propagate(*orbitDate);
    propGS->Propagate(*orbitDateGS);



    //------ Manually Set Propagation Parameters ------
    //tPropQ = 30;
    //tInpQ = 0.6;
    //missionDays = 0.1;
    //-------------------------------------------------



    //Debugging
    cout << endl << "----- Propagation Parameters -----" << endl;
    cout << "+--- Ephemeris Data: SMA(" << ephemerisData[0] <<
         ") | Ecc(" << ephemerisData[1] <<
         ") | Incl(" << ephemerisData[2] <<
         ") | RAAN(" << ephemerisData[3] <<
         ") | Per(" << ephemerisData[4] <<
         ") | TrueA(" << ephemerisData[5] <<
         ")" << endl;
    cout << "+-------------- GridSize: " << gridSize << endl;
    cout << "+--------- Number Points: " << pointsOfInterest->GetNumPoints() << endl;
    cout << "+---------- Mission Days: " << missionDays << endl;
    cout << "+------------ Start Date: " << orbitDate->GetJulianDate() << endl;
    cout << "+------- Interp Timestep: " << tInpQ << endl;
    cout << "+-- Calc Interp Timestep: " << tInp_minreq << endl;
    cout << "+--------  Prop Timestep: " << tPropQ << endl;
    cout << "----------------------------------" << endl;
    Real tenPD  = (Real) missionDays * 0.1;Real bZero  = startDate;Real bOne   = startDate + (tenPD*1.0);Real bTwo   = startDate + (tenPD*2.0);Real bThree = startDate + (tenPD*3.0);Real bFour  = startDate + (tenPD*4.0);Real bFive  = startDate + (tenPD*5.0);Real bSix   = startDate + (tenPD*6.0);Real bSeven = startDate + (tenPD*7.0);Real bEight = startDate + (tenPD*8.0);Real bNine  = startDate + (tenPD*9.0);bool p1 = false; bool p2 = false; bool p3 = false;bool p4 = false; bool p5 = false; bool p6 = false;bool p7 = false; bool p8 = false; bool p9 = false;

    //Debugging


    metricsInterpTime = tInpQ;


    cout << endl << "-- Propagating Sat: " << (satelliteNum + 1) << " Constellation: " << (constellationNum + 1) << " -- " << endl;
    while (orbitDate->GetJulianDate() < ((Real) startDate + missionDays)) //This loop continues as long as our current simulated date is before the end of the mission
    {
        orbitDate->Advance  (tPropQ);
        orbitDateGS->Advance(tPropQ);
        prop->Propagate     (*orbitDate); //first 3 elements (position) -- last 3 (velocity)
        propGS->Propagate   (*orbitDateGS);

        propTime =  orbitDate->GetJulianDate();
        simSecs  = (orbitDate->GetJulianDate()-(Real)startDate)*24*60*60; // mission time elapsed (sec)

        if(sat->TimeToInterpolate(propTime, midRange))
        {
            while(interpTime < (propTime - midRange)) //Loop until our interpolation time equals our propagated time
            {
                IntegerArray accessPoints   = poiChecker->AccumulateCoverageData(interpTime);
                IntegerArray accessPointsGS = gsChecker->AccumulateCoverageData(interpTime);
                interpTime                 += (tInpQ / GmatTimeConstants::SECS_PER_DAY);
                interpStep++;
            }
        }


        //Write to the obs.csv file
        Real     jDate = sat->GetJulianDate();
        Rvector6 cartState = sat->GetCartesianState();
        Rvector3 inertialPosVec(cartState(0), cartState(1), cartState(2));
        Rvector3 latLonHeight = earth->InertialToBodyFixed(inertialPosVec,jDate,"Ellipsoid");
        Rvector6 keplState = state->GetKeplerianState();

        if(obsfile.is_open() and outputStates)
        {
            //Num seconds since propagation started
            obsfile << floor(simSecs) << ",";
            obsfile << keplState[1] << ",";                //ecc
            obsfile << keplState[2]*DEG_PER_RAD << ",";    //inc
            obsfile << keplState[0] << ",";                //sma
            obsfile << keplState[4]*DEG_PER_RAD << ",";    //aop
            obsfile << keplState[3]*DEG_PER_RAD << ",";    //raan
            obsfile << keplState[5]*DEG_PER_RAD << ",";    //ma
            obsfile << latLonHeight[0]*DEG_PER_RAD << ","; //lat
            obsfile << latLonHeight[1]*DEG_PER_RAD << ","; //lon
            obsfile << latLonHeight[2] << ",";             //alt
            obsfile << cartState[0] << ",";                //x
            obsfile << cartState[1] << ",";                //y
            obsfile << cartState[2] << ",";                //z
            obsfile << cartState[3] << ",";                //vx
            obsfile << cartState[4] << ",";                //vy
            obsfile << cartState[5] << endl;               //vz

        }
        else if(outputStates)
        {
            cout << "Unable to write to Obs.csv file" << endl;
        }

        //Output percentage completed
        if(print_output)
        {
            if(propTime > bOne and !p1)   {cout << "-- 10% --" << endl; p1 = true;}
            if(propTime > bTwo and !p2)   {cout << "-- 20% --" << endl; p2 = true;}
            if(propTime > bThree and !p3) {cout << "-- 30% --" << endl; p3 = true;}
            if(propTime > bFour and !p4)  {cout << "-- 40% --" << endl; p4 = true;}
            if(propTime > bFive and !p5)  {cout << "-- 50% --" << endl; p5 = true;}
            if(propTime > bSix and !p6)   {cout << "-- 60% --" << endl; p6 = true;}
            if(propTime > bSeven and !p7) {cout << "-- 70% --" << endl; p7 = true;}
            if(propTime > bEight and !p8) {cout << "-- 80% --" << endl; p8 = true;}
            if(propTime > bNine and !p9)  {cout << "-- 90% --" << endl; p9 = true;}
        }


        propStep++;
    } // -----> Now we are out of the propagation loop

    if(print_output)
    {
        cout << "-- 100% --" << endl;
    }


    if(outputStates)
    {
        obsfile.close();
    }



    //Bounds for interpolation percentage completed
    propTime = orbitDate->GetJulianDate();
    tenPD    = (propTime - interpTime) * 0.1;
    bZero    = interpTime;
    bOne     = interpTime + (tenPD*1.0);
    bTwo     = interpTime + (tenPD*2.0);
    bThree   = interpTime + (tenPD*3.0);
    bFour    = interpTime + (tenPD*4.0);
    bFive    = interpTime + (tenPD*5.0);
    bSix     = interpTime + (tenPD*6.0);
    bSeven   = interpTime + (tenPD*7.0);
    bEight   = interpTime + (tenPD*8.0);
    bNine    = interpTime + (tenPD*9.0);

    //Interpolate to End

    if(print_output)
    {
        cout << "-- Finishing Interpolation --" << endl;
    }


    while (interpTime <= propTime)
    {
        IntegerArray accessPoints   = poiChecker->AccumulateCoverageData(interpTime);
        IntegerArray accessPointsGS = gsChecker->AccumulateCoverageData(interpTime);
        interpTime                 += (tInpQ / GmatTimeConstants::SECS_PER_DAY);

        //Output percentage completed
        if(print_output)
        {
            if(interpTime > bOne and p1)    {cout << "-- 10% --" << endl; p1 = false;}
            if(interpTime > bTwo and p2)    {cout << "-- 20% --" << endl; p2 = false;}
            if(interpTime > bThree and p3)  {cout << "-- 30% --" << endl; p3 = false;}
            if(interpTime > bFour and p4)   {cout << "-- 40% --" << endl; p4 = false;}
            if(interpTime > bFive and p5)   {cout << "-- 50% --" << endl; p5 = false;}
            if(interpTime > bSix and p6)    {cout << "-- 60% --" << endl; p6 = false;}
            if(interpTime > bSeven and p7)  {cout << "-- 70% --" << endl; p7 = false;}
            if(interpTime > bEight and p8)  {cout << "-- 80% --" << endl; p8 = false;}
            if(interpTime > bNine and p9)   {cout << "-- 90% --" << endl; p9 = false;}
        }

    }

    if(print_output)
    {
        cout << "-- 100% --" << endl;
    }


    // ----- 5 -----






    // ----- 6 -----
    bool gsSeen  = false;
    bool poiSeen = false;

    gsEvents.clear();
    coverageEvents.clear();

    gsEvents       = gsChecker->ProcessCoverageData();
    coverageEvents = poiChecker->ProcessCoverageData();

    if(!gsEvents.empty())      {gsSeen = true;}
    if(!coverageEvents.empty()){poiSeen = true;}


    //Debugging
    cout << endl << "-------> Propagation Events <-------" << endl;
    cout << "+----- GS Events: " << gsEvents.size() << endl;
    cout << "+---- POI Events: " << coverageEvents.size() << endl;
    cout << "------------------------------------" << endl << endl;
    // ----- 6 -----








    // ----- 7 -----
    int                         numSuccess = 0;
    int                         numFail = 0;
    if(runCorrections)
    {
        vector<IntervalEventReport> allPoiReports;
        vector<IntervalEventReport> tempReports;
        IntervalEventReport         currEvent;
        Real                        numEvents;
        Real                        tpEvents;
        int                         eventNum = 0;


        numEvents = coverageEvents.size();

        // Set the propagation and interoplation step for the correction step
        tpEvents  = numEvents * 0.1;
        tPropC    = tInpQ / 10.0;
        if( (tPropC/10.0) > tInp_minreq)
        {
            tInpC = tInp_minreq; //Propagation time-step for correct step needs to be the calculated one
        }
        else
        {
            tInpC = (tPropC/10.0);
        }
        cout << "--> tPropC: " << tPropC << endl;
        cout << "--> tInpC: "  << tInpC << endl;


        if(print_output)
        {
            cout << endl << "-- Running Corrections --" << endl;
        }


        vector<IntervalEventReport>::iterator report;
        for(report = coverageEvents.begin(); report != coverageEvents.end(); report++) //POI events
        {
            currEvent   = (*report);
            tempReports = intervalCorrection(missionEpoch, tPropC, tInpC, tInpQ, currEvent, eventNum, numEvents, numSuccess, numFail);

            if(tempReports.size() > 0)
            {
                allPoiReports.insert(allPoiReports.end(), tempReports.begin(), tempReports.end());
            }

            //Calculate Percentage Completed
            if(print_output)
            {
                if(eventNum > tpEvents and !p1){cout << "-- 10% --" << endl; p1 = true;}
                if(eventNum > (tpEvents*2) and !p2){cout << "-- 20% --" << endl; p2 = true;}
                if(eventNum > (tpEvents*3) and !p3){cout << "-- 30% --" << endl; p3 = true;}
                if(eventNum > (tpEvents*4) and !p4){cout << "-- 40% --" << endl; p4 = true;}
                if(eventNum > (tpEvents*5) and !p5){cout << "-- 50% --" << endl; p5 = true;}
                if(eventNum > (tpEvents*6) and !p6){cout << "-- 60% --" << endl; p6 = true;}
                if(eventNum > (tpEvents*7) and !p7){cout << "-- 70% --" << endl; p7 = true;}
                if(eventNum > (tpEvents*8) and !p8){cout << "-- 80% --" << endl; p8 = true;}
                if(eventNum > (tpEvents*9) and !p9){cout << "-- 90% --" << endl; p9 = true;}
            }

        }

        if(print_output){
            cout << "-- 100% --" << endl << endl;
        }

        coverageEvents = allPoiReports;


        //writeAccessIntervals(satellite_directory_path);
        cache->WritePoiAccessFile(satellite_directory_path, &coverageEvents, missionEpoch, missionDays);
        cache->WriteGsAccessFile(satellite_directory_path, &gsEvents);


        //Debugging
        cout << "+-- Successful Corrections: " << numSuccess << endl;
        cout << "+------ Failed Corrections: " << numFail << endl << endl;
    }
    else
    {
        //writeAccessIntervals(satellite_directory_path); //Write satellite access intervals
        cache->WritePoiAccessFile(satellite_directory_path, &coverageEvents, missionEpoch, missionDays);
        cache->WriteGsAccessFile(satellite_directory_path, &gsEvents);
    }
    // ----- 7 -----







    if(outputStates)
    {
        cache->CreateHardLink(cache_obsPath, link_obsPath);
    }
    if(outputInstrument)
    {
        cache->CreateHardLink(cache_satAccessCSV, link_satAccessCSV);
    }



    // ---------- Here we are going to write the record file containing all the information on the satellite's propagation parameters ----------
    Json::Value        recordObj;
    Json::StyledWriter styledWriter;
    ofstream           outputRecord;


    if(runCorrections)
    {
        recordObj["propagationParameters"]["smallFOV"]["prop-timestep"]   = tPropC;
        recordObj["propagationParameters"]["smallFOV"]["interp-timestep"] = tInpC;
        recordObj["propagationParameters"]["smallFOV"]["numSuccess"]      = numSuccess;
        recordObj["propagationParameters"]["smallFOV"]["numFail"]         = numFail;
    }
    else
    {
        recordObj["propagationParameters"]["smallFOV"]    = runCorrections;
    }

    recordObj["propagationParameters"]["interp-timestep"] = tInpQ;
    recordObj["propagationParameters"]["prop-timestep"]   = tPropQ;
    recordObj["propagationParameters"]["gridSize"]        = gridSize;
    recordObj["propagationParameters"]["numPOIs"]         = pointsOfInterest->GetNumPoints();
    recordObj["propagationParameters"]["missionDays"]     = missionDays;
    recordObj["propagationParameters"]["missionEpoch"]    = missionEpoch;

    outputRecord.open(cache_recordFile);
    outputRecord << styledWriter.write(recordObj);
    outputRecord.close();
    // -----------------------------------------------------------------------------------------------------------------------------------------



    // ----- 8 -----
    if(isRectangular){ delete rectangular;}
    else{              delete conical;}
    delete sat;        delete satGS;
    delete poiChecker; delete gsChecker;
    delete prop;       delete propGS;
    delete orbitDate;  delete orbitDateGS;
    delete dateConverter;
    delete earth;

    return true;
    // ----- 8 -----
}




vector<IntervalEventReport> OrbitPropagator::intervalCorrection(Real missionEpoch, Real tPropC, Real tInpC, Real tInpQ, IntervalEventReport currEvent, int& eventNum, int totalEvents, int& numSuccess, int& numFail)
{
    //We are going to pass the IntervalEventReport only and gather the data in this function

    Real jd = currEvent.GetStartDate().GetJulianDate(); //This is the start date of the event

    Real poiIndex = currEvent.GetPOIIndex(); //The point that we are propagating over



    Real lat;
    Real lon;

    pointsOfInterest->GetLatAndLon(poiIndex, lat, lon); //In radians

    Real eventDuration  = (currEvent.GetEndDate().GetJulianDate() - currEvent.GetStartDate().GetJulianDate()); //Days

    if(poiIndex == 277)
    {
        cout << "Event Duration for Point 277: " << to_string(eventDuration * 86400.0) << endl;
    }



    if( (Real) eventDuration * GmatTimeConstants::SECS_PER_DAY < 0.0000001 ) //If the true event duration is less than tInpQ, it will be 0. Therefore we will set the event duration to tInpQ!!
    {
        //cout << " -event duration reset- ";
        eventDuration = tInpQ / GmatTimeConstants::SECS_PER_DAY;
    }


    //Here we push back the beginning of the event by 25% of the event duration. We will also increase the event duration by 50%
    jd            = jd - (eventDuration * .25);
    eventDuration = eventDuration * 1.5;





    //Now we will get the satellite cartesian state at the start of the event
    vector<VisiblePOIReport> discreteEvents = currEvent.GetPOIEvents();
    VisiblePOIReport eventZero = discreteEvents[0];
    Rvector6 satCartState(eventZero.GetObsPosInertial()[0],
                          eventZero.GetObsPosInertial()[1],
                          eventZero.GetObsPosInertial()[2],
                          eventZero.GetObsVelInertial()[0],
                          eventZero.GetObsVelInertial()[1],
                          eventZero.GetObsVelInertial()[2]);



    //  --- Manually set correct step propagation parameters ---
//    eventDuration = 0.00004629606;// days
//    jd = 2.45743e+06;             // days
//    lat = 0.0; lon = 0.488692;    // radians
//    satCartState[0] = -2743.28; satCartState[1] = 6530.19; satCartState[2] = 0;
//    satCartState[3] = 3.0308; satCartState[4] = -6.86221; satCartState[5] = 0;
//    tPropC = 0.1; tInpC = 0.0001; // seconds



    //Debugging
//    cout << endl << "---------- Interval Correction on Event " << eventNum << " of " << totalEvents << " ----------" << endl;
//    cout << "+------------ Duration: " << ((Real)eventDuration * 24.0 * 60.0 * 60.0) << endl;
//    cout << "+---------- Start Date: " << jd << endl;
//    cout << "+- Point lat/lon (deg): " << lat * DEG_PER_RAD << " " << lon * DEG_PER_RAD << endl;
//    cout << "+-------------- tPropC: " << tPropC << endl;
//    cout << "+--------------- tInpC: " << tInpC << endl;
//    cout << "+--------------- tInpQ: " << tInpQ << endl;
//    cout << "+----------- CartState: " << satCartState[0] << " | " << satCartState[1] << " | " << satCartState[2] << " | " << satCartState[3] << " | " << satCartState[4] << " | " << satCartState[5] << endl;





    AbsoluteDate             *date;
    OrbitState               *state;
    Spacecraft               *satCorrect;
    Propagator               *prop;
    PointGroup               *pGroup;
    Earth                    *earth;
    NadirPointingAttitude    *attitudeCorrect;
    LagrangeInterpolator     *interpCorrect;
    CoverageChecker          *covChecker;
    CustomSensor             *rectangular;
    ConicalSensor            *conical;

    vector<IntervalEventReport> poiEvents;



    //Create the point group
    RealArray latArray;
    RealArray lonArray;

    latArray.push_back(lat); //Add 10 degrees for the mock latitude point
    lonArray.push_back(lon); //Add 10 degrees for the mock longitude point


    //POI index 0 is our real point and POI index 1 is our mock point
    pGroup = new PointGroup();
    pGroup->AddUserDefinedPoints(latArray,lonArray);


    // --------------- Propagation Steps ---------------
    //1. Create one date object (orbitDate) using two separate date objects
    //2. Create one Orbit State object, all of the coverages will use this one object
    //3. Make a Spacecraft Object for each coverage in this Orb, using the one date created, the Orbit State, and then add sensors
    //4. Create all the coverage checkers for the Area of Interest and Ground Networks
    //5. Create a propagator using only one of the spacecraft -- propagate the orbit
    //6. Calculate coverage metrics based on the Coverage Checkers
    //7. Delete dynamically allocated memory


    //1.
    date = new AbsoluteDate();
    date->SetJulianDate(jd);



    //2.
    state = new OrbitState();
    state->SetCartesianState(satCartState);



    //3.
    attitudeCorrect     = new NadirPointingAttitude();
    interpCorrect       = new LagrangeInterpolator("TATCLagrangeInterpolator", 6, 7);
    satCorrect          = new Spacecraft(date, state, attitudeCorrect, interpCorrect);
    Rvector instSpecs   = coverage->getSensorAngles(); //Use the regular sensor (not proxy)
    Rvector eulerParams = coverage->getEulerParameters();
    bool isRectangular  = coverage->isRectangular();

    if(isRectangular) // ----- Rectangular -----
    {
        Rvector coneIP;
        coneIP.SetSize(4);
        coneIP[0] = instSpecs[0];
        coneIP[1] = instSpecs[1];
        coneIP[2] = instSpecs[2];
        coneIP[3] = instSpecs[3];


        Rvector clockIP;
        clockIP.SetSize(4);
        clockIP[0] = instSpecs[4];
        clockIP[1] = instSpecs[5];
        clockIP[2] = instSpecs[6];
        clockIP[3] = instSpecs[7];

        //Debugging
//        cout << "+--------- Cone Angles: " << coneIP[0] << " | " << coneIP[1] << " | " << coneIP[2] << " | " << coneIP[3] << endl;
//        cout << "+-------- Clock Angles: " << clockIP[0] << " | " << clockIP[1] << " | " << clockIP[2] << " | " << clockIP[3] << endl;

        rectangular = new CustomSensor(coneIP,clockIP);
        rectangular->SetSensorBodyOffsetAngles(eulerParams[0], eulerParams[1], eulerParams[2], eulerParams[3], eulerParams[4], eulerParams[5]);
        satCorrect->AddSensor(rectangular);
    }
    else              // ----- Conical -----
    {
        //Debugging
//        cout << "+---------- Cone Angle: " << instSpecs[0]*DEG_PER_RAD << endl;

        conical = new ConicalSensor(instSpecs[0]);
        conical->SetSensorBodyOffsetAngles(eulerParams[0], eulerParams[1], eulerParams[2], eulerParams[3], eulerParams[4], eulerParams[5]);
        satCorrect->AddSensor(conical);
    }


    //4.
    covChecker = new CoverageChecker(pGroup, satCorrect);
    covChecker->SetComputePOIGeometryData(true);


    //5.
    prop                   = new Propagator(satCorrect);
    earth                  = new Earth();
    Real epoch             = date->GetJulianDate();
    Real interpCorrectTime = epoch;
    Real midRange          = 0.0;
    Real propTime          = date->GetJulianDate();


    prop->Propagate(*date);
    for(int x = 0; x < 6; x++)
    {
        date->Advance(0.000001);
        prop->Propagate(*date);
        IntegerArray accessPoints = covChecker->AccumulateCoverageData(); //The requested data is before the first data
    }


    int propCount   = 0;
    int interpCount = 0;
    while (date->GetJulianDate() < ((Real) (epoch + eventDuration)) )
    {
        date->Advance(tPropC);
        prop->Propagate(*date);
        propTime = date->GetJulianDate();

        // Interpolate when and if needed
        if (satCorrect->TimeToInterpolate(propTime, midRange))
        {
            while (interpCorrectTime < (propTime - midRange))
            {
                IntegerArray accessPoints = covChecker->AccumulateCoverageData(interpCorrectTime); //The requested data is before the first data
                interpCorrectTime += (tInpC / GmatTimeConstants::SECS_PER_DAY);
                interpCount++;
            }
        }
        propCount++;
    }

    //Interpolate to End
    propTime = date->GetJulianDate();
    while (interpCorrectTime <= propTime)
    {
        IntegerArray accessPoints = covChecker->AccumulateCoverageData(interpCorrectTime);
        interpCorrectTime += (tInpC / GmatTimeConstants::SECS_PER_DAY);
        interpCount++;
    }


    //6.
    poiEvents = covChecker->ProcessCoverageData();

    //Debugging
//    cout << "+---- Prop Interations: " << propCount << endl;
//    cout << "+-- Interp Interations: " << interpCount << endl;
//    cout << "+------ Num Sub-Events: " << poiEvents.size() << endl;




    //7.
    if(isRectangular){delete rectangular;}
    else             {delete conical;}
    delete                   satCorrect;
    delete                   covChecker;
    delete                   prop;
    delete                   pGroup;
    delete                   earth;


    if(poiEvents.size() == 0)
    {
        numFail++;
    }
    else
    {
        numSuccess++;

        //If we have an event with 0 duration, return an empty vector to not disturb the metrics
        if(poiEvents[0].GetEndDate().GetJulianDate() == poiEvents[0].GetStartDate().GetJulianDate())
        {
            //cout << "Zero Event!!!" << endl;
            poiEvents.clear();
            return poiEvents;
        }

    }



    //Set the correct POI index for each IntervalEventReport
    for(int x = 0; x < poiEvents.size(); x++)
    {
        poiEvents[x].SetPOIIndex(poiIndex);
    }

    eventNum++;
    return poiEvents;
}







// ------------------- Metrics Functions ------------------
vector<IntervalEventReport> OrbitPropagator::getGsEvents()
{
    return gsEvents;
}

vector<IntervalEventReport> OrbitPropagator::getCoverageEvents()
{
    return coverageEvents;
}

Real OrbitPropagator::getMissionStartDate()
{
    return startDate;
}

int OrbitPropagator::getNumPoints()
{
    return pointsOfInterest->GetNumPoints();
}

Real OrbitPropagator::getMissionDays()
{
    return missionDays;
}

int OrbitPropagator::getNumGS()
{
    int numGS = gsOfInterest->GetNumPoints();
    return numGS;
}

vector< pair< Real, Real > > OrbitPropagator::getCoordVec()
{
    vector< pair< Real, Real > > toReturn;
    Integer points = pointsOfInterest->GetNumPoints();
    toReturn.resize(points);

    double lat, lon;
    for(int x = 0; x < points; x++)
    {
        Rvector3 *vec = pointsOfInterest->GetPointPositionVector(x);
        lat = GmatMathUtil::ASin(vec->GetElement(2)/vec->GetMagnitude())*DEG_PER_RAD;
        lon = GmatMathUtil::ATan(vec->GetElement(1),vec->GetElement(0))*DEG_PER_RAD;
        pair<Real, Real> temp(lat, lon);
        toReturn[x] = temp;
    }



    return toReturn;
}



// ------------------- Testing Functions ------------------
void OrbitPropagator::printOrbitalParameters()
{
    orbitParams->printElements();
}



// ------------------- Message Handler Functions ------------------
bool OrbitPropagator::handleMessage(string memo)
{
    if(memo == "")
    {
        return true;
    }
    else if(memo == "abort")
    {
        abort();
        return false;
    }
    else if(memo == "pause")
    {
        pause();
        return true;
    }


    return true;
}

void OrbitPropagator::abort()
{

}

void OrbitPropagator::pause()
{
    bool onWait = true;
    string memo;

    while(onWait)
    {
        //Keep checking messages until the continue message is sent from the GUI
        memo = messages->checkMessages();
        if(memo == "continue")
        {
            onWait = false;
        }
    }

    return;
}



// ------------------- Date Parsing Functions ------------------
vector<Integer> OrbitPropagator::parseDate(string date)
{
    vector<Integer> toReturn;
    Integer year = stoi(date.substr(0,4));
    Integer month = stoi(date.substr(5,2));
    Integer day = stoi(date.substr(8,2));
    Integer hour = stoi(date.substr(11,2));
    Integer minute = stoi(date.substr(14,2));
    Integer second = stoi(date.substr(17,2));

    toReturn.push_back(year);
    toReturn.push_back(month);
    toReturn.push_back(day);
    toReturn.push_back(hour);
    toReturn.push_back(minute);
    toReturn.push_back(second);

    return toReturn;
}

Real OrbitPropagator::parseDuration(string dur)
{
    Real days = 0;

    string year;
    string month;
    string day;

    size_t pos_t;
    int pos;

    int strLength = dur.length();
    string parsed = dur.substr(1, (strLength-1) ); //Take out the first "P" in the duration field

    //Get the years
    pos_t = parsed.find("Y");
    pos = pos_t;
    year = parsed.substr(0, pos);
    parsed = parsed.substr( (pos+1) , (parsed.length() - (pos+1)) );


    //Get the months
    pos_t = parsed.find("M");
    pos = pos_t;
    month = parsed.substr(0, pos);
    parsed = parsed.substr( (pos+1) , (parsed.length() - (pos+1)) );




    //Get the days
    pos_t = parsed.find("D");
    pos = pos_t;
    day = parsed.substr(0, pos);


    int y = stoi(year);
    int m = stoi(month);
    int d = stoi(day);

    days = (y * 365) + (m * 30) + (d);

    return days;
}



// ------------------- Helper Functions ------------------
Real OrbitPropagator::shiftLongitude(Real lon)
{
    Real longitude = lon;

    if(longitude < 0)
    {
        longitude += 360;
    }

    if(longitude > 360)
    {
        longitude -= 360;
    }

    if(longitude == 360)
    {
        longitude = 0;
    }

    return longitude;
}

void OrbitPropagator::useCache(bool cacheValue)
{
    use_cache = cacheValue;
}

bool OrbitPropagator::does_directory_exist(string directoryPath)
{
    struct stat info;

    if ( stat( directoryPath.c_str(), &info ) != 0 )
    {
        return false;
    }
    else if(info.st_mode & S_IFDIR)
    {
        return true;
    }
    else
    {
        return false;
    }

}




// ------------------- Output Functions ------------------
void OrbitPropagator::writeAccessIntervals(string write_path)
{
    cout << "-- WRITING ACCESS INTERVALS --> " << write_path << endl;
    /*
     * When this function is called, we need to create the access interval files for both the ground stations and the points of interest
     *
     */

    string satAccessFileNameT       = write_path + "/sat_accessInfo.csv";
    string satAccessFileNameT_GS    = write_path + "/sat_accessInfo_GS.csv";

    ofstream satelliteStateFileT;
    ofstream satelliteStateFileT_GS;

    satelliteStateFileT.precision(20);
    satelliteStateFileT_GS.precision(20);

    satelliteStateFileT.open(satAccessFileNameT.c_str(),ios::binary | ios::out);
    satelliteStateFileT_GS.open(satAccessFileNameT_GS.c_str(),ios::binary | ios::out);


    //First 5 header lines for the sat_accessInfo.csv file
    string headerLineOneT   = "Satellite states are in Earth-Centered-Inertial equatorial plane.";
    string headerLineTwoT   = "Epoch[JDUT1] is " + to_string(missionEpoch);
    string headerLineThreeT = "All time is referenced to the Epoch.";
    string headerLineFourT  = "Mission Duration [Days] is " + to_string(missionDays);
    satelliteStateFileT << headerLineOneT   << "," << endl;
    satelliteStateFileT << headerLineTwoT   << "," << endl;
    satelliteStateFileT << headerLineThreeT << "," << endl;
    satelliteStateFileT << headerLineFourT  << "," << endl;
    satelliteStateFileT << "EventNum" << ",";
    satelliteStateFileT << "POI" << ",";
    satelliteStateFileT << "AccessFrom[Days]" << ",";
    satelliteStateFileT << "Duration[s]" << ",";
    satelliteStateFileT << "Time[Days]" << ",";
    satelliteStateFileT << "X[km]" << ",";
    satelliteStateFileT << "Y[km]" << ",";
    satelliteStateFileT << "Z[km]" << ",";
    satelliteStateFileT << "VX[km/s]" << ",";
    satelliteStateFileT << "VY[km/s]" << ",";
    satelliteStateFileT << "VZ[km/s]" << endl;


    //Create headers for sat_accessInfo_GS.csv file
    satelliteStateFileT_GS << "gsIndex"   << ",";
    satelliteStateFileT_GS << "startDate" << ",";
    satelliteStateFileT_GS << "endDate"   << endl;




    int eventID = 0;
    vector<IntervalEventReport>::iterator report;
    for(report = coverageEvents.begin(); report != coverageEvents.end(); report++) //Loop through all the reports for this propagation step
    {
        Integer poiNum = report->GetPOIIndex();

        Real accessFrom = (report->GetStartDate().GetJulianDate() - missionEpoch); //Days
        //Real accessFromSeconds = accessFrom * 24 * 60 * 60;

        Real eventDuration = ((report->GetEndDate().GetJulianDate()) - (report->GetStartDate().GetJulianDate())); //Days
        Real eventDurationSeconds = eventDuration * 24.0 * 60.0 * 60.0; //Seconds

        //Get all the VisiblePOIReports and determine the middle one
        vector<VisiblePOIReport> discreteEvents = report->GetPOIEvents();
        VisiblePOIReport ev = discreteEvents[int(discreteEvents.size()/2)];

        Real midJulianDate = ev.GetStartDate().GetJulianDate() - missionEpoch;

        satelliteStateFileT << eventID << ",";
        satelliteStateFileT << poiNum << ",";
        satelliteStateFileT << accessFrom << ",";
        satelliteStateFileT << (eventDurationSeconds) << ",";
        satelliteStateFileT << midJulianDate << ",";

        satelliteStateFileT << ev.GetObsPosInertial()[0] << ",";
        satelliteStateFileT << ev.GetObsPosInertial()[1] << ",";
        satelliteStateFileT << ev.GetObsPosInertial()[2] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[0] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[1] << ",";
        satelliteStateFileT << ev.GetObsVelInertial()[2] << endl;

        eventID++;
    }


    for(report = gsEvents.begin(); report != gsEvents.end(); report++)
    {
        Integer poiIndex = report->GetPOIIndex(); //This tells us which point of interest the report is referring to
        Real startDate   = report->GetStartDate().GetJulianDate();
        Real endDate     = report->GetEndDate().GetJulianDate();

        std::ostringstream tempStream1;
        std::ostringstream tempStream2;
        std::ostringstream tempStream3;

        tempStream1 << setprecision(20);
        tempStream2 << setprecision(20);
        tempStream3 << setprecision(20);

        tempStream1 << poiIndex;
        tempStream2 << startDate;
        tempStream3 << endDate;

        satelliteStateFileT_GS << tempStream1.str() << ",";
        satelliteStateFileT_GS << tempStream2.str() << ",";
        satelliteStateFileT_GS << tempStream3.str() << endl;
    }





}


bool OrbitPropagator::create_access_txt(string write_path_poi, string write_path_gs)
{
    ofstream cache_access_file_poi;
    cache_access_file_poi.open(write_path_poi.c_str(),ios::binary | ios::out);  // access.txt


    vector<IntervalEventReport>::iterator report;
    for(report = coverageEvents.begin(); report != coverageEvents.end(); report++) //Loop through all the reports for this propagation step
    {
        Integer poiIndex = report->GetPOIIndex(); //This tells us which point of interest the report is referring to
        Real startDate   = report->GetStartDate().GetJulianDate();
        Real endDate     = report->GetEndDate().GetJulianDate();

        std::ostringstream tempStream1;
        std::ostringstream tempStream2;
        std::ostringstream tempStream3;
        tempStream1 << setprecision(20);
        tempStream2 << setprecision(20);
        tempStream3 << setprecision(20);

        tempStream1 << poiIndex;
        tempStream2 << startDate;
        tempStream3 << endDate;

        cache_access_file_poi << tempStream1.str() << " ";
        cache_access_file_poi << tempStream2.str() << " ";
        cache_access_file_poi << tempStream3.str() << endl;
    }
    cache_access_file_poi.close();


    ofstream cache_access_file_gs;
    cache_access_file_gs.open(write_path_gs.c_str(),ios::binary | ios::out);  // access.txt

    for(report = gsEvents.begin(); report != gsEvents.end(); report++) //Loop through all the reports for this propagation step
    {
        Integer poiIndex = report->GetPOIIndex(); //This tells us which point of interest the report is referring to
        Real startDate   = report->GetStartDate().GetJulianDate();
        Real endDate     = report->GetEndDate().GetJulianDate();

        std::ostringstream tempStream1;
        std::ostringstream tempStream2;
        std::ostringstream tempStream3;
        tempStream1 << setprecision(20);
        tempStream2 << setprecision(20);
        tempStream3 << setprecision(20);

        tempStream1 << poiIndex;
        tempStream2 << startDate;
        tempStream3 << endDate;

        cache_access_file_gs << tempStream1.str() << " ";
        cache_access_file_gs << tempStream2.str() << " ";
        cache_access_file_gs << tempStream3.str() << endl;
    }
    cache_access_file_gs.close();

    return true;
}


Real OrbitPropagator::round(Real temp)
{
//    Real value = (int)(temp * 10 + .5);
//    return (Real)value / 10;
    return temp;
}
