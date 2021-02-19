#include "SlicedPolygon.hpp"
#include <iostream>

Edge::Edge()
{
	Rvector3 pole = {1200000,120000,1222};
	Real bound1 = 0;
	Real bound2 = 0;
	Real B = 0;
}

Rvector3 Edge::getPole()
{
	return pole;
}

Edge::Edge(Rvector3 cartNode1, Rvector3 cartNode2)
{
	pole = Cross(cartNode1,cartNode2);
	
	AnglePair node1 = util::cartesianToSpherical(cartNode1);
	AnglePair node2 = util::cartesianToSpherical(cartNode2);
	
	// For strike condition edge case
	B = node2[1];
	
	// Sets bounds1 to the lesser of the two longitudes/thetas
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

Edge::Edge(AnglePair node1, AnglePair node2)
{
	// For strike condition edge case
	B = node2[1];
	
	// Sets bounds1 to the lesser of the two longitudes/thetas
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
	
	// These direction definitions are hard
	pole = Cross(node1Cart,node2Cart);

	Rvector3 shooter = {0,0,1.0};
	shooterDotPole = shooter*pole;
}

// Condition of necessary strike
bool Edge::boundsPoint(double lon)
{
	
	if (B == lon)
	{
		return 0;
	}

	if ((bound2 - bound1) < M_PI)
	{
		return ((lon >= bound1) && (lon <= bound2));
	}
	else
	{

		return !((lon >= bound1) && (lon <= bound2));
	}
}

int Edge::crossesBoundary(Rvector3 query)
{
	Real queryDotPole = query*pole;
	
	// Directly on an edge
	if ( queryDotPole == 0.0)
 		return -100000;
	// On opposite side of edge as shooter
 	else if (queryDotPole*shooterDotPole < 0)
 		return 1;
 	else
 		return 0;
 }

int Edge::contains(Rvector3 query, Real lon)
{
	if (boundsPoint(lon))
		return crossesBoundary(query);
	
	return 0;
}


SlicedPolygon::SlicedPolygon(std::vector<Rvector3> nodesIn, Rvector3 containedIn) :
Polygon(nodesIn)
{
	contained = containedIn;
	generateEdgeArray();
}

SlicedPolygon::SlicedPolygon(std::vector<AnglePair> nodesIn, AnglePair containedIn) :
Polygon (nodesIn)
{
	contained = util::sphericalToCartesian(containedIn);
	TI = generateTI();
	edgeArray = generateEdgeArray();
}

SlicedPolygon::~SlicedPolygon(){}


int SlicedPolygon::numCrossings(AnglePair query)
{
	int numCrossings = 0;

	// Query point in initial frame I
	Rvector3 cartQueryI = util::sphericalToCartesian(query);

	Rvector3 cartQueryT = TI*cartQueryI;
	AnglePair sphericalQueryT = util::cartesianToSpherical(cartQueryT);
	
	for (Edge edge : edgeArray)
	{
		numCrossings += edge.contains(cartQueryT,sphericalQueryT[1]);
	}
	return numCrossings;
}

Rmatrix33 SlicedPolygon::generateTI()
{
	// Z axis of coordinate system is known point given as input
	Rvector3 z = contained;
	z.Normalize();
	// X axis is cross of Z and the first node (arbitrary)
	Rvector3 x = Cross(z,nodes[0]);
	x.Normalize();
	Rvector3 y = Cross(z,x);
	y.Normalize();
	
	Rmatrix33 IT(x[0],y[0],z[0],
		         x[1],y[1],z[1],
		         x[2],y[2],z[2]);
	
	Rmatrix33 TI(x[0],x[1],x[2],
		         y[0],y[1],y[2],
		         z[0],z[1],z[2]);

	return TI;

}


std::vector<Edge> SlicedPolygon::generateEdgeArray()
{
	std::vector<Rvector3> nodesTransformed(nodes.size());
	for (int i = 0;i < nodes.size();i++)
		nodesTransformed[i] = TI*nodes[i];
	
	std::vector<Edge> edgeArray;
	edgeArray.resize(nodes.size()-1);

	int i;
	for (i = 0;i < edgeArray.size();i++)
	{
		// Defines inclusion hemisphere
		edgeArray[i] = Edge(nodesTransformed[i],nodesTransformed[i+1]);
	}
	
	return edgeArray;
}

// Getters

std::vector<Edge> SlicedPolygon::getEdgeArray()
{
	return edgeArray;
}

Rmatrix33 SlicedPolygon::getTI()
{
	return TI;
}

