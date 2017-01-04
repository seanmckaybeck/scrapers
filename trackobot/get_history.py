"""
Get game history for the current month.
Optionally start from a certain page.
Save results to a JSON file.
"""
import argparse
import datetime
import json
import time

import requests

from config import USERNAME, TOKEN


URL = 'https://trackobot.com/profile/history.json'
PARAMS = {'username': USERNAME, 'token': TOKEN, 'page': 1}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=int, default=1, help='The page to start from')
    parser.add_argument('-o', default='games.json', help='The file to save game data to')
    return parser.parse_args()


def main():
    args = get_args()
    PARAMS['page'] = args.s
    today = datetime.datetime.utcnow()
    end_of_month = False
    games = []
    while not end_of_month:
        print('Requesting page {}'.format(PARAMS['page']))
        r = requests.get(URL, params=PARAMS)
        for game in r.json()['history']:
            d = datetime.datetime.strptime(game['added'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if d.year != today.year or d.month != today.month:
                print('Hit the end of the month!')
                end_of_month = True
                break
            games.append(game)
        PARAMS['page'] += 1
        print('Sleeping')
        time.sleep(1)  # be nice to the site
    print('Writing games out')
    with open(args.o, 'w') as f:
        f.write(json.dumps(games))
    print('Done!')


if __name__ == '__main__':
    main()

