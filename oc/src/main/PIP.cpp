#include "PointInPolygon.hpp"

int main(int argc, char **argv)
{
    std::string inputPoly = argv[1];
    std::string inputQueries = argv[2];
    std::string prepOutput = argv[3];

    std::vector<AnglePair> vertices = util::csvRead(inputPoly);
    AnglePair contained = vertices.back();
    vertices.pop_back();
    
    SlicedPolygon* poly = new SlicedPolygon(vertices,contained);
    Preprocessor* prep = new SliceArray(poly->getLonArray(),poly->getEdgeArray());

    std::vector<AnglePair> queries = util::csvRead(inputQueries);

    if (argc == 5)
    {
        std::string output = argv[4];
        analysis::generateQueryReport(poly,queries,output);
    }

    analysis::generatePrepReport(prep);
    poly->addPreprocessor(prep);
    analysis::generateQueryReport(poly,queries,prepOutput);

    delete(poly);

    return 0;
}