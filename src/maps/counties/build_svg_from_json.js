const D3Node = require("d3-node");
const fs = require("fs");
const topojson = require("topojson-client")

const width = 500,
    height = 700;

// Load in TopoJSON
const rawdata = fs.readFileSync(process.argv[2]);
const counties = JSON.parse(rawdata);

const d3n = new D3Node();
const d3 = d3n.d3;

let merged = topojson.merge(counties, [
    counties.objects["roi"],
    counties.objects["OSNI_Open_Data_-_Largescale_Boundaries_-_County_Boundaries_"],
    counties.objects["england_wales_counties"],
    counties.objects["pub_las"],
])

// We don't need a projection - as the topojson is pre-projected
// we just use one to fit the SVG to the required width and height
let fitSize = d3.geoIdentity().reflectY(true).fitSize([width, height], merged);
let geoGenerator = d3.geoPath().projection(fitSize);

const svg = d3n.createSVG(width, height)
    .attr("height", "65vh")
    .attr("width", "65vw")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round");

var roi_feature = topojson.feature(counties, counties.objects["roi"])

// process Ireland and the UK seperately...
// Appending a path element for each feature in the GeoJSON FeatureCollection's features array
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

countyObjects.forEach(function(countyObject, index, array) {
    countiesGroup.append('g').selectAll('path')
      .data(topojson.feature(counties, counties.objects[countyObject]).features)
      .enter()
      .append('path')
      .attr('d', geoGenerator)
      .attr('id', function(feature) {
          switch(countyObject) {
            case "pub_las":
              return feature.properties.local_auth;
            case "england_wales_counties":
              return feature.properties.NAME;
            default:
              return feature.properties.CountyName;
          }
      });  
})

fs.writeFileSync(process.argv[3], d3n.svgString());

