import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jdtest.items import JdtestItem
import time,random
from selenium import webdriver

class jdspider(scrapy.Spider):
    name="jdtest"
    allowed_domains=["jd.com"]
    start_urls=[
        #整体橱柜
        "https://search.jd.com/search?keyword=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&enc=utf-8&qrst=1&rt=1&stop=1&lastprice=1000gt&vt=2&suggest=1.his.0.0&psort=2&click=0"
    ]
    driver = webdriver.Chrome('/home/260199/chrome/chromedriver')  # 创建一个driver用于打开网页，记得找到brew安装的chromedriver的位置，在创建driver的时候指定这个位置
    def get_url(self,driver):
        # 将页面滚动条拖到底部
        # url=response.url
        js = "var q=document.documentElement.scrollTop=10000"
        driver.execute_script(js)
        time.sleep(3)
        # 搜索
        soup = BeautifulSoup(driver.page_source, 'lxml')
        productid_info = soup.find_all('li', class_='gl-item')
        print(len(productid_info))
        if len(productid_info) == 30:
            print("未翻页")
            js = "var q=document.documentElement.scrollTop=10000"
            driver.execute_script(js)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            productid_info = soup.find_all('li', class_='gl-item')
            print(len(productid_info))

        for pro in productid_info[0:2]:
            ProductID = re.findall('data-sku=\"(.*?)\"', str(pro))[0]
            price = re.findall('<em>￥</em><i>(.*?)</i>', str(pro))[0]
            item=JdtestItem()
            item['ProductID']=ProductID
            item['price']=price
            goods_web = "https://item.jd.com/" + str(ProductID) + ".html"
            request = scrapy.Request(url=goods_web, callback=self.goods, meta={'item': item}, dont_filter=True)
            yield request
        time.sleep(3)
        next_page = driver.find_element_by_xpath(".//div[@class='page clearfix']/div/span[@class='p-num']/a[@class='pn-next']").click()
        # time.sleep(2)
        print("page")
        self.get_url(next_page)
        time.sleep(2)

        # yield scrapy.Request(url=next_page, callback=self.get_url)


    def parse(self, response):
        # sel=scrapy.Selector(response)
        # 整体橱柜
        # url = 'https://search.jd.com/Search?keyword=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&enc=utf-8&wq=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&pvid=a7933b8c1eb341849cebc6e466f1bd74'
        driver = webdriver.Chrome('/home/260199/chrome/chromedriver')  # 创建一个driver用于打开网页，记得找到brew安装的chromedriver的位置，在创建driver的时候指定这个位置
        url=driver.get(self.start_urls[0])  # 打开网页
        return self.get_url(url) # 打开网页)
        # # url="https://item.jd.hk/18739277759.html"    #京东全球购   与普通网址不同，不同的地方为“https://item.jd.com/4251335.html”
        # goods_info=sel.xpath(".//div[@id='J_goodsList']/ul/li")
        # for goods in goods_info:
        #     goods_web1=goods.xpath(".//div[@class='p-img']/a/@href").extract()
        #     print(goods_web1[0])
        #     ProductID=goods_web1[0].split('/')[-1][:-5]
        #     # ProductID=goods.xpath(".//div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()       #商品编号
        #     # print(ProductID)
        #     if len(ProductID[0])!=0:
        #         # goods_web="https://item.jd.com/"+str(ProductID)+".html"         #商品链接   包含商品型号,店铺名称,类别,品牌,型号等
        #         goods_web="https:"+goods_web1[0]
        #         item=JdtestItem(ProductID=ProductID)
        #         request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
        #         # yield request
        #     else:
        #         print("parse中ProductID为空  没有读到")
        # #测试用
        # ProductID='16377640943'
        # item = JdtestItem(ProductID=ProductID)
        # url="https://item.jd.com/"+str(ProductID)+".html"
        # request = scrapy.Request(url=url, callback=self.goods,meta={'item':item}, dont_filter=True)
        # yield request

        # #翻页功能
        # next_page=sel.xpath(".//div[@class='p-wrap']/span[@class='p-num']/a[@class='pn-next']/@href").extract()
        # if next_page:
        #     next="https://list.jd.com/"+next_page[0]
        #     yield scrapy.Request(next,callback=self.parse)

    def goods(self,response):
        item=response.meta['item']
        sel=scrapy.Selector(response)
        url=response.url
        ProductID=item['ProductID']
        price = item['price']
            #---------------------普通网页-----------------------------------
        if 'item.jd.com/' in url:
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

            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '')
            detail_1=detail_info.extract()

            try:
                # a = requests.get(url).text
                # s = BeautifulSoup(a, 'lxml')
                s=BeautifulSoup(url.text,'lxml')
                # print (a)
                guige = s.find('div', class_='Ptable')
                guige1 = guige.find_all('div', class_='Ptable-item')
                x = {}
                for gg in guige1:
                    guige2 = gg.find_all('dt', class_=None)
                    guige3 = gg.find_all('dd', class_=None)
                    for i in range(len(guige2)):
                        dt = re.findall(">(.*?)<", str(guige2[i]))
                        dd = re.findall(">(.*?)<", str(guige3[i]))
                        x.setdefault(dt[0], dd[0])
            except:
                x=None

            try:
                brand=detail_info.xpath(".//ul[@id='parameter-brand']/li/a/text()").extract()[0].strip()    #商品品牌
            except:
                try:
                    brand=sel.xpath(".//div[@class='inner border']/div[@class='head']/a/text()").extract()[0].strip()
                except:
                    try:
                        brand=x['品牌']
                    except:
                        brand=None

            if ("（" and "）") in brand:
                dd=re.findall("（.*?）",brand)[0]
                brand=brand.replace(dd,'').replace(' ','')
            if ("(" and ")") in brand:
                dd=re.findall("\(.*?\)",brand)[0]
                brand=brand.replace(dd,'').replace(' ','')
            if brand=="HANSBERGER":
                brand="汉斯伯格"
            if brand=="JQS":
                brand="金骑士"

            try:
                try:
                    huohao=re.findall(">货号：(.*?)<",detail_1[0])[0].strip()
                    X_name=brand+huohao
                except:
                    try:
                        huohao=x['型号']
                        X_name = brand + huohao
                    except:
                        X_name=re.findall(">商品名称：(.*?)<",detail_1[0])[0].strip().replace('\t','')      #商品名称
                        if len(X_name)==0:
                            X_name=p_Name
                        if p_Name==None:
                            p_Name=X_name
            except:
                X_name=p_Name

            try:
                shape=re.findall(">形状：(.*?)<",detail_1[0])[0].strip()
            except:
                try:
                    shape=x['形状']
                except:
                    shape=None

            try:
                X_type=re.findall(">类别：(.*?)<",detail_1[0])[0].strip()
            except:
                try:
                    X_type=x['类别']
                except:
                    X_type=None

            comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
            price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
            # price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(ProductID)+"&pdbp=0&pdtk=vJSo%2BcN%2B1Ot1ULpZg6kb4jfma6jcULJ1G2ulutvvlxgL3fj5JLFWweQbLYhUVX2E&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1510210566056"


            # --------------------全球购网页---------------------------------------------
        else:
            print("全球购：", url)

            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/@title").extract()
            product_detail = ' '.join(detail).replace('\t', '')
            detail_1 = detail_info.extract()

            try:
                p_Name = sel.xpath(".//div[@class='sku-name']/text()").extract()[-1].strip('\"').strip('\n').strip().replace('\t', '')
            except:
                p_Name = None

            # detail_info=sel.xpath(".//div[@class='p-parameter']/text()").extract()

            try:
                shop_name = sel.xpath(".//div[@class='shopName']/strong/span/a/text()").extract()[0]  # 店铺名称
            except:
                try:
                    shop_name = re.findall(">店铺：(.*?)<", detail_1[0])[0].strip()
                except:
                    shop_name = None

            try:
                # a = requests.get(url).text
                # s = BeautifulSoup(a, 'lxml')
                s=BeautifulSoup(url.text,'lxml')
                # print (a)
                guige = s.find('div', id_='specifications')
                x = {}
                guige2 = guige.find_all('td', class_='tdTitle')
                guige3 = guige.find_all('td', class_=None)
                for i in range(len(guige2)):
                    dt = re.findall(">(.*?)<", str(guige2[i]))
                    dd = re.findall(">(.*?)<", str(guige3[i]))
                    x.setdefault(dt[0], dd[0])
            except:
                x=None

            try:
                brand=detail_info.xpath(".//ul[@id='parameter-brand']/li/a/text()").extract()[0].strip()    #商品品牌
            except:
                try:
                    brand=sel.xpath(".//div[@class='inner border']/div[@class='head']/a/text()").extract()[0].strip()
                except:
                    try:
                        brand=x['品牌']
                    except:
                        brand=None

            if ("（" and "）") in brand:
                dd=re.findall("（.*?）",brand)[0]
                brand=brand.replace(dd,'').replace(' ','')
            if ("(" and ")") in brand:
                dd=re.findall("\(.*?\)",brand)[0]
                brand=brand.replace(dd,'').replace(' ','')
            if brand=="HANSBERGER":
                brand="汉斯伯格"
            if brand=="JQS":
                brand="金骑士"

            try:
                try:
                    huohao=re.findall(">货号：(.*?)<",detail_1[0])[0].strip()
                    X_name=brand+huohao
                except:
                    try:
                        huohao=x['型号']
                        X_name = brand + huohao
                    except:
                        X_name=re.findall(">商品名称：(.*?)<",detail_1[0])[0].strip().replace('\t','')      #商品名称
                        if len(X_name)==0:
                            X_name=p_Name
                        if p_Name==None:
                            p_Name=X_name
            except:
                X_name=p_Name

            try:
                shape=re.findall(">形状：(.*?)<",detail_1[0])[0].strip()
            except:
                try:
                    shape=x['形状']
                except:
                    shape=None

            try:
                X_type=re.findall(">类别：(.*?)<",detail_1[0])[0].strip()
            except:
                try:
                    X_type=x['类别']
                except:
                    X_type=None


            comment_web="https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
            price_web="https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_"+str(ProductID)

        # 商品评价   json格式

        # comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
        # comment_web="https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds="+str(ProductID)

        try:
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
            except IndexError:
                keyword=None

            rate = urls['productCommentSummary']
            try:
                CommentCount = rate['commentCount']  # 评论总数
            except IndexError:
                CommentCount=None
                print("评价总数",CommentCount)
            try:
                GoodRateShow = rate['goodRateShow']  # 好评率
            except IndexError:
                GoodRateShow=None
                print("好评率:",GoodRateShow)
            try:
                GoodCount = rate['goodCount']  # 好评数
            except IndexError:
                GoodCount=None
                print("好评数:",GoodCount)
            try:
                GeneralCount = rate['generalCount']  # 中评数
            except IndexError:
                GeneralCount =None
                print("中评数:",GeneralCount)
            try:
                PoorCount = rate['poorCount']  # 差评数
            except IndexError:
                PoorCount=None
                print("差评数:",PoorCount)
        except:
            time.sleep(random.randint(500,600))
            try:
                comment_webs = requests.get(comment_web, timeout=1000).text
                urls = json.loads(comment_webs)
                try:
                    comment = urls['hotCommentTagStatistics']
                    keyword_list = []
                    for i in range(len(comment)):
                        keyword_list.append(comment[i]['name'])
                    keyword = ' '.join(keyword_list)  # 关键词
                except:
                    keyword = None

                rate = urls['productCommentSummary']
                try:
                    CommentCount = rate['commentCount']  # 评论总数
                except:
                    print("评论:",comment_web)
                    CommentCount = None
                try:
                    GoodRateShow = rate['goodRateShow']  # 好评率
                except:
                    GoodRateShow = None
                    print("except中好评率：",GoodRateShow)
                try:
                    GoodCount = rate['goodCount']  # 好评数
                except:
                    GoodCount =None
                try:
                    GeneralCount = rate['generalCount']  # 中评数
                except:
                    GeneralCount = None
                try:
                    PoorCount = rate['poorCount']  # 差评数
                except:
                    PoorCount =None
            except:
                time.sleep(random.randint(1600,1800))
                try:
                    comment_webs = requests.get(comment_web, timeout=3000).text
                    urls = json.loads(comment_webs)
                    try:
                        comment = urls['hotCommentTagStatistics']
                        keyword_list = []
                        for i in range(len(comment)):
                            keyword_list.append(comment[i]['name'])
                        keyword = ' '.join(keyword_list)  # 关键词
                    except:
                        keyword = None

                    rate = urls['productCommentSummary']
                    try:
                        CommentCount = rate['commentCount']  # 评论总数
                    except:
                        print("评论:", comment_web)
                        CommentCount = None
                    try:
                        GoodRateShow = rate['goodRateShow']  # 好评率
                    except:
                        GoodRateShow = None
                        print("except中好评率：", GoodRateShow)
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
                except:
                    # CommentCount = None
                    # GoodRateShow = None
                    # GeneralCount=None
                    # GoodCount = None
                    # PoorCount = None
                    print("连接失败：",comment_web)

        # #商品价格（json格式）
        # # "https://p.3.cn/prices/mgets?skuIds=J_19131673204"
        # # price_web="https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_"+str(ProductID)
        # # price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(ProductID)+"&pdbp=0&pdtk=vJSo%2BcN%2B1Ot1ULpZg6kb4jfma6jcULJ1G2ulutvvlxgL3fj5JLFWweQbLYhUVX2E&pdpin=&pduid=1508741337887922929012&source=list_pc_front&_=1510210566056"
        #
        # try:
        #     price_webs = requests.get(price_web,timeout=1000).text
        #     price_json = json.loads(price_webs)[0]
        #     try:
        #        price = price_json['m']
        #     except:
        #        price_info = re.findall('\"p\":\".*?\"', str(price_webs))
        #        price = price_info[0][5:-1]
        #     try:
        #        PreferentialPrice = price_json['p']
        #     except:
        #         PreferentialPrice=price             #商品价格
        # except:
        #     time.sleep(random.randint(400,600))
        #     try:
        #         price_webs = requests.get(price_web,timeout=1000).text
        #         price_json = json.loads(price_webs)[0]
        #         try:
        #             PreferentialPrice = price_json['p']
        #         except:
        #             try:
        #                 PreferentialPrice_info = re.findall('\"p\":\".*?\"', str(price_webs))
        #                 PreferentialPrice = PreferentialPrice_info[0][5:-1]
        #             except:
        #                 PreferentialPrice=None
        #         try:
        #             price = price_json['m']
        #         except:
        #             try:
        #                price_info = re.findall('\"m\":\".*?\"', str(price_webs))
        #                price = price_info[0][5:-1]
        #             except:
        #                 price=PreferentialPrice
        #     except:
        #         time.sleep(random.randint(1500,1800))
        #         try:
        #             price_webs = requests.get(price_web,timeout=3000).text
        #             price_json = json.loads(price_webs)[0]
        #             try:
        #                 PreferentialPrice = price_json['p']
        #             except:
        #                 try:
        #                     PreferentialPrice_info = re.findall('\"p\":\".*?\"', str(price_webs))
        #                     PreferentialPrice = PreferentialPrice_info[0][5:-1]
        #                 except:
        #                     PreferentialPrice=None
        #             try:
        #                 price = price_json['m']
        #             except:
        #                 try:
        #                    price_info = re.findall('\"m\":\".*?\"', str(price_webs))
        #                    price = price_info[0][5:-1]
        #                 except:
        #                     price=PreferentialPrice
        #         except:
        #             print("连接失败：",price_web)


        item = JdtestItem()
        item['ProductID']=ProductID
        item['p_Name']=p_Name
        item['shop_name']=shop_name
        item['price']=price
        item['PreferentialPrice']=price
        item['CommentCount']=CommentCount
        item['GoodRateShow']=GoodRateShow
        item['GoodCount']=GoodCount
        item['GeneralCount']=GeneralCount
        item['PoorCount']=PoorCount
        item['keyword']=keyword
        item['type']=product_detail
        item['brand']=brand
        item['X_name']=X_name
        item['X_type']=X_type
        item['shape'] = shape
        item['price_range'] = None
        item['product_url'] = url
        item['source']="京东"
        yield item

