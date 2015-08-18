'''
scrapes the free section of the specified
craigslist. single-threaded, non-recursive
'''
import argparse
import time

import requests
from bs4 import BeautifulSoup


FREE_QUERY = '/search/zip'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', type=str, default='http://baltimore.craigslist.org', help='your local craigslist website, including HTTP schema')
    return parser.parse_args()


def extract_entry_data(entry, url):
    link = entry.select('a')[0]['href']
    submitted = entry.select('time')[0]['datetime']
    title = entry.find_all('a', class_='hdrlnk')[0].text
    title = '{}{}'.format(url, title)
    return {'link': link, 'submitted': submitted, 'title': title}


def parse(url):
    u = '{}{}'.format(url, FREE_QUERY)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Cookie': 'cl_tocmode=sss%3Agrid'
    }
    start = time.time()
    resp = requests.get(u, headers=headers)
    print('Took {} seconds to retrieve page'.format(time.time()-start))
    soup = BeautifulSoup(resp.content, 'html.parser')
    entries = soup.select('p.row')
    a = []
    start = time.time()
    for entry in entries:
        a.append(extract_entry_data(entry))
    print('Took {} seconds to retrieve item details'.format(time.time()-start))
    [print(entry) for entry in a]


if __name__ == '__main__':
    args = get_args()
    parse(args.w)
