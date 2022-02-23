#ifndef GridFilter_hpp
#define GridFilter_hpp

#include "Spacecraft.hpp"
#include "Grid.hpp"
#include "gmatdefs.hpp"

// Pure virtual class
class GridFilter
{
    public:
        virtual IntegerArray FilterGrid();
        // Returns true if the filter is set to prefilter
        bool IsPrefilter();
        // Set the filter to be applied before the FOV check
        void SetPrefilter();
        // Set the filter to be applied after the FOV check
        void SetPostfilter();

    protected:
        bool prefilter = 1;
};

#endif /* GridFilter_hpp */