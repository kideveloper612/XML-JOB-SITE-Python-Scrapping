import os
import requests
from bs4 import BeautifulSoup
import xml


class All:
    def __init__(self):
        pass

    def target(self):
        initial_url = 'https://targetjobs.co.uk/search/all/group_facet/Employers'
        res = requests.request('GET', url=initial_url).text
        print(res)


if __name__ == '__main__':
    print('=============================Start===============================')
    a = All()
    a.target()
    print('============================= The End ===========================')
