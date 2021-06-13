#ifndef PointInPolygon_hpp
#define PointInPolygon_hpp

#include "SliceArray.hpp"
#include<chrono>

namespace analysis
{
    void generateFullReport(std::string,std::string,std::string);
    void generateQueryReport(Polygon*, std::vector<AnglePair> &, std::string);
    void generatePrepReport(Preprocessor*);
    Real containedOut(Polygon*,std::vector<AnglePair> &,std::string);
    Real preprocess(Preprocessor*);
}

#endif /* PointInPolygon_hpp */