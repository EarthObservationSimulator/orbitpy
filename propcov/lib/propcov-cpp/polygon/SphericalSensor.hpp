#ifndef SphericalSensor_hpp
#define SphericalSensor_hpp

#include "../Sensor.hpp"
#include "SlicedPolygon.hpp"
#include "SliceArray.hpp"

class SphericalSensor : public Sensor
{
    public:
    
        // Class construction/destruction 
        SphericalSensor(const Rvector &coneAngleVecIn, const Rvector &clockAngleVecIn, AnglePair contained);
        ~SphericalSensor();


        virtual bool CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle);

    protected:

        SlicedPolygon* poly;
};

#endif /* SphericalSensor_hpp */