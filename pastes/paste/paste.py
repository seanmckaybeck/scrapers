"""
Contains a base Site class for pastebin-like sites.
Each child class only needs to specify a base url,
the relative url to the public pastes archive,
and a lambda function to get the paste links out of
the page.
"""
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


LOGGER = logging.getLogger(__name__)


class Site(object):
    """
    Base class for all paste sites to inherit from.
    """
    def __init__(self, url_base, url_archive, paste_tag, target_patterns, paste):
        self.url_base = url_base
        self.url_archive = url_archive
        self.paste_tag = paste_tag
        self.target_patterns = target_patterns
        self.headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
                        '(KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'}
        self.paste = paste

    def get(self):
        """
        Gets the archive page for the paste site.

        Returns list of links to pastes.
        """
        req = requests.get(self.url_base+self.url_archive, headers=self.headers)
        LOGGER.debug('Got the response for the archive page')
        while req.status_code != 200:
            LOGGER.error('Response was not 200. Trying again...')
            req = requests.get(self.url_base+self.url_archive)
        soup = BeautifulSoup(req.text, 'lxml')
        links = soup.find_all(self.paste_tag)
        LOGGER.debug('Got %d links from page', len(links))
        return [self.paste(urljoin(self.url_base, link.a.get('href'))) for link in links]

    def get_paste(self, paste):
        """
        Gets the supplied paste url.

        Returns list of tuples of matches in paste.
        """
        req = requests.get(paste.url, headers=self.headers)
        LOGGER.debug('Got response for paste')
        while req.status_code != 200:
            LOGGER.error('Response was not 200. Trying again...')
            req = requests.get(paste.url)
        found = []
        for name, pattern in self.target_patterns:
            LOGGER.debug('Trying pattern: %s', pattern)
            matches = re.findall(pattern, req.text)
            LOGGER.debug('Got %d matches', len(matches))
            if matches:
                found.append((name, len(matches)))
        return found


class Paste(object):
    """
    Base class for pastes. Parses paste ID
    from supplied URL
    """
    def __init__(self, url):
        _id = url.split('/')[-1]
        self._id = _id


class PastebinPaste(Paste):
    """
    Paste for Pastebin
    """
    def __init__(self, url):
        super().__init__(url)
        self.url = 'http://pastebin.com/raw.php?i={}'.format(self._id)


class PastiePaste(Paste):
    """
    Paste for Pastie
    """
    def __init__(self, url):
        super().__init__(url)
        self.url = 'http://pastie.org/pastes/{}/text'.format(self._id)


class SlexyPaste(Paste):
    """
    Paste for Slexy
    """
    def __init__(self, url):
        super().__init__(url)
        self.url = 'http://slexy.org/raw/{}'.format(self._id)


class Pastebin(Site):
    """
    Pastebin class
    """
    def __init__(self, target_patterns):
        self.url_base = 'http://pastebin.com/'
        self.url_archive = '/archive'
        self.paste_tag = lambda tag: tag.name == 'td' and tag.a and \
                         '/archive/' not in tag.a['href'] and tag.a['href'][1:]
        super().__init__(self.url_base, self.url_archive, self.paste_tag, target_patterns,
                         PastebinPaste)


class Pastie(Site):
    """
    Pastie class
    """
    def __init__(self, target_patterns):
        self.url_base = 'http://pastie.org'
        self.url_archive = '/pastes'
        self.paste_tag = lambda tag: tag.name == 'p' and tag.a and self.url_base in tag.a['href']
        super().__init__(self.url_base, self.url_archive, self.paste_tag, target_patterns,
                         PastiePaste)


class Slexy(Site):
    """
    Slexy site
    """
    def __init__(self, target_patterns):
        self.url_base = 'http://slexy.org'
        self.url_archive = '/recent'
        self.paste_tag = lambda tag: tag.name == 'td' and tag.a and '/view/' in tag.a['href']
        super().__init__(self.url_base, self.url_archive, self.paste_tag, target_patterns,
                         SlexyPaste)
