'''
gets all products on Provident Metals' website.
does so in multiple processes
'''
import multiprocessing
import os
import sqlite3
import time

import requests
from bs4 import BeautifulSoup


BASE_URLS = ['http://www.providentmetals.com/bullion/silver.html',
             'http://www.providentmetals.com/bullion/gold.html']
SCHEMA = 'create table products (id integer primary key autoincrement not null,title text not null,link text not null)'
DATABASE = 'provident.db'


def get_url(url):
    return requests.get(url).content


def scrape_items(links):
    items = []
    for link in links:
        print('Scraping page {}'.format(link))
        html = get_url(link)
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select('h1')[0].text.lstrip().rstrip()
        items.append((title,link))
    return items


def scrape_item_lists(soup):
    all_items = []
    hds = soup.select('div.item h5')
    a = [hd.select('a')[0]['href'] for hd in hds] # link to product pages
    items = scrape_items(a)
    all_items.append(items)
    btn = soup.select('a.next.i-next')
    while btn:
        html = get_url(btn[0]['href'])
        soup = BeautifulSoup(html, 'html.parser')
        hds = soup.select('div.item h5')
        a = [hd.select('a')[0]['href'] for hd in hds] # link to product pages
        items = scrape_items(a)
        all_items += items
        btn = soup.select('a.next.i-next')
    return all_items

def scrape(url, rets):
    all_items = []
    html = get_url(url)
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.select('div.item.col-xs-6 a')
    links = [link['href'] for link in a]
    for link in links:
        print('Trying link {}'.format(link))
        html = get_url(link)
        soup = BeautifulSoup(html, 'html.parser')
        a = soup.select('div.item.col-xs-6 a')
        if a:
            # got another page to dig through
            links += [link['href'] for link in a]
        else:
            i = scrape_item_lists(soup)
            all_items += i
    rets[url] = all_items


def save_to_db(items):
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            conn.executescript(SCHEMA)
            conn.commit()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for item in items:
            cursor.execute('insert into products (title,link) values (?,?)', item)
        conn.commit()


if __name__ == '__main__':
    print('Getting products')
    m = multiprocessing.Manager()
    rets = m.dict()
    jobs = []
    start = time.time()
    for url in BASE_URLS:
        p = multiprocessing.Process(target=scrape, args=(url,rets))
        jobs.append(p)
        p.start()
    for j in jobs:
        j.join()
    print('Took {} seconds'.format(time.time() - start))
    # convert to list
    items = []
    for k in rets.keys():
        for l in rets[k]:
            if isinstance(l, list):
                for item in l:
                    items.append(item)
            else:
                items.append(l)
    print('Saving to db')
    start = time.time()
    save_to_db(items)
    print('Took {} seconds'.format(time.time() - start))
