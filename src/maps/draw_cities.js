const fs = require("fs");
const topojson = require("topojson-client")
const { drawTopoJSON, drawCircles } = require("./draw_topojson.js");
const { drawCounties } = require("./draw_counties.js");

// Load in TopoJSON
const rawdata = fs.readFileSync(process.argv[2]);
const topoj = JSON.parse(rawdata);

let featureCollection = topojson.merge(topoj, [
    topoj.objects["roi"],
    topoj.objects["OSNI_Open_Data_-_Largescale_Boundaries_-_County_Boundaries_"],
    topoj.objects["england_wales_counties"],
    topoj.objects["pub_las"],
    topoj.objects["gb_cities"],
    topoj.objects["ni_cities"],
])

function getID(feature) {
  if (feature.properties.hasOwnProperty('NAME')) {
    return feature.properties.NAME;
  }
  if (feature.properties.NAME2_LANG != "eng") {
    return feature.properties.NAME1;
  }
  return feature.properties.NAME2;
}

function drawCities (svg, geoGenerator) {
    var roi_feature = topojson.feature(topoj, topoj.objects["roi"])

    drawCounties(svg, geoGenerator, false)

    let cityObjects = [
        "ni_cities",
        "gb_cities",
    ]

    const citiesGroup = svg.append('g').attr("id", "cities")

    cityObjects.forEach(function(cityObject, index, array) {
        var enterSelection = citiesGroup.append('g').selectAll('g')
          .data(topojson.feature(topoj, topoj.objects[cityObject]).features)
          .enter()
          .filter((feature) => getID(feature) != "London")
          .append('g')
          .attr('id', getID);

        drawCircles(enterSelection, (feature) => geoGenerator.projection()(feature.geometry.coordinates))
    })
}

drawTopoJSON(featureCollection, process.argv[3], drawCities)
