#ifndef GridFilter_hpp
#define GridFilter_hpp

#include "Spacecraft.hpp"
#include "Grid.hpp"
#include "gmatdefs.hpp"

// Pure virtual class
class GridFilter
{
    public:
        virtual std::vector<Integer> FilterGrid() = 0;
        // Returns true if the filter is set to prefilter
        bool IsPrefilter();
        // Returns true if the filter is set to postfilter
        bool IsPostfilter();
        // Set the filter to be applied before the FOV check
        void SetPrefilter(bool);
        // Set the filter to be applied after the FOV check
        void SetPostfilter(bool);

    protected:
        // Default set to prefilter
        bool prefilter = 1;
        bool postfilter = 0;
};

#endif /* GridFilter_hpp */
