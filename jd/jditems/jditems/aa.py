
from bs4 import BeautifulSoup
import requests
import re
import json
p_Name='汉美驰 电转大容量 台式 电烤箱 32L 31103-CN Item#:729006'
ProductID='11816773134'
price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
search_web = "https://search.jd.com/Search?keyword=" + str(p_Name) + "&enc=utf-8&wq=" + str(p_Name)
print("search页面：", search_web)
search_webs = requests.get(search_web, timeout=1000).text
soup = BeautifulSoup(search_webs, 'lxml')
skuid = "J_" + str(ProductID)

try:
    price_info = soup('strong', class_=skuid)
    PreferentialPrice = re.findall("<em>ï¿¥</em><i>(.*?)</i>", str(price_info[0]))[0]
    # 会有<strong class="J_10108922808" data-done="1" data-price="639.00"><em>ï¿¥</em><i></i></strong>出现
    # 如id=10108922808  p_Name=柏翠（petrus） 38L电烤箱家用多功能 精准控温 PE7338 升级版
    if len(PreferentialPrice) == 0:
        PreferentialPrice = re.findall('data-price=\"(.*?)\"', str(price_info[0]))[0]
    price = PreferentialPrice
except:
    try:
        price_webs = requests.get(price_web, timeout=1000).text
        price_json = json.loads(price_webs)[0]
        PreferentialPrice = price_json['p']
        price = price_json['m']
    except:
        price = None
        PreferentialPrice = None

print(price,PreferentialPrice)
# price=re.findall("<i>(.*?)</i>",price_info[0])
# print (price)

# import requests
# from  lxml.etree import HTML
# import json
# import re
#
# url="https://item.jd.com/435168.html"
# rrr=requests.get(url).text
# sel=HTML(rrr)
# p_Name = sel.xpath(".//div[@class='sku-name']/text()")[-1].strip('\"').strip('\n').strip().replace('\t', '')
# print(p_Name)




#pipelines.py
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jditems.settings import FIELDS_TO_EXPORT
from scrapy import signals
from scrapy.exporters import CsvItemExporter
import time

class JdtestPipeline(object):
    def process_item(self, item, spider):
        return item


class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    file = open('jd电烤箱_%s.csv' % (self.printfNow()), 'wb')
    # file = open('%s_pages_%s.csv' % (spider.name,self.printfNow()), 'a+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = FIELDS_TO_EXPORT
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item

  def printfNow(self):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
