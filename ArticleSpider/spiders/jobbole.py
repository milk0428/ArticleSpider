# -*- coding: utf-8 -*-
import datetime
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobboleArticleItem
from ArticleSpider.utils import common

from scrapy.loader import ItemLoader

class JobboleSpider ( scrapy.Spider ):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self , response):
        """
        1、获取文章列表页中的文章url并交给scrapy下载后进行解析
        2、获取到下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        """

        #获取文章列表页中的文章url并交给scrapy下载后进行解析
        post_nodes=response.css("#archive .floated-thumb .post-thumb a")
        #从获取到的url列表中每个取url进行爬取，其中yield是scrapy运行的命令，parse.urljoin是对url进行连接的函数，回调函数是解析。
        for post_node in post_nodes:
            #获取封面图片地址
            image_url=post_node.css("img::attr(src)").extract_first("")
            post_url=post_node.css("::attr(href)").extract_first("")
            #parse.urljoin()函数将根域名与后边的域名拼接起来，如果后边的域名自带根域名，则不会拼接。
            #这里通过meta（字典）参数把封面图的url传递到response中，以便下边parse_detail()函数中读取。
            yield Request(url=parse.urljoin(response.url,post_url), meta={"front_image_url":parse.urljoin(response.url,image_url)},callback=self.parse_detail)

        ##archive > div.navigation.margin-20 > a.next.page-numbers
        next_url=response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)





    def parse_detail(self,response):
        #实例化item
        jobbole_item=JobboleArticleItem()

        #获取封面图的url地址（使用get函数以防止空指针异常）
        image_url=response.meta.get("front_image_url","")
        # ----------------使用xpath获取数据--------------------
        # 获取标题（注意extract()[0]与extract_first()的区别）
        title = response.xpath ( '//div[@class="entry-header"]/h1/text()' ).extract_first()
        # 获取创建时间
        create_date = response.xpath ( '//p[@class="entry-meta-hide-on-mobile"]/text()' ).extract ()[0].strip ().replace (
            ' ·' , '' )
        # 获取点赞数
        praise_nums = int ( response.xpath ( '//span[contains(@class,"vote-post-up")]/h10/text()' ).extract ()[0] )

        # 获取收藏数，注意收藏数为0的情况，故要加入判断（注意正则表达式中的贪婪与非贪婪模式）
        # fav_nums=int(re.match(".*(\d+).*",response.xpath('//*[@id="post-112535"]/div[3]/div[14]/span[2]/text()').extract()[0]).group(1))
        fav_nums = response.xpath ( '//span[contains(@class,"bookmark-btn")]/text()' ).extract ()[0]
        match_re = re.match ( ".*?(\d+).*" , fav_nums )
        if match_re:
            fav_nums = int ( match_re.group ( 1 ) )
        else:
            fav_nums = 0

        # 获取评论数，注意评论数为0的情况，故要加入判断
        # comment_nums=int(re.match(".*(\d+).*",response.xpath('//*[@id="post-112535"]/div[3]/div[14]/a/span/text()').extract()[0]).group(1))
        comment_nums = response.xpath ( '//a[@href="#article-comment"]/span/text()').extract ()[0]
        match_re = re.match ( ".*?(\d+).*" , comment_nums )
        if match_re:
            comment_nums = match_re.group ( 1 )
        else:
            comment_nums = 0
        content = response.xpath ( '//div[@class="entry"]' ).extract ()[0]

        # -------------使用css选择器获取数据-----------------
        # response.css(".#post-112569 > div.entry-header > h1::text")

        #通过字典方式填充item，key与item类的定义的属性名字对应
        #注意因为我们需要用scrapy的自动下载图片功能下载图片到本地，该下载类智能接受数组类型的地址，故image_url需转换成数组类型。
        jobbole_item["url"]=response.url
        jobbole_item["url_object_id"] = common.get_md5 ( response.url )
        jobbole_item["front_image_url"]=[image_url]
        #格式化日期格式
        try:
            create_date=datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date=datetime.datetime.now().date()
        jobbole_item["create_date"] = create_date
        jobbole_item["title"] =title
        jobbole_item["praise_nums"] =praise_nums
        jobbole_item["fav_nums"] =fav_nums
        jobbole_item["comment_nums"] =comment_nums
        jobbole_item["content"] =content

        #通过item loader加载item--------------------------------------------
        #初始化ItemLoader对象，注意传入实例化的item对象及response对象
        item_loader=ItemLoader(item=JobboleArticleItem(),response=response)
        #ItemLoader有三种方法：add_css(),add_xpath(),add_value()；css和xpath类似response对象中的css和xpath方法。
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",common.get_md5(response.url))
        item_loader.add_value("front_image_url",[image_url])
        item_loader.add_value("create_date",create_date)
        item_loader.add_xpath("title",'//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath("praise_nums",'//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("fav_nums",'//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath("comment_nums", '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath("content", '//div[@class="entry"]')

        #当使用ItemLoader解析完数据后，需调用load_item()函数，才能生成item文件
        article_item=item_loader.load_item()

        #通过yield命令将jobbole_item提交到piplines.py
        yield jobbole_item
