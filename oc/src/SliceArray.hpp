#ifndef SliceArray_hpp
#define SliceArray_hpp

#include <algorithm>
#include "SlicedPolygon.hpp"

class SliceArray : public Preprocessor
{
    public:

        SliceArray(std::vector<Real>,const std::vector<Edge> &);
        ~SliceArray();
        void preprocess();


        void preprocess(std::vector<int>,int,int);
        std::vector<int> getEdges(AnglePair query);
        std::vector<Real> getLonArray();

    private:

        std::vector<Real> lonArray;
        std::vector<Edge> edgeArray;
        std::vector<std::vector<int>> classified;

        bool contains(Edge,Real,Real);
        std::vector<int> classifyEdges(const std::vector<int> &,int,int);

};

#endif /* SliceArray_hpp */