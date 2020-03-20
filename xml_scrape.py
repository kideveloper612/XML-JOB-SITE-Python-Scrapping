import os
import requests
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html
import json
import re


class All:
    def __init__(self):
        pass

    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(html.unescape(elem), 'utf-8')
        rep = minidom.parseString(rough_string)
        return rep.toprettyxml(indent="  ")

    def generator_xml(self, lines, filename):
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
        output_file.write(self.prettify(root))
        output_file.close()

    def brightnetwork(self):
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
                    try:
                        employer_link = 'https://www.brightnetwork.co.uk' + row.find('a', {'class': 'result-link'})[
                            'href']
                        print(employer_link)
                        link_soup = BeautifulSoup(requests.request('GET', url=employer_link).content, 'html5lib')
                        title = link_soup.select('.page-header')[0].text.replace(' - ', ' ').strip()
                        employer = link_soup.find('div', {'class': 'field-related-company'}).a.text.strip()
                        sector = link_soup.find('div', {'class': 'field-sectors'}).find(
                            class_='field-item').text.strip()
                        location = link_soup.find('div', {'class': 'field-locations'}).find(
                            class_='field-item').text.replace('\n', ' ').replace('  ', '').strip()
                        line = [employer, title, sector, location, provider, employer_link + '||View']
                        if line not in lines:
                            print(line)
                            lines.append(line)
                        self.generator_xml(lines=lines, filename='{}.xml'.format(provider))
                    except Exception as e:
                        print(e)
                        continue
            else:
                break

    def target(self):
        initial_url = 'https://targetjobs.co.uk/search/all/group_facet/Vacancies?page='
        page = 0
        provider = 'Targetjobs'
        urls = []
        lines = []
        while True:
            page += 1
            url = initial_url + str(page)
            print(page, url)
            soup = BeautifulSoup(requests.get(url=url).content, 'html5lib')
            views = soup.select('.views-row')
            if not views:
                break
            for view in views:
                if view.select('div.pane-content > a'):
                    employer = view.select('div.pane-content > a')[0].text.strip()
                    job = view.select('div.pane-content > h3 >a')[0]
                    title = job.text.strip()
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
                    line = [employer, title, sector, location, provider, link + '||View']
                    if line not in lines:
                        print(line)
                        lines.append(line)
                        self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def milkround(self):
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
                    title = card.find('div', {'class': 'job-title'}).text.replace('\n', '').replace('  ', '').strip()
                    link = card.find('div', {'class': 'job-title'}).a['href']
                    employer = card.find('li', {'class': 'company'}).text.strip()
                    location = card.find('li', {'class': 'location'}).text.replace('\n', '').replace('  ', '').strip()
                    line = [employer.replace(' - ', ' '), title.replace(' - ', ' '), sec.replace(' - ', ' '),
                            location.replace(' - ', ' '), provider, link + '||View']
                    if line not in lines:
                        print(line)
                        lines.append(line)
                self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def prospects(self):
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
                title = row.find(attrs={'class': 'card-secondary-title'}).text.strip()
                employer = row.find(class_='card-secondary-meta').li.text.strip()
                link = 'https://www.prospects.ac.uk' + row.a['href']
                soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
                if soup.find(class_='dl'):
                    dd = soup.find(class_='dl').dl.find_all('dd')
                    location = ''
                    for d in dd:
                        location += d.text.strip() + '|'
                    line = [employer, title, sector, location[:-1], provider, link + '||View']
                    if line not in lines:
                        print(line)
                        lines.append(line)
            self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def gradcracker(self):
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
                self.generator_xml(lines=lines, filename='{}_Again.xml'.format(provider))

    def gradcracker_process(self):
        tree = ElementTree.parse('xml/Gradcracker.xml').getroot()
        links = []
        lines = []
        for item in tree.iter('job'):
            employer = item.attrib['Employer']
            title = item.attrib['Title']
            sector = item.attrib['Sector']
            location = item.attrib['Location']
            provider = item.attrib['Provider']
            link = item.attrib['Link']
            if link not in links:
                links.append(link)
                line = [employer, title, 'Engineering', location, provider, link]
                if line not in lines:
                    print(line)
                    lines.append(line)
        self.generator_xml(lines=lines, filename='Gradcracker.xml')

    def GRB(self):
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
                title = vacancy['title']
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
            self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def graduate(self):
        initial_url = 'https://www.graduate-jobs.com/jobs/?page='
        page = 0
        urls = []
        lines = []
        provider = 'Graduate'
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
            self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def Debut(self):
        initial_url = 'https://jobs.debut.careers'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
        sectors = initial_soup.select('#industry_sector-container > li > a')
        lines = []
        for sec in sectors:
            sector = sec.text.strip()
            sec_url = initial_url + sec['href'] + '-from_'
            count = -29
            provider = 'Debut_careers'
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
                    title = card.select('.details .position')[0].text.strip()
                    employer = card.select('.details .description')[0].text.split('·')[0].strip()
                    location = card.select('.details .description')[0].text.split('·')[2].strip()
                    line = [employer, title, sector, location, provider, link + '||View']
                    if line not in lines:
                        print(line)
                        lines.append(line)
            self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def gradtouch(self):
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
            self.generator_xml(lines=lines, filename='{}.xml'.format(provider))

    def Add(self):
        path = 'xml/'
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
        self.generator_xml(lines=lines, filename='Total.xml')


if __name__ == '__main__':
    print('=============================Start===============================')
    a = All()
    a.Add()
    print('============================= The End ===========================')
