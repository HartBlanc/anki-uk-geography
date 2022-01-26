set -e

# $1 is the scale of the map - valid values are 01 03 10 and 20 at the time of writing
# https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts

SHAPEFILE=NUTS_RG_"$1"M_2021_3035.shp

curl -O 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/'"$SHAPEFILE"'.zip'
mkdir shapefiles
unzip "$SHAPEFILE".zip -d shapefiles
rm "$SHAPEFILE".zip

mapshaper \
    shapefiles/"$SHAPEFILE" \
    -filter 'NUTS_ID == "IE0" || ( NUTS_ID.startsWith("UK") && LEVL_CODE == 1 )' \
    -proj EPSG:27700 \
    -clean \
    -o regions_epsg_27700.geojson format=geojson
rm -r shapefiles

node build_svg_from_json.js
rm regions_epsg_27700.geojson

svgo out.svg -o regions_"$1".min.svg
rm out.svg
