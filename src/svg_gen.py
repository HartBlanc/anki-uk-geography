""" Methods for generating svg files associated with each card """

import csv
import subprocess
from pathlib import Path
from typing import List, Optional

import lxml.etree as etree

# TODO: Parameterise fill colours and sort out namespaces.

WHITE = "#ffffff"
GREY = "#efefef"
DODGER_BLUE = "#1e90ff"
LIME = "#00ff00"
BLUE = "#0000ff"
RED = "#ff0000"
CYAN = "#00ffff"
DARK_ORANGE = "#ff8c00"
YELLOW = "#ffff00"
PURPLE = "#663399"
MAGENTA = "#ff00ff"
BLACK = "#000000"
GREEN = "#008000"
PERU = "#cd853f"
PINK = "#ff69b4"
DARK_OLIVE = "#556B2F"

COUNTY_COLOURS = [LIME, BLUE, RED, CYAN, DARK_ORANGE, YELLOW, PURPLE, MAGENTA]
REGION_COLOURS = [
    LIME,
    BLUE,
    RED,
    CYAN,
    DARK_ORANGE,
    YELLOW,
    PURPLE,
    MAGENTA,
    BLACK,
    GREEN,
    PERU,
    PINK,
]


def get_style_attrib(
    attrib: str, element: etree.ElementBase, default: Optional[str] = None
) -> Optional[str]:

    style_str = element.get("style")

    if style_str is None:
        return default

    styles = style_str.split(";")

    for style in styles:
        if attrib in style:
            return style.split(":")[1]

    return None


def set_style(attrib: str, element: etree.ElementBase, value: Optional[str]) -> None:

    if value is None:
        raise ValueError(f'Cannot set {attrib} value to None, try "none" instead?')

    style_str = element.get("style")
    curr_value = get_style_attrib(attrib, element)

    if curr_value:
        element.set("style", style_str.replace(f"{attrib}:{curr_value}", f"{attrib}:{value}"))
    elif style_str:
        element.set("style", f"{style_str};{attrib}:{value}")
    else:
        element.set("style", f"{attrib}:{value}")


def set_style_recursive(attrib: str, element: etree.ElementBase, value: Optional[str]) -> None:

    if value is None:
        raise ValueError(f'Cannot set {attrib} value to None, try "none" instead?')

    set_style(attrib, element, value)

    for child in element.iterchildren():
        set_style_recursive(attrib, child, value)


def file_per_attrib(
    attrib: str,
    root: etree.ElementBase,
    prefix: str,
    elements: List[etree.ElementBase],
    outfolder: Path,
    inactive_value: str = GREY,
    values: Optional[List[Optional[str]]] = None,
) -> None:
    """
    Creates a new SVG file for each `element` in elements where `element` is
    highlighted using a value in values and all other elements have the inactive_value.

    :param attrib: the attribute used to highlight elements (e.g. "fill")
    :param root: the root node of the lxml tree of the template SVG
    :param prefix: the filename prefix (e.g. "county")
    :param elements: the svg elements to be highlighted
    :param outfolder: the path to write out the highlighted svg files to
    :param inactive_value: the inactive colour, grey by default
    :param values: the style attribute values, if None, uses the values in the template SVG
    """

    if values is None:
        values = [get_style_attrib(attrib, element) for element in elements]

    for element in elements:
        set_style_recursive(attrib, element, inactive_value)

    assert len(values) == len(elements)
    for fill, element in zip(values, elements):
        set_style_recursive(attrib, element, fill)

        # Move element to foreground
        parent = element.getparent()
        parent.remove(element)
        parent.append(element)

        element_name = element.get("id")

        with (outfolder / f"{prefix}-{element_name}.svg").open(mode="wb") as attrib_file:
            attrib_file.write(etree.tostring(root))

        set_style_recursive(attrib, element, inactive_value)


def bodies_of_water(infile):
    """
    Select all regions, set fill to gray
    for each body of water:
        set to blue
        write to file
        set to none
    """
    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    regions = root.xpath('//*[@id="Areas"]')[0]
    set_style_recursive("fill", regions, GREY)

    b_o_w = list(root.xpath('//*[@id="Bodies of Water"]/*'))
    file_per_attrib(
        "fill",
        root,
        "bow",
        b_o_w,
        Path("crowdanki", "src", "media"),
        inactive_value="none",
        values=[DODGER_BLUE] * len(b_o_w),
    )


def regions(infile):
    """
    Select all regions, set fill to gray
    for each region:
        set to fill colour
    """

    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()

    svg_root = etree.fromstring(svg_string)
    region_elems = list(svg_root.xpath('//*[@id="Areas"]/*'))

    for (fill, region) in zip(REGION_COLOURS, region_elems):
        set_style_recursive("fill", region, fill)

    with Path("crowdanki", "src", "media", "uk_regions.svg").open(mode="wb") as region_file:
        region_file.write(etree.tostring(svg_root))

    file_per_attrib(
        "fill",
        svg_root,
        "r",
        region_elems,
        Path("crowdanki", "src", "media"),
        values=REGION_COLOURS,
    )


def counties(infile):
    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    counties = list(root.xpath('//*[@id="Areas"]/*/*'))

    file_per_attrib("fill", root, "c", counties, Path("crowdanki", "src", "media"))


def extract_counties_svg(infile, outfile):

    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    regions = list(root.xpath('//*[@id="Areas"]/*'))

    rows = []

    for region in regions:
        region_name = region.attrib["id"]

        for county in region.xpath("./*"):
            county_name = county.attrib["id"]

            rows.append([county_name, region_name])

    with open(outfile, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def extract_bow_svg(infile, outfile):

    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    bows = list(root.xpath('//*[@id="Bodies of Water"]/*'))

    with open(outfile, "w") as file:
        writer = csv.writer(file)
        writer.writerows([bow.attrib["id"] for bow in bows])


def gen_locator_maps(outfolder: Path):

    for child_path in outfolder.iterdir():
        if child_path.name.startswith("r-"):
            with child_path.open(mode="rb") as svg_file:
                svg_string = svg_file.read()

            region = child_path.stem.replace("r-", "")

            root = etree.fromstring(svg_string)
            county_elems = list(root.xpath(f'//*[@id="{region}"]/*'))
            print(region)
            region_colour = get_style_attrib("fill", county_elems[0])

            stroke_colour = BLACK
            if region_colour == BLACK:
                stroke_colour = RED

            file_per_attrib(
                "stroke",
                root,
                "locator",
                county_elems,
                outfolder,
                values=[stroke_colour] * len(county_elems),
            )


def minify_svgs(folder):
    args = ["--enable-viewboxing", "--enable-comment-stripping", "--shorten-ids", "--indent=none"]

    for child_path in folder.iterdir():
        if child_path.suffix == ".svg":
            temp_path = folder / f"t-{child_path.name}"
            subprocess.run(["scour", "-i", str(child_path), "-o", str(temp_path)] + args)
            subprocess.run(["mv", str(temp_path), str(child_path)])


if __name__ == "__main__":

    MEDIA_FOLDER = Path("crowdanki", "src", "media")

    infile = "template_map.svg"
    subprocess.run(["cp", infile, str(MEDIA_FOLDER / "uk_counties.svg")])
    extract_counties_svg(infile, "counties.csv")
    extract_bow_svg(infile, "bow.csv")
    bodies_of_water(infile)
    regions(infile)
    counties(infile)
    gen_locator_maps(MEDIA_FOLDER)
    minify_svgs(MEDIA_FOLDER)
