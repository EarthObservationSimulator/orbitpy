#include "SlicedPolygon.hpp"
#include "SliceTree.hpp"
#include <iostream>

Edge::Edge()
{
	Rvector3 pole = {1200000,120000,1222};
	Real bound1 = 0;
	Real bound2 = 0;
}

Rvector3 Edge::getPole()
{
	return pole;
}

Real Edge::getBound1()
{
	return bound1;
}

Real Edge::getBound2()
{
	return bound2;
}

std::ostream& operator<<(std::ostream& os, const Edge& edge)
{
    os << "Bound 1: " << edge.bound1 << "\n" << "Bound 2: " << edge.bound2 << "\n";
    return os;
}

Edge::Edge(Rvector3 cartNode1, Rvector3 cartNode2)
{
	pole = Cross(cartNode1,cartNode2);
	
	AnglePair node1 = util::cartesianToSpherical(cartNode1);
	AnglePair node2 = util::cartesianToSpherical(cartNode2);
	
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

	/*
	if ((bound2 - bound1) >= M_PI)
	{
		bound1 = bound2;
		bound2 = 2*M_PI;
	} 
	*/
	

	Rvector3 shooter = {0,0,1.0};
	shooterDotPole = shooter*pole;
}

Edge::Edge(AnglePair node1, AnglePair node2)
{	
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
	
	if (lon == bound1 || lon == bound2)
	{	
		Real delta = std::numeric_limits<double>::min();		
		return boundsPoint(lon + delta);
	}

	//return ((lon >= bound1) && (lon <= bound2));
	return util::lonBounded(bound1,bound2,lon);
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

SlicedPolygon::SlicedPolygon(std::vector<Rvector3> &nodesIn, Rvector3 containedIn) :
Polygon ()
{
	nodes = nodesIn;

	processed = false;
	contained = containedIn;
	generateEdgeArray();
}

SlicedPolygon::SlicedPolygon(std::vector<AnglePair> &nodesIn, AnglePair containedIn) :
Polygon ()
{
	nodes.resize(nodesIn.size());
	for (int i = 0;i < nodesIn.size();i++)
	{
		nodes[i] = util::sphericalToCartesian(nodesIn[i]);
	}	

	processed = false;
	contained = util::sphericalToCartesian(containedIn);
	TI = generateTI();
	edgeArray = generateEdgeArray();
}

SlicedPolygon::~SlicedPolygon(){}

AnglePair SlicedPolygon::toQueryFrame(AnglePair query)
{
	Rvector3 cartQueryI = util::sphericalToCartesian(query);
	Rvector3 cartQueryT = this->TI * cartQueryI;
	AnglePair sphericalQueryT = util::cartesianToSpherical(cartQueryT);

	return sphericalQueryT;
}


int SlicedPolygon::numCrossings(AnglePair query)
{
	int numCrossings = 0;

	
	// Query point in initial frame I
	Rvector3 cartQueryI = util::sphericalToCartesian(query);

	Rvector3 cartQueryT = TI*cartQueryI;
	AnglePair sphericalQueryT = util::cartesianToSpherical(cartQueryT);
	
	std::vector<int> indices = getSubset(sphericalQueryT);

	for (int index : indices)
	{
		Edge edge = this->edgeArray[index];
		numCrossings += edge.contains(cartQueryT,sphericalQueryT[1]);
	}
	
	return numCrossings;
}

void SlicedPolygon::addPreprocessor(Preprocessor* speedy)
{
	this->processed = true;
	this->sliceTree = speedy;
}

/*
void SlicedPolygon::preprocess()
{
	this->processed = true;

	Real crit1 = 1;
	Real crit2 = 16;

	this->sliceTree = new SliceTree(this->edgeArray,crit1,crit2);
}*/

std::vector<int> SlicedPolygon::getSubset(AnglePair query)
{
	if (this->processed)
		return this->sliceTree->getEdges(query);
	else
		return this->indexArray;
}

bool SlicedPolygon::contains(AnglePair query)
{
	int num;

	num = numCrossings(query);

	return ((num % 2) == false);
}

std::vector<int> SlicedPolygon::numCrossings(std::vector<AnglePair> queries)
{
	std::vector<int> results(queries.size());

	for (int i = 0; i < queries.size(); i++)
	{
		results[i] = numCrossings(queries[i]);
	}

	return results;
}

std::vector<bool> SlicedPolygon::contains(std::vector<AnglePair> queries)
{
	int num;
	std::vector<bool> results(queries.size());

	for (int i = 0; i < queries.size(); i++)
	{
		num = numCrossings(queries[i]);
		results[i] = ((num % 2) == false);
	}

	return results;
}

Rmatrix33 SlicedPolygon::generateTI()
{
	// Z axis of coordinate system is known point given as input
	Rvector3 z = contained;
	z.Normalize();
	// Y axis is cross of Z and the first node
	Rvector3 y = Cross(z,nodes[0]);
	y.Normalize();
	Rvector3 x = Cross(y,z);
	x.Normalize();
	
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
	for (int i = 0;i < nodes.size();i++)
		nodes[i] = TI * nodes[i];
		
	std::vector<Edge> edgeArray(nodes.size() - 1);
	indexArray.resize(nodes.size() - 1);

	int i;
	for (i = 0; i < edgeArray.size(); i++)
	{
		// Defines inclusion hemisphere
		edgeArray[i] = Edge(nodes[i],nodes[i+1]);
		indexArray[i] = i;
	}
	
	return edgeArray;
}

// Getters

std::vector<Edge> SlicedPolygon::getEdgeArray()
{
	return edgeArray;
}

std::vector<Real> SlicedPolygon::getLonArray()
{
	AnglePair latLon;
	
	std::vector<Real> lonArray(nodes.size());
	for (int i = 0; i < nodes.size(); i++)
	{
		latLon = util::cartesianToSpherical(nodes[i]);
		lonArray[i] = latLon[1];
	}

	return lonArray;
}

std::vector<Real> SlicedPolygon::getLatArray()
{
	AnglePair latLon;
	
	std::vector<Real> lonArray(nodes.size());
	for (int i = 0; i < nodes.size(); i++)
	{
		latLon = util::cartesianToSpherical(nodes[i]);
		lonArray[i] = latLon[0];
	}

	return lonArray;
}

std::ostream& operator<<(std::ostream& os, const SlicedPolygon& poly)
{
	int i = 0;

	os << "----------------\n";
	os << "DCM Description\n";
	os << "----------------\n";

	os << poly.TI;

	os << "----------------\n";

	os << "----------------\n";
	os << "Edge Description\n";
	os << "----------------\n";
	for (Edge edge : poly.edgeArray)
	{
    	os << "Edge " << i << ":\n" << edge;
		i++;
	}
	os << "----------------\n";

    return os;
}

Rmatrix33 SlicedPolygon::getTI()
{
	return TI;
}

