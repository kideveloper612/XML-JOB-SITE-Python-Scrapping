import os
import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html
import json
import re


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(html.unescape(elem), 'utf-8')
    rep = minidom.parseString(rough_string)
    return rep.toprettyxml(indent="  ")


def generator_xml(lines, filename):
    if not os.path.isdir('output'):
        os.mkdir('output')
    filename = 'output/' + filename
    root = ET.Element("jobs")

    for line in lines:
        ET.SubElement(root, "job", {
            'Employer': line[0],
            'Title': line[1],
            'Sector': line[2],
            'Location': line[3],
            'Provider': line[4],
            'Link': line[5]
        })

    output_file = open(filename, 'w')
    output_file.write(prettify(root))
    output_file.close()


def post_request(industry_no):
    request_url = 'https://www.gradtouch.com/jobs'
    page = 0
    lines = []
    while True:
        page += 1
        payload = {
            'filters[graduate][]': '2',
            'filters[internship][]': '3',
            'filters[placement][]': '4',
            'page': '{}'.format(page),
            'js': 'true',
            'filters[industry][]': '{}'.format(industry_no)
        }
        response = requests.request("POST", url=request_url, data=payload)
        if response.status_code != 200:
            return False
        res_soup = BeautifulSoup(response.content, 'html5lib')
        cards = res_soup.find_all('li', {'class': 'c-tile--reg'})
        if not cards:
            return lines
        for card in cards:
            employer = card.find(attrs={'class': 'c-tile__title'}).text.strip()
            title = card.find(attrs={'class': 'c-tile__subtitle'}).text.strip()
            link = card.a['href']
            loc = card.find('ul', {'class': 'c-jobTile__locations'})
            location = ''
            if loc:
                ls = loc.find_all('li', {'class': 'c-jobTile__location'})
                for min_ls in ls:
                    location += min_ls.text + ', '
                location = location[:-2]
            else:
                location = card.find(attrs={'class': 'c-jobTile__locationText'}).text.strip()
            print([employer, title, location, link])
            lines.append([employer, title, location, link])


def gradtouch():
    land_url = 'https://www.gradtouch.com/jobs'
    land_soup = BeautifulSoup(requests.get(url=land_url).content, 'html5lib')
    data_filters = land_soup.find(id='jobsearch-industry').find_all('option')
    rows = []
    provider = 'Gradtouch'
    for data_filter in data_filters:
        industry = data_filter['value']
        sector = data_filter.text.strip()
        lines = post_request(industry_no=industry)
        for line in lines:
            if line not in rows:
                rows.append([line[0], line[1], sector, line[2], provider, line[3]])
                generator_xml(lines=rows, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    gradtouch()
    print('============================= The End ===========================')
