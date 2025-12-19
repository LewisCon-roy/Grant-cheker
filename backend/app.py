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
    print(shapePoints)
    transformedPoints = gc.transformPointsRounded(gc.mapToImgTransfrom,shapePoints)
    pointsInShape = gc.getPointsInShape(shapePoints,transformedPoints)
    classifiedPoints = gc.classifyCords(pointsInShape)
    # add to testing 
    reduced = classifiedPoints[:]
    reduced = list(map(lambda x : x[:2],reduced))
    reduced = np.array(list(map(lambda x : [x[0][0],x[0][1],x[1]],reduced)))
    if TESTING :
      np.savetxt("../testing/TestData.txt",reduced)
    # print("reduced ",reduced)
  return "Good"
 
@app.route("/",methods=['POST'])
def homePost():
  return "POSTING"  


if __name__ == "__main__":
    app.run(debug=True)
