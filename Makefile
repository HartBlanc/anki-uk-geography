# TODO: Body-of-Water maps
# TODO: Body-of-Water templates
# TODO: Include mapshaper in project node_modules
# TODO: Include SVGO in project node_moudles
# TODO: requires node, jq, zip, unzip (versions)
# TODO: split out maps into seperate makefile

all: build/resolved_templates/Region\ -\ Map.html \
	build/resolved_templates/County\ -\ Map.html \
	build/resolved_templates/City\ -\ Map.html \
	build/resolved_templates/Map\ -\ Region.html \
	build/resolved_templates/Map\ -\ County.html \
	build/resolved_templates/Map\ -\ City.html \
	build/resolved_templates/County\ -\ Region.html \
	build/resolved_templates/City\ -\ County.html


build/maps/gb_boundaries.shp.zip:
	mkdir -p build/maps

	curl -L \
		'https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=ESRI%C2%AE+Shapefile&redirect' \
		-o build/maps/gb_boundaries.shp.zip

	unzip -Z1 build/maps/gb_boundaries.shp.zip | \
		grep -v '\(Data/Supplementary_Country/\|Data/Supplementary_Ceremonial/\)' | \
		xargs -I '{}' zip -d build/maps/gb_boundaries.shp.zip "{}"

build/maps/gb_boundaries/Data/Supplementary_Country/* build/maps/gb_boundaries/Data/Supplementary_Ceremonial/*: build/maps/gb_boundaries.shp.zip
	mkdir -p build/maps/gb_boundaries

	unzip -o build/maps/gb_boundaries.shp.zip -d "build/maps/gb_boundaries"
	touch build/maps/gb_boundaries/Data/Supplementary_Ceremonial/*
	touch build/maps/gb_boundaries/Data/Supplementary_Country/*

build/maps/not_scotland/*: build/maps/gb_boundaries/Data/Supplementary_Country/*
	mkdir -p build/maps/not_scotland

	mapshaper \
		-i build/maps/gb_boundaries/Data/Supplementary_Country/*.shp \
		-filter 'NAME != "Scotland"' \
		-o build/maps/not_scotland/not_scotland.shp


build/maps/england_wales_counties/*: build/maps/gb_boundaries/Data/Supplementary_Ceremonial/* build/maps/not_scotland/*
	mkdir -p build/maps/england_wales_counties

	mapshaper \
		-i build/maps/gb_boundaries/Data/Supplementary_Ceremonial/*.shp \
		-clip \
			source=build/maps/not_scotland/not_scotland.shp \
			remove-slivers \
		-o build/maps/england_wales_counties/england_wales_counties.shp

build/maps/n_ire_counties.shp.zip:
	mkdir -p build/maps

	curl \
		'https://osni-spatialni.opendata.arcgis.com/datasets/spatialni::osni-open-data-largescale-boundaries-county-boundaries-.zip?outSR=%7B%22latestWkid%22%3A29902%2C%22wkid%22%3A29900%7D' \
		-o build/maps/n_ire_counties.shp.zip

build/maps/n_ire_counties/*: build/maps/n_ire_counties.shp.zip
	mkdir -p build/maps/n_ire_counties

	unzip -o build/maps/n_ire_counties.shp.zip -d build/maps/n_ire_counties
	touch build/maps/n_ire_counties/*

	mapshaper \
		-i build/maps/n_ire_counties/*.shp \
		-proj EPSG:27700 \
		-o build/maps/n_ire_counties/*.shp force

build/maps/scotland_council_areas.shp.zip:
	mkdir -p build/maps

	curl \
		'https://geo.spatialhub.scot/geoserver/sh_las/wfs?authkey=b85aa063-d598-4582-8e45-e7e6048718fc&request=GetFeature&service=WFS&version=1.1.0&typeName=pub_las&outputFormat=SHAPE-ZIP' \
		-o build/maps/scotland_council_areas.shp.zip

build/maps/scotland_council_areas/*: build/maps/scotland_council_areas.shp.zip
	mkdir -p build/maps/scotland_council_areas

	unzip -o build/maps/scotland_council_areas.shp.zip -d build/maps/scotland_council_areas
	touch build/maps/scotland_council_areas/*

build/maps/nuts_boundaries.shp.zip:
	mkdir -p build/maps

	curl \
		'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_03M_2021_3035.shp.zip' \
		-o build/maps/nuts_boundaries.shp.zip

build/maps/nuts_boundaries/*: build/maps/nuts_boundaries.shp.zip
	mkdir -p build/maps/nuts_boundaries

	unzip -o build/maps/nuts_boundaries.shp.zip -d build/maps/nuts_boundaries
	touch build/maps/nuts_boundaries/*

build/maps/roi/*: build/maps/nuts_boundaries/*
	mkdir -p build/maps/roi

	mapshaper \
		-i build/maps/nuts_boundaries/*.shp \
		-proj EPSG:27700 \
		-filter 'NUTS_ID == "IE0"' \
		-o build/maps/roi/roi.shp

build/maps/counties.topojson: build/maps/roi/* build/maps/england_wales_counties/* build/maps/roi/* build/maps/n_ire_counties/* build/maps/scotland_council_areas/*
	mapshaper \
		-i \
			build/maps/england_wales_counties/*.shp \
			build/maps/roi/*.shp \
			build/maps/n_ire_counties/*.shp \
			build/maps/scotland_council_areas/*.shp \
			combine-files \
		-clean \
		-simplify 0.3% \
		-o build/maps/counties.topojson format=topojson

build/maps/counties.svg: build/maps/counties.topojson src/maps/draw_counties.js src/maps/draw_topojson.js
	node src/maps/draw_counties.js build/maps/counties.topojson build/maps/counties.svg

build/maps/counties.min.svg: build/maps/counties.svg src/maps/svgo.config.js
	svgo --config=src/maps/svgo.config.js build/maps/counties.svg -o build/maps/counties.min.svg

build/maps/regions.topojson: build/maps/nuts_boundaries/*
	mapshaper \
		-i build/maps/nuts_boundaries/*.shp \
		-filter 'NUTS_ID == "IE0" || ( NUTS_ID.startsWith("UK") && LEVL_CODE == 1 )' \
		-proj EPSG:27700 \
		-clean \
		-o build/maps/regions.topojson format=topojson

build/maps/regions.svg: build/maps/regions.topojson src/maps/draw_regions.js src/maps/draw_topojson.js
	node src/maps/draw_regions.js build/maps/regions.topojson build/maps/regions.svg

build/maps/regions.min.svg: build/maps/regions.svg src/maps/svgo.config.js
	svgo --config=src/maps/svgo.config.js build/maps/regions.svg -o build/maps/regions.min.svg

build/maps/gb_cities.csv:
	mkdir -p build/maps/gb_cities

	curl -L \
		'https://api.os.uk/downloads/v1/products/OpenNames/downloads?area=GB&format=CSV&redirect=' \
		-o build/maps/gb_cities.csv.zip

	unzip build/maps/gb_cities.csv.zip -d build/maps/gb_cities
	rm build/maps/gb_cities.csv.zip

	cut -d ',' -f 3,4,5,6,8,9,10 build/maps/gb_cities/Doc/OS_Open_Names_Header.csv > build/maps/gb_cities.csv
	cut -d ',' -f 3,4,5,6,8,9,10 build/maps/gb_cities/Data/* | grep ,City, >> build/maps/gb_cities.csv

	rm -r build/maps/gb_cities

define SPARQL_QUERY
SELECT DISTINCT ?itemLabel ?location WHERE {
	?item wdt:P31 wd:Q515;
	(wdt:P131/(wdt:P131*)) wd:Q26;
	wdt:P625 ?location.
	SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
endef
export SPARQL_QUERY

build/maps/ni_cities.csv:
	echo "NAME,GEOMETRY_X,GEOMETRY_Y" > build/maps/ni_cities.csv

	curl 'https://query.wikidata.org/sparql?format=json' --data-urlencode query="$$SPARQL_QUERY" | \
		jq -r '.results.bindings[] | [.itemLabel.value, .location.value] | @csv' | \
		sed 's/"//g' | \
		sed -r 's/Point\((.*) (.*)\)/\1,\2/g' \
		>> build/maps/ni_cities.csv

build/maps/cities.topojson: build/maps/gb_cities.csv build/maps/ni_cities.csv build/maps/counties.topojson
	mkdir -p build/maps/tmp

	mapshaper \
		-i build/maps/gb_cities.csv \
		-points x=GEOMETRY_X y=GEOMETRY_Y \
		-o build/maps/tmp/gb_cities.topojson format=topojson

	mapshaper \
		-i build/maps/ni_cities.csv \
		-points x=GEOMETRY_X y=GEOMETRY_Y \
		-proj EPSG:27700 \
		-o build/maps/tmp/ni_cities.topojson format=topojson

	mapshaper \
		-i \
			build/maps/tmp/gb_cities.topojson \
			build/maps/tmp/ni_cities.topojson \
			build/maps/counties.topojson \
			combine-files \
		-o build/maps/cities.topojson force

	rm -r build/maps/tmp

build/maps/cities.svg: build/maps/cities.topojson src/maps/draw_cities.js src/maps/draw_counties.js src/maps/draw_topojson.js
	node src/maps/draw_cities.js build/maps/cities.topojson build/maps/cities.svg

build/maps/cities.min.svg: build/maps/cities.svg src/maps/svgo.config.js
	svgo --config=src/maps/svgo.config.js build/maps/cities.svg -o build/maps/cities.min.svg

build/resolved_templates/Region\ -\ Map.html: utils/uk_geog/build_note_templates.py build/maps/regions.min.svg utils/uk_geog/templates/Region\ -\ Map.template.html
	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/Region - Map.template.html" -o=build/resolved_templates

build/resolved_templates/Map\ -\ Region.html: utils/uk_geog/build_note_templates.py build/maps/regions.min.svg utils/uk_geog/templates/Map\ -\ Region.template.html
	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/Map - Region.template.html" -o=build/resolved_templates

build/resolved_templates/County\ -\ Map.html: utils/uk_geog/build_note_templates.py \
	build/maps/counties.min.svg \
	utils/uk_geog/templates/County\ -\ Map.template.html \
	utils/uk_geog/snippets/zoombox.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/County - Map.template.html" -o=build/resolved_templates

build/resolved_templates/Map\ -\ County.html: utils/uk_geog/build_note_templates.py \
	build/maps/counties.min.svg \
	utils/uk_geog/templates/Map\ -\ County.template.html \
	utils/uk_geog/snippets/zoombox_optional.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/Map - County.template.html" -o=build/resolved_templates

build/resolved_templates/City\ -\ Map.html: utils/uk_geog/build_note_templates.py \
	build/maps/cities.min.svg \
	utils/uk_geog/templates/City\ -\ Map.template.html \
	utils/uk_geog/snippets/highlight_multiple_counties.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/City - Map.template.html" -o=build/resolved_templates

build/resolved_templates/Map\ -\ City.html: utils/uk_geog/build_note_templates.py \
	build/maps/cities.min.svg \
	utils/uk_geog/templates/Map\ -\ City.template.html \
	utils/uk_geog/snippets/highlight_multiple_counties.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/Map - City.template.html" -o=build/resolved_templates

build/resolved_templates/City\ -\ County.html: utils/uk_geog/build_note_templates.py \
	build/maps/counties.min.svg \
	build/maps/cities.min.svg \
	utils/uk_geog/templates/City\ -\ County.template.html \
	utils/uk_geog/snippets/highlight_multiple_counties.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/City - County.template.html" -o=build/resolved_templates

build/resolved_templates/County\ -\ Region.html: utils/uk_geog/build_note_templates.py \
	build/maps/regions.min.svg \
	build/maps/counties.min.svg \
	utils/uk_geog/templates/County\ -\ Region.template.html \
	utils/uk_geog/snippets/zoombox_optional.html

	mkdir -p build/resolved_templates

	python utils/uk_geog/build_note_templates.py "utils/uk_geog/templates/County - Region.template.html" -o=build/resolved_templates

clean:
	find build -not \( -name '*.shp.zip' -o -name '*.csv' \) -delete

