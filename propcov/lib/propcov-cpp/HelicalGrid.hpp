#ifndef HelicalGrid_hpp
#define HelicalGrid_hpp

#include "Grid.hpp"

class HelicalGrid : public Grid
{
public:
    /// Class construction/destruction
    HelicalGrid();
    HelicalGrid(const HelicalGrid &copy);
    HelicalGrid &operator=(const HelicalGrid &copy);

    virtual ~HelicalGrid();

    /// Add user defined points to the group
    virtual void AddUserDefinedPoints(const RealArray &lats,
                                      const RealArray &lons);
    /// Compute and add the specified number of user-defined points
    virtual void AddHelicalPointsByNumPoints(Integer numGridPoints);
    /// Compute and add points to the list of points, based on the input
    /// angle
    virtual void AddHelicalPointsByAngle(Real angleBetweenPoints);
    /// Get point position for given index
    // virtual Rvector3* GetPointPositionVector(Integer idx);
    /// Get the latitude and longitude for the given index
    virtual void GetLatAndLon(Integer idx, Real &theLat, Real &theLon);
    std::pair<Real, Real> GetLatAndLon(Integer idx);
    /// Get the number of points
    virtual Integer GetNumPoints();
    /// Get the latitude and longitude vectors
    virtual void GetLatLonVectors(RealArray &lats, RealArray &lons);
    virtual std::pair<RealArray, RealArray> GetLatLonVectors();

    /// Set the latitude and longitude bounds values
    virtual void SetLatLonBounds(Real latUp, Real latLow,
                                 Real lonUp, Real lonLow);

    // Get string representation for output file
    virtual std::vector<std::string> GetPointHeader();
    virtual std::vector<Real> GetPoint(Integer idx);
    virtual std::vector<RealArray> GetPoints();

    // todo 
    //virtual std::vector<RealArray> GetPoints(Integer idx);

protected:
    /// Latitude coordinates of grid points
    RealArray lat;
    /// Longitude coordinates of grid points
    RealArray lon;

    /// Upper bound on allowable latitude -pi/2 <= latUpper <= pi/2
    Real latUpper;
    /// Upper bound on allowable latitude -pi/2 <= latLower <= pi/2
    Real latLower;
    /// Upper bound on allowable longitude
    Real lonUpper;
    /// Upper bound on allowable longitude
    Real lonLower;

    /// Protected methods for managing points

    void AccumulatePoints(Real lat1, Real lon1);
    void ComputeTestPoints(const std::string &modelName, Integer numGridPts);
    void ComputeHelicalPoints(Integer numReqPts);
};

#endif /* HelicalGrid_hpp */