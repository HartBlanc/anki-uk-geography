#!/usr/bin/python3

"""
    parse_wikitable.py

    MediaWiki Action API Code Samples
    Demo of `Parse` module: Parse a section of a page, fetch its table data and save
    it to a CSV file

    MIT license
"""

import csv
import requests

S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"

PARAMS = {
    'action': "parse",
    'prop': 'wikitext',
    'section': 4,
    'format': "json"
}

def get_table(page, filename):
    """ Parse a section of a page, fetch its table data and save it to a CSV file
    """
    params = PARAMS.copy()
    params['page'] = page
    res = S.get(url=URL, params=params)
    data = res.json()
    wikitext = data['parse']['wikitext']['*']
    lines = wikitext.split('|-')[2:]
    entries = []

    # print("hello", wikitext)
    # print("hello2", lines)


    for line in lines:
        line = line.strip()
        if line.startswith("|"):
            entry = line.split("]")[0].replace("|[[", "")
            entries.append([entry])

    with open(filename, "w") as file:
        writer = csv.writer(file)
        writer.writerows(entries)

from lxml import html, etree

def extract_all_links(url, xpath):

    r = requests.get(url)
    r.raise_for_status()
    tree = html.fromstring(r.text)
    links = tree.xpath(xpath)
    rows = [(link.text, "https://en.wikipedia.org" + link.get('href')) for link in links]
    return rows

def city_to_county(city, lookup):

    if 'constituent country' in lookup:
        country_type = 'constituent country'
    else:
        country_type = 'country'

    if lookup[country_type] == 'Scotland':
        return lookup['council area']
    
    elif lookup[country_type] in ("England", "Wales", "Northern Ireland"):
        if "status" in lookup:
            if "county" in lookup['status']:
                return city
        if "ceremonial county" in lookup:
            key = "ceremonial county"
        else:
            for k in lookup:
                if 'county' in k:
                    key = k
                    break

        return lookup[key]
    

    print("ERROR", lookup)

def get_infobox_items(url):
    r = requests.get(url)
    r.raise_for_status()
    tree = html.fromstring(r.text)
    
    infobox = tree.xpath("//table[contains(concat(' ',normalize-space(@class),' '),' infobox ')]")[0]
    label_elems = infobox.xpath('.//th[@scope="row"]')
    value_elems = infobox.xpath('.//th[@scope="row"]/following-sibling::td[1]')

    labels = [' '.join(elem.xpath('.//text()')).lower().replace("\xa0", " ").strip() for elem in label_elems]
    values = [' '.join(elem.xpath('.//text()')).replace("\xa0", " ").strip() for elem in value_elems]
    assert (len(labels) == len(values))
    lookup = {label: value for (label, value) in zip(labels, values)} 
    return lookup

if __name__ == '__main__':
    # get_table("Ceremonial_counties_of_England", "counties.csv")

    urls = extract_all_links("https://en.wikipedia.org/wiki/List_of_cities_in_the_United_Kingdom",'/html/body/div[3]/div[3]/div[4]/div/div[5]/div/div[1]/div//a')

    city_county = []
    for (city, url) in urls:
        infobox = get_infobox_items(url)
        print("City:", f"{city},", "County:", city_to_county(city, infobox))
        city_county.append((city, city_to_county(city, infobox)))

    with open("cities.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(city_county)