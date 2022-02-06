const fs = require("fs");
const topojson = require("topojson-client")
const { drawTopoJSON } = require("./draw_topojson.js");

// Load in TopoJSON
const rawdata = fs.readFileSync(process.argv[2]);
const topoj = JSON.parse(rawdata);

const featureCollection = topojson.feature(topoj, topoj.objects["NUTS_RG_03M_2021_3035"])

function drawRegions(svg, geoGenerator) {
    svg.selectAll('path')
      .data(featureCollection.features)
      .enter()
      .filter((feature) => feature.properties.NAME_LATN == "Ireland")
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
      .data(featureCollection.features)
      .enter()
      .filter((feature) => feature.properties.NAME_LATN != "Ireland")
      .append('path')
      .attr('d', geoGenerator)
      .attr('id', (feature) => feature.properties.NAME_LATN);
}

drawTopoJSON(featureCollection, process.argv[3], drawRegions)

