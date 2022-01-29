all: build/regions.min.svg

build/nuts_boundaries.shp.zip:
	mkdir -p build
	curl 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_03M_2021_3035.shp.zip' -o build/nuts_boundaries.shp.zip

build/nuts_boundaries/regions_epsg_27700.geojson: build/nuts_boundaries.shp.zip
	mkdir -p build/nuts_boundaries
	unzip build/nuts_boundaries.shp.zip -d build/nuts_boundaries
	touch build/nuts_boundaries/*

	mapshaper \
		build/nuts_boundaries/*.shp \
		-filter 'NUTS_ID == "IE0" || ( NUTS_ID.startsWith("UK") && LEVL_CODE == 1 )' \
		-proj EPSG:27700 \
		-clean \
		-o \
			build/nuts_boundaries/regions_epsg_27700.geojson \
			format=geojson \
			force

build/regions.svg: build/nuts_boundaries/regions_epsg_27700.geojson build_svg_from_json.js
	node build_svg_from_json.js build/nuts_boundaries/regions_epsg_27700.geojson build/regions.svg

build/regions.min.svg: build/regions.svg ../svgo.config.js
	svgo --config=../svgo.config.js build/regions.svg -o build/regions.min.svg

clean:
	find build -not -name '*.shp.zip' -delete
