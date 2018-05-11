from scrapy.cmdline import execute
import sys
import os

#要先添加当前项目的主目录路径，才能执行scrapy的execute命令
#其中os.path.abspath(__file__)为找出当前源文件路径
#os.path.dirname()函数为当前文件所在的目录
#jobbole为爬虫的名字，不是项目名字

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","jobbole"])
