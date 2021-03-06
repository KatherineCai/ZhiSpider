# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhispiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PaperItem(scrapy.Item):
    href = scrapy.Field()
    name = scrapy.Field()
    authors = scrapy.Field()
    institutions = scrapy.Field()
    refs = scrapy.Field()
    num_refs = scrapy.Field()

class Author(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()

class Ref(scrapy.Item):
    href = scrapy.Field()
    name = scrapy.Field()
