#include "Projector.hpp"
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include "json.hpp"
#include <iomanip>
#include "oci_utils.h"

#define DEBUG_CONSISE
//#define DEBUG_CHK_INPS

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;
using json = nlohmann::json;


/*
    * @param _date date in Julian Day UT1 
    * @param _state_eci Satellite Cartesian state in ECI as a string ("X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s]")
    * @param _satOrien satellite orientation (sequence and euler angles in degrees, eg: "1,2,3,20,10,30")
    * @param _senOrien sensor orientation (sequence and euler angles in degrees, eg: "1,2,3,20,10,30")
    * @param angleWidth Sensor FOV width (along sensor-frame X-axis) in degrees
    * @param angleHeight Sensor FOV height (along sensor-frame Y-axis) in degrees
    * @param widthDetectors Number of detector rows
    * @param heightDetectors Number of detector columns
    * @param outFilePath Output file path
*/

int main(int argc, char *argv[])
{
    /** Set up the messaging and output **/
    std::string outFormat = "%16.9f";

    /** Set up the message receiver and log file **/
    //Uncomment to set up receving debug messages on console 
    ConsoleMessageReceiver *consoleMsg = ConsoleMessageReceiver::Instance();
    MessageInterface::SetMessageReceiver(consoleMsg);

    /** Parse input arguments **/
    Real _date; 
    string _state_eci;
    string _satOrien; 
    string _senOrien;
    Real angleWidth;
    Real angleHeight;
    Integer widthDetectors;
    Integer heightDetectors;
    string outFilePath;

    if(argc=10){            
        _date = Real(stod(argv[1]));
        _state_eci = argv[2];
        _satOrien = argv[3];
        _senOrien = argv[4];
        angleWidth = Real(stod(argv[5]));
        angleHeight = Real(stod(argv[6]));
        widthDetectors = Integer(stoi(argv[7]));
        heightDetectors = Integer(stoi(argv[8]));
        outFilePath = argv[9];
    }else{
        MessageInterface::ShowMessage("Please input right number of arguments.\n");
        exit(1);
    }  

    RealArray state_eci(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_state_eci, ',')));
    if(state_eci.size()!=6){
        MessageInterface::ShowMessage("s/c state must be specified in the following format: 'X[km],Y[km],Z[km],VX[km/s],VY[km/s],VZ[km/s'\n");
        exit(1);
    }
    RealArray satOrien(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_satOrien, ',')));
    if(satOrien.size()!=6){
        MessageInterface::ShowMessage("Satellite orientation must be specified in a set of euler angles and sequence.'\n");
        exit(1);
    }
    RealArray senOrien(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_senOrien, ',')));
    if(senOrien.size()!=6){
        MessageInterface::ShowMessage("Sensor orientation must be specified in a set of euler angles and sequence.\n");
        exit(1);
    }

    #ifdef DEBUG_CHK_INPS
    #endif

    DiscretizedSensor* sensor;
    Attitude* attitude;
    AbsoluteDate* date;
    OrbitState* state;
    LagrangeInterpolator* interpolator;
    Spacecraft* sat;
    Projector* coverage;   

    attitude = new NadirPointingAttitude();
    date = new AbsoluteDate();
    date->SetJulianDate(_date);
    state = new OrbitState();
    state->SetCartesianState(Rvector6(state_eci));
    interpolator = new LagrangeInterpolator();
    sat = new Spacecraft(date,state,attitude,interpolator);
    sat->SetBodyNadirOffsetAngles(satOrien[3], satOrien[4], satOrien[5], satOrien[0], satOrien[1], satOrien[2]); // careful: angle in degrees

    sensor = new DiscretizedSensor(angleWidth*GmatMathConstants::RAD_PER_DEG ,angleHeight*GmatMathConstants::RAD_PER_DEG ,widthDetectors,heightDetectors);
    sensor->SetSensorBodyOffsetAngles(senOrien[3], senOrien[4], senOrien[5], senOrien[0], senOrien[1], senOrien[2]); // careful: angle in degrees
   
    sat->AddSensor(sensor);
   
    coverage = new Projector(sat,sensor);
	
	std::vector<AnglePair> center_intersection, corner_intersection;
    std::vector<Rvector3> pole_intersection;	
	
	center_intersection = coverage->checkIntersection();
    corner_intersection = coverage->checkCornerIntersection();
	pole_intersection = coverage->checkPoleIntersection();	

    /*
    MessageInterface::ShowMessage("Lat and lon of pixel-center \n");
    for(int k=0; k<center_intersection.size(); k++){
        // Lat and lon of pixel-center
        Real lat, lon;
        lat = center_intersection[k][0];
        lon = center_intersection[k][1];
        MessageInterface::ShowMessage("%f, %f \n", lat,lon);
    }

    MessageInterface::ShowMessage("Lat and lon of pixel-coorners \n");
    for(int k=0; k<corner_intersection.size(); k++){
        // Lat and lon of pixel-coorners
        Real lat, lon;
        lat = corner_intersection[k][0];
        lon = corner_intersection[k][1];
        MessageInterface::ShowMessage("%f, %f \n", lat,lon);
    }

    MessageInterface::ShowMessage("EF Cartesian coords of poles \n");
    for(int k=0; k<pole_intersection.size(); k++){
        // EF Cartesian coords of poles
        MessageInterface::ShowMessage("%f, %f, %f \n", pole_intersection[k][0],pole_intersection[k][1],pole_intersection[k][2]);
    }
    */

    // convert from radians to degrees
    for(int k=0; k<center_intersection.size(); k++){
        Real lat, lon;
        center_intersection[k][0] = center_intersection[k][0]*GmatMathConstants::DEG_PER_RAD;
        center_intersection[k][1] = center_intersection[k][1]*GmatMathConstants::DEG_PER_RAD;
    }
    // convert from radians to degrees
    for(int k=0; k<corner_intersection.size(); k++){
        Real lat, lon;
        corner_intersection[k][0] = corner_intersection[k][0]*GmatMathConstants::DEG_PER_RAD;
        corner_intersection[k][1] = corner_intersection[k][1]*GmatMathConstants::DEG_PER_RAD;
    }
    // convert pole_intersection datatype to one compactible with the json class
    typedef std::array<Real,3> CartesianPositionVector;
    std::vector<CartesianPositionVector> pole_intersection_json_compactable(pole_intersection.size());
    for(int k=0; k<pole_intersection.size(); k++){
        pole_intersection_json_compactable[k][0] = pole_intersection[k][0];
        pole_intersection_json_compactable[k][1] = pole_intersection[k][1];
        pole_intersection_json_compactable[k][2] = pole_intersection[k][2];
    }    

    json j;
    // add a number that is stored as double (note the implicit conversion of j to an object)
    j["centerIntersection"] = {center_intersection};
    j["cornerIntersection"] = {corner_intersection};
    j["poleIntersection"] = {pole_intersection_json_compactable};

    std::ofstream o;
    o.open(outFilePath.c_str(),ios::binary | ios::out);
    o << std::setw(4) << j << std::endl;

    delete(sensor);
    delete(attitude);
    delete(date);
    delete(state);
    delete(interpolator);
    delete(coverage);

    return 0;

}