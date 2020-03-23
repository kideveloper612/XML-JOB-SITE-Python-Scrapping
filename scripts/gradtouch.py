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


def gradtouch():
    path = 'HTML/gradtouch.html'
    file = open(file=path)
    data = file.read()
    soup = BeautifulSoup(data, 'html5lib')
    cards = soup.find_all('li', {'class': 'c-tile--reg'})
    provider = 'Gradtouch'
    lines = []
    for card in cards:
        link = card.a['href']
        print(link)
        employer = card.find(class_='c-jobTile__title--reg').text.strip()
        title = card.find(class_='c-tile__subtitle--reg').text.strip()
        loc = card.find('ul', class_='c-jobTile__locations')
        location = ''
        if loc:
            sub_ls = loc.find_all('li')
            for sub_l in sub_ls:
                location += sub_l.text + ', '
            location = location.strip()[:-1].strip()
        else:
            location = card.find('span', {'class': 'c-jobTile__locationText'}).text.strip()
        line = [employer, title, '', location, provider, link]
        if line not in lines:
            print(line)
            lines.append(line)
        generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    gradtouch()
    print('============================= The End ===========================')
