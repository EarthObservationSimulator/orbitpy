//
// Created by Gabriel Apaza on 2019-02-07.
//

#include "Metrics.hpp"



#define SEC_TO_DAY 1.15741e-5
#define DAY_TO_SEC 86400



Metrics::Metrics(Json::Value ms, int points, Real startD, Integer gsNum, Real mD, string path_writeFiles, string path_cache, vector< pair< Real, Real > > pointCoordsVec)
{
    writeFiles  = path_writeFiles; // /Users/gapaza/Documents/TAT-C/vinay-architecture/arch-0
    writeCache  = path_cache;
    startDate   = (Real)startD;    //In Seconds
    numPoints   = points;
    numGS       = gsNum;
    missionDays = mD;
    missionSeconds = missionDays * DAY_TO_SEC;
    tsr         = ms;




    pointDuration.resize(numPoints);
    pointPasses.resize(numPoints);
    pointWhenCombined.resize(numPoints);
    timeToCovDSM.resize(numPoints);

    lat_lon_vector = pointCoordsVec;

    gsDuration.resize(numGS);
    gsWhenCombined.resize(numGS);
    gsAverageAccess.resize(numGS);
    gsAverageRevisit.resize(numGS);
    gsMaxAccess.resize(numGS);
    gsMaxRevisit.resize(numGS);
    gsMinAccess.resize(numGS);
    gsMinRevisit.resize(numGS);
    gsPassesDSM.resize(numGS);


    pointMinRevisit.resize(numPoints);
    pointMaxRevisit.resize(numPoints);
    pointAverageRevisit.resize(numPoints);

    pointMeanResponse.resize(numPoints);


    pointMinAccess.resize(numPoints);
    pointMaxAccess.resize(numPoints);
    pointAverageAccess.resize(numPoints);

    gsMinRevisit.resize(gsNum);
    gsMaxRevisit.resize(gsNum);
    gsAverageRevisit.resize(gsNum);

    gsMinAccess.resize(gsNum);
    gsMaxAccess.resize(gsNum);
    gsAverageAccess.resize(gsNum);


    //Set these variables to 0 in case there is no access
    pointsSeen = 0;
    pointsRevisited = 0;
    totalDLtimeDSM = 0;

    algsMinAccess = 0;
    algsMaxAccess = 0;
    algsSumAccess = 0;
    algsMinRevisit = 0;
    algsMaxRevisit = 0;
    algsSumRevisit = 0;

    minTime2Coverage = 0;
    maxTime2Coverage = 0;
    sumTime2Coverage = 0;

    maxAccess = 0;
    minAccess = 0;
    sumAccess = 0;
    minRevisit = 0;
    maxRevisit = 0;
    sumRevisit = 0;

    minResponse = 0;
    maxResponse = 0;
    sumResponse = 0;

    minPAS = 0;
    maxPAS = 0;
    sumPAS = 0;

    interpTime = 0;





    for(int x = 0; x < numPoints; x++)
    {
        pointDuration[x] = 0;
        pointPasses[x] = 0;
        timeToCovDSM[x] = 0;
    }

    for(int x = 0; x < numGS; x++)
    {
        gsPassesDSM[x] = 0;
        gsDuration[x] = 0;
    }



    algsPassesDSM = 0;
    numGS_Seen = 0;
    numGS_Revisit = 0;

    cache = new CacheInterface(path_cache);

}

Metrics::Metrics(const Metrics &orig)
{

}

Metrics::~Metrics()
{
    delete cache;
}




// ---------- Point of Interest Metrics ----------
void Metrics::addPOIData(vector<IntervalEventReport> coverageEvents)
{
    if(coverageEvents.size() == 0)
    {
        //cout << endl <<  "-- NO POI EVENTS FOR THIS SAT --" << endl;
        return;
    }



    //This will iterate over all the coverage events
    vector<IntervalEventReport>::iterator report;
    for(report = coverageEvents.begin(); report != coverageEvents.end(); report++) //Loop through all the reports for this propagation step
    {
        Integer poiIndex = report->GetPOIIndex(); //This tells us which point of interest the report is referring to
        Real eventDuration = (report->GetEndDate().GetJulianDate()) - (report->GetStartDate().GetJulianDate());
        if(eventDuration == 0){eventDuration = (interpTime / 2.0);}

        pointDuration[poiIndex] = pointDuration[poiIndex] + eventDuration;
        pointPasses[poiIndex] = pointPasses[poiIndex] + 1;

        pair<Real, Real> event(report->GetStartDate().GetJulianDate(), report->GetEndDate().GetJulianDate());
        pointWhenCombined[poiIndex].push_back(event);

    }


    //Calculate overall metrics on the number of times a point was passed --- make this an end calculation
    minPAS = pointPasses[0];
    maxPAS = pointPasses[0];
    sumPAS = 0;
    for(int x = 0; x < pointPasses.size(); x++)
    {
        if(pointPasses[x] > maxPAS){maxPAS = pointPasses[x];}
        if(pointPasses[x] < minPAS){minPAS = pointPasses[x];}
        sumPAS += pointPasses[x];
    }

    struct FirstColumnOnlyCmp
    {
        bool operator()(const std::pair<Real, Real>& lhs,
                        const std::pair<Real, Real>& rhs) const
        {
            return lhs.first < rhs.first;
        }
    };

    //This should sort points then turn them into a smooth continuation - needs to be throughly checked for 0 up numbering
    pointsSeen = 0;
    for(int x = 0; x < numPoints; x++) //Each loop iteration is looking at all the events for one point
    {
         //If no access was seen for this point
         if(pointWhenCombined[x].empty())
         {
             timeToCovDSM[x] = NAN;
             continue;
         }

         pointsSeen += 1;
         sort(pointWhenCombined[x].begin(), pointWhenCombined[x].end(), FirstColumnOnlyCmp());
         pointWhenCombined[x] = combineEvents(pointWhenCombined[x]);
    }
}

void Metrics::calculateMetrics_POI()
{
    // Determine which points meet access and revisit criteria
    vector<bool> hadAccess;
    vector<bool> hadRevisit;
    hadAccess.resize(numPoints);
    hadRevisit.resize(numPoints);
    for(int x = 0; x < numPoints; x++)
    {
        if(pointWhenCombined[x].empty()){hadAccess[x] = false;}
        else{hadAccess[x] = true;}

        if(pointWhenCombined[x].size() > 1)
        {
            hadRevisit[x] = true;
            pointsRevisited++;
        }
        else{hadRevisit[x] = false;}
    }




    // How long until the first sighting of a specific point of interest
    for(int x = 0; x < numPoints; x++)
    {
        if (hadAccess[x])
        {
            timeToCovDSM[x] = (pointWhenCombined[x][0].first - (Real)startDate)*24*3600;
            minTime2Coverage = timeToCovDSM[x];
            maxTime2Coverage = timeToCovDSM[x];
        }
    }
    sumTime2Coverage = 0;
    for(int x = 0; x < numPoints; x++)
    {
        if(hadAccess[x])
        {
            sumTime2Coverage = sumTime2Coverage + timeToCovDSM[x];
            if(minTime2Coverage > timeToCovDSM[x]){minTime2Coverage = timeToCovDSM[x];}
            if(maxTime2Coverage < timeToCovDSM[x]){maxTime2Coverage = timeToCovDSM[x];}
        }

    }





    // ---------- ACCESS LOCAL ----------
    for(int x = 0; x < numPoints; x++)
    {
        if(hadAccess[x])
        {
            // ---------- Set initial values for these metrics (LOCAL) ----------
            Real minAccessP = (pointWhenCombined[x][0].second - pointWhenCombined[x][0].first) * DAY_TO_SEC;
            Real maxAccessP = (pointWhenCombined[x][0].second - pointWhenCombined[x][0].first) * DAY_TO_SEC;
            Real sumAccessP = 0;

            //If we have an access duration of 0, set it to the min interp time
            if(minAccessP == 0 or maxAccessP == 0)
            {
                minAccessP = (interpTime / 2.0);
                maxAccessP = (interpTime / 2.0);
            }


            for(int y = 0; y < pointWhenCombined[x].size(); y++)
            {
                Real accessTime = (pointWhenCombined[x][y].second - pointWhenCombined[x][y].first) * DAY_TO_SEC;
                if(accessTime == 0){accessTime = (interpTime / 2.0);} //If access duration is 0, set it to half the interpolation time

                if(minAccessP > accessTime){minAccessP = accessTime;}
                if(maxAccessP < accessTime){maxAccessP = accessTime;}
                sumAccessP += accessTime;
            }
            //Local - Access
            pointAverageAccess[x] = (sumAccessP/pointWhenCombined[x].size());
            pointMinAccess[x] = (minAccessP);
            pointMaxAccess[x] = (maxAccessP);
        }
        else
        {
            pointAverageAccess[x] = NAN;
            pointMinAccess[x] = NAN;
            pointMaxAccess[x] = NAN;
        }

    }

    // ---------- ACCESS GLOBAL ----------
    // 1. Find average access duration for each point
    // 2. Find min and max of those averages
    for(int x = 0; x < numPoints; x++)
    {
        if(hadAccess[x])
        {
            minAccess = pointMinAccess[x];
            maxAccess = pointMaxAccess[x];
            sumAccess = 0;
            break;
        }
    }
    for(int point = 0; point < numPoints; point++)
    {
        if(hadAccess[point])
        {
            if(minAccess > pointMinAccess[point]){minAccess = pointMinAccess[point];}
            if(maxAccess < pointMaxAccess[point]){maxAccess = pointMaxAccess[point];}
            sumAccess += pointAverageAccess[point];
        }
    }










    for(int point = 0; point < numPoints; point++)  //Revisit Time
    {
        if(hadRevisit[point])
        {
            // ---------- Set initial values for these metrics (LOCAL) ----------
            Real minRevisitP = (pointWhenCombined[point][1].first - pointWhenCombined[point][0].second) * DAY_TO_SEC;
            Real maxRevisitP = (pointWhenCombined[point][1].first - pointWhenCombined[point][0].second) * DAY_TO_SEC;
            Real sumRevisitP = 0;
            Real avgResponseP = 0; //Summate the squares of all the gaps then divide by (2*missionDuration)

            for(int access = 0; access < (pointWhenCombined[point].size() - 1); access++)
            {
                Real gap = (pointWhenCombined[point][access + 1].first - pointWhenCombined[point][access].second) * DAY_TO_SEC; //Seconds

                avgResponseP = avgResponseP + (gap * gap); //Summate the squares of all the gaps

                if(minRevisitP > gap){minRevisitP = gap;}
                if(maxRevisitP < gap){maxRevisitP = gap;}
                sumRevisitP += gap;
            }
            //Local - Revisit
            pointMinRevisit[point]     = (minRevisitP);
            pointMaxRevisit[point]     = (maxRevisitP);
            pointAverageRevisit[point] = (sumRevisitP/(pointWhenCombined[point].size() - 1));
            pointMeanResponse[point]   = avgResponseP / (2 * missionSeconds);
        }
        else
        {
            pointMinRevisit[point]     = NAN;
            pointMaxRevisit[point]     = NAN;
            pointAverageRevisit[point] = NAN;
            pointMeanResponse[point]   = NAN;
        }
    }
    // ---------- Set initial values for these metrics (GLOBAL) ----------
    for(int point = 0; point < numPoints; point++)
    {
        if(hadRevisit[point])
        {
            minResponse = pointMeanResponse[point];
            maxResponse = pointMeanResponse[point];
            sumResponse = 0;

            minRevisit = pointMinRevisit[point];
            maxRevisit = pointMaxRevisit[point];
            sumRevisit = 0;
            break;
        }
    }
    for(int point = 0; point < numPoints; point++)
    {
        if(hadRevisit[point])
        {
            if(minRevisit > pointMinRevisit[point]){minRevisit = pointMinRevisit[point];}
            if(maxRevisit < pointMaxRevisit[point]){maxRevisit = pointMaxRevisit[point];}
            sumRevisit += pointAverageRevisit[point];

            if(minResponse > pointMeanResponse[point]){minResponse = pointMeanResponse[point];}
            if(maxResponse < pointMeanResponse[point]){maxResponse = pointMeanResponse[point];}
            sumResponse += pointMeanResponse[point];

        }
    }



}





// ---------- Ground Station Metrics ----------
void Metrics::addGSData( vector<IntervalEventReport> gsEvents)
{
    if(gsEvents.size() == 0)
    {
        //cout << endl <<  "-- NO GS EVENTS FOR THIS SAT --" << endl;
        return;
    }



    //Create a smooth continuation of access
    vector<IntervalEventReport>::iterator report;
    for(report = gsEvents.begin(); report != gsEvents.end(); report++) //Each loop iteration represents one step of the Propagation Phase
    {
        algsPassesDSM += 1; //Make sure this is correct!!!

        Integer poiIndex = report->GetPOIIndex();
        Real eventDuration = (report->GetEndDate().GetJulianDate()) - (report->GetStartDate().GetJulianDate());

        gsDuration[poiIndex] = gsDuration[poiIndex] + eventDuration;
        gsPassesDSM[poiIndex] = gsPassesDSM[poiIndex] + 1;

        pair<Real, Real> event(report->GetStartDate().GetJulianDate(), report->GetEndDate().GetJulianDate());
        gsWhenCombined[poiIndex].push_back(event);

    }

    struct FirstColumnOnlyCmp
    {
        bool operator()(const std::pair<Real, Real>& lhs,
                        const std::pair<Real, Real>& rhs) const
        {
            return lhs.first < rhs.first;
        }
    };


    //This merges any access events that overlap, simplifying calculations and reducing memory usage
    for(int x = 0; x < numGS; x++)
    {
        if(gsWhenCombined[x].empty()){continue;}

        sort(gsWhenCombined[x].begin(), gsWhenCombined[x].end(), FirstColumnOnlyCmp()); //Sorted
        gsWhenCombined[x] = combineEvents(gsWhenCombined[x]);
    }

}

void Metrics::calculateMetrics_GS()
{
    vector<bool> hadAccess;
    vector<bool> hadRevisit;
    hadAccess.resize(numGS);
    hadRevisit.resize(numGS);

    for(int x = 0; x < numGS; x++)
    {
        if(gsWhenCombined[x].empty())
        {
            hadAccess[x] = false;
        }
        else
        {
            hadAccess[x] = true;
            numGS_Seen++;
        }

        if(gsWhenCombined[x].size() > 1)
        {
            hadRevisit[x] = true;
            numGS_Revisit++;
        }
        else
        {
            hadRevisit[x] = false;
        }
    }





    for(int x = 0; x < numGS; x++)  //Access Time
    {
        if(hadAccess[x])
        {
            // ---------- Set initial values for these metrics (LOCAL) ----------
            Real minAccessP = (gsWhenCombined[x][0].second - gsWhenCombined[x][0].first) * DAY_TO_SEC;
            Real maxAccessP = (gsWhenCombined[x][0].second - gsWhenCombined[x][0].first) * DAY_TO_SEC;
            Real sumAccessP = 0;

            //We don't want 0 to be a min access
            if(minAccessP == 0 or maxAccessP == 0)
            {
                minAccessP = (interpTime / 2.0);
                maxAccessP = (interpTime / 2.0);
            }


            for(int y = 0; y < gsWhenCombined[x].size(); y++)
            {
                Real accessTime = (gsWhenCombined[x][y].second - gsWhenCombined[x][y].first) * DAY_TO_SEC;
                if(accessTime == 0){accessTime = (interpTime / 2.0);} //If access duration is 0, set it to half the interpolation time

                if(minAccessP > accessTime){minAccessP = accessTime;}
                if(maxAccessP < accessTime){maxAccessP = accessTime;}
                sumAccessP += accessTime;
            }
            //Local - Access
            gsAverageAccess[x] = (sumAccessP/gsWhenCombined[x].size());
            gsMinAccess[x] = (minAccessP);
            gsMaxAccess[x] = (maxAccessP);
        }
        else
        {
            gsAverageAccess[x] = NAN;
            gsMinAccess[x] = NAN;
            gsMaxAccess[x] = NAN;
        }

    }
    // ---------- Set initial values for these metrics (GLOBAL) ----------
    for(int x = 0; x < numGS; x++)
    {
        if(hadAccess[x])
        {
            algsMinAccess = gsMinAccess[x];
            algsMaxAccess = gsMaxAccess[x];
            algsSumAccess = 0;
            break;
        }
    }

    //We are recalculating the average downlink time
    for(int point = 0; point < numGS; point++)
    {
        if(hadAccess[point])
        {
            if(algsMinAccess > gsMinAccess[point]){algsMinAccess = gsMinAccess[point];}
            if(algsMaxAccess < gsMaxAccess[point]){algsMaxAccess = gsMaxAccess[point];}
            algsSumAccess += gsAverageAccess[point];
        }
    }







    for(int point = 0; point < numGS; point++)  //Revisit Time
    {
        if(hadRevisit[point])
        {
            // ---------- Set initial values for these metrics (LOCAL) ----------
            Real minRevisitP = (gsWhenCombined[point][1].first - gsWhenCombined[point][0].second) * DAY_TO_SEC;
            Real maxRevisitP = (gsWhenCombined[point][1].first - gsWhenCombined[point][0].second) * DAY_TO_SEC;
            Real sumRevisitP = 0;
            for(int access = 0; access < (gsWhenCombined[point].size() - 1); access++)
            {
                Real gap = (gsWhenCombined[point][access + 1].first - gsWhenCombined[point][access].second) * DAY_TO_SEC;
                if(minRevisitP > gap){minRevisitP = gap;}
                if(maxRevisitP < gap){maxRevisitP = gap;}
                sumRevisitP += gap;
            }
            //Local - Revisit
            gsMinRevisit[point] = (minRevisitP);
            gsMaxRevisit[point] = (maxRevisitP);
            gsAverageRevisit[point] = (sumRevisitP/(gsWhenCombined[point].size() - 1));
        }
        else
        {
            gsMinRevisit[point] = NAN;
            gsMaxRevisit[point] = NAN;
            gsAverageRevisit[point] = NAN;
        }
    }
    // ---------- Set initial values for these metrics (GLOBAL) ----------
    for(int point = 0; point < numGS; point++)
    {
        if(hadRevisit[point])
        {
            algsMinRevisit = gsMinRevisit[point];
            algsMaxRevisit = gsMaxRevisit[point];
            algsSumRevisit = 0;
            break;
        }
    }
    for(int point = 0; point < numGS; point++)
    {
        if(hadRevisit[point])
        {
            if(algsMinRevisit > gsMinRevisit[point]){algsMinRevisit = gsMinRevisit[point];}
            if(algsMaxRevisit < gsMaxRevisit[point]){algsMaxRevisit = gsMaxRevisit[point];}
            algsSumRevisit += gsAverageRevisit[point];
        }
    }
    



    for(int x = 0; x < gsPassesDSM.size(); x++)
    {
        if(hadAccess[x])
        {
            totalDLtimeDSM = totalDLtimeDSM + gsPassesDSM[x] * gsAverageAccess[x];
        }
    }




}








// ------------------- Testing Functions ------------------
void Metrics::printPointAccess(vector< pair<Real, Real> > toPrint, int pNum)
{
    cout << endl << "----- Point num " << pNum << " -----" << endl;
    for(int x = 0; x < toPrint.size(); x++)
    {
        cout << fixed;
        cout << x << "   " << toPrint[x].first << "   " << toPrint[x].second << "   " << (toPrint[x].second - toPrint[x].first)*24.0*60*60  << endl;
    }
    cout << "------------------------" << endl;

}






// ------------------- Output Functions ------------------
void Metrics::writeGlobals()
{
    //cout << "----- Writing gbl.json -----" << endl;
    string outputPath = writeFiles + "/gbl.json";

    Json::Value gblObj;
    Json::StyledWriter styledWriter;

    gblObj["Time"]["min"] = 0;
    gblObj["Time"]["max"] = missionDays*24*3600;


    Real TCavg;
    if(pointsSeen == 0){TCavg = 0;}
    else{TCavg = sumTime2Coverage/pointsSeen;}
    gblObj["TimeToCoverage"]["avg"] = TCavg;
    gblObj["TimeToCoverage"]["min"] = minTime2Coverage;
    gblObj["TimeToCoverage"]["max"] = maxTime2Coverage;


    Real ATavg;
    if(pointsSeen == 0){ATavg = 0;}
    else{ATavg = sumAccess/pointsSeen;}
    gblObj["AccessTime"]["avg"] = ATavg;
    gblObj["AccessTime"]["min"] = minAccess;
    gblObj["AccessTime"]["max"] = maxAccess;


    Real RTavg;
    if(pointsSeen == 0){RTavg = 0;}
    else{RTavg = sumRevisit/pointsRevisited;}
    gblObj["RevisitTime"]["avg"] = RTavg;
    gblObj["RevisitTime"]["min"] = minRevisit;
    gblObj["RevisitTime"]["max"] = maxRevisit;

    gblObj["Coverage"] = 100*(pointsSeen/numPoints);


    Real PASavg;
    if(numPoints == 0){PASavg = 0;}
    else{PASavg = sumPAS/numPoints;}
    gblObj["NumOfPOIpasses"]["avg"] = PASavg;
    gblObj["NumOfPOIpasses"]["min"] = minPAS;
    gblObj["NumOfPOIpasses"]["max"] = maxPAS;


    Real DLavg;
    if(numGS_Revisit == 0){DLavg = 0;}
    else{DLavg = algsSumRevisit / numGS_Revisit;}
    gblObj["DataLatency"]["avg"] = DLavg;
    gblObj["DataLatency"]["min"] = algsMinRevisit;
    gblObj["DataLatency"]["max"] = algsMaxRevisit;

    gblObj["NumGSpassesPD"] = algsPassesDSM/missionDays;

    gblObj["TotalDownlinkTimePD"] = totalDLtimeDSM/missionDays;


    Real DLTavg;
    if(numGS_Seen == 0){DLTavg = 0;}
    else{DLTavg = algsSumAccess / numGS_Seen;}
    gblObj["DownlinkTimePerPass"]["avg"] = DLTavg; //Recalculated on line 465
    gblObj["DownlinkTimePerPass"]["min"] = algsMinAccess;
    gblObj["DownlinkTimePerPass"]["max"] = algsMaxAccess;


    Real RSPavg;
    if(pointsSeen == 0){RSPavg = 0;}
    else{RSPavg = sumResponse / pointsRevisited;}
    gblObj["ResponseTime"]["avg"] = RSPavg;
    gblObj["ResponseTime"]["min"] = minResponse;
    gblObj["ResponseTime"]["max"] = maxResponse;



    ofstream globalJson;
    globalJson.open(outputPath);

    globalJson << styledWriter.write(gblObj);
    globalJson.close();


}

void Metrics::writeLocals()
{
    string outputPath = writeFiles + "/lcl.csv";

    vector<string> colHeader1;
    colHeader1.push_back("Time [s]");
    colHeader1.push_back("");
    colHeader1.push_back("POI");
    colHeader1.push_back("[deg]");
    colHeader1.push_back("[deg]");
    colHeader1.push_back("[km]");
    colHeader1.push_back("AccessTime [s]");
    colHeader1.push_back("");
    colHeader1.push_back("");
    colHeader1.push_back("RevisitTime [s]");
    colHeader1.push_back("");
    colHeader1.push_back("");
    colHeader1.push_back("TimeToCoverage [s]");
    colHeader1.push_back("Number of Passes");

    vector<string> colHeader2;
    colHeader2.push_back("t0");
    colHeader2.push_back("t1");
    colHeader2.push_back("POI");
    colHeader2.push_back("lat");
    colHeader2.push_back("lon");
    colHeader2.push_back("alt");
    colHeader2.push_back("ATavg");
    colHeader2.push_back("ATmin");
    colHeader2.push_back("ATmax");
    colHeader2.push_back("RvTavg");
    colHeader2.push_back("RvTmin");
    colHeader2.push_back("RvTmax");
    colHeader2.push_back("TCcov");
    colHeader2.push_back("numPass");


    ofstream localfile;
    localfile.open(outputPath.c_str(),ios::binary | ios::out);
    if(localfile.is_open())
    {
        for (Integer ii=0;ii<colHeader1.size()-1;ii++)
        {
            localfile << colHeader1[ii] << ",";
        }
        localfile << colHeader1[colHeader1.size()-1] << endl;
        for (Integer ii=0;ii<colHeader2.size()-1;ii++)
        {
            localfile << colHeader2[ii] << ",";
        }
        localfile << colHeader2[colHeader2.size()-1] << endl;


        for (Integer num = 0; num < numPoints; num++)
        {
            localfile << 0 << ",";
            localfile << missionDays*24*3600 << ",";
            localfile << num << ",";
            localfile << lat_lon_vector[num].first << ",";
            localfile << lat_lon_vector[num].second << ",";
            localfile << 0 << ",";
            localfile << pointAverageAccess[num] << ",";
            localfile << pointMinAccess[num] << ",";
            localfile << pointMaxAccess[num] << ",";
            localfile << pointAverageRevisit[num] << ",";
            localfile << pointMinRevisit[num] << ",";
            localfile << pointMaxRevisit[num] << ",";
            localfile << timeToCovDSM[num] << ",";
            localfile << pointPasses[num] << endl;
        }

    }
    else
    {
        cout << "Unable to write lcl.csv" << endl;
    }



}

void Metrics::writeAccess()
{
    string outputPath = writeFiles + "/access.csv";


    //Create File Headers
    vector<string> accHeader;
    accHeader.push_back("Lat[deg]");
    accHeader.push_back("Lon[deg]");
    accHeader.push_back("Access From [s]");
    accHeader.push_back("Access To [s]");

    ofstream accfile;
    accfile.open(outputPath.c_str(),ios::binary | ios::out);

    //Write Headers
    for (Integer ii=0;ii<accHeader.size()-1;ii++)
    {
        accfile << accHeader[ii] << ",";
    }
    accfile << accHeader[accHeader.size()-1] << endl;


    for(int point = 0; point < pointWhenCombined.size(); point++)
    {

        for(int acc = 0; acc < pointWhenCombined[point].size(); acc++)
        {
            accfile << lat_lon_vector[point].first << ",";
            accfile << lat_lon_vector[point].second << ",";
            accfile << pointWhenCombined[point][acc].first - (Real)startDate << ",";
            accfile << pointWhenCombined[point][acc].second - (Real)startDate << endl;
        }

    }
}

void Metrics::writePOI()
{
    string outputPath = writeCache + "/poi.csv";
    string outputLink = writeFiles + "/poi.csv";

    cache->WritePoiFile(&lat_lon_vector, numPoints);
    cache->CreateHardLink(outputPath, outputLink);
}





// ------------------- Combining Access Intervals ------------------
vector< pair<Real, Real> > Metrics::combineEvents(vector< pair<Real, Real> > events)
{
    int numEvents = events.size();
    vector< pair<Real,Real> > toReturn;

    stack< pair<Real, Real> > combinedEvents;
    combinedEvents.push(events[0]);
    for(int x = 1; x < numEvents; x++)
    {
        pair<Real, Real> top = combinedEvents.top();
        if(top.second < events[x].first) //The event doesn't need to be combined
        {
            combinedEvents.push(events[x]);
        }
        else if(top.second < events[x].second)
        {
            top.second = events[x].second;
            combinedEvents.pop();
            combinedEvents.push(top);
        }
    }

    while(!combinedEvents.empty())
    {
        toReturn.insert(toReturn.begin(), 1, combinedEvents.top());
        combinedEvents.pop();
    }

    return toReturn;
}



void Metrics::setInterpTime(Real time)
{
    interpTime = time;
}





