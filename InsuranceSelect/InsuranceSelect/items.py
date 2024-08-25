# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InsuranceselectItem(scrapy.Item):

    """
    所有保险产品的共同基类
    """
    name = scrapy.Field()
    company = scrapy.Field()
    url = scrapy.Field()
    sex = scrapy.Field()
    premium = scrapy.Field()
    sum_assured = scrapy.Field()
    pv = scrapy.Field()
    type = scrapy.Field()

