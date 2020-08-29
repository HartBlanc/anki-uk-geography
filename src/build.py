""" methods associtated with generating the anki-dm data.csv file """

import csv
from pathlib import Path
from typing import Iterator, Optional, Sequence, TypeVar

from lxml import etree

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


def build_deck_csv(anki_dm_src_path: Path, guids: Optional[Sequence[str]] = None) -> None:
    """
    constructs the data.csv file for anki-dm which is ultimately used to
    generate the crowdanki json. Optionally retains old guids to ensure that
    Anki does
    not lose track of progress.

    :param anki_dm_src_path: The path to the anki-dm src folder, which is used
                             by the anki-dm build command to generate the crowdanki
                             json.
    :param guids: A sequence of the globally unique IDs to use for each card, if
                  not included, guids can be set automatically by calling
                  anki-dm reindex
                  later, which will generate a new set of random guids.
    """

    COUNTY_MAP = Path("uk_counties.svg")

    with (anki_dm_src_path / "data.csv").open(mode="w") as outfile:
        fieldnames = [
            "guid",
            "Location",
            "MacroLocation",
            "City",
            "County",
            "Region",
            "BoW",
            "Fill",
            "MacroFill",
            "tags",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        padded_guids = pad_none(guids) if guids else pad_none([])

        # Regions
        with COUNTY_MAP.open(mode="rb") as svg_file:
            svg_string = svg_file.read()

        svg_root = etree.fromstring(svg_string)

        region_elems = list(svg_root.xpath('//*[@id="Regions"]/*'))

        for region_elem in region_elems:
            region_name = region_elem.attrib["id"]
            fill_colour = region_elem.attrib["fill"]

            writer.writerow(
                {
                    "guid": next(padded_guids),
                    "Location": region_name,
                    "Region": region_name,
                    "Fill": fill_colour,
                    "tags": f"Region {region_country[region_name]}",
                }
            )

        # Counties
        with COUNTY_MAP.open(mode="rb") as svg_file:
            svg_string = svg_file.read()

        svg_root = etree.fromstring(svg_string)

        region_elems = list(svg_root.xpath('//*[@id="Regions"]/*'))

        county_country = dict()
        county_fill = dict()

        for region_elem in region_elems:
            region_name = region_elem.attrib["id"]
            region_colour = region_elem.attrib["fill"]
            for county_elem in region_elem.xpath("./*"):
                county_name = county_elem.attrib["id"]
                fill_colour = county_elem.attrib["fill"]
                print(county_name)
                county_country[county_name] = region_country[region_name]
                county_fill[county_name] = fill_colour

                writer.writerow(
                    {
                        "guid": next(padded_guids),
                        "Location": county_name,
                        "MacroLocation": region_name,
                        "County": county_name,
                        "Fill": fill_colour,
                        "MacroFill": region_colour,
                        "tags": f"County {county_country[county_name]}",
                    }
                )

        # Bodies of Water
        bow_elems = list(svg_root.xpath('//*[@id="Bodies of Water"]/*'))

        for bow_elem in bow_elems:
            bow_name = bow_elem.attrib["id"]
            writer.writerow(
                {
                    "guid": next(padded_guids),
                    "Location": bow_name,
                    "BoW": bow_name,
                    "Fill": "#29f",
                    "tags": "BoW",
                }
            )

        # Cities
        with open("cities.csv", "r") as csvfile:
            city_county = list(csv.reader(csvfile))[1:]  # Skip Header Row

        for (city_name, county_name) in city_county:
            if "/" in county_name:
                first_county = county_name.split("/")[0].strip()
                country = county_country[first_county]
            else:
                country = county_country[county_name]

            writer.writerow(
                {
                    "guid": next(padded_guids),
                    "Location": city_name,
                    "MacroLocation": county_name,
                    "City": city_name,
                    "MacroFill": county_fill.get(county_name, None),
                    "tags": f"City {country}",
                }
            )


if __name__ == "__main__":
    # with Path("crowdanki", "src", "data.csv").open(mode="r") as curr_datafile:
    #     reader = csv.DictReader(curr_datafile)
    #     next(reader)  # Skip header row
    #     curr_guids = [row["guid"] for row in reader]
    #
    # build_deck(curr_guids)
    build_deck_csv(Path("anki_dm", "src"))
