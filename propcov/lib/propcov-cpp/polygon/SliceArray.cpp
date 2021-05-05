#include "SliceArray.hpp"

SliceArray::SliceArray(std::vector<Real> lonArray, const std::vector<Edge> &edgeArray)
{
    // Set the last longitude in lonArray (always = 0) to 2*PI
    lonArray[lonArray.size() - 1] = 2*M_PI;

    this->lonArray = lonArray;
    this->edgeArray = edgeArray;
}

void SliceArray::preprocess()
{
    std::sort(this->lonArray.begin(),this->lonArray.end());

    std::vector<int> parentIndices;
    for (int i = 0; i < edgeArray.size(); i++)
    {
        parentIndices.push_back(i);
    }

    this->classified.resize(lonArray.size() - 1);
    preprocess(parentIndices,0,lonArray.size() - 1);
}

SliceArray::~SliceArray(){}

void SliceArray::preprocess(std::vector<int> parentIndices,int start,int end)
{
    std::vector<int> childIndices = classifyEdges(parentIndices,start,end);

    if ((end - start) == 1)
    {
        this->classified[start] = childIndices;
        return;
    }

    int mid = start + (end - start)/2;

    preprocess(childIndices,start,mid);
    preprocess(childIndices,mid,end);
}

std::vector<int> SliceArray::classifyEdges(const std::vector<int> &parentIndices, int start, int end)
{
    Real bound1 = this->lonArray[start];
    Real bound2 = this->lonArray[end];

    std::vector<int> childIndices;

    for (int index : parentIndices)
    {
        Edge edge = this->edgeArray[index];

        if (contains(edge,bound1,bound2))
            childIndices.push_back(index);
    }

    return childIndices;
}

bool SliceArray::contains(Edge edge, Real bound1, Real bound2)
{
    Real vertex1 = edge.getBound1();
	Real vertex2 = edge.getBound2();

    bool condition1_1 = (vertex1 >= bound1) && (vertex1 <= bound2);
	bool condition1_2 = (vertex2 >= bound1) && (vertex2 <= bound2);

    /*
	bool condition2_1 = (bound1 >= vertex1) && (bound1 <= vertex2);
	bool condition2_2 = (bound2 >= vertex1) && (bound2 <= vertex2);
    */
    
    bool condition2_1 = util::lonBounded(vertex1,vertex2,bound1);
	bool condition2_2 = util::lonBounded(vertex1,vertex2,bound2);

    return condition1_1 || condition1_2 || condition2_1 || condition2_2;
}

std::vector<int> SliceArray::getEdges(AnglePair query)
{
    int start = 0,mid,end = this->lonArray.size();
    Real lon = query[1];
    Real lonVal;

    while ((end - start) != 1)
    {
        mid = start + (end - start)/2;
        lonVal = this->lonArray[mid];

        if (lon <= lonVal)
            end = mid;
        else
            start = mid;
    }

    return this->classified[start];
}

std::vector<Real> SliceArray::getLonArray()
{
    return this->lonArray;
}