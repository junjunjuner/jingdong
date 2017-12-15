import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jdtest.items import JdtestItem
import time

class jdspider(scrapy.Spider):
    name="jdtest"
    allowed_domains=["jd.com"]
    start_urls=[
        "https://list.jd.com/list.html?cat=737,794,870&ev=1554_584893&JL=3_%E7%A9%BA%E8%B0%83%E7%B1%BB%E5%88%AB_%E5%A3%81%E6%8C%82%E5%BC%8F%E7%A9%BA%E8%B0%83#J_crumbsBar"   #壁挂式空调
    ]

    def parse(self, response):
        sel=scrapy.Selector(response)
        productid_list=sel.xpath(".//div[@id='plist']/ul/li/div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()
        print(productid_list)
        print(len(productid_list))
        productid_str='%2CJ_'.join(productid_list)
        # time.sleep(random.randint(60,120))
        price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(productid_str)
        price_webs = requests.get(price_web, timeout=1000).text
        price_jsons = json.loads(price_webs)
        for price_json in price_jsons:
            try:
                id = price_json['id']
                ProductID = id[2:]
                PreferentialPrice = price_json['p']
                price = price_json['m']
            except:
                ProductID=None
                PreferentialPrice = None
                price = None  # 商品价格
            if ProductID:
                item=JdtestItem()
                item['ProductID']=ProductID
                item['PreferentialPrice'] = PreferentialPrice
                item['price'] = price
                goods_web = "https://item.jd.com/" + str(ProductID) + ".html"
                request = scrapy.Request(url=goods_web, callback=self.goods, meta={'item': item}, dont_filter=True)
                yield request
            else:
                print("ProductID未获取到")
                self.num=self.num+1
            if (self.num)>60:
                print("ProductID多次未获取到")
                exit()
        #翻页功能
        next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        if next_page:
            next="https://list.jd.com/"+next_page[0]
            yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        sel=scrapy.Selector(response)
        body=response.body
        ProductID=item['ProductID']
        price = item['price']
        PreferentialPrice = item['PreferentialPrice']
        url=response.url
        if len(ProductID)!=0:
            try:
                shop_name=sel.xpath(".//div[@class='name']/a/text()").extract()[0]       #店铺名称
            except:
                shop_name="京东自营"

            try:
                p_Name=sel.xpath(".//div[@class='sku-name']/text()").extract()[0].strip('\"').strip('\n').strip().replace('\t','')    #商品名称
                if len(p_Name)==0:
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t','')
            except:
                try:
                    p_Name=sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t','')
                except:
                    p_Name=None

            # 京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '').replace('\n','')
            detail_1 = detail_info.extract()

            #京东规格与包装部分（读取为字典格式）
            try:
                s = BeautifulSoup(body, 'lxml')
                # print(s)
                guige = s.find('div', class_='Ptable')
                # print (guige)
                guige1 = guige.find_all('div', class_='Ptable-item')
                # print (guige1)
                x = {}
                for gg in guige1:
                    guige2 = gg.find_all('dt', class_=None)
                    guige3 = gg.find_all('dd', class_=None)
                    for i in range(len(guige2)):
                        dt = re.findall(">(.*?)<", str(guige2[i]))
                        dd = re.findall(">(.*?)<", str(guige3[i]))
                        x.setdefault(dt[0], dd[0])
            except:
                x = None
            print(x)

            try:
                try:
                    brand=detail_info.xpath(".//ul[@id='parameter-brand']/li/a/text()").extract()[0].strip()    #商品品牌(在商品详情部分)
                except:
                    try:
                        brand=sel.xpath(".//div[@class='inner border']/div[@class='head']/a/text()").extract()[0].strip()   #在表头部分
                    except:
                        brand=x["品牌"]
            except:
                brand=None

            if brand:
                if ("（" and "）") in brand:
                    dd = re.findall("（.*?）", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if ("(" and ")") in brand:
                    dd = re.findall("\(.*?\)", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')

            if brand=="Panasonic":
                brand="松下"
            if brand=="CHEBLO":
                brand="樱花"
            if brand=="MBO":
                brand="美博"
            if brand=="YAIR":
                brand="扬子"
            if brand=="PHLGCO":
                brand="飞歌"
            if brand=="FZM":
                brand="方米"
            if brand=="inyan":
                brand="迎燕"
            if brand=="JENSANY":
                brand="金三洋"

            try:
                X_name=re.findall(">商品名称：(.*?)<",detail_1[0])[0].strip().replace('\t','').replace('\n','')     #商品名称
                if len(X_name)==0:
                    X_name=p_Name
                if p_Name==None:
                    p_Name=X_name
            except:
                X_name=p_Name
            try:
                X_type = re.findall('>变频/定频：(.*?)<', detail_1[0])[0].strip()  # 类别（定变频）
            except:
                try:
                    X_type=x["定频/变频"]
                except:
                    X_type=None

            try:
                capacity = re.findall('>商品匹数：(.*?)<', detail_1[0])[0].strip()  # 商品容量（匹数）
            except:
                try:
                    capacity=x["匹数"]
                except:
                    capacity=None

            # 商品评价链接   json格式
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
            # comment_web="https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds="+str(ProductID)
            comment_webs = requests.get(comment_web, timeout=1000).text
            urls = json.loads(comment_webs)
            try:
                comment = urls['hotCommentTagStatistics']
                keyword_list = []
                for i in range(len(comment)):
                    keyword_list.append(comment[i]['name'])
                if len(keyword_list) == 0:
                    keyword = None
                else:
                    keyword = ' '.join(keyword_list)  # 关键词
            except:
                keyword = None

            rate = urls['productCommentSummary']
            try:
                CommentCount = rate['commentCount']  # 评论总数
            except:
                CommentCount = None
                print("评价总数", CommentCount)
            try:
                GoodRateShow = rate['goodRateShow']  # 好评率
            except:
                GoodRateShow = None
            try:
                GoodCount = rate['goodCount']  # 好评数
            except:
                GoodCount = None
            try:
                GeneralCount = rate['generalCount']  # 中评数
            except:
                GeneralCount = None
            try:
                PoorCount = rate['poorCount']  # 差评数
            except:
                PoorCount = None


            if PreferentialPrice==None:
                item = JdtestItem()
                item['ProductID']=ProductID
                item['p_Name']=p_Name
                item['shop_name']=shop_name
                item['price']=price
                item['PreferentialPrice']=PreferentialPrice
                item['CommentCount']=CommentCount
                item['GoodRateShow']=GoodRateShow
                item['GoodCount']=GoodCount
                item['GeneralCount']=GeneralCount
                item['PoorCount']=PoorCount
                item['keyword']=keyword
                item['type']=product_detail
                item['brand']=brand
                item['X_type']=X_type
                item['X_name']=X_name
                item['capacity']=capacity
                item['source']="京东"
                yield item

            elif float(PreferentialPrice)>300.00:
                item = JdtestItem()
                item['ProductID']=ProductID
                item['p_Name']=p_Name
                item['shop_name']=shop_name
                item['price']=price
                item['PreferentialPrice']=PreferentialPrice
                item['CommentCount']=CommentCount
                item['GoodRateShow']=GoodRateShow
                item['GoodCount']=GoodCount
                item['GeneralCount']=GeneralCount
                item['PoorCount']=PoorCount
                item['keyword']=keyword
                item['type']=product_detail
                item['brand']=brand
                item['X_type']=X_type
                item['X_name']=X_name
                item['capacity']=capacity
                item['source']="京东"
                yield item
            else:
                print("广告及无效页面:","https://item.jd.com/"+str(ProductID)+".html")
        else:
            print ("goods中ProductID未找到  没有传进去")

