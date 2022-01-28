all: build/counties.min.svg

build/gb_boundaries.shp.zip:
	mkdir -p build
	curl -L 'https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=ESRI%C2%AE+Shapefile&redirect' -H 'Cookie: CookieControl={"necessaryCookies":["TS01*","omse-*","AMP_TOKEN"]' -o build/gb_boundaries.shp.zip

build/gb_boundaries/Data/Supplementary_Country/* build/gb_boundaries/Data/Supplementary_Ceremonial/*: build/gb_boundaries.shp.zip
	mkdir -p build/gb_boundaries
	unzip -o build/gb_boundaries.shp.zip "Data/Supplementary_Ceremonial/*" -d "build/gb_boundaries"
	touch build/gb_boundaries/Data/Supplementary_Ceremonial/*
	unzip -o build/gb_boundaries.shp.zip "Data/Supplementary_Country/*" -d "build/gb_boundaries"
	touch build/gb_boundaries/Data/Supplementary_Country/*


build/not_scotland/*: build/gb_boundaries/Data/Supplementary_Country/*
	mkdir -p build/not_scotland
	mapshaper \
	build/gb_boundaries/Data/Supplementary_Country/*.shp \
	-filter 'NAME != "Scotland"' \
	-o build/not_scotland/not_scotland.shp

build/england_wales_counties/*: build/gb_boundaries/Data/Supplementary_Ceremonial/* build/not_scotland/*
	mkdir -p build/england_wales_counties
	mapshaper \
	build/gb_boundaries/Data/Supplementary_Ceremonial/*.shp \
	-clip \
		source=build/not_scotland/not_scotland.shp \
		remove-slivers \
	-o build/england_wales_counties/england_wales_counties.shp

build/n_ire_counties.shp.zip:
	mkdir -p build
	curl 'https://osni-spatialni.opendata.arcgis.com/datasets/spatialni::osni-open-data-largescale-boundaries-county-boundaries-.zip?outSR=%7B%22latestWkid%22%3A29902%2C%22wkid%22%3A29900%7D' -o build/n_ire_counties.shp.zip

build/n_ire_counties/*: build/n_ire_counties.shp.zip
	mkdir -p build/n_ire_counties
	unzip -o build/n_ire_counties.shp.zip -d build/n_ire_counties
	touch build/n_ire_counties/*
	mapshaper \
		build/n_ire_counties/*.shp \
		-proj EPSG:27700 \
		-o build/n_ire_counties/*.shp force


build/scotland_council_areas.shp.zip:
	mkdir -p build
	curl 'https://geo.spatialhub.scot/geoserver/sh_las/wfs?authkey=b85aa063-d598-4582-8e45-e7e6048718fc&request=GetFeature&service=WFS&version=1.1.0&typeName=pub_las&outputFormat=SHAPE-ZIP' -o build/scotland_council_areas.shp.zip

build/scotland_council_areas/*: build/scotland_council_areas.shp.zip
	mkdir -p build/scotland_council_areas
	unzip -o build/scotland_council_areas.shp.zip -d build/scotland_council_areas
	touch build/scotland_council_areas/*

build/nuts_boundaries.shp.zip:
	mkdir -p build
	curl 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_03M_2021_3035.shp.zip' -o build/nuts_boundaries.shp.zip 

build/nuts_boundaries/*: build/nuts_boundaries.shp.zip
	mkdir -p build/nuts_boundaries
	unzip -o build/nuts_boundaries.shp.zip -d build/nuts_boundaries
	touch build/nuts_boundaries/*

build/roi/*: build/nuts_boundaries/*
	mkdir -p build/roi
	mapshaper \
	build/nuts_boundaries/*.shp \
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
		-o build/counties.topojson format=topojson

build/counties.svg: build/counties.topojson build_svg_from_json.js
	node build_svg_from_json.js build/counties.topojson build/counties.svg

build/counties.min.svg: build/counties.svg ../svgo.config.js
	svgo --config=../svgo.config.js build/counties.svg -o build/counties.min.svg

clean:
	find build -not -name '*.shp.zip' -delete
