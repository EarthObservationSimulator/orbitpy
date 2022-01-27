/**
 * Definition of the DSPIPCustomSensor class. This class models a custom sensor based on the algorithm in:
 * 
 * *R. Ketzner, V. Ravindra and M. Bramble, 'A Robust, Fast, and Accurate Algorithm for Point in Spherical Polygon Classification with Applications in Geoscience and Remote Sensing', Computers and Geosciences, under review.*
 * 
 * This is a subclass of the Sensor class. 
 * 
 * It can be used to evaluate the presence/absence of a point-location in a sensor FOV (custom shape). 
 * 
 * Some definitions:
 *      * 'Queries' here refers to the operation of finding if a point is inside or outside the sensor FOV.
 *      * This class defines two frames for the Sensor: Initial frame (Sensor Frame), and a Query Frame (alternate Sensor frame in which Queries are conducted.)
 *      * 'interior' point is a point known to be inside the sensor FOV
 *      * Any reference to Spherical coordinates here means expressing the position in cone/clock (in radians) NOT RA/DEC
 * 
 */
//------------------------------------------------------------------------------
#ifndef DSPIPCustomSensor_hpp
#define DSPIPCustomSensor_hpp

#include "../Sensor.hpp"
#include "SlicedPolygon.hpp"
#include "SliceArray.hpp"
#include "frame.hpp"
class DSPIPCustomSensor : public Sensor
{
    public:
    
        /// class construction/destruction
        DSPIPCustomSensor(const Rvector& coneAngleVecIn, const Rvector& clockAngleVecIn, AnglePair interiorIn);
        ~DSPIPCustomSensor();

        bool CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle) override;

        /// Override function in Sensor parent class
        /// Set the sensor-to-body offset angles (in degrees)
        void  SetSensorBodyOffsetAngles(
                        Real angle1 = 0.0, Real angle2 = 0.0, Real angle3 = 0.0,
                        Integer seq1 = 1, Integer seq2 = 2,   Integer seq3 = 3) override;
        /// Get the spacecraft-body-to-sensor (Query frame) matrix.
        Rmatrix33 GetBodyToSensorMatrix(Real forTime) override;

        Rmatrix33 getQI();

    protected:

        SlicedPolygon* poly;
        Rmatrix33 QI; // rotation matrix from Initial frame to Query frame
        Rmatrix33 Rot_ScBody2SensorQuery; // rotation matrix from spacecraft body to Sensor Query frame 

        /// stereographic projection of the polygon vertices for creation of the bounding box
        Rvector xProjectionCoordArray;   // numFOVpoints x values
        Rvector yProjectionCoordArray;   // numFOVpoints y values
        Real maxXExcursion;
        Real minXExcursion;
        Real maxYExcursion;
        Real minYExcursion;
        bool CheckTargetMaxExcursionCoordinates(Real xCoord, Real yCoord);
};

#endif /* DSPIPCustomSensor_hpp */