import lxml.etree as etree
import csv
import argparse
import os
import subprocess
#TO DO: Parameterise fill colours and sort out namespaces.

WHITE = "#ffffff"
GREY = "#efefef"
DODGER_BLUE = "#1e90ff"
LIME = "#00ff00"
BLUE = "#0000ff"
RED =  "#ff0000"
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
REGION_COLOURS = [LIME, BLUE, RED, CYAN, DARK_ORANGE, YELLOW, PURPLE, MAGENTA, BLACK, GREEN, PERU, PINK]


def get_fill(element, default=None):
    
    style_str = element.get("style")

    if style_str is None:
        return default

    styles = style_str.split(";")
    
    for style in styles:
        if "fill" in style:
            return style.split(":")[1] 

def set_fill(element, fill_colour):
    
    style_str = element.get('style')
    curr_fill = get_fill(element)

    if curr_fill:
        element.set("style", style_str.replace(f"fill:{curr_fill}", f"fill:{fill_colour}"))
    elif style_str:
       element.set("style", style_str+f";fill:{fill_colour}")
    else:
        element.set("style", f"fill:{fill_colour}")


def set_fill_children(element, fill_colour):
    
    set_fill(element, fill_colour)
    for child in element.iterchildren():
        set_fill_children(child, fill_colour)

def get_stroke(element, default=None):
    
    style_str = element.get("style")

    if style_str is None:
        return default

    styles = style_str.split(";")
    
    for style in styles:
        if "stroke" in style:
            return style.split(":")[1] 

def set_stroke(element, fill_colour):
    
    style_str = element.get('style')
    curr_fill = get_stroke(element)

    if curr_fill:
        element.set("style", style_str.replace(f"stroke:{curr_fill}", f"stroke:{fill_colour}"))
    elif style_str:
       element.set("style", style_str+f";stroke:{fill_colour}")
    else:
        element.set("style", f"stroke:{fill_colour}")


def set_stroke_children(element, fill_colour):
    
    set_stroke(element, fill_colour)
    for child in element.iterchildren():
        set_stroke_children(child, fill_colour)



def fill_each(root, prefix, elements, outfolder, inactive_colour=GREY, fills=None):
    """
        Open SVG file
        lxml the file
        select the group of areas
        [for each area in areas extract the base colour]
        set all areas to grey
        copy = svg_file.read()
        for area in areas:
            set area colour to base colour
            save to file
            re-set area to grey
    """

    if fills is None:   
        fills = [get_fill(element) for element in elements]

    for element in elements:
        set_fill_children(element, inactive_colour)
    

    assert len(fills) == len(elements)
    for fill, element in zip(fills, elements):
        set_fill_children(element, fill)
        try:
            element_name = element.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        except KeyError:
            element_name = element.attrib['id']

        with open(f"{outfolder}/{prefix}-{element_name}.svg", "wb") as fill_file:
            fill_file.write(etree.tostring(root))
        
        set_fill_children(element, inactive_colour)


def stroke_each(root, prefix, elements, outfolder, stroke_fills, inactive_fill=WHITE):
    """
        Open SVG file
        lxml the file
        select the group of areas
        [for each area in areas extract the base colour]
        set all areas to grey
        copy = svg_file.read()
        for area in areas:
            set area colour to base colour
            save to file
            re-set area to grey
    """

    for element in elements:
        set_stroke_children(element, inactive_fill)

    assert len(stroke_fills) == len(elements)
    for fill, element in zip(stroke_fills, elements):
        set_stroke(element, fill)
        parent = element.getparent()
        parent.remove(element)
        parent.append(element)
        try:
            element_name = element.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        except KeyError:
            element_name = element.attrib['id']
        
        with open(f"{outfolder}/{prefix}-{element_name}.svg", "wb") as fill_file:
            fill_file.write(etree.tostring(root))
        
        set_stroke(element, inactive_fill)


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
    set_fill_children(regions, GREY)

    b_o_w = list(root.xpath('//*[@id="Bodies of Water"]/*'))
    fill_each(root, "bow", b_o_w, "src/media", inactive_colour="none", fills=[DODGER_BLUE]*len(b_o_w))

def regions(infile):
    """
    Select all regions, set fill to gray
    for each region:
        set to fill colour
    """

    with open(infile, "rb") as svg_file:
       svg_string = svg_file.read()
    
    root = etree.fromstring(svg_string)
    regions = list(root.xpath('//*[@id="Areas"]/*'))
    
    for (fill, region) in zip(REGION_COLOURS, regions):
        set_fill_children(region, fill)

    with open("src/media/uk_regions.svg", "wb") as region_file:
        region_file.write(etree.tostring(root))

    fill_each(root, "r", regions, "src/media", fills=REGION_COLOURS)


def counties(infile):
    with open(infile, "rb") as svg_file:
        svg_string = svg_file.read()
    
    root = etree.fromstring(svg_string)
    counties = list(root.xpath('//*[@id="Areas"]/*/*'))

    fill_each(root, "c", counties, "src/media")

def extract_counties_svg(infile, outfile):
    
    with open(infile, "rb") as svg_file:
       svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    regions = list(root.xpath('//*[@id="Areas"]/*'))

    rows = []

    for region in regions:
        try:
            region_name = region.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        except KeyError:
            region_name = region.attrib['id'] 
        
        for county in region.xpath("./*"):
            try:
                county_name = county.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
            except KeyError:
                county_name = county.attrib['id'] 
            
            rows.append([county_name, region_name])

    with open(outfile, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def extract_bow_svg(infile, outfile):
    
    with open(infile, "rb") as svg_file:
       svg_string = svg_file.read()

    root = etree.fromstring(svg_string)
    bows = list(root.xpath('//*[@id="Bodies of Water"]/*'))

    rows = []

    for bow in bows:
        try:
            bow_name = bow.attrib['{http://www.inkscape.org/namespaces/inkscape}label']
        except KeyError:
            bow_name = bow.attrib['id'] 
            
        rows.append([bow_name])
    
    with open(outfile, "w") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def gen_locator_maps(infile, outfolder):
    """
    For each region file:
        fill_each(root, "locator", counties, outfolder, inactive_colour=region_colour, fills=[highlighted_colour]*len(counties))
    """

    for filename in os.listdir(outfolder):
        if filename.startswith('r-'):
            with open(outfolder+"/"+filename, "rb") as svg_file:
                svg_string = svg_file.read()
            
            region = filename.replace('r-', '').replace('.svg', '')
            
            root = etree.fromstring(svg_string)
            counties = list(root.xpath(f'//*[@id="{region}"]/*'))
            print(region)
            region_colour = get_fill(counties[0])

            stroke_colour = BLACK
            if region_colour == BLACK:
                stroke_colour = RED

            stroke_each(root, "locator", counties, outfolder, [stroke_colour]*len(counties))





if __name__ == '__main__':

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--infile", "-i", action="store", required=True)
    # parser.add_argument("--outfolder", "-o", action="store", required=True)
    # parser.add_argument("--xpath", "-x", action="store", default=AREAS_XPATH)
    # args = vars(parser.parse_args())
    # print(args)

    infile = "Map.svg"
    subprocess.run(["cp", infile, "src/media/uk_counties.svg"])
    extract_counties_svg(infile, "counties.csv")
    extract_bow_svg(infile, "bow.csv")
    bodies_of_water(infile)
    regions(infile)
    counties(infile)
    gen_locator_maps(infile, "src/media")