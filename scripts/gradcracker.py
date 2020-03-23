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


def gradcracker():
    initial_url = 'https://www.gradcracker.com/search/all-disciplines/engineering-jobs'
    initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
    lis = initial_soup.select('ul.group-disciplines > ul >li')
    provider = 'Gradcracker'
    lines = []
    for li in lis:
        sector = li.span.find(text=True, recursive=False)
        page = 0
        while True:
            page += 1
            sector_link = 'https://www.gradcracker.com' + li.a['href'] + '?page={}'.format(page)
            sector_soup = BeautifulSoup(requests.get(url=sector_link).content, 'html5lib')
            last_page = int(sector_soup.select('.pagination > li')[-2].text)
            if page > last_page:
                break
            result_cards = sector_soup.find_all('div', {'class': ['result-card']})
            print(sector_link)
            for result_card in result_cards:
                if result_card.has_attr('class') and 'carousel' in result_card['class']:
                    continue
                if result_card.find(attrs={'class': 'masthead'}):
                    employer = result_card.find(attrs={'class': 'masthead'})['title'].split('with')[1].strip()
                else:
                    employer = ''
                jobs = result_card.find_all(attrs={'class': 'job'})
                for job in jobs:
                    if job.find('h2'):
                        title = job.find('h2').text.replace('\n', ' ').replace('  ', '').strip()
                        job_link = job.h2.find('a')['href']
                        job_soup = BeautifulSoup(requests.get(url=job_link).content, 'html5lib')
                        location = job_soup.find('span', attrs={'title': 'Location'}).parent.find('span', {
                            'class': 'font-semibold'}).find(text=True, recursive=False).strip()
                        line = [employer, title, sector, location, provider, job_link + '||View']
                        if line not in lines:
                            print(line)
                            lines.append(line)
            generator_xml(lines=lines, filename='{}_Again.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    gradcracker()
    print('============================= The End ===========================')
