# Board Game Geek

These are scrapers for the site [Board Game Geek](http://www.boardgamegeek.com).
Each serves a distinct purpose in data collection.

Because ID assignments are not intuitive (at least to me) for games, in order
to get game details you have to know the ID beforehand.
With clever scraping of BGG's board game section, you can get game IDs for all
board games on the site along with basic rating information.
If you so desire, you can then use the extracted IDs to get information on all
of the different games on the site.

Use `scrapy` to first run `spider.py` with `scrapy runspider spider.py -o items.csv`.
This CSV will contain game names, IDs, and ratings.
Next, run `python extract_ids.py` to put all of the IDs into a file called `ids.txt`.
This file is then used by the last script.
Run `python get_game_info.py` to retrieve all games whose IDs are in `ids.txt`.
This data will be written to a CSV called `games.csv` and is much more detailed
than the information contained in `items.csv`.
Note that there are 80000+ games, so each of these steps will take some time.
To be nice to the site, a request is made for 30 games at a time and is only made
once every 2 seconds.
In the forums the operator mentions 2 requests per second is fine, but just to be safe
I only do 1 every 2 seconds.
