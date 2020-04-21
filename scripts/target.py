import os
import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html
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


def check_available(sub_url):
    url = 'https://targetjobs.co.uk' + sub_url
    available_soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
    sorry = available_soup.find(text=re.compile("Sorry"))
    return sorry


def target():
    initial_url = 'https://targetjobs.co.uk/search/all/group_facet/Vacancies?page='
    page = 0
    provider = 'TARGETjobs'
    urls = []
    lines = []
    while True:
        page += 1
        url = initial_url + str(page)
        print(page, url)
        soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
        views = soup.select('.views-row')
        print(views)
        if not views:
            print('not')
            break
        for view in views:
            if view.select('div.pane-content > a'):
                employer = view.select('div.pane-content > a')[0].text.strip()
                job = view.select('div.pane-content > h3 >a')[0]
                avail = check_available(sub_url=job['href'])
                if avail is not None:
                    print('Oops, not available')
                    exit()
                title = job.text.replace(' – ', ' - ').strip()
                link = 'https://targetjobs.co.uk' + job['href']
                if link in urls:
                    continue
                urls.append(link)
                link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
                if link_soup.find('div', {'class': 'field-name-field-ad-vac-locations'}):
                    location = link_soup.find('div', {'class': 'field-name-field-ad-vac-locations'}).find('div', {
                        'class': 'field-item'}).text.strip()
                else:
                    location = link_soup.find('div', {'class': 'field-name-taxonomy-vocabulary-73'}).find('div', {
                        'class': 'field-item'}).text.strip()
                sector = ''
                if link_soup.select('a.sector.name'):
                    sectors = link_soup.select('a.sector.name')
                    for s in sectors:
                        sector += s.text.strip() + '|'
                    sector = sector[:-1]
                line = [employer, title.replace('’', ''), sector, location.replace('ü', 'u').replace('–', '-').replace('’', ''), provider, link + '||View']
                if line not in lines:
                    print(line)
                    lines.append(line)
                    # generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    target()
    print('============================= The End ===========================')
