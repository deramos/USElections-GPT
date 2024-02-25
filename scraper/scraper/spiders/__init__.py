# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from cnn import CNNSpider


class SpidersEnum:
    CNNSpider = 'CNNSpider'


__all__ = ['CNNSpider', 'FoxNewsSpider', 'MSNBCSpider', 'ReutersSpider', 'SpidersEnum']