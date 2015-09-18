import os
import re
import sqlite3

import requests
from bs4 import BeautifulSoup


URL = 'http://www.foia.cia.gov/'
EXT = 'collection/PDBs'
UA = 'Friendly neighborhood scraper bot'
HEADERS = {'User-Agent': UA}
DB = 'briefings.db'
SCHEMA = '''create table briefings (id integer primary key autoincrement not null,title text not null,link text not null,
         doc_num text not null, create_date text not null, release_date text not null, pub_date text not null,
         body text, document blob)'''
TEMP_PDF = 'lol.pdf'


class Document(object):
    def __init__(self, link, cre, rel, pub, title, doc_num):
        self.link = link
        self.cre = cre
        self.rel = rel
        self.pub = pub
        self.title = title
        self.doc_num = doc_num


def init_db():
    if not os.path.exists(DB):
        with sqlite3.connect(DB) as conn:
            conn.executescript(SCHEMA)
            conn.commit()

def get_page(url):
    req = requests.get(url, headers=HEADERS)
    return BeautifulSoup(req.content, 'lxml')

def get_links(soup):
    return soup.find_all('a', href=re.compile('^/document/')) or []

def get_next_page_link(soup):
    lis = soup.select('li.pager-next')
    if lis:
        return lis[0].find('a')
    return None

def download_pdf(url):
    req = requests.get(url, headers=HEADERS)
    with open(TEMP_PDF, 'wb') as pdf:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk)
                pdf.flush()

def extract_page(link_tag):
    url = URL + link_tag.get('href')
    soup = get_page(url)
    doc_num = link_tag.get('href').split('/')[2] # eek a magic number
    try:
        title = soup.select('h1.documentFirstHeading')[0].text
    except:
        title = 'NA'
    pdf_link = soup.find('a', href=re.compile('.+\.pdf')).get('href')
    # getting dates is tricky. get all of them then assign in order: creation, release, publication
    dates = soup.select('span.date-display-single')
    try:
        cre = dates[0].text
    except:
        cre = 'NA'
    try:
        rel = dates[1].text
    except:
        rel = 'NA'
    try:
        pub = dates[2].text
    except:
        pub = 'NA'
    download_pdf(pdf_link)
    return Document(url, cre, rel, pub, title, doc_num)

def save_to_db(doc):
    with open(TEMP_PDF, 'rb') as pdf:
        data = pdf.read()
        blob = sqlite3.Binary(data)
        with sqlite3.connect(DB) as conn:
            sql = '''insert into briefings (title, link, doc_num, create_date, release_date,
                     pub_date, document) values (?,?,?,?,?,?,?);'''
            params = [doc.title, doc.link, doc.doc_num, doc.cre, doc.rel, doc.pub, blob]
            conn.execute(sql, params)
            conn.commit()

def main():
    init_db()
    url = URL + EXT
    print('Getting {}'.format(url))
    soup = get_page(url)
    links = get_links(soup)
    print('Got links')
    next_page = get_next_page_link(soup)
    while next_page:
        print('Got a next page')
        url = URL + next_page.get('href')
        print('Getting {}'.format(url))
        soup = get_page(url)
        links += get_links(soup)
        print('Got links')
        next_page = get_next_page_link(soup)
    for link in links:
        print('Extracting page {}'.format(link.get('href')))
        doc = extract_page(link)
        print('Saving to db')
        save_to_db(doc)
    print('Done')


if __name__ == '__main__':
    main()
