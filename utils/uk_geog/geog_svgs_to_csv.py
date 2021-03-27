""" methods associtated with generating the anki-dm data.csv file """

import argparse
import csv
from pathlib import Path
from typing import Iterator, Optional, Sequence, TypeVar

from lxml import etree

region_country = {
    "Scotland": "Scotland",
    "Wales": "Wales",
    "Northern Ireland": "NorthernIreland",  # tags are delimited by spaces
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
        if count < len(items):
            yield items[count]
            count += 1
        else:
            yield None


def build_deck_csv(
    uk_counties_path: Path,
    cities_csv_path: Path,
    outfile_path: Path,
    guids: Optional[Sequence[Optional[str]]] = None,
) -> None:

    with outfile_path.open(mode="w") as outfile:
        fieldnames = [
            "guid",
            "location",
            "macrolocation",
            "city",
            "county",
            "region",
            "bow",
            "tags",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        padded_guids = pad_none(guids) if guids else pad_none([])

        # Regions
        with uk_counties_path.open(mode="rb") as svg_file:
            svg_string = svg_file.read()

        svg_root = etree.fromstring(svg_string)

        region_elems = list(svg_root.xpath('//*[@id="Regions"]/*'))

        for region_elem in region_elems:
            region_name = region_elem.attrib["id"]

            writer.writerow(
                {
                    "guid": next(padded_guids),
                    "location": region_name,
                    "region": region_name,
                    "tags": f"Region {region_country[region_name]}",
                }
            )

        # Counties
        county_country = dict()
        for region_elem in region_elems:
            region_name = region_elem.attrib["id"]
            for county_elem in region_elem.xpath("./*"):
                county_name = county_elem.attrib["id"]
                print(county_name)
                county_country[county_name] = region_country[region_name]

                writer.writerow(
                    {
                        "guid": next(padded_guids),
                        "location": county_name,
                        "macrolocation": region_name,
                        "county": county_name,
                        "tags": f"County {county_country[county_name]}",
                    }
                )

        # Bodies of Water
        bow_elems = list(svg_root.xpath('//*[@id="Bodies of Water"]/*'))

        for bow_elem in bow_elems:
            bow_name = bow_elem.attrib["id"]
            writer.writerow(
                {"guid": next(padded_guids), "location": bow_name, "bow": bow_name, "tags": "BoW"}
            )

        # Cities
        with cities_csv_path.open(mode="r") as csvfile:
            city_county = list(csv.reader(csvfile))[1:]  # Skip header row

        for (city_name, county_name) in city_county:
            if "/" in county_name:
                first_county = county_name.split("/")[0].strip()
                country = county_country[first_county]
            else:
                country = county_country[county_name]

            writer.writerow(
                {
                    "guid": next(padded_guids),
                    "location": city_name,
                    "macrolocation": county_name,
                    "city": city_name,
                    "tags": f"City {country}",
                }
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A utility for extracting data from SVG files into the brain brew CSV format",
    )
    parser.add_argument(
        "uk_counties",
        type=Path,
        help=(
            "The path to the SVG file containing all of the regions, counties, cities, and bodies "
            "of water"
        ),
    )
    parser.add_argument(
        "cities_csv",
        type=Path,
        help=(
            "The path to a CSV file which contains a full list of cities in the UK and their "
            "associated counties"
        ),
    )
    parser.add_argument(
        "outfile",
        type=Path,
        help=(
            "The path to write the output CSV to. This is typically the input CSV for brain brew."
        ),
    )
    parser.add_argument(
        "--guids",
        action="store_true",
        help=(
            "A boolean flag indicating whether to re-use the GUIDs defined in outfile. "
            "If omitted, the guid column will be left blank and brain brew will generate new ones."
        ),
    )

    curr_guids: Optional[Sequence[Optional[str]]]

    args = parser.parse_args()
    if args.guids:
        with args.outfile.open(mode="r") as curr_datafile:
            reader = csv.DictReader(curr_datafile)
            curr_guids = [row["guid"] for row in reader]
    else:
        curr_guids = None

    build_deck_csv(args.uk_counties, args.cities_csv, args.outfile, curr_guids)
