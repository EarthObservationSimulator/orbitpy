#ifndef GMATPolygon_hpp
#define GMATPolygon_hpp

#include "../GMATCustomSensor.hpp"
#include "SlicedPolygon.hpp"

class GMATPolygon : public SlicedPolygon
{
    public: 

        GMATPolygon(std::vector<AnglePair> &vertices,AnglePair contained);
        ~GMATPolygon();

        void genCustomSensor();

        virtual std::vector<int> contains(std::vector<AnglePair>);

    protected:

        GMATCustomSensor* sensor;
};

#endif /* GMATPolygon_hpp */