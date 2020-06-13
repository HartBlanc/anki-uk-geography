
import csv

def build_deck():
    with open("counties.csv", "r") as csvfile:
        rows = list(csv.reader(csvfile))
        
    with open("./src/data.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["guid","Location", "Macrolocation", "Sublocation", "LocationType", "Macrotype", "Placeholder", "Map", "LocatorMap", "MacroPlaceholder"])
        
        "Regions"
        seen = set()
        for (county, region) in rows:
            if region not in seen:
                writer.writerow([None, region, None, None, "Region", None, '<img src="uk_regions.svg" />', f'<img src="r-{region}.svg" />', None, None])
                seen.add(region)

        "Counties"
        for (county, region) in rows:
            writer.writerow([None, county, region, None, "County", "Region", '<img src="uk_counties.svg" />', f'<img src="c-{county}.svg" />', f'<img src="locator-{county}.svg" />', '<img src="uk_regions.svg" />'])

        "Bodies of Water"
        with open("bow.csv", "r") as csvfile:
            rows = list(csv.reader(csvfile))

        for (bow, ) in rows:
            writer.writerow([None, bow, None, None, "Body of Water", None, None, f'<img src="bow-{bow}.svg" />', None, None])

        "Cities"
        with open("cities.csv", "r") as csvfile:
            rows = list(csv.reader(csvfile))
        
        for (city, county) in rows:
            if "/" in county:
                writer.writerow([None, city, county, None, "City", "County", None, None, None, None])
            else:
                writer.writerow([None, city, county, None, "City", "County", None, None, f'<img src="c-{county}.svg" />', '<img src="uk_counties.svg" />'])

if __name__ == "__main__":
    build_deck()