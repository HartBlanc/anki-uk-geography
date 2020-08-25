""" Methods for parsing information from wikipedia articles. """

import csv
from typing import List, Dict, Tuple

from lxml import html, etree
import requests


def extract_links(wiki_url: str, link_xpath: str) -> List[Tuple[str, str]]:
    """
    :param wiki_url: URL for a wikipedia article to extract links from
    :param link_xpath: the XPath for identifying which elements to extract
    :return: a list of pairs of link texts and link URLs
             (e.g. "Durham", "https://en.wikipedia.org/wiki/Durham,_England")
    """

    r = requests.get(wiki_url)
    r.raise_for_status()

    tree = html.fromstring(r.text)

    link_elems = tree.xpath(link_xpath)
    rows = [(link_elem.text, f"https://en.wikipedia.org{link_elem.get('href')}")
            for link_elem in link_elems]

    return rows


def city_to_county(city: str, city_infobox: Dict[str, str]) -> str:
    """
    Returns the corresponding county that the city is in,
    based on the wikipedia infobox from the article for that city.
    Naming differences between articles are resolved and edge cases are handled.

    :param city: the city for which the county is needed.
    :param city_infobox: the infobox for the wikipedia article for this city
    :return: The county of the city.
    """

    if 'constituent country' in city_infobox:
        country_type = 'constituent country'
    else:
        country_type = 'country'

    if city_infobox[country_type] == 'Scotland':
        return city_infobox['council area']

    elif city_infobox[country_type] in ("England", "Wales", "Northern Ireland"):
        if "status" in city_infobox:
            if "county" in city_infobox['status']:
                return city

        if "ceremonial county" in city_infobox:
            key = "ceremonial county"
        else:
            for k in city_infobox:
                if 'county' in k:
                    key = k
                    break

        return city_infobox[key]

    print("ERROR", city_infobox)


def get_infobox_items(article_url: str) -> Dict[str, str]:
    """
    :param article_url: A URL for a Wikipedia article with an infobox
    :return: a label->value dictionary of the rows of the infobox
    """
    r = requests.get(article_url)
    r.raise_for_status()
    tree = html.fromstring(r.text)
    
    infobox_elem = tree.xpath("//table[contains(concat(' ',normalize-space(@class),' '),' infobox ')]")[0]
    label_elems = infobox_elem.xpath('.//th[@scope="row"]')
    value_elems = infobox_elem.xpath('.//th[@scope="row"]/following-sibling::td[1]')

    labels = [' '.join(elem.xpath('.//text()')).lower().replace("\xa0", " ").strip() for elem in label_elems]
    values = [' '.join(elem.xpath('.//text()')).replace("\xa0", " ").strip() for elem in value_elems]
    assert (len(labels) == len(values))

    return {label: value for (label, value) in zip(labels, values)}


if __name__ == '__main__':

    CITY_MAP_XPATH = '//div[@class="locmap noviewer thumb tleft"]/div/div[1]/div//a'

    city_urls = extract_links('https://en.wikipedia.org/wiki/List_of_cities_in_the_United_Kingdom',
                              CITY_MAP_XPATH)

    city_county = []
    for (city, url) in city_urls:

        infobox_map = get_infobox_items(url)
        county = city_to_county(city, infobox_map)
        print("City:", f"{city},", "County:", county)
        city_county.append((city, county))

    with open("cities.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(city_county)

