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


def Debut():
    initial_url = 'https://jobs.debut.careers'
    initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
    sectors = initial_soup.select('#industry_sector-container > li > a')
    lines = []
    for sec in sectors:
        sector = sec.text.strip()
        sec_url = initial_url + sec['href'] + '-from_'
        count = -29
        provider = 'Debut'
        while True:
            count += 30
            url = sec_url + str(count)
            print(url)
            soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
            cards = soup.find_all('a', {'class': 'job-card'})
            if not cards:
                break
            for card in cards:
                link = 'https://jobs.debut.careers/' + card['href']
                title = card.select('.details .position')[0].text.replace(' – ', ' - ').strip()
                employer = card.select('.details .description')[0].text.split('·')[0].strip()
                location = card.select('.details .description')[0].text.split('·')[2].strip()
                line = [employer, title, sector, location, provider, link.replace('-–-', '-') + '||View']
                if line not in lines:
                    print(line)
                    lines.append(line)
        generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    Debut()
    print('============================= The End ===========================')
