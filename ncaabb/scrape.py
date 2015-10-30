'''
TODO
'''
import asyncio
import sqlite3
import re

import aiohttp
from bs4 import BeautifulSoup


DB = 'data.db'
BASE_URL = 'http://www.covers.com'
DATA_URL = '/pageLoader/pageLoader.aspx?page=/data/ncb/teams/pastresults/{}/team{}.html'
YEARS = ['2014-2015', '2013-2014', '2012-2013', '2011-2012', '2010-2011', '2009-2010',
         '2008-2009', '2007-2008', '2006-2007', '2005-2006', '2004-2005', '2003-2004']
ERROR_MSG = 'Oh no, we are sorry!'
NUM_TASKS = 5


def get_teams():
    '''
    Returns list of all team IDs
    '''
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('select id from teams;')
        teams = cursor.fetchall()
    return [team[0] for team in teams]


async def get_page(client, url):
    '''
    Coroutine to get page contents
    '''
    async with client.get(url) as resp:
        assert resp.status == 200
        return await resp.read()


async def parse_year(client, url, _id):
    '''
    Coroutine that parses yearly data for a team and saves it to the db
    '''
    content = await get_page(client, url)
    soup = BeautifulSoup(content, 'lxml')
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr', class_='datarow')
        for row in rows:
            tds = row.find_all('td')
            date = tds[0].text.strip()
            against = tds[1].text.strip()
            try:
                against_id = re.search(r'\d+', tds[1].a.get('href'))
                against_id = against_id.group(0)
            except AttributeError:
                against_id = ''
            score = tds[2].text.strip()
            try:
                boxscore = tds[2].a.get('href')
            except AttributeError:
                boxscore = ''
            type_ = tds[3].text.strip()
            # TODO save to db
            s = '------------------\n{}\n{}\n{}\n{}\n-------------'.format(url, date, against_id, score)
            print(s)


async def parse_team(client, _id):
    '''
    Coroutine that gets data for team, parses it, and adds it to the db
    '''
    for year in YEARS:
        url = BASE_URL+DATA_URL.format(year, _id)
        await parse_year(client, url, _id)


async def work(client, chunk):
    '''
    Coroutine that starts the parsing for each team in its chunk
    '''
    for _id in chunk:
        await parse_team(client, _id)


async def main(client):
    '''
    Main routine
    '''
    ids = get_teams()
    # chunks = [ids[i:i+NUM_TASKS] for i in range(0, len(ids), NUM_TASKS)]
    chunks = [ids[i::NUM_TASKS] for i in range(NUM_TASKS)]
    workers = [asyncio.ensure_future(work(client, chunk)) for chunk in chunks]
    await asyncio.gather(*workers)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = aiohttp.ClientSession(loop=loop)
    loop.run_until_complete(main(client))
    client.close()
