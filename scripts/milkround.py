import os
import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html


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


def duplicated_sector(lines):
    for i in range(len(lines)-2):
        for j in range(i+1, len(lines)-1):
            if lines[i][5] == lines[j][5]:
                lines[i][2] = lines[i][2] + ', ' + lines[j][2]
                lines.pop(j)
    return lines


def milkround():
    initial_url = 'https://www.milkround.com/'
    soup = BeautifulSoup(requests.request('GET', url=initial_url).content, 'html5lib')
    sector_links = soup.select('div#sectorTabContent a')
    sectors = []
    locations = []
    lines = []
    provider = 'Milkround'
    for sector_link in sector_links:
        sector = sector_link.text.strip()
        sectors.append(sector)
    location_url = 'https://www.milkround.com/jobs/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.122 Safari/537.36 '
    }
    res = requests.request('GET', url=location_url, headers=headers).text
    l_soup = BeautifulSoup(res, 'html5lib')
    l_url = l_soup.select('ul#Popular_locations a')
    for loc in l_url:
        locations.append(loc.text)
    for sec in sectors:
        for loc in locations:
            url = location_url + sec.replace(' ', '-').lower() + '/in-' + loc.replace(' ', '-').lower()
            response = requests.request('GET', url=url, headers=headers)
            url_soup = BeautifulSoup(response.content, 'html5lib')
            cards = url_soup.find_all('div', {'class': 'job'})
            print(url)
            for card in cards:
                title = card.find('div', {'class': 'job-title'}).a.text.replace('\n', '').replace('  ', '').replace(' – ', ' - ').strip()
                link = card.find('div', {'class': 'job-title'}).a['href']
                employer = card.find('li', {'class': 'company'}).text.strip()
                card.find('li', {'class': 'location'}).find('div', {'class': 'commute-time-info'}).decompose()
                location = card.find('li', {'class': 'location'}).text.replace('\n', '').replace('  ', '').strip()
                line = [employer.replace(' - ', ' '), title.replace(' - ', ' '), sec.replace(' - ', ' '),
                        location.replace(' - ', ' '), provider, link + '||View']
                if line not in lines:
                    print(line)
                    lines.append(line)
        rows = duplicated_sector(lines=lines)
        generator_xml(lines=rows, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    milkround()
    print('============================= The End ===========================')
