import "./style.css";

import "@arcgis/map-components/components/arcgis-map";
import "@arcgis/map-components/components/arcgis-zoom";
import "@arcgis/map-components/components/arcgis-sketch";
import "@arcgis/core/geometry/support/webMercatorUtils"
import {explode} from "@odoe/explode"
import { xyToLngLat } from "@arcgis/core/geometry/support/webMercatorUtils";

await customElements.whenDefined("arcgis-sketch");

let graphics = document.querySelector('arcgis-sketch');
// change color to red as defualt hard to see 
graphics.addEventListener("arcgisCreate",(e)=>{
  graphics.layer.graphics.map((g)=>{
    if(g.geometry.type==="polygon"){
      g.symbol.outline.color = [255,20,20,255]
    }
  })
})

// button 
let submitButton = document.getElementById("Submit");
submitButton.addEventListener('click',async (e)=>{
  //Reads the points to send to server 
  // follows [SHAPE][POINT][lng/lat]
  let lngLatArr = []
  graphics.layer.graphics.forEach(element => {
    let shapePointArr = []
    let shape = element.geometry
    if(shape.type == "polygon"){
      const lines = explode(shape)
      const points = lines.map(explode).flat()
      for (let j = 0; j < points.length; j++) {
        // need to do this for some reason
        const X = points[j].longitude
        const Y = points[j].latitude
        // swap around for google chekcing
        shapePointArr.push(xyToLngLat(X,Y).reverse())
        //console.log(xyToLngLat(X,Y).reverse())
      }
      lngLatArr.push(shapePointArr)
    }
  });
  // remove duplicates but keep order 
  for (let i = 0; i < lngLatArr.length; i++) {
  lngLatArr[i] = [...new Map(lngLatArr[i].map(c => [c.join(','), c])).values()];  
  }
  console.log("array" ,lngLatArr)

  // console.log(JSON.stringify(lngLatArr))
  // send them to server
  let response = await postToSever(JSON.stringify(lngLatArr))
  // TODO do something with the response 
})

async function postToSever(data) {
  const response = await fetch("/api",{
    method:"POST",
    "headers": {"Content-Type": "application/json"},
    "body": data,
  })
  
}


const response = await fetch("/api",
  {
    method:"GET"
  }
)

const data = await response.text()
console.log(data)

