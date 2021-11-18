#ifndef GMATPolygon_hpp
#define GMATPolygon_hpp

#include "../CustomSensor.hpp"
#include "SlicedPolygon.hpp"

class GMATPolygon : public SlicedPolygon
{
    public: 

        GMATPolygon(std::vector<AnglePair> &vertices,AnglePair contained);
        ~GMATPolygon();

        void genCustomSensor();

        virtual std::vector<int> contains(std::vector<AnglePair>);

    protected:

        CustomSensor* sensor;
};

#endif /* GMATPolygon_hpp */