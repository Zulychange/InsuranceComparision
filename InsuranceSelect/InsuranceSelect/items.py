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
    # feature = scrapy.Field()
    company = scrapy.Field()
    url = scrapy.Field()
    # birthday = scrapy.Field()
    sex = scrapy.Field()
    # career = scrapy.Field()
    # Intime = scrapy.Field()
    # collection_date = scrapy.Field()

    # contri_method = scrapy.Field()
    # contribution_period = scrapy.Field()
    premium = scrapy.Field()

    sum_assured = scrapy.Field()
    # annuities = scrapy.Field()
    # death_benefit = scrapy.Field()

    pv = scrapy.Field()

    type = scrapy.Field()

