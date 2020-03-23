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


def Add():
    path = 'output/'
    for origin, directories, files in os.walk(path):
        file_list = files
    lines = []
    for file in file_list:
        print(file, '===========================================================================')
        base_tree = ElementTree.parse(path + file).getroot()
        for item in base_tree.iter('job'):
            employer = item.attrib['Employer']
            title = item.attrib['Title']
            sector = item.attrib['Sector']
            location = item.attrib['Location']
            provider = item.attrib['Provider']
            link = item.attrib['Link']
            line = [employer, title, sector, location, provider, link]
            if line not in lines:
                print(line)
                lines.append(line)
    generator_xml(lines=lines, filename='Total.xml')


if __name__ == '__main__':
    print('=============================Start===============================')
    Add()
    print('============================= The End ===========================')
