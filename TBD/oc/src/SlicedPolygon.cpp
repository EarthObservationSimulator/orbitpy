#include "SlicedPolygon.hpp"
#include "SliceTree.hpp"
#include <iostream>

// Edge class

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

// Sliced Polygon Class

// Constructor using cartesian vectors
SlicedPolygon::SlicedPolygon(std::vector<Rvector3> &verticesIn, Rvector3 containedIn)
{
	init(verticesIn,containedIn);
}

// Constructor using spherical coordinates
SlicedPolygon::SlicedPolygon(std::vector<AnglePair> &verticesIn, AnglePair containedIn)
{
	// Convert vertices to cartesian coordinates
	std::vector<Rvector3> cartVertices(verticesIn.size());
	for (int i = 0;i < verticesIn.size();i++)
	{
		cartVertices[i] = util::sphericalToCartesian(verticesIn[i]);
	}	
	Rvector3 cartContained = util::sphericalToCartesian(containedIn);

	init(cartVertices,cartContained);
}

// Common initializer for constructors
void SlicedPolygon::init(std::vector<Rvector3> &verticesIn, Rvector3 containedIn)
{
	vertices = verticesIn;
	processed = false;
	contained = containedIn;
	QI = generateQI();
	edgeArray = generateEdgeArray();
}

// Destructor
SlicedPolygon::~SlicedPolygon()
{
	if (processed)
		delete(preprocessor);
}

// Spherical coordinate transformation from initial frame to the query frame.
AnglePair SlicedPolygon::toQueryFrame(AnglePair query)
{
	Rvector3 cartQueryI = util::sphericalToCartesian(query);
	Rvector3 cartQueryQ = this->QI * cartQueryI;
	AnglePair sphericalQueryQ = util::cartesianToSpherical(cartQueryQ);

	return sphericalQueryQ;
}

// Adds a preprocessor to the sliced polygon
void SlicedPolygon::addPreprocessor(Preprocessor* speedy)
{
	this->processed = true;
	this->preprocessor = speedy;
}

// Returns the subset of eligible edges from the preprocessor, if present 
std::vector<int> SlicedPolygon::getSubset(AnglePair query)
{
	if (this->processed)
		return this->preprocessor->getEdges(query);
	else
		return this->indexArray;
}

// Counts number of crossings for the arc PQ for a single query point
// Returns -1 for number of crossings if the query point lies on the boundary
int SlicedPolygon::numCrossings(AnglePair query)
{
	int numCrossings = 0;

	// Query point assumed to be in initial frame I
	Rvector3 cartQueryI = util::sphericalToCartesian(query);

	Rvector3 cartQueryT = QI*cartQueryI;
	AnglePair sphericalQueryT = util::cartesianToSpherical(cartQueryT);
	
	std::vector<int> indices = getSubset(sphericalQueryT);

	for (int index : indices)
	{
		Edge edge = this->edgeArray[index];
		int contained = edge.contains(cartQueryT,sphericalQueryT[1]);

		if (contained == -1)
			return -1;

		numCrossings += edge.contains(cartQueryT,sphericalQueryT[1]);
	}
	
	return numCrossings;
}

// Counts number of crossings for the arc PQ for a vector of queries
// Returns -1 for number of crossings if the query point lies on the boundary
std::vector<int> SlicedPolygon::numCrossings(std::vector<AnglePair> queries)
{
	std::vector<int> results(queries.size());

	for (int i = 0; i < queries.size(); i++)
	{
		results[i] = numCrossings(queries[i]);
	}

	return results;
}

// Core query method for a single query point
// Returns 1 if contained, 0 if not contained, -1 if on boundary
int SlicedPolygon::contains(AnglePair query)
{
	int num = numCrossings(query);

	if (num == -1)
		return -1;

	return ((num % 2) == false);
}

// Core query method for a vector of queries
// Returns 1 if contained, 0 if not contained, -1 if on boundary
std::vector<int> SlicedPolygon::contains(std::vector<AnglePair> queries)
{
	int num;
	std::vector<int> results(queries.size());

	for (int i = 0; i < queries.size(); i++)
	{
		num = numCrossings(queries[i]);

		if (num == -1)
			results[i] = -1;

		results[i] = (int)((num % 2) == false);
	}

	return results;
}

// Generates the transformation matrix from the initial frame to the query frame
Rmatrix33 SlicedPolygon::generateQI()
{
	// Z axis of coordinate system is known point given as input
	Rvector3 z = contained;
	z.Normalize();
	// Y axis is cross of Z and the first node
	Rvector3 y = Cross(z,vertices[0]);
	y.Normalize();
	Rvector3 x = Cross(y,z);
	x.Normalize();
	
	Rmatrix33 QI(x[0],x[1],x[2],
		         y[0],y[1],y[2],
		         z[0],z[1],z[2]);

	return QI;
}

// Generates the vector of edge objects in the query frame
std::vector<Edge> SlicedPolygon::generateEdgeArray()
{
	for (int i = 0;i < vertices.size();i++)
		vertices[i] = QI * vertices[i];
		
	std::vector<Edge> edgeArray(vertices.size() - 1);
	indexArray.resize(vertices.size() - 1);

	int i;
	for (i = 0; i < edgeArray.size(); i++)
	{
		// Defines inclusion hemisphere
		edgeArray[i] = Edge(vertices[i],vertices[i+1]);
		indexArray[i] = i;
	}
	
	return edgeArray;
}

// Getters

std::vector<Edge> SlicedPolygon::getEdgeArray()
{
	return edgeArray;
}

// Returns a vector of vertex longitudes in the query frame
std::vector<Real> SlicedPolygon::getLonArray()
{
	AnglePair latLon;
	
	std::vector<Real> lonArray(vertices.size());
	for (int i = 0; i < vertices.size(); i++)
	{
		latLon = util::cartesianToSpherical(vertices[i]);
		lonArray[i] = latLon[1];
	}

	return lonArray;
}

// Returns a vector of vertex latitudes in the query frame
std::vector<Real> SlicedPolygon::getLatArray()
{
	AnglePair latLon;
	
	std::vector<Real> latArray(vertices.size());
	for (int i = 0; i < vertices.size(); i++)
	{
		latLon = util::cartesianToSpherical(vertices[i]);
		latArray[i] = latLon[0];
	}

	return latArray;
}

// Returns transformation matrix from initial to query frame
Rmatrix33 SlicedPolygon::getQI()
{
	return QI;
}

// Override function to print a SlicedPolygon
std::ostream& operator<<(std::ostream& os, const SlicedPolygon& poly)
{
	int i = 0;

	os << "----------------\n";
	os << "DCM Description\n";
	os << "----------------\n";

	os << poly.QI;

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