#include "Polygon.hpp"

// Utilities

// Read a vector of AnglePairs from a CSV file
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

// Write a vector of booleans to CSV
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

// Write a vector of integers to CSV
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

// Transform a set of spherical coordinates to a different frame using the matrix transform 
AnglePair util::transformSpherical(const AnglePair &spherical,const Rmatrix33 &transform)
{
	Rvector3 cart = util::sphericalToCartesian(spherical);
	Rvector3 transformedCart = transform*cart;
	AnglePair transformedSpherical = util::cartesianToSpherical(transformedCart);

	return transformedSpherical;
}

// Checks whether a longitude is bounded by the minor arc defined by two other longitudes. 
bool util::lonBounded(Real bound1, Real bound2, Real lon)
{
	if ((bound2 - bound1) < M_PI)
		return ((lon >= bound1) && (lon <= bound2));
	else
		return !((lon >= bound1) && (lon <= bound2));
}

// Transform from cartesian to spherical coordinates (cone/clock)
AnglePair util::cartesianToSpherical(const Rvector3 &cart)
{
	Real x = cart[0];
	Real y = cart[1];
	Real z = cart[2];
	
	Real az = atan2(y,x); // clock angle
	Real inc = acos(z); // cone angle

	while (az < 0)
	{
		az += 2*M_PI;
	}

	
	AnglePair spherical = {inc,az};
	
	return spherical;
}

// Transform from spherical to cartesian coordinates (cone/clock to Cartesian unit-vector)
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