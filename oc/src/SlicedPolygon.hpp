#ifndef SlicedPolygon_hpp
#define SlicedPolygon_hpp

#include "Polygon.hpp"
#include "Preprocessor.hpp"
#include <limits>

class SliceTree;

class Edge
{
	public:
	
		Edge();
		Edge(Rvector3 node1, Rvector3 node2);
		Edge(AnglePair node1, AnglePair node2);
		
		int contains(Rvector3 query, Real lon);
		
		int crossesBoundary(Rvector3 query);
		bool boundsPoint(Real lon);

		// Getters
		Rvector3 getPole();
		Real getBound1();
		Real getBound2();

		friend std::ostream& operator<<(std::ostream& os, const Edge& edge);

	protected:
	
		Rvector3 pole;
		Real bound1;
		Real bound2;

		Real shooterDotPole;
};

class SlicedPolygon : public Polygon
{

	public:

		// Constructors
		SlicedPolygon(std::vector<Rvector3> &poly, Rvector3 contained);
		SlicedPolygon(std::vector<AnglePair> &poly, AnglePair contained);

		// Destructor
		~SlicedPolygon();
		
		void addPreprocessor(Preprocessor*);

		int contains(AnglePair query);
		std::vector<int> contains(std::vector<AnglePair> queries);
		int numCrossings(AnglePair query);
		std::vector<int> numCrossings(std::vector<AnglePair> queries);

		std::vector<int> getSubset(AnglePair query);
		
		std::vector<Edge> generateEdgeArray();
		
		// Coordinate Transformation
		Rmatrix33 generateTI();
		AnglePair toQueryFrame(AnglePair query);

		// Getters
		std::vector<Edge> getEdgeArray();
		std::vector<Real> getLonArray();
		std::vector<Real> getLatArray();
		Rmatrix33 getTI();

		// Overide print function 
		friend std::ostream& operator<<(std::ostream& os, const SlicedPolygon& poly);
		
	protected:
		bool processed;
		Rvector3 contained;
		Preprocessor* preprocessor;
		std::vector<Edge> edgeArray;
		std::vector<int> indexArray;
		std::vector<Rvector3> nodes;
		Rmatrix33 TI;
};

#endif /* SlicedPolygon_hpp */