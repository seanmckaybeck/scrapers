'''
gets new podcasts from a supplied list of podcasts. if any new ones
are found, the user is notified via email with a list of new podcasts

usage:
    python podcasts_requests.py -u urls.txt -s smtp.mail.yahoo.com:587 -e myyahooemail@yahoo.com  -p password -t toaddress@lol.com

currently logs debugging messages to stdout. change debug level at beginning to suppress messages
requires running local mongodb instance
'''
import argparse
import logging
import multiprocessing
import smtplib
import sys
from email.mime.text import MIMEText

import pymongo
import requests
from bs4 import BeautifulSoup


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def get_args():
    '''
    gets the command line args
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', type=str, default='urls.txt', help='The file containing the Podcast feed URLs to parse')
    parser.add_argument('-e', type=str, required=True, help='Email address to send from')
    parser.add_argument('-s', type=str, required=True, help='SMTP server address')
    parser.add_argument('-p', type=str, required=True, help='Password to login to SMTP server')
    parser.add_argument('-t', type=str, required=True, help='Address to send email to')
    return parser.parse_args()


def get_urls(url_file):
    '''
    extracts name:url pairs from the supplied file
    '''
    with open(url_file) as f:
        l = [line.strip() for line in f.readlines()]
        d = []
        for line in l:
            sp = line.split()
            if len(sp) != 2:
                raise Exception('URL file incorrectly formatted at line: {}'.format(line))
            d.append(sp)
        logging.debug('Finished extracting URLs to crawl')
        return d


def get_db():
    '''
    returns an instance of the mongodb client
    '''
    client = pymongo.MongoClient()
    db = client['podcasts']
    logging.debug('Got the database instance')
    return db


def parse(url):
    '''
    returns dictionary of name to list of podcast dicts
    '''
    d = {url[0]: []}
    resp = requests.get(url[1])
    soup = BeautifulSoup(resp.content, 'xml')
    items = soup.find_all('item')
    for item in items:
        i = {}
        i['title'] = item.title.text
        i['link'] = item.link.text
        if item.description is not None:
            i['description'] = item.description.text
        if item.pubDate is not None:
            i['date'] = item.pubDate.text
        if item.duration is not None:
            i['duration'] = item.duration.text
        if item.summary is not None:
            i['summary'] = item.summary.text
        if item.author is not None:
            i['author'] = item.author.text
        d[url[0]].append(i)
    logging.debug('Finished parsing {}'.format(url[0]))
    return d


def split_work(urls):
    '''
    returns list of each of ret values from parse()
    uses multiprocessing pool to parallelize the process
    '''
    cpus = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=cpus)
    pool_outputs = pool.map(parse, urls)
    pool.close()
    pool.join()
    logging.debug('All processes completed parsing')
    return pool_outputs


def save(d, db):
    '''
    saves the given name:list of dicts to mongodb
    adds entry to db if it isnt already there
    '''
    name = list(d.keys())[0]
    collection = db[name]
    added = []
    for item in d[name]:
        if collection.find_one({'title': item['title']}) is None:
            collection.update({'title': item['title']}, item, upsert=True)
            added.append(item)
    logging.debug('Finished saving {} items to {} collection'.format(len(added), name))
    return {name: added}


def save_to_db(podcast_dicts, db):
    '''
    calls save on each set of extracted url info
    '''
    res = []
    for d in podcast_dicts:
        res.append(save(d, db))
    logging.debug('Finished saving all new items to database')
    return res


def email(podcasts, server, user, password, to):
    '''
    emails specified user when new podcasts are found
    '''
    body = ''
    for d in podcasts:
        name = list(d.keys())[0]
        if not d[name]:
            continue
        body += '<h2>{}</h2><br>'.format(name)
        for item in d[name]:
            body += '<b>{}</b><br>'.format(item['title'])
            body += 'Link: {}<br>'.format(item['link'])
    if not body:
        logging.debug('No new podcasts')
        return
    head = '<html><head></head><body>'
    body = head + body
    body += '</body></html>'
    msg = MIMEText(body, 'html')
    msg['Subject'] = 'New podcasts'
    msg['From'] = user
    msg['To'] = to
    s = smtplib.SMTP(server)
    s.starttls()
    logging.debug('Logging in to email server')
    s.login(user, password)
    logging.debug('Sending email')
    s.send_message(msg)
    logging.debug('Email sent')
    s.quit()


if __name__ == '__main__':
    args = get_args()
    urls = get_urls(args.u)
    db = get_db()
    podcast_dicts = split_work(urls)
    new_podcasts = save_to_db(podcast_dicts, db)
    email(new_podcasts, args.s, args.e, args.p, args.t)
