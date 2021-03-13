import csv
from pathlib import Path

from lxml import etree

# Counties
CONSTITUENCY_MAP = Path("UK_Constituencies_2017_(blank).svg")

with CONSTITUENCY_MAP.open(mode="rb") as svg_file:
    svg_string = svg_file.read()

svg_root = etree.fromstring(svg_string)
constituency_elems = list(svg_root.xpath('//*[@id="Constituencies"]/*'))

con_to_counties = dict()
with open("constituency_to_county.txt") as f:
    for con, counties in csv.reader(f, delimiter="|"):
        con_to_counties[con] = counties.split(";")

for elem in constituency_elems:
    names = elem.xpath(".//text()")
    if len(names) != 3:
        print(names)
    con = names[1]
    elem.attrib["id"] = con
    elem.attrib["class"] = " ".join(
        map(lambda x: x.replace(" ", "_").replace(",", ""), con_to_counties[con])
    )

et = etree.ElementTree(svg_root)
et.write("uk_constituencies.svg", pretty_print=True)
