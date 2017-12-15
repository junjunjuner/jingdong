import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jd.items import JdItem
import time,random

class jdspider(scrapy.Spider):
    name="jd_dfb"                 #京东电饭煲
    allowed_domains=["jd.com"]
    num=0
    page=1
    start_urls=[
        "https://list.jd.com/list.html?cat=737,752,753"   #电饭煲
        # "https://list.jd.com/list.html?cat=737,752,759"   #电烤箱
    ]
    ProgramStarttime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def parse(self, response):
        sel=scrapy.Selector(response)
        # url="https://item.jd.hk/18739277759.html"    #京东全球购与普通网址不同，不同的地方为“https://item.jd.com/4251335.html”

        '''''''''
        方法二
        '''''''''
        productid_list=sel.xpath(".//div[@id='plist']/ul/li/div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()
        print(productid_list)
        print(len(productid_list))
        productid_str='%2CJ_'.join(productid_list)
        # time.sleep(random.randint(60,120))
        price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(productid_str)
        print(price_web)
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
                item=JdItem()
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
        '''''
        方法一
        '''''
        # goods_info = sel.xpath(".//div[@id='plist']/ul/li")
        # for goods in goods_info:
        #     ProductID=goods.xpath(".//div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()[0]       #商品编号
        #     if len(ProductID)!=0:
        #         goods_web="https://item.jd.com/"+str(ProductID)+".html"         #商品链接   包含商品型号,店铺名称,类别,品牌,型号等
        #         item=JdItem(ProductID=ProductID)
        #         request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
        #         # yield request
        #     else:
        #         print("parse中ProductID为空  没有读到")

        # #测试用
        # ProductID='1552845'
        # item = JdtestItem(ProductID=ProductID)
        # # url="https://item.jd.hk/1971910764.html"
        # url="https://item.jd.com/1552845.html"
        # request = scrapy.Request(url=url, callback=self.goods,meta={'item':item}, dont_filter=True)
        # yield request

        #翻页功能
        time.sleep(random.randint(60, 120))
        next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        if next_page:
            next="https://list.jd.com/"+next_page[0]
            yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        sel=scrapy.Selector(response)
        url=response.url
        body=response.body
        ProductID=item['ProductID']
        PreferentialPrice = item['PreferentialPrice']
        price = item['price']

        if "error" in url:        #302重定向页面,写回原页面处理
            url="https://item.jd.com/"+str(ProductID)+".html"
            item = JdItem()
            item['ProductID'] = ProductID
            item['PreferentialPrice'] = PreferentialPrice
            item['price'] = price
            yield scrapy.Request(url,callback=self.goods,meta={'item':item})
            return None

        # --------------------全球购网页---------------------------------------------
        elif "hk" in url:
            print("全球购：", url)

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '')
            detail_1 = detail_info.extract()          #缩小范围，从商品介绍部分获取想要的内容

            #商品名称
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[-1].strip('\"').strip('\n').strip().replace('\t', '')
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
                if brand == "GUOER":
                    brand = "果儿"
                if brand == "TATUNG":
                    brand = "大同"

            #商品名称（品牌+型号）
            try:
                try:
                    huohao = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                    X_name = brand + huohao
                except:
                    try:
                        huohao = x['型号']
                        X_name = brand + huohao
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                fire = re.findall(">加热方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    fire = x['加热方式']
                except:
                    fire = ''

            try:
                control = re.findall(">操作方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['操作方式']
                except:
                    control = ''

            try:
                yuyue = re.findall(">预约功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    yuyue = x['预约功能']
                    if yuyue=="支持":
                        yuyue="预约"
                    else:
                        yuyue="不可预约"
                except:
                    yuyue = ''

            total=fire+' '+control+' '+yuyue

            try:
                X_type=re.findall(">功能：(.*?)<", detail_1[0])[0].strip()
            except:
                if len(total.strip())>0:
                    X_type=total.strip()
                else:
                    X_type=None

            try:
                capacity = re.findall(">容量：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    capacity = x['容量']
                except:
                    capacity = None

            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['颜色']
                except:
                    color = None

            # price_web="https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_"+str(ProductID)
            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # ---------------------普通网页-----------------------------------
        else:

            #商品名称（1.从名称处读；2.从表头的名称处读）
            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[0].strip('\"').strip('\n').strip().replace('\t', '')  # 商品名称
                if len(p_Name) == 0:     # 如发生商品名称读取结果为空的情况
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '')
            except:
                try:
                    p_Name = sel.xpath(".//div[@class='item ellipsis']/@title").extract()[0].replace('\t', '')
                except:
                    p_Name = None

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '')
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

            #不是(品牌：**)的形式，不用find
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

            #商品名称（品牌+货号）
            try:
                try:
                    huohao = re.findall(">货号：(.*?)<", detail_1[0])[0].strip()
                    X_name = brand + huohao
                except:
                    try:
                        huohao = x['型号']
                        X_name = brand + huohao
                    except:
                        X_name = re.findall(">商品名称：(.*?)<", detail_1[0])[0].strip().replace('\t', '')  # 商品名称
                        if len(X_name) == 0:
                            X_name = p_Name
                        if p_Name == None:
                            p_Name = X_name
            except:
                X_name = p_Name

            try:
                fire = re.findall(">加热方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    fire = x['加热方式']
                except:
                    fire = ''

            try:
                control = re.findall(">操作方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['操作方式']
                except:
                    control = ''

            try:
                yuyue = re.findall(">预约功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    yuyue = x['预约功能']
                    if yuyue=="支持":
                        yuyue="预约"
                    else:
                        yuyue="不可预约"
                except:
                    yuyue = ''

            total=fire+' '+control+' '+yuyue

            #功能（加热方式+操作方式+预约功能）
            try:
                X_type=re.findall(">功能：(.*?)<", detail_1[0])[0].strip()
            except:
                if len(total.strip())>0:
                    X_type=total.strip()
                else:
                    X_type=None

            #容量
            try:
                capacity = re.findall(">容量：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    capacity = x['容量']
                except:
                    capacity = None

            #颜色
            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['颜色']
                except:
                    color = None

            # price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
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


        # #商品价格（京东对价格会封）
        # try:
        #     price_webs = requests.get(price_web,timeout=1000).text
        #     price_json = json.loads(price_webs)[0]
        #     try:
        #         PreferentialPrice = price_json['p']
        #     except:
        #         PreferentialPrice=None
        #     try:
        #         price = price_json['m']
        #     except:
        #         price=PreferentialPrice            #商品价格
        # except:
        #     time.sleep(random.randint(400,600))
        #     try:
        #         price_webs = requests.get(price_web,timeout=1000).text
        #         price_json = json.loads(price_webs)[0]
        #         try:
        #             PreferentialPrice = price_json['p']
        #         except:
        #             PreferentialPrice=None
        #         try:
        #             price = price_json['m']
        #         except:
        #             price=PreferentialPrice
        #     except:
        #         time.sleep(random.randint(1500,1800))
        #         try:
        #             price_webs = requests.get(price_web, timeout=3000).text
        #             price_json = json.loads(price_webs)[0]
        #             try:
        #                 PreferentialPrice = price_json['p']
        #             except:
        #                 PreferentialPrice = None
        #             try:
        #                 price = price_json['m']
        #             except:
        #                 price = PreferentialPrice
        #         except:
        #             price=None
        #             PreferentialPrice=None
        #             print("连接失败：",price_web)
        #             self.num = self.num + 1
        #
        # if self.num>5:
        #     print("多次连接失败，退出")
        #     exit()
        # print (price,PreferentialPrice)
        if float(PreferentialPrice)>0.00:
            item = JdItem()
            item['ProductID']=ProductID
            item['p_Name']=p_Name
            item['shop_name']=shop_name
            item['PreferentialPrice']=PreferentialPrice
            item['price']=price
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
            item['color'] = color
            item['product_url'] = url
            item['source']="京东"
            item['ProgramStarttime']=self.ProgramStarttime
            yield item
        else:
            print("广告及无效页面：",url)


