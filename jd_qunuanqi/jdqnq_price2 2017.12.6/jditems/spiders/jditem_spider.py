import scrapy
from bs4 import BeautifulSoup
import requests
import re
import json
from jditems.items import JdItem
import time,random

class jdspider(scrapy.Spider):
    name="jd_qnq"                 #京东取暖器
    allowed_domains=["jd.com"]
    start_urls=[
        "https://list.jd.com/list.html?cat=737,738,747"   #取暖器
    ]
    num=0
    ProgramStarttime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def parse(self, response):
        sel = scrapy.Selector(response)

        '''''''''
        方法二
        '''''''''
        productid_list=sel.xpath(".//div[@id='plist']/ul/li/div[@class='gl-i-wrap j-sku-item']/@data-sku").extract()
        print(productid_list)
        print(len(productid_list))
        productid_str='%2CJ_'.join(productid_list)
        # time.sleep(random.randint(60,120))
        # price_web = "https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_" + str(productid_str)
        price_web="https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_"+str(productid_str)+"&pdbp=0&pdtk=IkjukMAf4OSksZJdVdwoWzNqUKWsuk4e%2BusjgPTBC2lrnf%2Bu6kLlRyEV42%2BI5bho&pdpin=&pduid=1508741337887922929012&source=list_pc_front"
        price_webs = requests.get(price_web, timeout=1000).text
        price_jsons = json.loads(price_webs)
        for price_json in price_jsons:
            print(price_json)
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
        '''''''''''
        方法一
        '''''''''''
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
        # #测试用
        # ProductID='1976549923'
        # item = JdItem(ProductID=ProductID,PreferentialPrice=0,price=0)
        # # url="https://item.jd.hk/1971910764.html"
        # url="https://item.jd.hk/1976549923.html"
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

        #"https://z.jd.com/project/details/90713.html"  众筹页面
        # elif "/z.jd.com" in url:
        #     print("众筹页面：",url)
        #     return None

        #IndexError: list index out of range
        #"http://www.jd.com/?cdn40"

        # --------------------全球购网页---------------------------------------------
        elif "hk" in url:
            print("全球购：", url)

            #京东商品介绍部分
            detail_info = sel.xpath(".//div[@class='p-parameter']")  # 包含商品详情内容
            detail = detail_info.xpath(".//li/text()").extract()
            if detail[0]=='品牌： ':
                detail_brand=detail_info.xpath(".//li[1]/@title").extract()[0]
                detail[0]=detail[0]+detail_brand
            product_detail = '\"'+' '.join(detail).replace('\t', '').replace('\n', '').replace('  ','')+'\"'
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
                brand = brand[:0] + re.sub("\(.*?\)", '', brand)
                brand = brand[:0] + re.sub("（.*?）", '', brand)
                brand = brand[:0] + re.sub("（.*?\)", '', brand)
                brand = brand[:0] + re.sub("\(.*?）", '', brand)
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
                X_type = re.findall(">类型：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    X_type = x['类别']
                except:
                    X_type = None

            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['颜色']
                except:
                    color = None

            try:
                adapt_area = re.findall(">适用面积：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    adapt_area = x['适用面积m2']
                except:
                    adapt_area = None


            try:
                placement = re.findall(">放置方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    placement = x['操作方式']
                except:
                    placement = None

            try:
                heat = x['加热方式']
            except:
                try:
                    heat = re.findall(">加热方式：(.*?)<", detail_1[0])[0].strip()
                except:
                    heat = None
            # try:
            #     heat_list=heat.split('，')
            #     print(heat_list)
            #     if len(heat_list)>1:
            #         heat=None
            # except:
            #     heat=heat

            try:
                control = re.findall(">控制方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['控制方式']
                except:
                    control = None



            try:
                brand_num = re.findall(">加热片数量：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    brand_num = x['加热片数量']
                except:
                    brand_num = None

            try:
                gear=re.findall(">档位：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    gear = x['档位']
                except:
                    gear = None

            try:
                size = re.findall(">产品尺寸：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    size = x['产品尺寸(mm)']
                except:
                    size = None

            try:
                dump_off=re.findall(">倾倒断电：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    dump_off = x['倾倒断电']
                except:
                    dump_off = None

            try:
                time=re.findall(">定时功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    time = x['定时功能']
                except:
                    time = None

            try:
                constant_temp=re.findall(">恒温功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    constant_temp = x['恒温功能']
                except:
                    constant_temp = None

            try:
                telecontrol=re.findall(">遥控功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    telecontrol = x['遥控功能']
                except:
                    telecontrol = None

            try:
                waterproof=re.findall(">防水功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    waterproof = x['防水功能']
                except:
                    waterproof = None

            try:
                shake=re.findall(">摇头功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    shake = x['摇头功能']
                except:
                    shake = None

            try:
                bath_house=re.findall(">浴居两用：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    bath_house = x['浴居两用']
                except:
                    bath_house = None
            if bath_house == "不是":
                bath_house = "不支持"
            elif bath_house=="是":
                bath_house="支持"

            # price_web="https://p.3.cn/prices/mgets?pduid=15107253217849152442&skuIds=J_"+str(ProductID)
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
            detail = detail_info.xpath(".//li/text()").extract()
            if detail[0]=='品牌： ':
                detail_brand=detail_info.xpath(".//li[1]/@title").extract()[0]
                detail[0]=detail[0]+detail_brand
            product_detail = '\"'+' '.join(detail).replace('\t', '').replace('\n', '').replace('  ','')+'\"'
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
                brand=brand[:0]+re.sub("\(.*?\)",'',brand)
                brand = brand[:0] + re.sub("（.*?）", '', brand)
                brand = brand[:0] + re.sub("（.*?\)", '', brand)
                brand = brand[:0] + re.sub("\(.*?）", '', brand)
                if brand == "TOSOT":
                    brand = "大松"
                if brand == "Panasonic":
                    brand = "松下"

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
                X_type = re.findall(">类型：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    X_type = x['类别']
                except:
                    X_type = None

            try:
                color = re.findall(">颜色：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    color = x['颜色']
                except:
                    color = None

            try:
                adapt_area = re.findall(">适用面积：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    adapt_area = x['适用面积m2']
                except:
                    adapt_area = None


            try:
                placement = re.findall(">放置方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    placement = x['操作方式']
                except:
                    placement = None

            try:
                heat = re.findall(">加热方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    heat = x['加热方式']
                except:
                    heat = None
            # try:
            #     heat_list=heat.split('，')
            #     print(heat_list)
            #     if len(heat_list)>1:
            #         heat=None
            # except:
            #     heat=heat

            try:
                control = re.findall(">控制方式：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    control = x['控制方式']
                except:
                    control = None



            try:
                brand_num = re.findall(">加热片数量：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    brand_num = x['加热片数量']
                except:
                    brand_num = None

            try:
                gear=re.findall(">档位：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    gear = x['档位']
                except:
                    gear = None

            try:
                size = re.findall(">产品尺寸：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    size = x['产品尺寸(mm)']
                except:
                    size = None

            try:
                dump_off=re.findall(">倾倒断电：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    dump_off = x['倾倒断电']
                except:
                    dump_off = None

            try:
                time=re.findall(">定时功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    time = x['定时功能']
                except:
                    time = None

            try:
                constant_temp=re.findall(">恒温功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    constant_temp = x['恒温功能']
                except:
                    constant_temp = None

            try:
                telecontrol=re.findall(">遥控功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    telecontrol = x['遥控功能']
                except:
                    telecontrol = None

            try:
                waterproof=re.findall(">防水功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    waterproof = x['防水功能']
                except:
                    waterproof = None

            try:
                shake=re.findall(">摇头功能：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    shake = x['摇头功能']
                except:
                    shake = None

            try:
                bath_house=re.findall(">浴居两用：(.*?)<", detail_1[0])[0].strip()
            except:
                try:
                    bath_house = x['浴居两用']
                except:
                    bath_house = None
            if bath_house == "不是":
                bath_house = "不支持"
            elif bath_house=="是":
                bath_house="支持"

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

        # search_web = "https://search.jd.com/Search?keyword=" + str(p_Name) + "&enc=utf-8&wq=" + str(p_Name)
        # # print ("search页面：",search_web)
        # search_webs = requests.get(search_web, timeout=1000).text
        # soup = BeautifulSoup(search_webs, 'lxml')
        # skuid = "J_" + str(ProductID)
        # try:
        #     price_info = soup('strong', class_=skuid)
        #     PreferentialPrice = re.findall("<em>ï¿¥</em><i>(.*?)</i>", str(price_info[0]))[0]
        #     # 会有<strong class="J_10108922808" data-done="1" data-price="639.00"><em>ï¿¥</em><i></i></strong>出现
        #     #如id=10108922808  p_Name=柏翠（petrus） 38L电烤箱家用多功能 精准控温 PE7338 升级版
        #     if len(PreferentialPrice) == 0:
        #         PreferentialPrice = re.findall('data-price=\"(.*?)\"', str(price_info[0]))[0]
        #     price = PreferentialPrice
        # except:
        #     try:
        #         print("价格：",price_web)
        #         price_webs = requests.get(price_web, timeout=1000).text
        #         price_json = json.loads(price_webs)[0]
        #         PreferentialPrice = price_json['p']
        #         price = price_json['m']
        #     except:
        #         price=None
        #         PreferentialPrice=None
        # print(price,PreferentialPrice)
        # #品牌处理
        # print (brand)
        # if brand:
        #     if 'pocatan' in brand:
        #         brand = 'pocatan'
        #     if ('戴森' or 'dyson' or 'Dyson') in brand:
        #         brand = '戴森'
        #     if ('巴慕达' or 'BALMUDA') in brand:
        #         brand = '巴慕达'
        #     if 'AUX' in brand:
        #         brand = 'AUX'
        #     if ('Beurer' or '博雅') in brand:
        #         brand = '博雅'
        #     if 'BOKUK' in brand:
        #         brand = 'BOKUK'
        #     if 'BUSHENGDIANQI' in brand:
        #         brand = '步升电器'
        #     if ('CHIGO' or '志高') in brand:
        #         brand = '志高'
        #     if ('Delonghi' or '德龙') in brand:
        #         brand = '德龙'
        #     if ('Honeywell' or '霍尼韦尔') in brand:
        #         brand = '霍尼韦尔'
        #     # if 'HYUNDAI' in brand:
        #     #     brand = '韩国现代'
        #     if 'IRIS' in brand:
        #         brand = '爱丽思'
        #     # if 'JY吉毅' in brand:
        #     #     brand = '吉毅'
        #     if 'Keyeon' in brand:
        #         brand = '凯易欧'
        #     if ('KONKA' or '康佳') in brand:
        #         brand = '康佳'
        #     if 'MIH' in brand:
        #         brand = '米拉德'
        #     if 'MORITA' in brand:
        #         brand = '森田'
        #     if 'namunani' in brand:
        #         brand = '纳木那尼'
        #     if ('NOIROT' or '诺朗') in brand:
        #         brand = '诺朗'
        #     if 'Paosecuxinv' in brand:
        #         brand = '普森斯瑞'
        #     if ('PHILCO' or '飞歌') in brand:
        #         brand = '飞歌'
        #     if 'renebelle' in brand:
        #         brand = 'renebelle'
        #     if 'Re-life' in brand:
        #         brand = 'Re-life'
        #     if 'RuiXinDa' in brand:
        #         brand = '瑞鑫达'
        #     if 'sichler' in brand:
        #         brand = 'sichler'
        #     if 'SANAU' in brand:
        #         brand = '三诺'
        #     if 'SANSHIAH' in brand:
        #         brand = '三夏'
        #     if 'Semptec' in brand:
        #         brand = 'Semptec'
        #     if 'SEGI' in brand:
        #         brand = '世纪'
        #     if 'SheerAIRE' in brand:
        #         brand = '席爱尔'
        #     if 'SK' in brand:
        #         brand = '艾斯凯杰'
        #     if 'Smart Frog' in brand:
        #         brand = '卡蛙'
        #     if 'SONGX' in brand:
        #         brand = '松心'
        #     if 'SVIII' in brand:
        #         brand = '山湖'
        #     if 'TCL' in brand:
        #         brand = 'TCL'
        #     if ('AKAI' or '雅佳') in brand:
        #         brand = '雅佳'
        #     if ('singfun' or '先锋') in brand:
        #         brand = '先锋'
        #     if ('Tefal' or '特福') in brand:
        #         brand = '特福'
        #     if ('Stadler Form' or '斯泰得乐') in brand:
        #         brand = '斯泰得乐'
        #     if ('奥克斯' or 'AUX') in brand:
        #         brand = '奥克斯'
        #     if 'YOSTAR' in brand:
        #         brand = 'YOSTAR'
        #     if '长虹' in brand:
        #         brand = '长虹'
        #     if '美的' in brand:
        #         brand = '美的'
        #     if '惠而浦' in brand:
        #         brand = '惠而浦'
        #     if '海尔' in brand:
        #         brand = '海尔'
        #     if '澳洲阳光' in brand:
        #         brand = '澳洲阳光'
        #     if 'Soleil' in brand:
        #         brand = 'Soleil'
        #     if 'World Marketing' in brand:
        #         brand = 'World Marketing'
        #     if 'Dura Heat' in brand:
        #         brand = 'Dura Heat'
        #     if 'Mr. Heater' in brand:
        #         brand = 'Mr. Heater'
        #     if 'Comfort Glow' in brand:
        #         brand = 'Comfort Glow'
        #     if 'Dyna-Glo' in brand:
        #         brand = 'Dyna-Glo'
        #     if 'Lasko' in brand:
        #         brand = 'Lasko'
        #     if 'Optimus' in brand:
        #         brand = 'Optimus'
        #     if ('百奥耐尔' or 'Bionaire') in brand:
        #         brand = '百奥耐尔'
        #     if 'Lifesource' in brand:
        #         brand = 'Lifesource'
        #     if '美的' in brand:
        #         brand = '美的'
        # print (brand)

        #档位处理
        # print(gear)
        if gear:
            gear = re.sub('调温', '', gear)
            gear = re.sub('位', '', gear)
            gear = re.sub('二', '2', gear)
            gear = re.sub('三', '3', gear)
            gear = re.sub('四', '4', gear)
            gear = re.sub('五', '5', gear)
        # print(gear)

        #适用面积处理
        # print(adapt_area)
        if adapt_area:
            adapt_area = re.sub('以及', '', adapt_area)
            adapt_area = re.sub('平米', '㎡', adapt_area)
            if re.findall('\d', adapt_area[-1]):
                adapt_area = adapt_area[:] + '㎡'
            if adapt_area == '10㎡以下':
                adapt_area = '10㎡以及以下'
            # if '-' in adapt_area:
            #     a1 = int(adapt_area.split('-')[0][:])
            #     a2 = int(adapt_area.split('-')[1][:-1])
            #     if a1 >= 10 and a2 <= 20:
            #         adapt_area = "11-20㎡"
            #     if a1 >= 20 and a2 <= 30:
            #         adapt_area = "21-30㎡"
            #     if a1 >= 30 and a2 <= 40:
            #         adapt_area = "31-40㎡"
            #     if a1 >= 40:
            #         adapt_area = "40㎡以上"
        # print(adapt_area)

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
        item['X_name']=X_name
        item['X_type']=X_type
        item['color']=color
        item['adapt_area']=adapt_area
        item['placement']=placement
        item['heat']=heat
        item['control']=control
        item['brand_num']=brand_num
        item['gear']=gear
        item['size']=size
        item['dump_off']=dump_off
        item['time']=time
        item['constant_temp']=constant_temp
        item['telecontrol']=telecontrol
        item['waterproof']=waterproof
        item['shake']=shake
        item['bath_house']=bath_house
        item['product_url'] = url
        item['source']="京东"
        item['ProgramStarttime']=self.ProgramStarttime
        yield item


