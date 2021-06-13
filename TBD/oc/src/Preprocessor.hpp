#ifndef Preprocessor_hpp
#define Preprocessor_hpp

#include "Polygon.hpp"

// Pure virtual class
class Preprocessor
{
    public:
        virtual std::vector<int> getEdges(AnglePair query) = 0;
        virtual void preprocess() = 0;
};

#endif /* Preprocessor_hpp */

