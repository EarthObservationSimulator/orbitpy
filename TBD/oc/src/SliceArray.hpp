#ifndef SliceArray_hpp
#define SliceArray_hpp

#include <algorithm>
#include "SlicedPolygon.hpp"

class SliceArray : public Preprocessor
{
    public:

        // Constructor
        SliceArray(std::vector<Real>,const std::vector<Edge> &);
        // Destructor
        ~SliceArray();

        // Run the preprocessing routine
        void preprocess();

        // Get the subset of edges that could contain query
        std::vector<int> getEdges(AnglePair query);

        // Getters
        std::vector<Real> getLonArray();

    protected:

        void preprocess(std::vector<int>,int,int);
        bool contains(Edge,Real,Real);
        std::vector<int> classifyEdges(const std::vector<int> &,int,int);

        std::vector<Real> lonArray;
        std::vector<Edge> edgeArray;
        std::vector<std::vector<int>> classified;
};

#endif /* SliceArray_hpp */