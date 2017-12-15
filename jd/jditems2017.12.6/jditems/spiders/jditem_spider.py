import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jditems.items import JdItem
import time,random

class jdspider(scrapy.Spider):
    name="jd_dkx"                 #京东电烤箱
    allowed_domains=["jd.com"]
    start_urls=[
        "https://list.jd.com/list.html?cat=737,752,759"   #电烤箱
    ]

    def parse(self, response):
        # sel=scrapy.Selector(response)
        # # url="https://item.jd.hk/18739277759.html"    #京东全球购与普通网址不同，不同的地方为“https://item.jd.com/4251335.html”
        # goods_info=sel.xpath(".//div[@id='plist']/ul/li")
        # for goods in goods_info:
        #     ProductID_info=goods.xpath(".//div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()       #商品编号
        #     if len(ProductID_info)==0:
        #         ProductID_info=goods.xpath(".//div[@class='gl-i-tab-content']/div[@class='tab-content-item tab-cnt-i-selected j-sku-item']/@data-sku").extract()
        #         ProductID=ProductID_info[0]
        #     else:
        #         ProductID=ProductID_info[0]
        #     # print(ProductID)
        #     if len(ProductID)!=0:
        #         goods_web="https://item.jd.com/"+str(ProductID)+".html"         #商品链接   包含商品型号,店铺名称,类别,品牌,型号等
        #         item=JdItem(ProductID=ProductID)
        #         request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
        #         yield request
        #     else:
        #         print("parse中ProductID为空  没有读到")
        #测试用
        ProductID='18806424765'
        item = JdItem(ProductID=ProductID)
        # url="https://item.jd.hk/1971910764.html"
        url="https://item.jd.com/18806424765.html"
        request = scrapy.Request(url=url, callback=self.goods,meta={'item':item}, dont_filter=True)
        yield request

        # #翻页功能
        # next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        # if next_page:
        #     next="https://list.jd.com/"+next_page[0]
        #     yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        sel=scrapy.Selector(response)
        url=response.url
        body=response.body
        ProductID=item['ProductID']

        if "error" in url:        #302重定向页面,写回原页面处理
            url="https://item.jd.com/"+str(ProductID)+".html"
            item = JdItem(ProductID=ProductID)
            yield scrapy.Request(url,callback=self.goods,meta={'item':item})
            return None

        # --------------------全球购网页---------------------------------------------
        elif "hk" in url:
            print("全球购：", url)

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '').replace('\n', '')
            detail_1 = detail_info.extract()          #缩小范围，从商品介绍部分获取想要的内容

            #商品名称
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[-1].strip('\"').strip('\n').strip().replace('\t', '').replace('\n', '')
                print(p_Name)
            except:
                p_Name = None

            # detail_info=sel.xpath(".//div[@class='p-parameter']/text()").extract()

            #店铺名称
            try:
                shop_name = sel.xpath(".//div[@class='shopName']/strong/span/a/text()").extract()[0]  # 店铺名称
            except:
                try:
                    shop = sel.xpath(".//div[@class='p-parameter']/ul[@class='parameter2']/li[3]/@title").extract()[0]
                    if '店' in shop:
                        shop_name = shop
                    else:
                        shop_name=None
                except:
                    shop_name = None

            #京东规格与包装部分（将这部分的内容读为字典形式，x为字典）
            try:
                s = BeautifulSoup(body, 'lxml')
                guige = s.find('div', id_='specifications')
                x = {}
                guige2 = guige.find_all('td', class_='tdTitle')
                guige3 = guige.find_all('td', class_=None)
                for i in range(len(guige2)):
                    dt = re.findall(">(.*?)<", str(guige2[i]))
                    dd = re.findall(">(.*?)<", str(guige3[i]))
                    x.setdefault(dt[0], dd[0])
            except:
                x = None

            #商品品牌
            try:
                brand = x['品牌']
            except:
                brand = p_Name

            if brand!=p_Name:
                if ("（" and "）") in brand:
                    dd = re.findall("（.*?）", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if ("(" and ")") in brand:
                    dd = re.findall("\(.*?\)", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if brand == "TOSOT":
                    brand = "大松"
                if brand == "Panasonic":
                    brand = "松下"

            #商品名称（型号）
            try:
                try:
                    X_name = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                    if p_Name == None:
                        p_Name = X_name
                except:
                    try:
                        X_name = x['型号']
                        if p_Name == None:
                            p_Name = X_name
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                control = re.findall(">操控方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['操控方式']
                except:
                    control = None

            try:
                X_type = re.findall(">外观式样：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    X_type = x['外观式样']
                except:
                    X_type = None

            try:
                temp_con = re.findall(">温控方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    temp_con = x['温控形式']
                except:
                    temp_con = None

            try:
                people=re.findall(">适用人数：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    people = x['适用人数']
                except:
                    people = None

            try:
                open_type = re.findall(">开门方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    open_type = x['开门方式']
                except:
                    open_type = None

            try:
                function=re.findall(">特色功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    function = x['特性']
                except:
                    function = None

            try:
                capacity = x['容量']
            except:
                try:
                    capacity = re.findall(">最大容量：(.*?)<", detail_1[0])[0].strip()
                except:
                    capacity = None

            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['外观颜色']
                except:
                    color = None

            price_web="https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_"+str(ProductID)
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # ---------------------普通网页-----------------------------------
        else:

            #商品名称（1.从名称处读；2.从表头的名称处读）
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[0].strip('\"').strip('\n').strip().replace('\t', '').replace('\n', '') # 商品名称
                if len(p_Name) == 0:     # 如发生商品名称读取结果为空的情况
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '').replace('\n', '')
            except:
                try:
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '').replace('\n', '')
                except:
                    p_Name = None

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '').replace('\n', '')
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

            #店铺名称
            try:
                try:
                    shop_name = sel.xpath(".//div[@class='name']/a/text()").extract()[0]  # 店铺名称
                except:
                    shop_name=re.findall(">店铺：(.*?)<", detail_1[0])[0].strip()
            except:
                shop_name = "京东自营"

            #不是品牌：**的形式，不用find
            try:
                brand = detail_info.xpath(".//ul[@id='parameter-brand']/li/a/text()").extract()[0].strip()  # 商品品牌
            except:
                try:
                    brand = x['品牌']
                except:
                    brand = None

            if brand:
                if ("（" and "）") in brand:
                    dd = re.findall("（.*?）", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if ("(" and ")") in brand:
                    dd = re.findall("\(.*?\)", brand)[0]
                    brand = brand.replace(dd, '').replace(' ', '')
                if brand == "TOSOT":
                    brand = "大松"
                if brand == "Panasonic":
                    brand = "松下"
                if brand == "GUOER":
                    brand = "果儿"
                if brand == "TATUNG":
                    brand = "大同"

            #商品名称（型号）
            try:
                try:
                    X_name = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                except:
                    try:
                        X_name = x['型号']
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '').replace('\n', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                control = re.findall(">操控方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['操控方式']
                except:
                    control = None

            try:
                X_type = re.findall(">外观式样：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    X_type = x['外观式样']
                except:
                    X_type = None

            try:
                temp_con = re.findall(">温控方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    temp_con = x['温控形式']
                except:
                    temp_con = None

            try:
                people=re.findall(">适用人数：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    people = x['适用人数']
                except:
                    people = None

            try:
                open_type=re.findall(">开门方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    open_type = x['开门方式']
                except:
                    open_type = None

            try:
                function=re.findall(">特色功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    function = x['特性']
                except:
                    function = None

            try:
                capacity = x['容量']
            except:
                try:
                    capacity = re.findall(">最大容量：(.*?)<", detail_1[0])[0].strip()
                except:
                    capacity = None

            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['外观颜色']
                except:
                    color = None

            price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
            # price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
            # price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(ProductID)+"&pdbp=0&pdtk=vJSo%2BcN%2B1Ot1ULpZg6kb4jfma6jcULJ1G2ulutvvlxgL3fj5JLFWweQbLYhUVX2E&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1510210566056"


        # 商品评价   json格式

        # comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # comment_web="https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds="+str(ProductID)

        comment_webs = requests.get(comment_web,timeout=1000).text
        urls = json.loads(comment_webs)
        try:
            comment = urls['hotCommentTagStatistics']
            keyword_list = []
            for i in range(len(comment)):
                keyword_list.append(comment[i]['name'])
            if len(keyword_list)==0:
                keyword=None
            else:
                keyword = ' '.join(keyword_list)                 #关键词
        except:
            keyword=None

        rate = urls['productCommentSummary']
        try:
            CommentCount = rate['commentCount']  # 评论总数
        except:
            CommentCount=None
            print("评价总数",CommentCount)
        try:
            GoodRateShow = rate['goodRateShow']  # 好评率
        except:
            GoodRateShow=None
        try:
            GoodCount = rate['goodCount']  # 好评数
        except:
            GoodCount=None
        try:
            GeneralCount = rate['generalCount']  # 中评数
        except:
            GeneralCount =None
        try:
            PoorCount = rate['poorCount']  # 差评数
        except:
            PoorCount=None

        search_web = "https://search.jd.com/Search?keyword=" + str(p_Name) + "&enc=utf-8&wq=" + str(p_Name)
        # print ("search页面：",search_web)
        search_webs = requests.get(search_web, timeout=1000).text
        soup = BeautifulSoup(search_webs, 'lxml')
        skuid = "J_" + str(ProductID)
        try:
            price_info = soup('strong', class_=skuid)
            PreferentialPrice = re.findall("<em>ï¿¥</em><i>(.*?)</i>", str(price_info[0]))[0]
            # 会有<strong class="J_10108922808" data-done="1" data-price="639.00"><em>ï¿¥</em><i></i></strong>出现
            #如id=10108922808  p_Name=柏翠（petrus） 38L电烤箱家用多功能 精准控温 PE7338 升级版
            if len(PreferentialPrice) == 0:
                PreferentialPrice = re.findall('data-price=\"(.*?)\"', str(price_info[0]))[0]
            price = PreferentialPrice
        except:
            try:
                print("价格：",price_web)
                price_webs = requests.get(price_web, timeout=1000).text
                price_json = json.loads(price_webs)[0]
                PreferentialPrice = price_json['p']
                price = price_json['m']
            except:
                price=None
                PreferentialPrice=None
        print(price,PreferentialPrice)

        item = JdItem()
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
        item['control']=control
        item['temp_con']=temp_con
        item['capacity']=capacity
        item['people']=people
        item['function']=function
        item['open_type']=open_type
        item['size']=None
        item['color'] = color
        item['product_url']=url
        item['source']="京东"
        yield item


