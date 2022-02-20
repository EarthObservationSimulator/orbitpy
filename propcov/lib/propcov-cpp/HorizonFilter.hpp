#ifndef HorizonFilter_hpp
#define HorizonFilter_hpp
#include "GridFilter.hpp"

class HorizonFilter : public GridFilter
{
    HorizonFilter();
    IntegerArray FilterGrid(Spacecraft* spacecraft, Grid* grid);

protected:

    Earth *centralBody;
    Real centralBodyRadius;
};

#endif /* HorizonFilter_hpp */