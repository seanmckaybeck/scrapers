'''
parses the free section of baltimore's
craigslist using scrapy. all data scraped
is saved to mongodb. this is not a
recursive scraper: it only gets the first page
and extracts the relevant sections
'''
import pymongo
from scrapy.spiders import Spider
from scrapy.item import Item, Field
from scrapy.exceptions import DropItem


class Entry(Item):
    title = Field()
    url = Field()
    submitted = Field()


class MongoPipeline(object):
    def __init__(self, server, port, db, collection):
        connection = pymongo.MongoClient(
                server, port
                )
        db = connection[db]
        self.collection = db[collection]

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('MONGODB_SERVER'),
                   settings.get('MONGODB_PORT'),
                   settings.get('MONGODB_DB'),
                   settings.get('MONGODB_COLLECTION'))

    def process_item(self, item, spider):
        self.collection.update({'url': item['url']}, dict(item), upsert=True)


class CraigslistSpider(Spider):
    name = 'craigslist'
    allowed_domains = ['craigslist.org']
    start_urls = ['http://baltimore.craigslist.org/search/zip']
    custom_settings = {
        'MONGODB_SERVER': 'localhost',
        'MONGODB_PORT': 27017,
        'MONGODB_DB': 'craigslist',
        'MONGODB_COLLECTION': 'free',
        'ITEM_PIPELINES': {'free_stuff_scrapy.MongoPipeline': 100}
    }

    def parse(self, response):
        for sel in response.xpath('//div[@class="content"]/p'):
            item = Entry()
            item['url'] = sel.xpath('a/@href').extract()[0]
            item['submitted'] = sel.xpath('span/span/time/@datetime').extract()[0]
            item['title'] = sel.xpath('span/span/a[@class="hdrlnk"]/text()').extract()[0]
            yield item
