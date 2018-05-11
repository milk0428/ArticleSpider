# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader.processors import MapCompose


#自动生成的模板item类
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# #自己新建的item类，名字自定
# class JobboleArticleItem(scrapy.Item):
#     url=scrapy.Field()
#     #该项为url的md5编码
#     url_object_id=scrapy.Field()
#     front_image_url=scrapy.Field()
#     #存放封面图的本地路径，该数据从pipelines.py文件中通过重写item_completed（）函数填充
#     front_image_path=scrapy.Field()
#     title=scrapy.Field()
#     create_date=scrapy.Field()
#     praise_nums=scrapy.Field()
#     fav_nums=scrapy.Field()
#     comment_nums=scrapy.Field()
#     content=scrapy.Field()


def add_jobbole(value):
    return value+"-weimin"


#自己新建的item类，名字自定（该item使用loader填充）
class JobboleArticleItem(scrapy.Item):
    url=scrapy.Field()
    #该项为url的md5编码
    url_object_id=scrapy.Field()
    front_image_url=scrapy.Field()
    #存放封面图的本地路径，该数据从pipelines.py文件中通过重写item_completed（）函数填充
    front_image_path=scrapy.Field()
    title=scrapy.Field(
        input_processor=MapCompose (lambda x:x+"-weimin",lambda x:x+"-kao")
    )
    create_date=scrapy.Field()
    praise_nums=scrapy.Field()
    fav_nums=scrapy.Field()
    comment_nums=scrapy.Field()
    content=scrapy.Field()
