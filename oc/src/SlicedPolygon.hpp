#ifndef SlicedPolygon_hpp
#define SlicedPolygon_hpp

#include "Polygon.hpp"

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
		
	protected:
	
		Rvector3 pole;
		Real bound1;
		Real bound2;
		double B;

		Real shooterDotPole;
};

class Slice
{
	//Slice(Rvector3
};


class SlicedPolygon : Polygon
{

	public:

		SlicedPolygon(std::vector<Rvector3> poly, Rvector3 contained);
		SlicedPolygon(std::vector<AnglePair> poly, AnglePair contained);
		~SlicedPolygon();
		
		//virtual void preprocess();
		//virtual int contains(std::vector<Rvector3> queries);
		//virtual int contains(Rvector3 query);
		
		virtual int numCrossings(AnglePair query);
		//virtual Slice findSlice(Real clock);
		
		std::vector<Edge> generateEdgeArray();
		
		// Coordinate Transformation
		Rmatrix33 generateTI();

		// Getters

		std::vector<Edge> getEdgeArray();
		Rmatrix33 getTI();
		
	protected:
		Rvector3 contained;
		std::vector<Edge> edgeArray;
		Rmatrix33 TI;
};

#endif /* SlicedPolygon_hpp */

