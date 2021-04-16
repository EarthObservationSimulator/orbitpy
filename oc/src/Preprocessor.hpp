#ifndef Preprocessor_hpp
#define Preprocessor_hpp

#include "Polygon.hpp"

class Preprocessor
{
    public:
        //Preprocessor();
        //~Preprocessor();
        virtual std::vector<int> getEdges(AnglePair query) = 0;
        virtual void preprocess() = 0;

};

#endif /* Preprocessor_hpp */

