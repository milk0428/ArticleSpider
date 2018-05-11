# -*- coding: utf-8 -*-
import MySQLdb
from scrapy.pipelines.images import ImagesPipeline

import codecs
import json

from scrapy.exporters import JsonItemExporter

from twisted.enterprise import adbapi
import MySQLdb.cursors

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#该处有两个类，为处理item数据的类，其中下边的ArticleImagePipeline为自定义，用于获取图片的本地路径。
#在setting.py文件中配置了这两个类，且配置了ArticleImagePipeline比ArticlespiderPipeline先执行。
class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

#该pipline使用codecs将item保存为json文件
# 需引入codecs及json
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file=codecs.open('article.json','w',encoding="utf-8")
    def process_item(self, item, spider):
        #注意json.dumps函数传递的item需转换成字典类型
        lines=json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(lines)
        return item

    def spider_closed(self,spider):
        self.file.closed()

#调用scrapy提供的json exporter导出json文件
class JsonExporterPipleline(object):
    def __init__(self):
        self.file=open("articleexport.json",'wb')
        self.exporter=JsonItemExporter(self.file,encoding="utf-8",ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        #注意json.dumps函数传递的item需转换成字典类型
        self.exporter.export_item(item)
        return item

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.closed()

#将item保存到mysql,该模块使用同步操作
class MysqlPipeline(object):
    def __init__(self):
        self.conn=MySQLdb.connect('127.0.0.1','root','123456','article_spider',charset='utf8',use_unicode=True)
        self.cursor=self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql="""
            insert into article(url_object_id,title,url,create_date,fav_nums)
            VALUE (%s,%s,%s,%s,%s)
        """
        #占位符数据传入对象是tuple，故使用括号把要传入的数据组合起来
        self.cursor.execute(insert_sql,(item["url_object_id"],item["title"],item["url"],item["create_date"],item["fav_nums"]))
        self.conn.commit()

# 将item保存到mysql,该模块使用异步操作，使用Twisted框架
class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    #读取settings.py中配置的数据库信息
    @classmethod
    def from_settings(cls,settings):
        #以字典方式传递数据库参数，注意该字典的参数名字要和MySQLdb.connect中的参数名字一致
        dbparms=dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool=adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    #使用twisted将mysql插入变成异步执行
    def process_item(self , item , spider):
        query=self.dbpool.runInteraction(self.do_insert,item)
        #处理异步存入数据库时候的错误
        query.addErrback(self.handle_error,item,spider)

    #执行具体的插入
    def do_insert(self,cursor,item):
        insert_sql = """
                    insert into article(url_object_id,title,url,create_date,fav_nums)
                    VALUE (%s,%s,%s,%s,%s)
                """
        # 占位符数据传入对象是tuple，故使用括号把要传入的数据组合起来
        cursor.execute ( insert_sql , (
        item["url_object_id"] , item["title"] , item["url"] , item["create_date"] , item["fav_nums"]) )
        #不用使用commit()函数，会自动提交

    #处理异步插入的异常。其中item和spider参数为自定义，可以删去，则调用的时候省略。
    def handle_error(self,failure,item,spider):
        print(failure)

#该类用于图像存储到本地文件夹（非数据库）
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for status,value in results:
                image_file_path=value["path"]
            item["front_image_path"]=image_file_path
        return item