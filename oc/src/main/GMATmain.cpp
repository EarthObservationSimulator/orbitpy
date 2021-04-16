#include "../PointInPolygon.hpp"
#include "../GMATPolygon.hpp"

int main(int argc, char **argv)
{
    std::string inputPoly = argv[1];
    std::string inputQueries = argv[2];
    std::string output = argv[3];

    std::vector<AnglePair> vertices = util::csvRead(inputPoly);
    AnglePair contained = vertices.back();
    vertices.pop_back();
    
    GMATPolygon* poly = new GMATPolygon(vertices,contained);

    std::vector<AnglePair> queries = util::csvRead(inputQueries);

    analysis::generateQueryReport(poly,queries,output);

    free(poly);
    return 0;
}
