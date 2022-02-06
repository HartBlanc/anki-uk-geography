const fs = require("fs");
const topojson = require("topojson-client")
const { drawTopoJSON, drawCircles} = require("./draw_topojson.js");

// Load in TopoJSON
const rawdata = fs.readFileSync(process.argv[2]);
const topoj = JSON.parse(rawdata);

let featureCollection = topojson.merge(topoj, [
    topoj.objects["roi"],
    topoj.objects["OSNI_Open_Data_-_Largescale_Boundaries_-_County_Boundaries_"],
    topoj.objects["england_wales_counties"],
    topoj.objects["pub_las"],
])


function getID(countyObject, feature) {
  switch(countyObject) {
    case "pub_las":
      return feature.properties.local_auth;
    case "england_wales_counties":
      return feature.properties.NAME;
    default:
      return feature.properties.CountyName;
  }
}

module.exports.drawCounties = function (svg, geoGenerator, shouldDrawCityMarkers = true){
    var roi_feature = topojson.feature(topoj, topoj.objects["roi"])
    svg.selectAll('path')
      .data(roi_feature.features)
      .enter()
      .append('path')
      .attr('d', geoGenerator)
      .attr('id', "Republic of Ireland")
      .attr("fill-opacity", 0)
      .attr("stroke-dasharray", "2,2")
      .attr("stroke", "#aaa");

    const countiesGroup = svg.append('g')
        .attr("id", "counties")
        .attr("fill", "#aaa")
        .attr("stroke", "#777");

    let countyObjects = [
        "OSNI_Open_Data_-_Largescale_Boundaries_-_County_Boundaries_",
        "england_wales_counties",
        "pub_las",
    ]

    let cityIDs = [
        "Bristol",
        "City and County of the City of London",
        "Dundee City",
        "Aberdeen City",
        "City of Edinburgh",
        "Glasgow City",
    ]

    countyObjects.forEach(function(countyObject, index, array) {

        countiesGroup.append('g').selectAll('path')
          .data(topojson.feature(topoj, topoj.objects[countyObject]).features)
          .enter()
          .append('path')
          .attr('d', geoGenerator)
          .filter((feature) => !cityIDs.includes(getID(countyObject, feature)))
          .attr('id', (feature) => getID(countyObject, feature));
        
        if (shouldDrawCityMarkers) {
            var enterSelection = countiesGroup.append('g').selectAll('path')
              .data(topojson.feature(topoj, topoj.objects[countyObject]).features)
              .enter()
              .filter((feature) => cityIDs.includes(getID(countyObject, feature)))
              .append('g')
              .attr('id', (feature) => getID(countyObject, feature));
            
            drawCircles(enterSelection, geoGenerator.centroid)
        }
    })
}
if (require.main === module) {
  drawTopoJSON(featureCollection, process.argv[3], module.exports.drawCounties)
}


