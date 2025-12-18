import numpy as np
import shapely 
from shapely import STRtree,Point,Polygon
from pyproj import Geod,CRS
import geocoding as gc 


# create bounding box then ray trace each line and check checking if inside
# unsure weather or not to use mapCord or imageCord or imgPixel
# use imgCord as thats what we get from the transform 
# TODO maybe change to map cord as may be more efficent

GEOD = CRS("EPSG:27700").get_geod()
# RETURNS : the pixels in shapes in LatLong Form 
def getAllPixelsInShape(latLongPoints,transformedPoints):
  # maybe swap these around
  cords = np.array(latLongPoints).T 
  coords = []
  for i in range(len(cords[0])):
    coords.append(tuple(cords[:,i]))
  coords = tuple(coords)
  polygonLatLong = Polygon(shell=coords,holes=None)
  polygonLatLong = normaliseShape(polygonLatLong)
  area = abs(GEOD.geometry_area_perimeter(polygonLatLong)[0])
  print("Area of the polygonLatLong: " , area)
  
  # convert to other points to make bounding box 
  cords = np.array(transformedPoints).T
  x_cords = cords[0,:]
  y_cords = cords[1,:]
  x_min , x_max = min(x_cords),max(x_cords)
  y_min , y_max = min(y_cords),max(y_cords)
  
  grid_Points= [(x,y) for x in range(x_min,x_max+1) for y in range(y_min,y_max+1)]
  coords = []
  for i in range(len(cords[0])):
    coords.append(tuple(cords[:,i]))
  coords = tuple(coords)
  polygonTransformed = Polygon(shell=coords,holes=None)
  
  pointsIn = list(map(lambda p: p if shapely.contains_xy(polygonTransformed,p[0],p[1]) else None,grid_Points))
  pointsIn = [x for x in pointsIn if x is not None]
  
  return np.array(pointsIn)


"""normalise a polygon so that it's area can be worked out
--- get first point and work out the differences between everypoint and this point 
--- first point (latitude ) delta * 111,195 
--- second (longitidue) delta * 71,474
    params :
    -- geometry the geometry of the shape
"""
def normaliseShape(geometry):
  LATITUDE_SCALE = 111.195 
  LONGITUDE_SCALE = 71.474
  
  points = geometry.exterior.xy
  latitude = points[0]
  longitude = points[1]
  fst_point = (latitude[0],longitude[0])
  
  latitude[0] = 0
  longitude[0] = 0
  for i in range(1,len(latitude)):
    latitude[i] = (latitude[i] - fst_point[0]) * LATITUDE_SCALE
    longitude[i] = (longitude[i] - fst_point[1]) * LONGITUDE_SCALE
    
  points = list(zip(latitude,longitude))
    
  return Polygon(shell=points,holes=None)