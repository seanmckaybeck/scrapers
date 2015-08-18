'''
Scrapes the free section of specified craigslist
using requests and beautifulsoup4. it only grabs
the first page and all of its elements. a threadexecutor
is used to try and speed up the process of extracting
all of the relevant data, but testing shows that
the single-thread version is faster.
'''
import argparse
import concurrent.futures
from multiprocessing import cpu_count
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
    count = cpu_count()
    data = []
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=count*2) as executor:
        res = [executor.submit(extract_entry_data, entry, url) for entry in entries]
        for future in concurrent.futures.as_completed(res):
            try:
                entry = future.result()
                data.append(entry)
            except Excecption as e:
                print(str(e))
    print('Took {} seconds to retrieve item details'.format(time.time()-start))
    [print(entry) for entry in data]


if __name__ == '__main__':
    args = get_args()
    parse(args.w)
