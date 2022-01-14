#ifndef Edge_hpp
#define Edge_hpp

#include "Polygon.hpp"
#include "Preprocessor.hpp"
#include <limits>

class Edge
{
	public:
	
		// Constructors
		Edge();
		Edge(Rvector3 node1, Rvector3 node2);
		Edge(AnglePair node1, AnglePair node2);

		// Destructor
		~Edge();
		
		// Checks whether edge is crossed using necessary strike and hemisphere check
		int contains(Rvector3 query, Real lon);
		// Hemisphere check
		int crossesBoundary(Rvector3 query);
		// Necessary strike condition
		bool boundsPoint(Real lon);

		// Getters
		Rvector3 getPole();
		Real getBound1();
		Real getBound2();

		// Print function override
		friend std::ostream& operator<<(std::ostream& os, const Edge& edge);

	protected:
	
		Rvector3 pole;
		Real bound1;
		Real bound2;
		Real shooterDotPole;
};
#endif /* Edge_hpp */