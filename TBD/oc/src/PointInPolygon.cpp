#include "PointInPolygon.hpp"

void analysis::generatePrepReport(Preprocessor* prep)
{
    Real timePrep = preprocess(prep);
    std::cout << "Polygon Preprocessing Time: " << timePrep << " (microseconds) \n";
}


void analysis::generateQueryReport(Polygon* poly, std::vector<AnglePair> &queries, std::string out)
{
    Real timeQuery = containedOut(poly,queries,out);
    std::cout << "Total Query Time: " << timeQuery << " (microseconds) \n";
}

void analysis::generateFullReport(std::string inputPoly,std::string inputQueries,std::string output)
{
    std::vector<AnglePair> vertices = util::csvRead(inputPoly);
    AnglePair contained = vertices.back();
    vertices.pop_back();

    // Construct
    auto start = std::chrono::high_resolution_clock::now();
    SlicedPolygon poly = SlicedPolygon(vertices,contained);
    auto stop = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    std::cout << poly;

    std::cout << "Polygon Construction Time: " << duration.count() << " (microseconds) \n";

    // Query
    std::vector<AnglePair> queries = util::csvRead(inputQueries);
    
    start = std::chrono::high_resolution_clock::now();
    std::vector<int> results = poly.numCrossings(queries);
    stop = std::chrono::high_resolution_clock::now();

    duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    std::cout << "Total Query Time: " << duration.count() << " (microseconds) \n";

    util::csvWrite(output,results);
    
    // Preprocess
    start = std::chrono::high_resolution_clock::now();
    Preprocessor* sliceArray = new SliceArray(poly.getLonArray(),poly.getEdgeArray());
    stop = std::chrono::high_resolution_clock::now();

    duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    std::cout << "Polygon Preprocessing Time: " << duration.count() << " (microseconds) \n";

    poly.addPreprocessor(sliceArray);

    // Query
    start = std::chrono::high_resolution_clock::now();
    results = poly.numCrossings(queries);
    stop = std::chrono::high_resolution_clock::now();

    duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    std::cout << "Total Query Time: " << duration.count() << " (microseconds) \n";

    //util::csvWrite(output,results);
}

Real analysis::containedOut(Polygon* poly, std::vector<AnglePair> &queries, std::string output)
{
    auto start = std::chrono::high_resolution_clock::now();
    std::vector<int> results = poly->contains(queries);
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    Real micros = duration.count();

    util::csvWrite(output,results);

    return micros;
}

Real analysis::preprocess(Preprocessor* prep)
{
    auto start = std::chrono::high_resolution_clock::now();
    prep->preprocess();
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(stop - start);

    Real micros = duration.count();

    return micros;
}