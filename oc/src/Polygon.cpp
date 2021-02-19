#include "Polygon.hpp"

// Utilities

AnglePair util::transformSpherical(const AnglePair &spherical,const Rmatrix33 &transform)
{
	Rvector3 cart = util::sphericalToCartesian(spherical);
	Rvector3 transformedCart = transform*cart;
	AnglePair transformedSpherical = util::cartesianToSpherical(transformedCart);

	return transformedSpherical;
}

AnglePair util::cartesianToSpherical(const Rvector3 &cart)
{
	Real x = cart[0];
	Real y = cart[1];
	Real z = cart[2];
	
	Real az = atan2(y,x);
	Real inc = acos(z);

	while (az < 0)
	{
		az += 2*M_PI;
	}

	
	AnglePair spherical = {inc,az};
	
	return spherical;
}

Rvector3 util::sphericalToCartesian(const AnglePair &spherical)
{
	Real x,y,z;
	Real inc = spherical[0];
	Real az = spherical[1];
	
	x = sin(inc)*cos(az);
	y = sin(inc)*sin(az);
	z = cos(inc);
	
	Rvector3 cartesian = {x,y,z};
	
	return cartesian;
}


AnglePair Polygon::cartesianToSpherical(const Rvector3 &cart)
{
	Real x = cart[0];
	Real y = cart[1];
	Real z = cart[2];
	
	Real phi = atan2(y,x);
	Real theta = acos(z);
	
	AnglePair spherical = {theta,phi};
	
	return spherical;
}

Rvector3 Polygon::sphericalToCartesian(const AnglePair &spherical)
{
	Real x,y,z;
	Real theta = spherical[0];
	Real phi = spherical[1];
	
	x = sin(theta)*cos(phi);
	y = sin(theta)*sin(phi);
	z = cos(theta);
	
	Rvector3 cartesian = {x,y,z};
	
	return cartesian;
}

Polygon::Polygon(std::vector<Rvector3> nodesIn) :
nodes (nodesIn)
{
}

Polygon::Polygon(std::vector<AnglePair> nodesIn)
{
	
	nodes.resize(nodesIn.size());
	for (int i = 0;i < nodesIn.size();i++)
	{
		nodes[i] = sphericalToCartesian(nodesIn[i]);
	}	
}

Polygon::~Polygon(){}

Rvector3 Polygon::getNode(int index)
{
	return nodes[index];
}

std::vector<Rvector3> Polygon::getNodeArray()
{
	return nodes;
}
