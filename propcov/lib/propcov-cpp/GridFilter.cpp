#include "GridFilter.hpp"

bool GridFilter::IsPrefilter()
{
    return prefilter;
}

void GridFilter::SetPrefilter()
{
    prefilter = 1;
}

void GridFilter::SetPostfilter()
{
    prefilter = 0;
}