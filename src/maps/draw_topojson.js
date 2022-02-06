const D3Node = require("d3-node");
const fs = require("fs");

const width = 500,
    height = 700;

const d3n = new D3Node();
const d3 = d3n.d3;

module.exports.drawTopoJSON = function (featureCollection, outputFile, drawMapCallback) {
    // We don't need a projection - as the geojson is pre-projected
    // we just used one to fit the SVG to the required width and height
    let fitSize = d3.geoIdentity().reflectY(true).fitSize([width, height], featureCollection);
    let geoGenerator = d3.geoPath().projection(fitSize);

    const svg = d3n.createSVG(width, height)
    .attr("height", "65vh")
    .attr("width", "65vw")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round");
    
    drawMapCallback(svg, geoGenerator)
    
    fs.writeFileSync(outputFile, d3n.svgString());
}

module.exports.drawCircles = function (selection, pointExtractor) {
    selection
      .append('circle') 
      .attr('cx', (feature) => pointExtractor(feature)[0])
      .attr('cy', (feature) => pointExtractor(feature)[1])
      .attr('r', 5);

    selection
      .insert('circle')
      .attr('cx', (feature) => pointExtractor(feature)[0])
      .attr('cy', (feature) => pointExtractor(feature)[1])
      .attr('r', 3)
      .attr('fill-opacity', '0')
      .attr('stroke', '#fff')
      .attr('stroke-with', '1');
}

