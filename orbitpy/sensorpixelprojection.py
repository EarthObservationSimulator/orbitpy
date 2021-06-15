import numpy as np
import os
import subprocess
import json
import shapely
import cartopy.geodesic
import math

from math import radians, cos, sin, asin, sqrt

import logging
logger = logging.getLogger(__name__)


'''
_date = 2451179.50000143
_state_eci = "-1092.4659444383967184,-4942.8057797955052592,-4947.4006284895149292,7.4143317234309798,-0.8342063358223765,-0.8027120651157109"
_satOrien = "1,2,3,0,25,0"
_senOrien = "1,2,3,0,0,0"
angleWidth = 60
angleHeight = 60
widthDetectors = 5
heightDetectors = 5
outFilePath = "../senFovProj.json"
'''

class SensorPixelProjection():

    @staticmethod
    def get_pixel_position_data(user_dir, date_JDUt1, state_eci, sat_orien, sen_orien, angleWidth, angleHeight, heightDetectors, widthDetectors):
        """
            :param state_eci: comma delimited string of the satellite ECI state
            :paramtype state_eci: str

            :param sat_orien: comma delimited string of the satellite orientation in format of Euler sequence and angles eg: "1,2,3,10,0,30"  
            :paramtype sat_orien: str

            :param sen_orien: comma delimited string of the sensor orientation in format of Euler sequence and angles eg: "1,2,3,10,0,30"
            :paramtype sen_orien: str

        """

        dir_path = os.path.dirname(os.path.realpath(__file__))

        outFilePath = user_dir + "oci_senFovProj.json" # temporary file TODO: delete later?
        
        try:
            result = subprocess.run([
                        os.path.join(dir_path, '..', 'oci', 'bin', 'sensor_fov_projector'),
                        str(date_JDUt1), str(state_eci), str(sat_orien), str(sen_orien), 
                        str(angleWidth), str(angleHeight), str(widthDetectors), str(heightDetectors), str(outFilePath)
                        ], check= True)
        except:
            raise RuntimeError('Error executing "sensor_fov_projection" OC script')

        with open(outFilePath) as f:
            pixel_pos = json.load(f)

        num_pixel_rows = int(pixel_pos['heightDetectors'])
        num_pixel_columns = int(pixel_pos['widthDetectors'])

        """ Discern each of the pixel edges and edge-poles from the data. Definition of the edges is as follows:

            edge_1 is the left edge of the pixel with endPoint_1 the upper point, and endPoint_2 the lower point.
            edge_2 is the bottom edge of the pixel with endPoint_1 the left point, and endPoint_2 the right point.
            edge_3 is the right edge of the pixel with endPoint_1 the lower point, and endPoint_2 the upper point.
            edge_4 is the upper edge of the pixel with endPoint_1 the right point, and endPoint_2 the left point.

            The pole-position is given for each edge as Cartesian position vector in EF frame. 

            eg: 
            ```
            {
                "pixel": 
                    { "@id":24, 
                    "center":{"lon[deg]": -1, "lat[deg]": 0}, 
                    "edge_1": ...., 
                    "edge_2":....., 
                    "edge_3":...., 
                    "edge_4":....
                    }
            }
            where,
                "edge_1" : {"pole_pos":[0.5, -0.1, 0.3], "endPoint_1":{"lon[deg]": -0.109032, "lat[deg]": 0.103518}, "endPoint_2":{"lon[deg]": -0.107251, "lat[deg]": -0.104817}}
            ```
        """

        pixel = []
        k = 0
        for n in range(0,num_pixel_columns):
            for m in range(0,num_pixel_rows):
                pixel.append({})
                pixel[k] = {
                                "pixel": {
                                "@id": (str(m)+str(n)),
                                "center":   {"lon[deg]": pixel_pos['centerIntersectionGeoCoords'][k][1], "lat[deg]": pixel_pos['centerIntersectionGeoCoords'][k][0]}
                                }
                            }                   
                k = k + 1

        # allocate edges, poles for all the pixels
        # geo coords
        k=0 # pixel number indexed from '0'
        for n in range(0,num_pixel_columns):
            for m in range(0,num_pixel_rows):
                pixel[k]["pixel"].update({
                                "edge_1": {
                                    "endPoint_geoc_1":{ "lon[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n][1], "lat[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n][0]},
                                    "endPoint_geoc_2":{ "lon[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+1][1], "lat[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+1][0]},
                                    "endPoint_cart_1": pixel_pos['cornerIntersectionCartesian'][k+n],
                                    "endPoint_cart_2": pixel_pos['cornerIntersectionCartesian'][k+n+1]
                                },
                                "edge_3": {
                                    "endPoint_geoc_1":{ "lon[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+1+num_pixel_rows+1][1], "lat[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+1+num_pixel_rows+1][0]},
                                    "endPoint_geoc_2":{ "lon[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+num_pixel_rows+1][1], "lat[deg]": pixel_pos['cornerIntersectionGeoCoords'][k+n+num_pixel_rows+1][0]},
                                    "endPoint_cart_1": pixel_pos['cornerIntersectionCartesian'][k+n+1+num_pixel_rows+1],
                                    "endPoint_cart_2": pixel_pos['cornerIntersectionCartesian'][k+n+num_pixel_rows+1]
                                }
                            })
                pixel[k]["pixel"].update({
                                "edge_2": {
                                    "endPoint_geoc_1":{ "lon[deg]": pixel[k]['pixel']['edge_1']['endPoint_geoc_2']["lon[deg]"], "lat[deg]": pixel[k]['pixel']['edge_1']['endPoint_geoc_2']["lat[deg]"]},
                                    "endPoint_geoc_2":{ "lon[deg]": pixel[k]['pixel']['edge_3']['endPoint_geoc_1']["lon[deg]"], "lat[deg]": pixel[k]['pixel']['edge_3']['endPoint_geoc_1']["lat[deg]"]},
                                    "endPoint_cart_1": pixel[k]['pixel']['edge_1']['endPoint_cart_2'],
                                    "endPoint_cart_2":pixel[k]['pixel']['edge_3']['endPoint_cart_1']
                                },
                                "edge_4": {
                                    "endPoint_geoc_1":{ "lon[deg]": pixel[k]['pixel']['edge_3']['endPoint_geoc_2']["lon[deg]"], "lat[deg]": pixel[k]['pixel']['edge_3']['endPoint_geoc_2']["lat[deg]"]},
                                    "endPoint_geoc_2":{ "lon[deg]": pixel[k]['pixel']['edge_1']['endPoint_geoc_1']["lon[deg]"], "lat[deg]": pixel[k]['pixel']['edge_1']['endPoint_geoc_1']["lat[deg]"]},
                                    "endPoint_cart_1": pixel[k]['pixel']['edge_3']['endPoint_cart_2'],
                                    "endPoint_cart_2": pixel[k]['pixel']['edge_1']['endPoint_cart_1']
                                }
                            })
                pixel[k]["pixel"]["edge_1"].update({"pole_pos_geoc":{"lon[deg]": pixel_pos["poleIntersectionGeocoords"][num_pixel_rows+1+n][1], "lat[deg]": pixel_pos["poleIntersectionGeocoords"][num_pixel_rows+1+n][0]}})
                pixel[k]["pixel"]["edge_3"].update({"pole_pos_geoc":{"lon[deg]": pixel_pos["poleIntersectionGeocoords"][num_pixel_rows+1+n+1][1], "lat[deg]": pixel_pos["poleIntersectionGeocoords"][num_pixel_rows+1+n+1][0]}})
                pixel[k]["pixel"]["edge_2"].update({"pole_pos_geoc":{"lon[deg]": pixel_pos["poleIntersectionGeocoords"][m+1][1], "lat[deg]": pixel_pos["poleIntersectionGeocoords"][m+1][0]}})
                pixel[k]["pixel"]["edge_4"].update({"pole_pos_geoc":{"lon[deg]": pixel_pos["poleIntersectionGeocoords"][m][1], "lat[deg]": pixel_pos["poleIntersectionGeocoords"][m][0]}})

                pixel[k]["pixel"]["edge_1"].update({"pole_pos_cart":pixel_pos["poleIntersectionCartesian"][num_pixel_rows+1+n]})
                pixel[k]["pixel"]["edge_3"].update({"pole_pos_cart":pixel_pos["poleIntersectionCartesian"][num_pixel_rows+1+n+1]})
                pixel[k]["pixel"]["edge_2"].update({"pole_pos_cart":pixel_pos["poleIntersectionCartesian"][m+1]})
                pixel[k]["pixel"]["edge_4"].update({"pole_pos_cart":pixel_pos["poleIntersectionCartesian"][m]})

                k = k + 1

        return pixel

        #with open("../pixeldata.json", 'w') as fp:
        #    print(json.dump( pixel, fp, indent=4))

class PixelShapelyPolygon():
    """
        :ivar pixeldata: List of dictinaries with each dictinary containing the pixel-data (center-position, edges, poles)
        :vartype pixeldata: list, dict
    """
    def __init__(self, pixeldata):
        self.pixeldata = pixeldata

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        if(lon1>180):
            lon1 = lon1-360.0
        if(lon2>180):
            lon2 = lon2-360.0
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        # Radius of earth in kilometers is 6371
        km = 6371* c
        return km

    @staticmethod
    def get_circle(pole_lon_c, pole_lat_c, radius_m):
        """ 
            :param pole_lon_c: Pole center longitude in degrees
            :paramtype pole_lon_c: float

            :param pole_lat_c: Pole center latitude in degrees
            :paramtype pole_lat_c: float

            :param radius_m: Radius of circle in meters
            :paramtype radius_m: float

            :returns: points along circle
            :rtype: np.array
        """
        if(pole_lon_c > 180):
            pole_lon_c = pole_lon_c - 360
        circle_points = cartopy.geodesic.Geodesic(flattening=0).circle(lon=pole_lon_c, lat=pole_lat_c, radius=radius_m, n_samples=10000, endpoint=False) # flattening=0 must be specified to indcate sphere, the radius is the along the sphere
        return np.asarray(circle_points)

    @staticmethod
    def get_arc_points(circle_points, corner_1, corner_2):
        """ Get the points along the circle (shortest arc) """
        
        def compute_great_circle_distance(pnt1, pnt2):
            return PixelShapelyPolygon.haversine(pnt1["lon[deg]"], pnt1["lat[deg]"], pnt2["lon[deg]"], pnt2["lat[deg]"])
        # compute the distances between the circle points and the pixel corners. Ideally for one of the entries the distance should be 0.
        dist_1 = []
        dist_2 = []
        for k in range(0, len(circle_points)):
            circle_pnt = {"lon[deg]":circle_points[k][0], "lat[deg]":circle_points[k][1]}
            dist_1.append(compute_great_circle_distance(corner_1, circle_pnt))
            dist_2.append(compute_great_circle_distance(corner_2, circle_pnt))
        
        #print(min(dist_1))
        #print(min(dist_2))
        # get the index of the arc extreme that is the shortest distance to corner_1, corner_2
        arc_ext_1_indx = dist_1.index(min(dist_1))
        arc_ext_2_indx = dist_2.index(min(dist_2))

        # get the arc-points
        # two arcs are possible, say arc-A, arc-B, the smaller lenght arc should be chosen
        if(arc_ext_2_indx > arc_ext_1_indx):
            arc_points_A = circle_points[arc_ext_1_indx:arc_ext_2_indx+1]
            arc_points_B = np.concatenate((circle_points[arc_ext_2_indx:-1],circle_points[0:arc_ext_1_indx+1]), axis=0) 
        else:
            arc_points_A = circle_points[arc_ext_2_indx:arc_ext_1_indx]
            arc_points_B = np.concatenate((circle_points[arc_ext_1_indx:-1],circle_points[0:arc_ext_2_indx+1]), axis=0) 

        if(np.shape(arc_points_A)[0] < np.shape(arc_points_B)[0]):
            return arc_points_A
        else:
            return arc_points_B

    @staticmethod
    def get_small_circle_radius(pole_pos_cart, edge_endPoint_cart):
        """  """
        pole_pos_cart = np.array(pole_pos_cart)
        edge_endPoint_cart = np.array(edge_endPoint_cart)

        # normalize the vectors
        pole_pos_cart = pole_pos_cart / np.linalg.norm(pole_pos_cart)
        edge_endPoint_cart = edge_endPoint_cart / np.linalg.norm(edge_endPoint_cart)

        # compute the angle between them
        theta = np.arccos(np.dot(pole_pos_cart, edge_endPoint_cart))

        #print("theta = ", theta*180/np.pi)
        #r_m = 6378.137e3*np.sin(theta)
        r_m = 6378.137e3*theta # radius along the sphere
        #print("r_m = ", r_m)

        return r_m

    def make_all_pixel_polygon(self):
        """
            :returns: Shapely polygons corresponding to each pixel and the pixel center position as list of dictionaries
            :rtype: shapely.Polygon, list of dict
        """
        
        # iterate over pixels and get list of polygons per pixel
        pixel_poly = []
        pixel_center_pos = []
        for k in range(0, len(self.pixeldata)):

            pixel = self.pixeldata[k]['pixel']
            #print(pixel['@id'])
            edges = [pixel['edge_1'], pixel['edge_2'], pixel['edge_3'], pixel['edge_4']]
            pixel_poly.append(PixelShapelyPolygon.make_pixel_polygon(edges))
            pixel_center_pos.append(pixel['center'])
        
        return [pixel_poly, pixel_center_pos]

    @staticmethod
    def make_pixel_polygon(edges):
        """ 
            :param edges: List of dictionaries (edges) with the parameters defining the edges of the pixel
            :paramtype edges: list, dict            

        """
        poly = []
        for k in range(0, len(edges)):
            #print("edge ", k+1)
            lon_c = edges[k]["pole_pos_geoc"]["lon[deg]"]
            lat_c = edges[k]["pole_pos_geoc"]["lat[deg]"]
            
            radius_m = PixelShapelyPolygon.get_small_circle_radius(edges[k]["pole_pos_cart"], edges[k]["endPoint_cart_1"])
            PixelShapelyPolygon.get_small_circle_radius(edges[k]["pole_pos_cart"], edges[k]["endPoint_cart_2"])
            circle_points = PixelShapelyPolygon.get_circle(lon_c, lat_c, radius_m)
            
            # filter the points that make up the edge
            edge_points = PixelShapelyPolygon.get_arc_points(circle_points, edges[k]["endPoint_geoc_1"], edges[k]["endPoint_geoc_2"])
            #print(circle_points)

            poly.extend(edge_points)
        #print(np.array(poly))
        # compute centroid
        cent= [sum([p[0] for p in poly])/len(poly),sum([p[1] for p in poly])/len(poly)]
        # sort by polar angle
        poly.sort(key=lambda p: math.atan2(p[1]-cent[1],p[0]-cent[0]))
        #print(poly)
        
        boxes = shapely.geometry.Polygon(np.array(poly))

        return boxes