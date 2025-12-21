import numpy as np
import shapely 
from shapely import STRtree,Point,Polygon,MultiPoint
from shapely.ops import orient
import geocoding as gc 


# RETURNS : the pixels in shapes in LatLong Form 
"""
returns all pixels in a shape in lat long form 
  params: 
    tranformedPoints - [(int,int)] - list of points that correspond to image coordinates
"""
def getAllPixelsInShape(transformedPoints):
  # convert to other points to make bounding box 
  cords = np.array(transformedPoints).T
  x_cords = cords[0,:]
  y_cords = cords[1,:]
  x_min , x_max = min(x_cords),max(x_cords)
  y_min , y_max = min(y_cords),max(y_cords)
  
    
  x_range = np.arange(x_min,x_max + 1)
  y_range = np.arange(y_min,y_max + 1)
  x,y = np.meshgrid(x_range,y_range)
  
  print(f"n_items = {x.shape[0] * x.shape[1]}")
  
  x_flat = x.flatten() 
  y_flat = y.flatten()
  
  coords = list(zip(x_cords,y_cords))  
  # right now only works for convex shapes which i suppose is a good thing as most areas wont be concave
  polygonTransformed = MultiPoint(coords).convex_hull
  # TODO fix so takes all shapes 
  polygonBuffered = polygonTransformed.buffer(5)
  
  mask = shapely.contains_xy(polygonBuffered,x_flat + 0.5,y_flat + 0.5)
  
  # print(f"points in = {np.count_nonzero(mask==True)}")
  # print(f"points out = {np.count_nonzero(mask==False)}")
  # print(f"percentage inside = {np.count_nonzero(mask==True)/(x.shape[0] * x.shape[1])}")
  x_points = x_flat[mask]
  y_points = y_flat[mask]
  
  pointsIn = np.vstack((x_points,y_points)).T
  
  return pointsIn


"""normalise a polygon so that it's area can be worked out
--- get first point and work out the differences between everypoint and this point 
--- first point (latitude ) delta * 111,195 
--- second (longitidue) delta * 71,474
    params :
    -- geometry the geometry of the shape
"""
def normaliseShape(geometry):
  LATITUDE_SCALE = 111195 
  LONGITUDE_SCALE = 71474
  
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

"""
returns the area of a shape in meters
"""
def area(polygon):
  return normaliseShape(polygon).area 

"""
returns the area of a shape in hectares
"""
def areaHectares(polygon):
  return area(polygon)/10000

def perimiter(polygon):
  return normaliseShape(polygon).length  