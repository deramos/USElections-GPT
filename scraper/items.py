# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    publication_date = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    created_at = scrapy.Field()
