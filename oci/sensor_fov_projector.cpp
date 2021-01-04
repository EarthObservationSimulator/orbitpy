#include "Projector.hpp"
#include "NadirPointingAttitude.hpp"
#include "LagrangeInterpolator.hpp"
#include "../third-party-tools/json/json.hpp"
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
	
	std::vector<AnglePair> center_intersection_cartesian, corner_intersection_geocoords;
    std::vector<Rvector3> pole_intersection_cartesian;	
	
	center_intersection_cartesian = coverage->checkIntersection();
    corner_intersection_geocoords = coverage->checkCornerIntersection();
	pole_intersection_cartesian = coverage->checkPoleIntersection();	

    /*
    MessageInterface::ShowMessage("Lat and lon of pixel-center \n");
    for(int k=0; k<center_intersection_cartesian.size(); k++){
        // Lat and lon of pixel-center
        Real lat, lon;
        lat = center_intersection_cartesian[k][0];
        lon = center_intersection_cartesian[k][1];
        MessageInterface::ShowMessage("%f, %f \n", lat,lon);
    }

    MessageInterface::ShowMessage("Lat and lon of pixel-coorners \n");
    for(int k=0; k<corner_intersection_geocoords.size(); k++){
        // Lat and lon of pixel-coorners
        Real lat, lon;
        lat = corner_intersection_geocoords[k][0];
        lon = corner_intersection_geocoords[k][1];
        MessageInterface::ShowMessage("%f, %f \n", lat,lon);
    }

    MessageInterface::ShowMessage("EF Cartesian coords of poles \n");
    for(int k=0; k<pole_intersection_cartesian.size(); k++){
        // EF Cartesian coords of poles
        MessageInterface::ShowMessage("%f, %f, %f \n", pole_intersection_cartesian[k][0],pole_intersection_cartesian[k][1],pole_intersection_cartesian[k][2]);
    }
    */
    
    Earth *centralBody;
    centralBody = new Earth();

    // convert from radians to degrees
    for(int k=0; k<center_intersection_cartesian.size(); k++){
        Real lat, lon;
        center_intersection_cartesian[k][0] = center_intersection_cartesian[k][0]*GmatMathConstants::DEG_PER_RAD;
        center_intersection_cartesian[k][1] = center_intersection_cartesian[k][1]*GmatMathConstants::DEG_PER_RAD;
    }
    // convert from radians to degrees and compute cartesian coords
    typedef std::array<Real,3> CartesianPositionVector;
    std::vector<CartesianPositionVector> corner_intersection_cartesian(corner_intersection_geocoords.size());
    for(int k=0; k<corner_intersection_geocoords.size(); k++){

        Real lat, lon;
        Rvector3 sph = {corner_intersection_geocoords[k][0], corner_intersection_geocoords[k][1], 0};
        Rvector3 cart = BodyFixedStateConverterUtil::SphericalToCartesian(sph,1,centralBody->GetRadius());

        corner_intersection_geocoords[k][0] = corner_intersection_geocoords[k][0]*GmatMathConstants::DEG_PER_RAD;
        corner_intersection_geocoords[k][1] = corner_intersection_geocoords[k][1]*GmatMathConstants::DEG_PER_RAD;
        
        corner_intersection_cartesian[k][0] = cart[0];
        corner_intersection_cartesian[k][1] = cart[1];
        corner_intersection_cartesian[k][2] = cart[2];
    }
    // convert pole_intersection_cartesian datatype to one compactible with the json class
    
    std::vector<CartesianPositionVector> pole_intersection_json_compactable(pole_intersection_cartesian.size());    
    std::vector<AnglePair> pole_intersection_geocoords(pole_intersection_cartesian.size());

    for(int k=0; k<pole_intersection_cartesian.size(); k++){
        pole_intersection_json_compactable[k][0] = pole_intersection_cartesian[k][0];
        pole_intersection_json_compactable[k][1] = pole_intersection_cartesian[k][1];
        pole_intersection_json_compactable[k][2] = pole_intersection_cartesian[k][2];
        
        Rvector3 sphericalPos = BodyFixedStateConverterUtil::CartesianToSpherical(pole_intersection_cartesian[k],1,centralBody->GetRadius());
        pole_intersection_geocoords[k][0] = sphericalPos[0]*GmatMathConstants::DEG_PER_RAD; // lat
        pole_intersection_geocoords[k][1] = sphericalPos[1]*GmatMathConstants::DEG_PER_RAD; // lon
    }    

    json j;
    // add a number that is stored as double (note the implicit conversion of j to an object)
    j["widthDetectors"] = widthDetectors;
    j["heightDetectors"] = heightDetectors;
    j["centerIntersectionGeoCoords"] = center_intersection_cartesian;
    j["cornerIntersectionCartesian"] = corner_intersection_cartesian;
    j["cornerIntersectionGeoCoords"] = corner_intersection_geocoords;
    j["poleIntersectionCartesian"] = pole_intersection_json_compactable;
    j["poleIntersectionGeocoords"] = pole_intersection_geocoords;

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