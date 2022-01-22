#ifndef SlicedPolygon_hpp
#define SlicedPolygon_hpp

#include "Polygon.hpp"
#include "Preprocessor.hpp"
#include "Edge.hpp"
#include "Rmatrix33.hpp"
#include "frame.hpp"
#include <limits>

class SlicedPolygon : public Polygon
{
	public:

		// Constructors
		SlicedPolygon(std::vector<Rvector3>& verticesIn, Rvector3 interior);
		SlicedPolygon(std::vector<AnglePair>& verticesIn, AnglePair interior);
		// Init function for constructors 
		void init(std::vector<Rvector3>& verticesIn, Rvector3 interior);
		// Function to generate array of Edge objects used by constructor
		std::vector<Edge> generateEdgeArray();

		// Destructor
		~SlicedPolygon();
		
		// Add preprocessor to the polygon
		void addPreprocessor(Preprocessor*);
		// Returns the subset of eligible edges from the preprocessor, if present
		std::vector<int> getSubset(AnglePair query);

		// Core query method for a single query point
		int contains(AnglePair query, const frametype frame=INITIAL);
		// Core query method for a vector of queries
		std::vector<int> contains(std::vector<AnglePair> queries, const frametype frame=INITIAL);

		// Counts number of crossings for the arc PQ for a single query point. The frame in which the query point is available must be specified as 'Initial' or 'Query'. 
		int numCrossings(AnglePair query, const frametype frame=INITIAL);
		// Counts number of crossings for the arc PQ for a vector of queries. The frame in which the query point is available must be specified as 'Initial' or 'Query'. 
		std::vector<int> numCrossings(std::vector<AnglePair> queries, const frametype frame=INITIAL);
		
		// Coordinate Transformation
		Rmatrix33 generateQI();
		AnglePair toQueryFrame(const AnglePair);

		// Getters
		std::vector<Edge> getEdgeArray();
		std::vector<Real> getLonArray();
		std::vector<Real> getLatArray();
		Rmatrix33 getQI();

		// Overide print function 
		friend std::ostream& operator<<(std::ostream& os, const SlicedPolygon& poly);
		
	protected:

		bool processed;
		Rvector3 interior;
		Preprocessor* preprocessor;
		std::vector<Edge> edgeArray;
		std::vector<int> indexArray;
		std::vector<Rvector3> vertices;
		Rmatrix33 QI;
};

#endif /* SlicedPolygon_hpp */