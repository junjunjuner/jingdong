import scrapy
import requests
import json
from jdprice.items import JdpriceItem
import time,random
import re

class jdspider(scrapy.Spider):
    name="jdprice"
    allowed_domains=["jd.com"]
    num=1
    start_urls=[
        "https://list.jd.com/list.html?cat=737,752,753"   #电饭煲
        # "https://list.jd.com/list.html?cat=737,752,753&page=3&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main"
    ]

    def parse(self, response):
        sel=scrapy.Selector(response)
        productid_list=[]
        # url="https://item.jd.hk/18739277759.html"    #京东全球购与普通网址不同，不同的地方为“https://item.jd.com/4251335.html”
        goods_info=sel.xpath(".//div[@id='plist']/ul/li")
        for goods in goods_info:
            ProductID=goods.xpath(".//div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()[0]       #商品编号
            productid_list.append(ProductID)
            goods_web="https://item.jd.com/"+str(ProductID)+".html"         #商品链接   包含商品型号,店铺名称,类别,品牌,型号等
        productid_str='%2CJ_'.join(productid_list)
        price_url="https://p.3.cn/prices/mgets?callback=jQuery4471802&ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(productid_str)+\
            "&pdbp=0&pdtk=IkjukMAf4OSksZJdVdwoWzNqUKWsuk4e%2BusjgPTBC2lrnf%2Bu6kLlRyEV42%2BI5bho&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1511838488195"
        item=JdpriceItem(ProductID=ProductID)
        request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
        # yield request
        # #测试用
        # ProductID='1971910764'
        # item = JdtestItem(ProductID=ProductID)
        # url="https://item.jd.hk/1971910764.html"
        # request = scrapy.Request(url=url, callback=self.goods,meta={'item':item}, dont_filter=True)
        # yield request

        #翻页功能
        next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        if next_page:
            next="https://list.jd.com/"+next_page[0]
            # yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        ProductID=item['ProductID']
        url=response.url
        if 'hk' in url:     #京东全球购
            price_web = "https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_" + str(ProductID)
        else:          #普通页面
            price_web="https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
        price_web = "https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_" + str(ProductID) + \
                    "&pdbp=0&pdtk=vJSo%2BcN%2B1Ot1ULpZg6kb4jfma6jcULJ1G2ulutvvlxgL3fj5JLFWweQbLYhUVX2E&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1510210566056"

        try:
            price_webs = requests.get(price_web,timeout=1000).text
            price_json = json.loads(price_webs)[0]
            try:
                PreferentialPrice = price_json['p']
            except:
                PreferentialPrice=None
            try:
                price = price_json['m']
            except:
                price=PreferentialPrice            #商品价格
        except:
            time.sleep(random.randint(400,600))
            try:
                price_webs = requests.get(price_web,timeout=1000).text
                price_json = json.loads(price_webs)[0]
                try:
                    PreferentialPrice = price_json['p']
                except:
                    PreferentialPrice=None
                try:
                    price = price_json['m']
                except:
                    price=PreferentialPrice
            except:
                time.sleep(random.randint(1500,1800))
                try:
                    price_webs = requests.get(price_web, timeout=3000).text
                    price_json = json.loads(price_webs)[0]
                    try:
                        PreferentialPrice = price_json['p']
                    except:
                        PreferentialPrice = None
                    try:
                        price = price_json['m']
                    except:
                        price = PreferentialPrice
                except:
                    price=None
                    PreferentialPrice=None
                    print("连接失败：",price_web)
                    self.num=self.num+1
        if self.num>5:
            print("多次连接失败，退出")
            exit()
        item['ProductID']=ProductID
        item['price']=price
        item['PreferentialPrice']=PreferentialPrice
        yield item
