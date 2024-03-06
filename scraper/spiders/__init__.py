# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import enum
from .cnn import CNNSpider


class SpidersEnum(enum.Enum):
    FoxNewsSpider = 'foxnews'
    CNNSpider = 'cnn'

    @classmethod
    def get_class_name(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        raise ValueError(f"Invalid enum value: {value}")


__all__ = ['CNNSpider', 'SpidersEnum']