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


def prospects():
    initial_url = 'https://www.prospects.ac.uk/browse-graduate-jobs'
    initial_soup = BeautifulSoup(requests.request('GET', url=initial_url).content, 'html5lib')
    cards = initial_soup.select('.list-browse-courses-jobs li')
    provider = 'Prospects'
    lines = []
    for card in cards:
        if 'All sectors' in card.text:
            continue
        sector = card.span.text.strip()
        sector_link = 'https://www.prospects.ac.uk' + card.a['href']
        sector_soup = BeautifulSoup(requests.get(url=sector_link).content, 'html5lib')
        all_link = 'https://www.prospects.ac.uk' + sector_soup.select('.list-browse-courses-jobs li')[0].a['href']
        link_soup = BeautifulSoup(requests.get(url=all_link).content, 'html5lib')
        rows = link_soup.select('.list-unstyled > li')
        print(all_link)
        for row in rows:
            title = row.find(attrs={'class': 'card-secondary-title'}).text.replace(' – ', ' - ').strip()
            employer = row.find(class_='card-secondary-meta').li.text.strip()
            link = 'https://www.prospects.ac.uk' + row.a['href']
            soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            location_detail = soup.find('dt', attrs={'id': 'section-location-details'})
            if location_detail:
                dd = location_detail.parent.find_all('dd')
                location = ''
                for d in dd:
                    location += d.text.strip() + '|'
                line = [employer, title, sector, location[:-1].replace(' · ', ' | '), provider, link + '||View']
                if line not in lines:
                    print(line)
                    lines.append(line)
        generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    prospects()
    print('============================= The End ===========================')
