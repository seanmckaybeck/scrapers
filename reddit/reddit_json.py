'''
uses the reddit JSON api to scrape subreddits for posts.
all posts are saved to a local mongodb instance

by default it only scrapes the first page, but the user
can specify more pages to scrape
'''
import argparse
import time

import pymongo
import requests


BASE_URL = 'https://www.reddit.com/r/'
POSTFIX = '/.json?count=25&after='


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, default='learnpython', help='Subreddit to scrape. Defaults to learnpython')
    parser.add_argument('-c', type=int, default=1, help='Recursion depth. Defaults to 1')
    return parser.parse_args()


def get_json(sub, after):
    url = '{}{}{}{}'.format(BASE_URL, sub, POSTFIX, after)
    headers = {'User-Agent': 'JSON scraper v1'}
    resp = requests.get(url, headers=headers)
    # have to account for constant 429 code from reddit
    # you'd think they would use gilding money for better servers...
    while resp.status_code != 200:
        resp = requests.get(url, headers=headers)
    return resp.json()['data']


def parse_posts(data):
    posts = []
    for post in data['children']:
        d = {}
        d['url'] = post['data']['permalink']
        d['title'] = post['data']['title']
        d['created'] = post['data']['created']
        d['subreddit'] = post['data']['subreddit']
        if not post['data']['is_self']:
            d['post'] = post['data']['url']
        else:
            d['post'] = post['data']['selftext']
        posts.append(d)
    return posts


def save_to_mongo(posts, sub):
    client = pymongo.MongoClient()
    db = client['reddit']
    collection = db[sub]
    for post in posts:
        collection.update({'url': post['url']}, post, upsert=True)


if __name__ == '__main__':
    args = get_args()
    after = ''
    posts = []
    for i in range(args.c):
        data = get_json(args.s, after)
        posts +=  parse_posts(data)
        after = data['after']
        time.sleep(1) # for rate limits
    save_to_mongo(posts, args.s)
