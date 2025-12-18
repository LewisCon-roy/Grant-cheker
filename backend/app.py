from flask import Flask,request
from flask_cors import CORS
import geocoding as gc

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
    gc.classifyCords(pointsInShape)
    
    # print(i)
  return "Good"
 
@app.route("/",methods=['POST'])
def homePost():
  return "POSTING"  


if __name__ == "__main__":
    app.run(debug=True)
