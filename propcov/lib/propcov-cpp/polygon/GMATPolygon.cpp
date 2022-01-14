#include "GMATPolygon.hpp"

GMATPolygon::GMATPolygon(std::vector<AnglePair> &vertices,AnglePair contained) :
SlicedPolygon(vertices,contained)
{
    genCustomSensor();
}

void GMATPolygon::genCustomSensor()
{
    Rvector coneArray = getLatArray();
    Rvector clockArray = getLonArray();

    sensor = new GMATCustomSensor(coneArray,clockArray);
}

std::vector<int> GMATPolygon::contains(std::vector<AnglePair> queries)
{
    std::vector<int> results;
    int i;

    for (i = 0; i < queries.size(); i++)
    {
        AnglePair query = toQueryFrame(queries[i]);
        Real clock = query[1];
        Real cone = query[0];

        results.push_back((int)(sensor->CheckTargetVisibility(cone,clock)));
    }

    return results;
}