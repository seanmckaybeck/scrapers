# Practical Webscraping

This repository aims to be a collection of examples
for useful web scraping written in Python. All examples scripts are provided
as is and are free to use according to the terms laid out
in the LICENSE file.

Each subdirectory contains scrapers relevant to a single service.
As an example, a subdirectory called "reddit" would contain
scrapers for Reddit and nothing else.

In mose cases there will be two scrapers that accomplish the same
thing. The only difference between the two scrapers is the set of
libraries used in each. Most commonly scrapers will be written
using the library [Scrapy](http://scrapy.org). If a second scraper
exists it will be written using [requests](http://www.python-requests.org/en/latest/)
and [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/).
