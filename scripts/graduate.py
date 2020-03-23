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


def graduate():
    initial_url = 'https://www.graduate-jobs.com/jobs/?page='
    page = 0
    urls = []
    lines = []
    provider = 'Graduate Jobs'
    while True:
        page += 1
        url = initial_url + str(page)
        soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
        items = soup.find_all('li', {'class': 'job-list__item'})
        if not items:
            break
        if url in urls:
            continue
        urls.append(url)
        print(url)
        for item in items:
            title = item.find('span', {'class': 'job-list__title'}).text.strip()
            emp = item.find('p', {'class': 'job-list__company'})
            if emp.find('span', {'class': 'job-list__rank'}):
                emp.find('span', {'class': 'job-list__rank'}).decompose()
            employer = emp.text.strip()
            link = 'https://www.graduate-jobs.com' + item.find('a', {'class': 'job-list__link'})['href']
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            loc = link_soup.find('dt', text=r'Location:').parent
            loc.find(class_='job-page-overview__title').decompose()
            location = loc.dd.text.strip()
            sec = link_soup.find('dt', text=r'Sectors:').parent
            sec.find(class_='job-page-overview__title').decompose()
            sector = sec.dd.text.strip()
            line = [employer, title, sector, location, provider, link + '||View']
            if line not in lines:
                print(line)
                lines.append(line)
        generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    graduate()
    print('============================= The End ===========================')
