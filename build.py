
import csv


region_country = {"Scotland": "Scotland",
                  "Wales": "Wales",
                  "Northern Ireland": "NorthernIreland",
                  "South East": "England",
                  "London" : "England",
                  "South West": "England",
                  "West Midlands": "England",
                  "East Midlands": "England",
                  "East of England": "England",
                  "North West": "England",
                  "North East": "England",
                  "Yorkshire and the Humber": "England",
                  }

county_country = dict()

def item_or_none(l):
    count = 0
    while True:
        if l:
            yield l[count]
            count += 1
        else:
            yield None


def build_deck(prev_guids=[]):
    with open("counties.csv", "r") as csvfile:
        rows = list(csv.reader(csvfile))
    
    with open("./src/data.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["guid", "Location", "Macrolocation", "Sublocation", "LocationType",
                         "Macrotype", "Placeholder", "Map", "LocatorMap", "MacroPlaceholder",
                         "tags"]
        )
        
        guids = item_or_none(prev_guids)

        "Regions"
        seen = set()
        for (county, region) in rows:
            county_country[county] = region_country[region]
            if region not in seen:
                writer.writerow([next(guids), region, None, None, "Region", None,
                                 '<img src="uk_regions.svg" />', f'<img src="r-{region}.svg" />',
                                 None, None, f"Region {region_country[region]}"]
                )
                seen.add(region)

        "Counties"
        for (county, region) in rows:
            writer.writerow([next(guids), county, region, None, "County", "Region",
                             '<img src="uk_counties.svg" />', f'<img src="c-{county}.svg" />',
                             f'<img src="locator-{county}.svg" />', '<img src="uk_regions.svg" />',
                             f"County {region_country[region]}"]
            )

        "Bodies of Water"
        with open("bow.csv", "r") as csvfile:
            rows = list(csv.reader(csvfile))

        for (bow, ) in rows:
            writer.writerow([next(guids), bow, None, None, "Body of Water", None, None,
                             f'<img src="bow-{bow}.svg" />', None, None, "BoW"]
            )

        "Cities"
        with open("cities.csv", "r") as csvfile:
            rows = list(csv.reader(csvfile))
        
        for (city, county) in rows:
            if "/" in county:
                writer.writerow([next(guids), city, county, None, "City", "County", None, None, None, None,
                                 f"City {county_country[county.split('/')[0].strip()]}"]
                )
            else:
                writer.writerow([next(guids), city, county, None, "City", "County", None, None,
                                 f'<img src="c-{county}.svg" />', '<img src="uk_counties.svg" />',
                                 f"City {county_country[county]}"]
                )

if __name__ == "__main__":
    with open("./src/data.csv", "r") as datafile:
        guids = [row[0] for row in csv.reader(datafile)]
        print(guids)
    build_deck(guids)