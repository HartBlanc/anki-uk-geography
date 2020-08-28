""" methods associtated with generating the crowdanki data.csv file """

# TODO: parameterise outpath in build_deck

import csv
from pathlib import Path
from typing import Iterator, Optional, Sequence, TypeVar

region_country = {
    "Scotland": "Scotland",
    "Wales": "Wales",
    "Northern Ireland": "NorthernIreland",
    "South East": "England",
    "London": "England",
    "South West": "England",
    "West Midlands": "England",
    "East Midlands": "England",
    "East of England": "England",
    "North West": "England",
    "North East": "England",
    "Yorkshire and the Humber": "England",
}

A = TypeVar("A")


def pad_none(items: Sequence[A]) -> Iterator[Optional[A]]:
    """A generator which pads the end of a sequence with Nones"""

    count = 0
    while True:
        if items:
            yield items[count]
            count += 1
        else:
            yield None


def build_deck(guids: Optional[Sequence[str]] = None) -> None:
    """
    constructs the data.csv file for crowdanki which is ultimately used to
    generate the Anki pkg. Optionally retains old guids to ensure that Anki does
    not lose track of progress.

    :param guids: A sequence of the globally unique ids to use for each card, if
                  not included all guids will be set to None and later set with
                  default values by crowdanki.
    """

    with Path("counties.csv").open(mode="r") as csvfile:
        county_regions = list(csv.reader(csvfile))

    with Path("crowdanki", "src", "data.csv").open(mode="w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(
            [
                "guid",
                "Location",
                "Macrolocation",
                "Sublocation",
                "LocationType",
                "Macrotype",
                "Placeholder",
                "Map",
                "LocatorMap",
                "MacroPlaceholder",
                "tags",
            ]
        )

        padded_guids = pad_none(guids) if guids else pad_none([])

        # Regions
        seen_regions = set()

        for (_, region) in county_regions:
            if region not in seen_regions:
                writer.writerow(
                    [
                        next(padded_guids),
                        region,
                        None,
                        None,
                        "Region",
                        None,
                        '<img src="uk_regions.svg" />',
                        f'<img src="r-{region}.svg" />',
                        None,
                        None,
                        f"Region {region_country[region]}",
                    ]
                )
                seen_regions.add(region)

        # Counties
        county_country = {county: region_country[region] for county, region in county_regions}

        for (county, _) in county_regions:
            writer.writerow(
                [
                    next(padded_guids),
                    county,
                    region,
                    None,
                    "County",
                    "Region",
                    '<img src="uk_counties.svg" />',
                    f'<img src="c-{county}.svg" />',
                    f'<img src="locator-{county}.svg" />',
                    '<img src="uk_regions.svg" />',
                    f"County {county_country[county]}",
                ]
            )

        # Bodies of Water
        with open("bow.csv", "r") as csvfile:
            bows = list(csv.reader(csvfile))

        for (bow,) in bows:
            writer.writerow(
                [
                    next(padded_guids),
                    bow,
                    None,
                    None,
                    "Body of Water",
                    None,
                    None,
                    f'<img src="bow-{bow}.svg" />',
                    None,
                    None,
                    "BoW",
                ]
            )

        # Cities
        with open("cities.csv", "r") as csvfile:
            city_county = list(csv.reader(csvfile))

        for (city, county) in city_county:
            if "/" in county:
                first_county = county.split("/")[0].strip()
                country = county_country[first_county]
            else:
                country = county_country[county]

            writer.writerow(
                [
                    next(padded_guids),
                    city,
                    county,
                    None,
                    "City",
                    "County",
                    None,
                    None,
                    f'<img src="c-{county}.svg" />',
                    '<img src="uk_counties.svg" />',
                    f"City {country}",
                ]
            )


if __name__ == "__main__":
    with Path("crowdanki", "src", "data.csv").open(mode="r") as curr_datafile:
        reader = csv.reader(curr_datafile)
        next(reader)  # Skip header row
        curr_guids = [row[0] for row in reader]

    build_deck(curr_guids)
