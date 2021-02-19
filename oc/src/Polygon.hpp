#ifndef Polygon_hpp
#define Polygon_hpp

#include "Rvector3.hpp"
#include "Rmatrix33.hpp"
#include "gmatdefs.hpp"
#include "RealUtilities.hpp"
#include "GmatConstants.hpp"

typedef std::array<Real,2> AnglePair;

namespace util
{
	AnglePair cartesianToSpherical(const Rvector3 &cart);
	Rvector3 sphericalToCartesian(const AnglePair &spherical);

	AnglePair transformSpherical(const AnglePair &sherical, const Rmatrix33 &transform);
}

class Polygon
{
	public:
		
		static AnglePair cartesianToSpherical(const Rvector3&);
		static Rvector3 sphericalToCartesian(const AnglePair&);

		Polygon(std::vector<Rvector3>);
		Polygon(std::vector<AnglePair>);
		
		~Polygon();
		
		//virtual void preprocess();
		//virtual int contains(std::vector<Rvector3>);
		//virtual int contains(Rvector3);
		
		// Getter
		std::vector<Rvector3> getNodeArray();
		Rvector3 getNode(int index);
		
	protected:
		
		std::vector<Rvector3> nodes;
};

#endif /* Polygon_hpp */
