# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class InstagramUserItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = table = 'user_post'
    postid = Field()
    userid = Field()
    username = Field()
    liked = Field()
    caption = Field()
    comment = Field()
    image_list = Field()
    video_list = Field()