from flask import Flask,request
from flask_cors import CORS
import geocoding as gc
import os 
import numpy as np

TESTING = True

app = Flask(__name__)
CORS(app)


@app.get("/api")
def home():
  return "Sever connected"

# TODO make functions return 200 instead of text for error checking 
@app.post("/api")
def recieveData():
  JSONdata = request.json
  # clean json data
  # TODO map to the tiff data
  for shapePoints in JSONdata:
    transformedPoints = gc.transformPointsRounded(gc.mapToImgTransfrom,shapePoints)
    pointsInShape = gc.getPointsInShape(transformedPoints)
    print(f"inshape {pointIn(pointsInShape)}")
    classifiedPoints = gc.classifyCords(pointsInShape)
    print(f"inshape {pointIn(classifiedPoints)}")
    # add to testing 
  
    reduced = classifiedPoints[:]
    # reduced = list(map(lambda x : x[:3],reduced))
    if TESTING :
      np.savetxt("../testing/TestData.txt",reduced,fmt="%d")
    # print("reduced ",reduced)
  return "Good"
 
 
# check if point in array 
def pointIn(arr):
  target = [343650,154200]
  return arr[(arr[:, :2] == target).all(axis=1)]
 
 
@app.route("/",methods=['POST'])
def homePost():
  return "POSTING"  


if __name__ == "__main__":
    app.run(debug=True)
