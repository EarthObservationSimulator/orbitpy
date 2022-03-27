#include "GridFilter.hpp"

bool GridFilter::IsPrefilter()
{
    return prefilter;
}

bool GridFilter::IsPostfilter()
{
    return postfilter;
}

void GridFilter::SetPrefilter(bool truthval)
{
    prefilter = truthval;
}

void GridFilter::SetPostfilter(bool truthval)
{
    postfilter = truthval;
}