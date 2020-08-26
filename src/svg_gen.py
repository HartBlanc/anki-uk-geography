""" Methods for generating svg files associated with each card """

import csv
import subprocess
from pathlib import Path
from typing import Optional, Sequence

import lxml.etree as etree

# TODO: Move logic of moving shapes to the foregound into seperate function.
# TODO: consider removal of bodies of water CSV
# TODO: rename Areas id to Regions
# TODO: create a county class in the svg
# TODO: review get_style_attrib - try dict approach
# TODO: consider whether everything can be refactored by using CSS instead

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
    """
    Gets the value of a style `attrib` for an `element`, returning a `default` value
    if the attribute is not set.

    :param attrib: style attribute to retrieve value for
    :param element: element from which to get style for
    :param default: default value to return if attribute is not set
    :return: the style attributes value
    """

    style_str = element.get("style")

    if style_str is None:
        return default

    styles = style_str.split(";")

    for style in styles:
        if attrib in style:
            return style.split(":")[1]

    return default


def set_style(attrib: str, element: etree.ElementBase, value: Optional[str]) -> None:
    """
    Sets a style `attrib` to `value` for an element, handling cases where the style
    is or isn't defined and if the attribute is overwritten or set for the first time.

    :param attrib: the style attribute to set
    :param element: the element to set the style attribute for
    :param value: the value to set the style attribute to
    """

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
    """
    Sets a style `attrib` to `value` for an element, and all of it's children elements.

    :param attrib: the style attribute to set
    :param element: the root element to set the style attribute for
    :param value: the value to set the style attribute to
    """

    if value is None:
        raise ValueError(f'Cannot set {attrib} value to None, try "none" instead?')

    set_style(attrib, element, value)

    for child in element.iterchildren():
        set_style_recursive(attrib, child, value)


def file_per_attrib(
    attrib: str,
    root: etree.ElementBase,
    prefix: str,
    elements: Sequence[etree.ElementBase],
    outfolder: Path,
    inactive_value: str = GREY,
    values: Optional[Sequence[Optional[str]]] = None,
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


def bodies_of_water(bow_template_svg: Path) -> None:
    """
    Generates an SVG file for each body of water, where the body of water is blue,
    all regions/counties are grey and other bodies of water are transparent.

    :param bow_template_svg: an SVG file which contains all of the BoW elements
                             two levels below the areas id
    """

    with open(bow_template_svg, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    region_group = root.xpath('//*[@id="Areas"]')[0]
    set_style_recursive("fill", region_group, GREY)

    b_o_w = list(root.xpath('//*[@id="Bodies of Water"]/*'))
    file_per_attrib(
        "fill",
        root,
        "bow",
        b_o_w,
        Path("crowdanki", "src", "media"),
        inactive_value="none",  # transparent
        values=[DODGER_BLUE] * len(b_o_w),
    )


def generate_region_svgs(region_template_svg: Path) -> None:
    """
    1. Generates an SVG file where each region is coloured according to a colour
       in REGION_COLOURS.
    2. Generates an SVG file for *each region*, where the region has a fill
       colour from REGION_COLOURS and all other regions are coloured grey.

    :param region_template_svg: an SVG file which contains all of the region
                                elements one level below the areas id.
    """

    with open(region_template_svg, "rb") as svg_file:
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


def generate_county_svgs(county_template_svg: Path) -> None:
    """
    Generates an SVG file for each county, where the county has it's fill colour in the
    template, and all other counties are coloured grey.

    :param county_template_svg: an SVG file which contains all of the county elements
           two levels below the areas id
    """

    with open(county_template_svg, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    county_elems = list(root.xpath('//*[@id="Areas"]/*/*'))

    file_per_attrib("fill", root, "c", county_elems, Path("crowdanki", "src", "media"))


def extract_county_region_mapping(county_region_svg: Path, county_region_csv: Path) -> None:
    """
    Generates a CSV file with a county and it's corresponding region on each line.

    :param county_region_svg: the path to an svg file with an Areas group
    :param county_region_csv: the path to write the mapping csv to.
    """

    with open(county_region_svg, "rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    region_elems = list(root.xpath('//*[@id="Areas"]/*'))

    rows = []

    for region in region_elems:
        region_name = region.attrib["id"]

        for county in region.xpath("./*"):
            county_name = county.attrib["id"]

            rows.append([county_name, region_name])

    with open(county_region_csv, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def extract_bow_names(bow_svg: Path, bow_csv: Path) -> None:
    """
    Generates a CSV file with a name for a Body of Water on each line.

    :param bow_svg: the path to an svg file with a Bodies of Water group
    :param bow_csv: the path to write the body of water names to.
    """

    with bow_svg.open(mode="rb") as svg_file:
        svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    bows = list(root.xpath('//*[@id="Bodies of Water"]/*'))

    with open(bow_csv, "w") as file:
        writer = csv.writer(file)
        writer.writerows([bow.attrib["id"] for bow in bows])


def gen_locator_maps(region_dir: Path, locator_dir: Path) -> None:
    """
    Generates an SVG file for each county which highlights that county in the
    context of it's region by changing the stroke of the county and moving it
    to the foreground.

    :param region_dir: the directory in which region maps can be found
                       (region files should be prefixed with "r-")
    :param locator_dir: the director to write locator maps to,
                        (locator files will be prefixed with "locator-")
    """

    for child_path in region_dir.iterdir():
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
                locator_dir,
                values=[stroke_colour] * len(county_elems),
            )


def minify_svgs(svg_folder: Path):
    """
    Reduces the size of all SVG files in a folder by stripping comments, shortening ids
    and removing whitespace. Uses the scour package.

    :param svg_folder: a folder which contains SVG files to be minimised.
    """

    args = ["--enable-viewboxing", "--enable-comment-stripping", "--shorten-ids", "--indent=none"]

    for child_path in svg_folder.iterdir():
        if child_path.suffix == ".svg":
            temp_path = svg_folder / f"t-{child_path.name}"
            subprocess.run(["scour", "-i", str(child_path), "-o", str(temp_path)] + args)
            subprocess.run(["mv", str(temp_path), str(child_path)])


if __name__ == "__main__":

    MEDIA_FOLDER = Path("crowdanki", "src", "media")
    TEMPLATE_MAP = Path("template_map.svg")

    subprocess.run(["cp", str(TEMPLATE_MAP), str(MEDIA_FOLDER / "uk_counties.svg")])
    extract_county_region_mapping(TEMPLATE_MAP, Path("counties.csv"))
    extract_bow_names(TEMPLATE_MAP, Path("bow.csv"))
    bodies_of_water(TEMPLATE_MAP)
    generate_region_svgs(TEMPLATE_MAP)
    generate_county_svgs(TEMPLATE_MAP)
    gen_locator_maps(MEDIA_FOLDER, MEDIA_FOLDER)
    minify_svgs(MEDIA_FOLDER)
