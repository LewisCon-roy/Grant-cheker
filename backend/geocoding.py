from osgeo import gdal,osr
import numpy as np
import rasterio as rio
import utility as ut 

LAND_TYPES = {
    1: "Deciduous woodland",
    2: "Coniferous woodland",
    3: "Arable",
    4: "Improved grassland",
    5: "Neutral grassland",
    6: "Calcareous grassland",
    7: "Acid grassland",
    8: "Fen Marsh Swamp",
    9: "Heather",
    10: "Heather grassland",
    11: "Bog",
    12: "Inland rock",
    13: "Saltwater",
    14: "Freshwater",
    15: "Supralittoral rock",
    16: "Supralittoral sediment",
    17: "Littoral rock",
    18: "Littoral sediment",
    19: "Saltmarsh",
    20: "Urban",
    21: "Suburban"
}

def newCordTransfrom(data,toLatLong):
  # change given coord system to wgs84 than able to convert to lat and long
  # GOING FROM IMG TO MAP
  old_cordsys = osr.SpatialReference()
  old_cordsys.ImportFromWkt(data.GetProjectionRef())
  wgs84_wkt = """
  GEOGCS["WGS 84",
    DATUM["WGS_1984",
      SPHEROID["WGS 84",6378137,298.257223563,
        AUTHORITY["EPSG","7030"]],
      AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
      AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
      AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""

  new_cordsys = osr.SpatialReference()
  new_cordsys.ImportFromWkt(wgs84_wkt)  

  transform = osr.CoordinateTransformation(old_cordsys,new_cordsys) if toLatLong else osr.CoordinateTransformation(new_cordsys,old_cordsys)
  return transform

def getImageConts(img):
  width = img.RasterXSize
  height = img.RasterYSize
  
  geoTransform = data.GetGeoTransform()
  x_min = geoTransform[0]
  x_size = geoTransform[1]
  y_min = geoTransform[3]
  y_size = geoTransform[5]
  
  return (width,height,x_min,x_size,y_min,y_size)
  
def transformPointsRounded(transform,points):
  transformed_points = set(transform.TransformPoints(points))
  transformed_points = list(map(lambda x: tuple(map(lambda y: round(y),x)),transformed_points))
  transformed_points = [(x[0],x[1]) for x in transformed_points]
  return transformed_points

def coordToPixel(affineTransform,point):
  # print("point: ", point)
  return np.matmul(np.linalg.inv(affineTransform),point)[:-1]

def getPointsInShape(transformedPoints):
  return ut.getAllPixelsInShape(transformedPoints)
  
# TODO make it work for multiple differnet images
data = gdal.Open(r'./data/ukregion-southwestengland.tif')
imgConts = getImageConts(data)
imgToMapTransform = newCordTransfrom(data,True)
mapToImgTransfrom = newCordTransfrom(data,False)

# only read greyscale layer 2nd layer 
dataRaster = rio.open(r'./data/ukregion-southwestengland.tif')
affineTransform = dataRaster.meta['transform']
affineTransform = np.array(affineTransform,dtype=np.int64)
affineTransform = np.reshape(affineTransform,(3,3))

# print((344113,154468) * ~affineTransform)
# print(affineTransform * ((26147.300000000003, 9158.199999999999)))

classificationIMG = dataRaster.read(1)
confidenceIMG = dataRaster.read(2) 
# print(classificationIMG[9158][26147])
# print(confidenceIMG[9158][26147])

# gets classification of cords and there confidence 
def classifyCords(cordinates):
  pointsArr = []
  # of the form 
  groundTypes = {}
  n_cords = len(cordinates)
  for cord in cordinates:
    # changing into np arrays to do the matrix multpilcation for affine transform
    # unpack the list inorder to place it into arry 
    cord2d = cord.tolist() 
    cord = np.reshape(np.append(np.array(cord),1),(3,1))
    # round the pixel 
    pixel = np.ndarray.astype(np.round(coordToPixel(affineTransform,cord),0),np.int32)    
    classification = classificationIMG[pixel[1][0]][pixel[0][0]].item()
    land_type = LAND_TYPES[classification]
    confidence = confidenceIMG[pixel[1][0]][pixel[0][0]].item()
    
    if land_type not in groundTypes:
      groundTypes[land_type] = (confidence,1)
      # print(groundTypes)
    groundTypes[land_type] = (groundTypes[land_type][0] + confidence,groundTypes[land_type][1])  
    pointsArr.append([cord2d[0],cord2d[1],classification,confidence])

    # print("classification: " + str(classification), "confidence: " + str(confidence))
    
  # go through all ground types getting total confidence 
  for k in groundTypes:
    groundTypes[k] = (groundTypes[k][1] /n_cords , groundTypes[k][0]/ groundTypes[k][1])
    
  # Also go and get the total area taken up by this ground type
  # Total area and confidence of that area 
  # print(groundTypes)
  return np.array(pointsArr)
  

# print("affine: " , (affineTransform))
# classifyCords([[343733,152979],[345655,153690]])
# print(mapToImgTransfrom.TransformPoint(51.29475195421389, -2.774935635501995))
# print(imgToMapTransform.TransformPoint(344113,154468))


# TODO algorithm that takes the points and there classifications and returns the shapes of the field
# can take as [[shapely point, classificationNum, confidence]]
# decides 
# returns [[polygon,class,confidence]] 
# def classifyArea()



# x,y test place axbridge 346064, 155355
# 51.29475195421389, -2.774935635501995 to convert back to xy



