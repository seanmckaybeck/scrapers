import re

from bs4 import BeautifulSoup

from scrapy.spiders import CrawlSpider
from scrapy.item import Item, Field


class Game(Item):
    id = Field()
    title = Field()
    geek_rate = Field()
    avg_rate = Field()
    num_votes = Field()

class GameSpider(CrawlSpider):
    name = 'boardgamegeek_spider'
    allowed_domains = ['boardgamegeek.com']
    start_urls = ['http://www.boardgamegeek.com/browse/boardgame']
    custom_settings = {'DOWNLOAD_DELAY': 1, 'BOT_NAME': 'Mr. Scraper Bot'}

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        next_page = soup.select('a[title^="next"]')
        if next_page:
            next_page = next_page[0].get('href')
        if next_page:
            yield self.make_requests_from_url(response.urljoin(next_page))
        rows = soup.select('tr#row_')
        for row in rows:
            g = Game()
            a = row.find_all('a', href=re.compile('^/boardgame'))
            for r in a:
                if r.text:
                    g['id'] = r.get('href').split('/')[2]
                    g['title'] = r.text
            geek_rate, avg_rate, num_votes = row.select('td.collection_bggrating')
            g['geek_rate'] = geek_rate.text.strip()
            g['avg_rate'] = avg_rate.text.strip()
            g['num_votes'] = num_votes.text.strip()
            yield g
