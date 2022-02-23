#ifndef HorizonFilter_hpp
#define HorizonFilter_hpp
#include "GridFilter.hpp"
#include "Earth.cpp"

class HorizonFilter : public GridFilter
{
public:

    HorizonFilter(Spacecraft* spacecraft, Grid* grid);
    IntegerArray FilterGrid();

protected:

    Grid *grid;
    Spacecraft *spacecraft;
    Earth *centralBody;
    Real centralBodyRadius;

    /// array of all unit position vectors of points @todo: Move this to the PointGroup class.
    std::vector<Rvector3*>     pointArray;
    /// feasibility values for each point
    std::vector<bool>          feasibilityTest;

    /// Get the central body fixed state at the input time for the input cartesian state
    virtual Rvector6          GetCentralBodyFixedState(Real jd, const Rvector6& scCartState);
    /// Check the grid feasibility for the input point with the input body fixed state
    virtual bool              CheckGridFeasibility(Integer ptIdx,
                                    const Rvector3& bodyFixedState);
    /// Check the grid feasibility for all points for the input body fixed state
    virtual void              CheckGridFeasibility(
                                    const Rvector3& bodyFixedState);
    
    /// local Rvectors used for Grid Feasibility calculations
    /// (for performance)
    Rvector3 rangeVec;
    Rvector3 unitRangeVec;  
    Rvector3 bodyUnit;
    Rvector3 unitPtPos;
    Rvector3 ptPos;
};

#endif /* HorizonFilter_hpp */