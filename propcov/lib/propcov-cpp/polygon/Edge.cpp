#include "Edge.hpp"
#include <iostream>

// Default constructor for edge
Edge::Edge()
{
	Rvector3 pole = {0,0,1};
	Real bound1 = 0;
	Real bound2 = 0;
}

// Constructor for an edge using cartesian coordinates
Edge::Edge(Rvector3 cartNode1, Rvector3 cartNode2)
{
	pole = Cross(cartNode1,cartNode2);
	
	AnglePair node1 = util::cartesianToSpherical(cartNode1);
	AnglePair node2 = util::cartesianToSpherical(cartNode2);
	
	// Sets bounds1 to the lesser of the two longitudes
	if (node1[1] < node2[1])
	{
		bound1 = node1[1];
		bound2 = node2[1];
	}
	else
	{
		bound1 = node2[1];
		bound2 = node1[1];
	}

	Rvector3 shooter = {0,0,1.0};
	shooterDotPole = shooter*pole;
}

// Constructor for an edge using spherical coordinates
Edge::Edge(AnglePair node1, AnglePair node2)
{	
	// Sets bounds1 to the lesser of the two longitudes
	if (node1[1] < node2[1])
	{
		bound1 = node1[1];
		bound2 = node2[1];
	}
	else
	{
		bound1 = node2[1];
		bound2 = node1[1];
	}
	
	Rvector3 node1Cart = util::sphericalToCartesian(node1);
	Rvector3 node2Cart = util::sphericalToCartesian(node2);
	
	pole = Cross(node1Cart,node2Cart);

	Rvector3 shooter = {0,0,1.0};
	shooterDotPole = shooter*pole;
}

// Destructor
Edge::~Edge()
{

}

// Condition of necessary strike
bool Edge::boundsPoint(double lon)
{
	
	if (lon == bound1 || lon == bound2)
	{	
		Real delta = std::numeric_limits<double>::min();		
		return boundsPoint(lon + delta);
	}

	return util::lonBounded(bound1,bound2,lon);
}

// Hemisphere check
int Edge::crossesBoundary(Rvector3 query)
{
	Real queryDotPole = query*pole;
	
	// Directly on an edge
	if ( queryDotPole == 0.0)
 		return -1;
	// On opposite side of edge as shooter
 	else if (queryDotPole*shooterDotPole < 0)
 		return 1;
	// On same side of edge as shooter
 	else
 		return 0;
 }

int Edge::contains(Rvector3 query, Real lon)
{
	if (boundsPoint(lon))
		return crossesBoundary(query);
	
	return 0;
}

// Getters for edge class

// Returns the pole associated with an edge in the query frame as a cartesian vector
Rvector3 Edge::getPole()
{
	return pole;
}

// Returns the smaller vertex longitude of an edge in the query frame
Real Edge::getBound1()
{
	return bound1;
}

// Returns the larger vertex longitude of an edge in the query frame
Real Edge::getBound2()
{
	return bound2;
}

// Override function to print an edge
std::ostream& operator<<(std::ostream& os, const Edge& edge)
{
    os << "Bound 1: " << edge.bound1 << "\n" << "Bound 2: " << edge.bound2 << "\n";
    return os;
}