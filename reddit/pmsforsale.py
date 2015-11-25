'''
Bot to monitor self-text posts for target words.
Intended for /r/pmsforsale but can be used for other subs as well.

Requires praw, requests (dependency of praw), and pyyaml.
Requires Mailgun account. See example.yml for needed info.
'''
import argparse
import datetime
import logging
import sys
import time

import praw
import requests
import yaml


AGENT = 'pmsforsale scraper by /u/thaweatherman v1.0'


def get_args():
    '''
    Gets the arguments passed on the command line
    Returns argparse Namespace object
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str, default='config.yml', help='Config file')
    parser.add_argument('-v', action='count', default=0,
                        help='Change logging verbosity by providing multiple v\'s')
    return parser.parse_args()


def notify(post_url, config):
    '''
    Use Mailgun to send a notification when a matching post is found
    '''
    req = requests.post(
        'https://api.mailgun.net/v3/{}/messages'.format(config['domain']),
        auth=('api', config['mailgun']),
        data={'from': 'Mailgun <mailgun@{}>'.format(config['domain']),
              'to': config['emails'],
              'subject': 'Matching post!',
              'text': 'Found a post matching your requirements. See {}'.format(post_url)
             }
    )
    if req.status_code == 200:
        logging.info('Email sent!')
    else:
        logging.error('Email not sent. Status code was %d', req.status_code)


def get_post_date(post):
    '''
    Converts the post's created time string to a datetime object
    Returns datetime object
    '''
    return datetime.datetime.fromtimestamp(post.created_utc)


def check_posts(sub, last_time, config):
    '''
    Checks the new queue of the target subreddit for posts matching the target words
    '''
    for post in sub.get_new(limit=25):
        logging.info('Checking post %s', post.id)
        if get_post_date(post) < last_time:
            logging.debug('Post is older than last check...breaking...')
            break
        if any(target in post.selftext.lower() or target in post.title.lower()
               for target in config['targets']):
            logging.info('Got a match! Notifying...')
            notify(post.url, config)


def main():
    '''
    The main routine
    '''
    args = get_args()
    if args.v > 4:
        args.v = 4
    level = 50 - args.v*10
    logging.basicConfig(stream=sys.stdout, level=level)
    with open(args.c) as conf:
        config = yaml.load(conf)

    reddit = praw.Reddit(AGENT)
    logging.debug('Logging in to Reddit using %s and %s', config['username'], config['password'])
    reddit.login(config['username'], config['password'], disable_warning=True)
    logging.debug('Getting subreddit %s', config['subreddit'])
    sub = reddit.get_subreddit(config['subreddit'])
    # set last check date to a day earlier
    last_time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    while True:
        try:
            logging.debug('Checking posts...')
            check_posts(sub, last_time, config)
            last_time = datetime.datetime.utcnow()
            logging.debug('Sleeping for %d seconds...', config['sleep'])
            time.sleep(config['sleep'])
        except Exception as exc:
            logging.error('Got an error:\n{}'.format(exc))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as exc:
        logging.info('Killing gracefully...')
