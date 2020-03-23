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


def GRB():
    post_url = 'https://www.grb.uk.com/index.php?id=1635&position_type=Full-Time&isExperienced=0&division_cond=0&is_external=0&and_or_condition='
    page = 0
    provider = 'GRB'
    lines = []
    urls = []
    while True:
        page += 1
        print(page)
        payload = {
            'page': page
        }
        res = requests.post(url=post_url, data=payload).text
        data = json.loads(res)['vacancies']
        print(data)
        if data is None:
            break
        for vacancy in data:
            title = vacancy['title'].replace(' – ', ' - ')
            url = 'https://www.grb.uk.com/graduate-jobs/' + vacancy['jobUrl']
            if url in urls:
                continue
            urls.append(url)
            print(page, url)
            soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
            emp = soup.find('b', text=re.compile('Company:')).parent
            emp.find('b').decompose()
            employer = emp.text.strip()
            loc = soup.find('b', text=re.compile('Location:')).parent
            loc.find('b').decompose()
            location = loc.text.strip()
            sec = soup.find('b', text=re.compile('Job Category:')).parent
            sec.find('b').decompose()
            sector = sec.text.replace('\n', '').replace('\t', '').strip()
            line = [employer, title, sector, location, provider, url + '||View']
            if line not in lines:
                print(line)
                lines.append(line)
        generator_xml(lines=lines, filename='{}.xml'.format(provider))


if __name__ == '__main__':
    print('=============================Start===============================')
    GRB()
    print('============================= The End ===========================')
