import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html
import os


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


def execute():
    initial_url = 'https://www.brightnetwork.co.uk/search/?job_types=1'
    page = 0
    provider = 'Brightnetwork'
    lines = []
    urls = []
    while True:
        page += 1
        url = initial_url + '&offset=%s' % page
        if url in urls:
            continue
        urls.append(url)
        initial_soup = BeautifulSoup(requests.request('GET', url=url).content, 'html5lib')
        rows = initial_soup.select('.search-result-row')
        if rows:
            for row in rows:
                employer_link = 'https://www.brightnetwork.co.uk' + row.find('a', {'class': 'result-link'})[
                    'href']
                print(employer_link)
                link_soup = BeautifulSoup(requests.request('GET', url=employer_link).content, 'html5lib')
                title = link_soup.select('.page-header')[0].text.replace(' – ', ' - ').strip()
                employer = link_soup.find('div', {'class': 'field-related-company'}).a.text.strip()
                sector = link_soup.find('div', {'class': 'field-sectors'}).find(
                    class_='field-item').text.strip()
                location = link_soup.find('div', {'class': 'field-locations'}).find(
                    class_='field-item').text.replace('\n', ' ').replace('  ', '').strip()
                line = [employer, title, sector, location, provider, employer_link + '||View']
                if line not in lines:
                    print(line)
                    lines.append(line)
                generator_xml(lines=lines, filename='{}.xml'.format(provider))
        else:
            break


if __name__ == '__main__':
    print('=============================Start===============================')
    execute()
    print('============================= The End ===========================')
