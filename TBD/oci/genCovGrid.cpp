//------------------------------------------------------------------------------
//                            Generate Coverage Grid
//------------------------------------------------------------------------------
//
// Author: Vinay Ravindra
// Created: 2020.02.15
//
/**
 * Generate coverage grid for input region (possibly multiple) bounds.
 * 
 * .. warning:: The OC "AddHelicalPointsByNumPoints" function adds the 
 * input number of points over entire globe and later discards points outside
 * the latitude, longitude bounds.
 * 
 */
//------------------------------------------------------------------------------

#include <iostream>
#include <string>
#include <sstream>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <iomanip> 
#include <fstream>
#include "gmatdefs.hpp"
#include "GmatConstants.hpp"
#include "Rvector6.hpp"
#include "Rvector3.hpp"
#include "Rmatrix.hpp"
#include "RealUtilities.hpp"
#include "MessageInterface.hpp"
#include "Earth.hpp"
#include "PointGroup.hpp"
#include "TimeTypes.hpp"

#include "oci_utils.h"

using namespace std;
using namespace GmatMathUtil;
using namespace GmatMathConstants;


void add_grid_points_in_region(const int regionID, const Real gridRes_deg, const Real latUp_deg, const Real latLow_deg, const Real lonUp_deg, const Real lonLow_deg, RealArray& regionIDArray, RealArray& latArray, RealArray& lonArray){
  
  PointGroup   *regionPgroup; // temporary point group to hold points at a region
  regionPgroup = new PointGroup();
  /*Set the bounds on the region */
  regionPgroup->SetLatLonBounds(latUp_deg*RAD_PER_DEG, latLow_deg*RAD_PER_DEG, lonUp_deg*RAD_PER_DEG, lonLow_deg*RAD_PER_DEG);
  regionPgroup->AddHelicalPointsByAngle(gridRes_deg*RAD_PER_DEG);
  for (Integer pointIdx = 0; pointIdx < regionPgroup->GetNumPoints(); pointIdx++)
  {
      Real latValue;
      Real lonValue;
      regionPgroup->GetLatAndLon(pointIdx, latValue, lonValue);
      regionIDArray.push_back(regionID);
      latArray.push_back(latValue);
      lonArray.push_back(lonValue);
  }  
  delete regionPgroup;
}

/**
 * 
 * Multiple below entries for each region.
 * @param regionID region index (integer)
 * @param lat_upper Latitude upper in degrees
 * @param lat_lower Latitude lower in degrees
 * @param lon_upper Longitude upper in degrees
 * @param lon_lower Longitude lower in degrees
 * @param gridRes Grid resolution in degrees
 * 
 * .. code-block:: bash

      /../examples/example1/covGrid 0,-22.16,-24.04,133.75,131.62,1
 *
 */
int main(int argc, char *argv[])
{
    string covGridFn;
    std::vector<std::string> _regionInf(argc-2);
    RealArray regionIDArray, latArray, lonArray;    
    if(argc<3){
      MessageInterface::ShowMessage("Error inprocessing inputs.\n");
      MessageInterface::ShowMessage("Please make sure to input: coverage grid filename and \
                                     atleast one region specifications.\n");
      exit(1);
    }

    covGridFn = argv[1];

    /** Process each region seperately **/
    for(int i=2; i<argc; i++){
      _regionInf[i-2] = argv[i];
      
      RealArray x(oci_utils::convertStringVectortoRealVector(oci_utils::extract_dlim_str(_regionInf[i-2], ',')));

      /** Extract region specifications **/
      int regionID = x[0];
      Real lat_upper = x[1];
      Real lat_lower = x[2];
      Real lon_upper = x[3];
      Real lon_lower = x[4];

      Real gridRes = x[5];

      add_grid_points_in_region(regionID, gridRes, lat_upper, lat_lower, lon_upper, lon_lower, 
                                regionIDArray, latArray, lonArray);  
    
    }

  // Write Coverage Grid file
  ofstream covGrid; 
  covGrid.open(covGridFn.c_str(),ios::binary | ios::out);
  covGrid<<"regi,gpi,lat[deg],lon[deg]\n";
  for (Integer gpi = 0; gpi < latArray.size(); gpi++)
  {
      Real lat_deg;
      Real lon_deg; 
      int rgi;
      
      rgi = regionIDArray[gpi];
      lat_deg = latArray[gpi] * DEG_PER_RAD;
      lon_deg = lonArray[gpi] * DEG_PER_RAD;

      // Bring the longitude value in the range -180 to +180 deg.
      if(lon_deg>180){
        lon_deg = lon_deg - 360;
      }else if(lon_deg<-180){
        lon_deg = lon_deg + 360;
      }

      covGrid << rgi << ",";
      covGrid << gpi << ",";
      covGrid << std::fixed << std::setprecision(4) << lat_deg << ",";
      covGrid << std::fixed << std::setprecision(4) << lon_deg << "\n";
  }
  covGrid.close();

  return 0;
}
