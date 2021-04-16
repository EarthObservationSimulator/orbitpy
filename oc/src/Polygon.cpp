#include "Polygon.hpp"

// Utilities

std::vector<AnglePair> util::csvRead(std::string filename)
{
	std::vector<AnglePair> vertices;

	std::ifstream ip(filename);

	std::string lat,lon;
	while (ip.good())
	{
		getline(ip,lat,',');
		getline(ip,lon,'\n');
		AnglePair latLon = {std::stod(lat),std::stod(lon)};
		vertices.push_back(latLon);
	}
	ip.close();

	return vertices;
}

void util::csvWrite(std::string filename, std::vector<bool> contained)
{
	std::ofstream myFile;
	myFile.open(filename);

	for (int i = 0; i < contained.size(); i++)
	{
		myFile << contained[i] << "\n";
	}
	myFile.close();
}

void util::csvWrite(std::string filename, std::vector<int> contained)
{
	std::ofstream myFile;
	myFile.open(filename);

	for (int i = 0; i < contained.size(); i++)
	{
		myFile << contained[i] << "\n";
	}
	myFile.close();
}

AnglePair util::transformSpherical(const AnglePair &spherical,const Rmatrix33 &transform)
{
	Rvector3 cart = util::sphericalToCartesian(spherical);
	Rvector3 transformedCart = transform*cart;
	AnglePair transformedSpherical = util::cartesianToSpherical(transformedCart);

	return transformedSpherical;
}

bool util::lonBounded(Real bound1, Real bound2, Real lon)
{
	if ((bound2 - bound1) < M_PI)
	{
		return ((lon >= bound1) && (lon <= bound2));
	}
	else
	{

		return !((lon >= bound1) && (lon <= bound2));
	}
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

Polygon::Polygon(){}

Polygon::~Polygon(){}