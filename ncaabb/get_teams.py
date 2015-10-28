'''
Gets the URL and team ID for each NCAA Basketball team from www.covers.com
'''
import os
import re
import sqlite3

import requests
from bs4 import BeautifulSoup


TEAMS_SQL = 'create table teams (id int primary key not null,' \
      'name text not null, url text not null);'
# TODO sql for other tables
BASE_URL = 'http://www.covers.com'
TEAM_URL = '/pageLoader/pageLoader.aspx?page=/data/ncb/teams/teams.html'
DB = 'data.db'


def init_db():
    '''
    Initializes the db if it doesn't exist
    '''
    if not os.path.exists(DB):
        with sqlite3.connect(DB) as conn:
            conn.execute(TEAMS_SQL)


def scrape():
    '''
    Scrapes the teams and adds them to the db
    '''
    req = requests.get(BASE_URL+TEAM_URL)
    soup = BeautifulSoup(req.content, 'lxml')
    links = soup.find_all('a', href=re.compile(r'/data/ncb/teams/team\d+\.html'))
    rows = []
    for link in links:
        _id = re.search(r'\d+', link.get('href'))
        _id = _id.group(0)
        rows.append((_id, link.text, link.get('href')))
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.executemany('insert into teams values (?,?,?);', rows)
        conn.commit()


def main():
    '''
    The main routine
    '''
    init_db()
    scrape()


if __name__ == '__main__':
    main()
