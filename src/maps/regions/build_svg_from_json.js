const D3Node = require("d3-node");
const fs = require("fs");

const width = 500,
    height = 700;

// Load in GeoJSON
const rawdata = fs.readFileSync('regions_epsg_27700.geojson');
const regions = JSON.parse(rawdata);

const d3n = new D3Node();
const d3 = d3n.d3;

// We don't need a projection - as the geojson is pre-projected
// we just used one to fit the SVG to the required width and height
let fitSize = d3.geoIdentity().reflectY(true).fitSize([width, height], regions);
let geoGenerator = d3.geoPath().projection(fitSize);

const svg = d3n.createSVG(width, height)
    .attr("height", "65vh")
    .attr("width", "65vw")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round");

// process Ireland and the UK seperately...
// Appending a path element for each feature in the GeoJSON FeatureCollection's features array
svg.selectAll('path')
  .data(regions.features)
  .enter()
  .filter(function(feature) { return feature.properties.NAME_LATN == "Ireland" })
  .append('path')
  .attr('d', geoGenerator)
  .attr('id', "Ireland")
  .attr("fill-opacity", 0)
  .attr("stroke-dasharray", "2,2")
  .attr("stroke", "#aaa");

const regionsGroup = svg.append('g')
    .attr("id", "regions")
    .attr("fill", "#aaa")
    .attr("stroke", "#777");

regionsGroup.selectAll('path')
  .data(regions.features)
  .enter()
  .filter(function(feature) { return feature.properties.NAME_LATN != "Ireland" })
  .append('path')
  .attr('d', geoGenerator)
  .attr('id', function(feature) {
    return feature.properties.NAME_LATN;
  });

fs.writeFileSync('out.svg', d3n.svgString());

