const D3Node = require("d3-node");
const fs = require("fs");
const topojson = require("topojson-client")

const width = 500,
    height = 700;

// Load in TopoJSON
const rawdata = fs.readFileSync(process.argv[2]);
const cities = JSON.parse(rawdata);

const d3n = new D3Node();
const d3 = d3n.d3;

let merged = topojson.merge(cities, [
    cities.objects["roi"],
    cities.objects["OSNI_Open_Data_-_Largescale_Boundaries_-_County_Boundaries_"],
    cities.objects["england_wales_counties"],
    cities.objects["pub_las"],
    cities.objects["gb_cities"],
    cities.objects["ni_cities"],
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

var roi_feature = topojson.feature(cities, cities.objects["roi"])

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
      .data(topojson.feature(cities, cities.objects[countyObject]).features)
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

let cityObjects = [
    "ni_cities",
    "gb_cities",
]

const citiesGroup = svg.append('g').attr("id", "cities")

cityObjects.forEach(function(cityObject, index, array) {
    var enterSelection = citiesGroup.append('g').selectAll('g')
      .data(topojson.feature(cities, cities.objects[cityObject]).features)
      .enter()
      .append('g')
      .attr('id', (feature) => feature.properties.NAME);

    enterSelection
      .append('circle') 
      .attr('cx', (feature) => fitSize(feature.geometry.coordinates)[0])
      .attr('cy', (feature) => fitSize(feature.geometry.coordinates)[1])
      .attr('r', 5);
    
    enterSelection
      .insert('circle')
      .attr('cx', (feature) => fitSize(feature.geometry.coordinates)[0])
      .attr('cy', (feature) => fitSize(feature.geometry.coordinates)[1])
      .attr('r', 3)
      .attr('fill-opacity', '0')
      .attr('stroke', '#fff')
      .attr('stroke-with', '1');
})

fs.writeFileSync(process.argv[3], d3n.svgString());

