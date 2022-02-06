all: build/counties.min.svg build/regions.min.svg build/cities.min.svg

# TODO: City formatting for City-Counties
# TODO: Body-of-Water maps
# TODO: Resolve yorkshire region / county mismatch
# TODO: Commonise counties js
# TODO: Include mapshaper in project node_modules
# TODO: Include SVGO in project node_moudles
# TODO: requires node, jq, zip, unzip (versions)
# TODO: Filter out london from cities

build/gb_boundaries.shp.zip:
	mkdir -p build

	curl -L \
		'https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=ESRI%C2%AE+Shapefile&redirect' \
		-o build/gb_boundaries.shp.zip

	unzip -Z1 build/gb_boundaries.shp.zip | \
		grep -v '\(Data/Supplementary_Country/\|Data/Supplementary_Ceremonial/\)' | \
		xargs -I '{}' zip -d build/gb_boundaries.shp.zip "{}"

build/gb_boundaries/Data/Supplementary_Country/* build/gb_boundaries/Data/Supplementary_Ceremonial/*: build/gb_boundaries.shp.zip
	mkdir -p build/gb_boundaries

	unzip -o build/gb_boundaries.shp.zip -d "build/gb_boundaries"
	touch build/gb_boundaries/Data/Supplementary_Ceremonial/*
	touch build/gb_boundaries/Data/Supplementary_Country/*

build/not_scotland/*: build/gb_boundaries/Data/Supplementary_Country/*
	mkdir -p build/not_scotland

	mapshaper \
		-i build/gb_boundaries/Data/Supplementary_Country/*.shp \
		-filter 'NAME != "Scotland"' \
		-o build/not_scotland/not_scotland.shp

build/england_wales_counties/*: build/gb_boundaries/Data/Supplementary_Ceremonial/* build/not_scotland/*
	mkdir -p build/england_wales_counties

	mapshaper \
		-i build/gb_boundaries/Data/Supplementary_Ceremonial/*.shp \
		-clip \
			source=build/not_scotland/not_scotland.shp \
			remove-slivers \
		-o build/england_wales_counties/england_wales_counties.shp

build/n_ire_counties.shp.zip:
	mkdir -p build

	curl \
		'https://osni-spatialni.opendata.arcgis.com/datasets/spatialni::osni-open-data-largescale-boundaries-county-boundaries-.zip?outSR=%7B%22latestWkid%22%3A29902%2C%22wkid%22%3A29900%7D' \
		-o build/n_ire_counties.shp.zip

build/n_ire_counties/*: build/n_ire_counties.shp.zip
	mkdir -p build/n_ire_counties

	unzip -o build/n_ire_counties.shp.zip -d build/n_ire_counties
	touch build/n_ire_counties/*

	mapshaper \
		-i build/n_ire_counties/*.shp \
		-proj EPSG:27700 \
		-o build/n_ire_counties/*.shp force


build/scotland_council_areas.shp.zip:
	mkdir -p build

	curl \
		'https://geo.spatialhub.scot/geoserver/sh_las/wfs?authkey=b85aa063-d598-4582-8e45-e7e6048718fc&request=GetFeature&service=WFS&version=1.1.0&typeName=pub_las&outputFormat=SHAPE-ZIP' \
		-o build/scotland_council_areas.shp.zip

build/scotland_council_areas/*: build/scotland_council_areas.shp.zip
	mkdir -p build/scotland_council_areas

	unzip -o build/scotland_council_areas.shp.zip -d build/scotland_council_areas
	touch build/scotland_council_areas/*

build/nuts_boundaries.shp.zip:
	mkdir -p build

	curl \
		'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_03M_2021_3035.shp.zip' \
		-o build/nuts_boundaries.shp.zip 

build/nuts_boundaries/*: build/nuts_boundaries.shp.zip
	mkdir -p build/nuts_boundaries

	unzip -o build/nuts_boundaries.shp.zip -d build/nuts_boundaries
	touch build/nuts_boundaries/*

build/roi/*: build/nuts_boundaries/*
	mkdir -p build/roi

	mapshaper \
		-i build/nuts_boundaries/*.shp \
		-proj EPSG:27700 \
		-filter 'NUTS_ID == "IE0"' \
		-o build/roi/roi.shp

build/counties.topojson: build/roi/* build/england_wales_counties/* build/roi/* build/n_ire_counties/* build/scotland_council_areas/*
	mapshaper \
		-i \
			build/england_wales_counties/*.shp \
			build/roi/*.shp \
			build/n_ire_counties/*.shp \
			build/scotland_council_areas/*.shp \
			combine-files \
		-clean \
		-simplify 0.3% \
		-o build/counties.topojson format=topojson

build/counties.svg: build/counties.topojson counties_svg_json.js
	node counties_svg_json.js build/counties.topojson build/counties.svg

build/counties.min.svg: build/counties.svg svgo.config.js
	svgo --config=svgo.config.js build/counties.svg -o build/counties.min.svg

build/regions_epsg_27700.geojson: build/nuts_boundaries/*
	mapshaper \
		-i build/nuts_boundaries/*.shp \
		-filter 'NUTS_ID == "IE0" || ( NUTS_ID.startsWith("UK") && LEVL_CODE == 1 )' \
		-proj EPSG:27700 \
		-clean \
		-o build/regions_epsg_27700.geojson format=geojson

build/regions.svg: build/regions_epsg_27700.geojson regions_svg_json.js
	node regions_svg_json.js build/regions_epsg_27700.geojson build/regions.svg

build/regions.min.svg: build/regions.svg svgo.config.js
	svgo --config=svgo.config.js build/regions.svg -o build/regions.min.svg

build/gb_cities.csv:
	mkdir -p build/gb_cities

	curl -L \
		'https://api.os.uk/downloads/v1/products/OpenNames/downloads?area=GB&format=CSV&redirect=' \
		-o build/gb_cities.csv.zip

	unzip build/gb_cities.csv.zip -d build/gb_cities
	rm build/gb_cities.csv.zip

	cut -d ',' -f 3,4,5,6,8,9,10 build/gb_cities/Doc/OS_Open_Names_Header.csv > build/gb_cities.csv 
	cut -d ',' -f 3,4,5,6,8,9,10 build/gb_cities/Data/* | grep ,City, >> build/gb_cities.csv

	rm -r build/gb_cities

define SPARQL_QUERY 
SELECT DISTINCT ?itemLabel ?location WHERE {
	?item wdt:P31 wd:Q515;
	(wdt:P131/(wdt:P131*)) wd:Q26;
	wdt:P625 ?location.
	SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
endef
export SPARQL_QUERY

build/ni_cities.csv:
	echo "NAME,GEOMETRY_X,GEOMETRY_Y" > build/ni_cities.csv

	curl 'https://query.wikidata.org/sparql?format=json' --data-urlencode query="$$SPARQL_QUERY" | \
		jq -r '.results.bindings[] | [.itemLabel.value, .location.value] | @csv' | \
		sed 's/"//g' | \
		sed -r 's/Point\((.*) (.*)\)/\1,\2/g' \
		>> build/ni_cities.csv

build/cities.topojson: build/gb_cities.csv build/ni_cities.csv build/counties.topojson
	mkdir -p build/tmp

	mapshaper \
		-i build/gb_cities.csv \
		-points x=GEOMETRY_X y=GEOMETRY_Y \
		-o build/tmp/gb_cities.topojson format=topojson

	mapshaper \
		-i build/ni_cities.csv \
		-points x=GEOMETRY_X y=GEOMETRY_Y \
		-proj EPSG:27700 \
		-o build/tmp/ni_cities.topojson format=topojson

	mapshaper \
		-i \
			build/tmp/gb_cities.topojson \
			build/tmp/ni_cities.topojson \
			build/counties.topojson \
			combine-files \
		-o build/cities.topojson force

	rm -r build/tmp

build/cities.svg: build/cities.topojson cities_svg_json.js
	node cities_svg_json.js build/cities.topojson build/cities.svg

build/cities.min.svg: build/cities.svg svgo.config.js
	svgo --config=svgo.config.js build/cities.svg -o build/cities.min.svg

clean:
	find build -not \( -name '*.shp.zip' -o -name '*.csv' \) -delete
