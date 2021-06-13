#include "SphericalSensor.hpp"

SphericalSensor::SphericalSensor(const Rvector &coneAngleVecIn, const Rvector &clockAngleVecIn, AnglePair contained) :
Sensor()
{
    std::vector<AnglePair> vertices(coneAngleVecIn.GetSize());
    for (int i = 0; i < coneAngleVecIn.GetSize(); i++)
    {
        vertices[i][0] = coneAngleVecIn[i];
        vertices[i][1] = clockAngleVecIn[i];
    }

    poly = new SlicedPolygon(vertices,contained);
    Preprocessor* prep = new SliceArray(poly->getLonArray(),poly->getEdgeArray());
    prep->preprocess();
    poly->addPreprocessor(prep);
}

SphericalSensor::~SphericalSensor()
{
    delete(poly);
}

bool SphericalSensor::CheckTargetVisibility(Real viewConeAngle, Real viewClockAngle)
{
    AnglePair query = {viewConeAngle,viewClockAngle};
    return poly->contains(query);
}