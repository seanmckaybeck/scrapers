"""
Scrapes paste sites for deepweb links
"""
import argparse
import logging
import sys
import threading
import time

from paste import Pastebin
from paste import Pastie
from paste import Slexy


class StopThread(threading.Thread):
    """
    Allows a thread to be gracefully killed
    """
    def __init__(self, site):
        super().__init__()
        self._stop = threading.Event()
        self.site = site

    def stop(self):
        """
        Stops the thread
        """
        self._stop.set()

    def stopped(self):
        """
        Checks if the thread as been stopped
        """
        return self._stop.is_set()

    def run(self):
        logger = logging.getLogger(self.site.__class__.__name__)
        seen = set()
        while not self.stopped():
            logger.info('Getting links')
            links = self.site.get()
            logger.debug('Got %d links. Sleeping for 1 second...', len(links))
            time.sleep(1)
            for link in links:
                if link not in seen:
                    logger.info('Checking link: %s', link)
                    found = self.site.get_paste(link)
                    seen.add(link)
                    if found:
                        # normally this would be tweeted or something
                        logger.debug('----------------------')
                        logger.debug(str(found))
                        logger.debug('----------------------')
                    time.sleep(1)
            logger.debug('Sleeping for 2 seconds before checking for new pastes...')
            time.sleep(2)


def get_args():
    """
    Gets the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', default=0, help='Change logging verbosity')
    parser.add_argument('-c', type=str, action='store', default='scraper.conf',
                        help='Config file containing patterns')
    return parser.parse_args()


def main():
    """
    The main function
    """
    args = get_args()
    if args.v > 4:
        args.v = 4
    level = 50 - args.v*10
    logging.basicConfig(stream=sys.stdout, level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__file__)

    patterns = []
    with open(args.c) as conf:
        for line in conf:
            pat = line.strip().split('---')
            if len(pat) == 2:
                patterns.append(pat)
            else:
                logger.error('Line in config file is improperly written: %s', line)
    if not patterns:
        logger.critical('No patterns specified in config file. Exiting...')
        sys.exit(1)

    sites = [Pastebin(patterns), Pastie(patterns), Slexy(patterns)]
    logger.debug('Created sites')
    threads = []
    for site in sites:
        thread = StopThread(site)
        threads.append((thread, site.__class__.__name__))
        logger.debug('Created thread for %s', site.__class__.__name__)
    try:
        for thread, name in threads:
            thread.start()
            logger.debug('Started thread for %s', name)
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        for thread, name in threads:
            thread.stop()
            thread.join()
            logger.debug('Stopped thread for %s', name)


if __name__ == '__main__':
    main()
