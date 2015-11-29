'''
Checks product pages for an Add to Cart option and notifies by email if there is one.
'''
import argparse
import logging
import sys
import time

import requests
import yaml


FOUND = set()


def get_args():
    '''
    Gets the arguments passed on the command line.
    Returns argparse Namespace object.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str, default='config.yml',
                        help='The config file to use. Defaults to config.yml.')
    parser.add_argument('-v', action='count', default=0,
                        help='Change logging verbosity by providing multiple v\'s.')
    return parser.parse_args()


def notify(config, product):
    '''
    Use Mailgun to send a notification when a matching post is found
    '''
    req = requests.post(
        'https://api.mailgun.net/v3/{}/messages'.format(config['domain']),
        auth=('api', config['mailgun']),
        data={'from': 'Mailgun <mailgun@{}>'.format(config['domain']),
              'to': config['emails'],
              'subject': 'Product available!',
              'text': 'Product is now available. See {}'.format(product)
             }
    )
    if req.status_code == 200:
        logging.info('Email sent!')
    else:
        logging.error('Email not sent. Status code was %d', req.status_code)


def check_urls(config):
    '''
    Checks all products URLs in the config for availability.
    '''
    for product in config['targets']:
        if product not in FOUND:
            logging.info('Checking {}'.format(product))
            req = requests.get(product,
                               headers={'User-Agent':
                                        'Availability checker v1 seanmckaybeck@yahoo.com'})
            while req.status_code != 200:
                logging.debug('Retrying {}'.format(product))
                req = requests.get(product,
                                   headers={'User-Agent':
                                            'Availability checker v1 seanmckaybeck@yahoo.com'})
            if config['cart'] in  req.text:
                logging.info('Product available! Notifying...')
                notify(config, product)
                FOUND.add(product)


def main():
    '''
    The main function, obviously.
    '''
    args = get_args()
    if args.v > 4:
        args.v = 4
    level = 50 - args.v*10
    logging.basicConfig(stream=sys.stdout, level=level)
    with open(args.c) as conf:
        config = yaml.load(conf)
    logging.debug('Using URLs: {}'.format(', '.join(config['targets'])))
    while True:
        try:
            logging.info('Checking products...')
            check_urls(config)
            logging.debug('Sleeping for {} seconds...'.format(config['sleep']))
            time.sleep(config['sleep'])
        except Exception as exc:
            logging.error('Got an error:\n{}'.format(exc))


if __name__ == '__main__':
    main()
