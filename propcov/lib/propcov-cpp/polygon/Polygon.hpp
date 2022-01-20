#ifndef Polygon_hpp
#define Polygon_hpp

#include "Rvector3.hpp"
#include "Rmatrix33.hpp"
#include "gmatdefs.hpp"
#include "RealUtilities.hpp"
#include "GmatConstants.hpp"
#include <iostream>
#include <fstream>
#include <array>

typedef std::array<Real,2> AnglePair;

namespace util
{
	AnglePair cartesianToSpherical(const Rvector3 &cart);
	Rvector3 sphericalToCartesian(const AnglePair &spherical);

	AnglePair transformSpherical(const AnglePair &sherical, const Rmatrix33 &transform);
	bool lonBounded(Real,Real,Real);

	std::vector<AnglePair> csvRead(std::string filename);
	void csvWrite(std::string filename, std::vector<bool>);
	void csvWrite(std::string filename, std::vector<int>);
}

class Polygon
{
	public:
		// Virtual function to define interface
		virtual std::vector<int> contains(std::vector<AnglePair>) = 0;
};

#endif /* Polygon_hpp */