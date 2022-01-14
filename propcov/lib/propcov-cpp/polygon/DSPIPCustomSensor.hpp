#ifndef DSPIPCustomSensor_hpp
#define DSPIPCustomSensor_hpp

#include "../Sensor.hpp"
#include "SlicedPolygon.hpp"
#include "SliceArray.hpp"

class DSPIPCustomSensor : public Sensor
{
    public:
    
        /// class construction/destruction
        DSPIPCustomSensor(const Rvector &coneAngleVecIn, const Rvector &clockAngleVecIn, AnglePair contained);
        ~DSPIPCustomSensor();


        virtual bool CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle);

    protected:

        SlicedPolygon* poly;
};

#endif /* DSPIPCustomSensor_hpp */