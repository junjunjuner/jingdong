import scrapy
import re
import requests
from lxml.etree import HTML
import time
import random
from gome.items import GomeItem
# import logging

# log_filename="gome_log.txt"

class gome_spider(scrapy.Spider):
    name="gome"
    allowed_domains=["gome.com.cn"]
    start_urls=[
        "http://list.gome.com.cn/cat10000198.html"
    ]


    def parse(self, response):
        sel=scrapy.Selector(response)
        paper =sel.xpath(".//span[@id='min-pager-number']/text()").extract()[0]
        title=sel.xpath(".//div[@class='nSearchWarp nSearch-crumb-category-results']/span[2]/em/text()").extract()[0]
        # print(paper)
        paper_start = paper.find('/') + 1
        page = int(paper[paper_start:])  #获取最大页数
        # print (page)
        print ("一共有"+str(page)+"页")
        print("一共有"+str(title)+"个商品")
        for i in range(1,page):
            urls="http://list.gome.com.cn/cat10000198.html?&page="+str(i)
            request=scrapy.Request(url=urls,callback=self.update,dont_filter=True)
            #time.sleep(random.choice(range(8,15)))
            yield request

    def update(self,response):        #每一页内容
        sel=scrapy.Selector(response)
        requests=sel.xpath(".//li[@class='product-item']")
        for url in requests:
            #time.sleep(6)
            goods_info=url.xpath(".//div[@class='item-tab-warp']/p[@class='item-name']/a/@href").extract()[0]      #商品链接
            goods_info_start=goods_info.find('item')
            goods_info1=goods_info[goods_info_start:]
            preid_start=goods_info.rfind('/')+1
            preid_end=goods_info.rfind('.html')
            preid=goods_info[preid_start:preid_end]
            preid_1=preid.split('-')[0]
            preid_2=preid.split('-')[1]

            p_Name=url.xpath(".//div[@class='item-tab-warp']/p[@class='item-name']/a/text()").extract()[0]      #商品名称

            try:         #店铺名称
                shop_name=url.xpath(".//div[@class='item-tab-warp']/p[@class='item-shop']/span[@class='nnamezy']/text()").extract()[0]
                if len(shop_name)==2:
                    shop_name="国美自营"
            except:
                shop_name=url.xpath(".//div[@class='item-tab-warp']/p[@class='item-shop']/a/text()").extract()[0]

            goods_web="http://"+goods_info1
            item=GomeItem(p_Name=p_Name,shop_name=shop_name,preid_1=preid_1,preid_2=preid_2,webs=goods_web)
            request=scrapy.Request(url=goods_web,callback=self.goods,meta={'item':item},dont_filter=True)
            yield request


    def goods(self,response):       #每个商品的内容
        item=response.meta['item']
        preid_1=item['preid_1']
        preid_2=item['preid_2']
        p_Name=item['p_Name']
        shop_name=item['shop_name']
        webs=item['webs']
        sel=scrapy.Selector(response)

        info_1=sel.xpath(".//div[@class='prd-firstscreen-left']")   #包含商品编号
        info_2 = sel.xpath(".//div[@class='sliderleft']")  # 包含商品详情
        try:
            product_number_info=info_1.xpath(".//div[@class='toolbar ']/span[@class='product-number']/text()").extract()[0]
            product_number=product_number_info.split('：')[1]            #商品编号
        except:
            product_number="0"



        try:
            capacity_info=re.findall("容量：.*<",info_2.extract()[0])[-1]
            capacity_start=capacity_info.find('：')+1
            capacity_end=capacity_info.rfind('<')
            capacity=capacity_info[capacity_start:capacity_end]         #商品容量
        except:
            try:
                capacity_info = re.findall("容量：.*<", info_2.extract()[0])[-1]
                capacity_start = capacity_info.find('：') + 1
                capacity_end = capacity_info.rfind('<')
                capacity = capacity_info[capacity_start:capacity_end]  # 商品容量
            except:
                capacity="none"


        try:
            X_name_info=re.findall(">商品名称：.*<",info_2.extract()[0])[0]
            X_name_start=X_name_info.find('：')+1
            X_name_end=X_name_info.rfind('<')
            X_name=X_name_info[X_name_start:X_name_end]         #商品名称
            #print (capacity)
        except:
            X_name=p_Name


        try:
            brand_info=re.findall(">品牌：.*<",info_2.extract()[0])[0]
            brand_start=brand_info.find('：')+1
            brand_end=brand_info.rfind('<')
            brand=brand_info[brand_start:brand_end]         #商品品牌
            #print(brand)
        except:
            try:
                brand_info = re.findall(">品牌：.*<", info_2.extract()[0])[0]
                brand_start = brand_info.find('：') + 1
                brand_end = brand_info.rfind('<')
                brand = brand_info[brand_start:brand_end]  # 商品品牌
                # print(brand)
            except:
                try:
                    brand_info = re.findall(">品牌：.*<", info_2.extract()[0])[0]
                    brand_start = brand_info.find('：') + 1
                    brand_end = brand_info.rfind('<')
                    brand = brand_info[brand_start:brand_end]  # 商品品牌
                    # print(brand)
                except:
                    brand="none"

        try:
            productid_info=re.findall(">型号：.*<",info_2.extract()[0])[0]
            productid_start=productid_info.find('：')+1
            productid_end=productid_info.rfind('<')
            productid=productid_info[productid_start:productid_end]         #商品型号
        except:
            productid="none"

        try:
            product_detail_info = info_2.xpath(".//div[@class='guigecanshu_wrap']/div[@class='guigecanshu']/@title").extract()
            product_detail = ' '.join(product_detail_info)  # 商品详情
            if len(product_detail) == 0:
                web=requests.get(webs).text
                www=HTML(web)
                product_detail_info = www.xpath(".//div[@class='sliderleft']/div[@class='guigecanshu_wrap']/div/text()")
                product_detail_info_1=product_detail_info+list([' '])
                product_detail_1 = []
                for i in range(len(product_detail_info)):
                    product_detail_start = product_detail_info[i].find('：') + 1
                    product_detail_1.append(product_detail_info[i][product_detail_start:])
                product_detail = ' '.join(product_detail_1)
                product_str=','.join(product_detail_info_1)
                if (capacity=="none") or (brand=="none"):
                    try:
                        capacity_1=re.findall("容量：.*?,",product_str)[-1]
                        capacity=capacity_1[3:-1]
                        print(capacity)
                    except:
                        capacity="none"
                    try:
                        brand_1=re.findall("品牌：.*?,",product_str)[-1]
                        brand=brand_1[3:-1]
                        print(brand)
                    except:
                        brand="none"
        except:
            web = requests.get(webs).text
            www = HTML(web)
            # info_2 = sel.xpath(".//div[@class='sliderleft']")  # 包含商品详情
            product_detail_info = www.xpath(".//div[@class='sliderleft']/div[@class='guigecanshu_wrap']/div/text()")
            product_detail_info_1 = product_detail_info + list([' '])
            # print(product_detail_info)
            product_detail_1 = []
            for i in range(len(product_detail_info)):
                product_detail_start = product_detail_info[i].find('：') + 1
                product_detail_1.append(product_detail_info[i][product_detail_start:])
            product_detail = ' '.join(product_detail_1)
            product_str = ','.join(product_detail_info_1)
            if (capacity == "none") or (brand == "none"):
                try:
                    capacity_1 = re.findall("容量：.*?,", product_str)[-1]
                    capacity = capacity_1[3:-1]
                    print(capacity)
                except:
                    capacity = "none"
                try:
                    brand_1 = re.findall("品牌：.*?,", product_str)[-1]
                    brand = brand_1[3:-1]
                    print(brand)
                except:
                    brand = "none"



        comment_url="http://review.gome.com.cn/"+str(preid_1)+"-0-1.html"     #商品评价链接
        item = GomeItem(p_Name=p_Name, shop_name=shop_name, preid_1=preid_1, preid_2=preid_2, \
                               product_number=product_number, product_detail=product_detail, \
                               capacity=capacity, brand=brand, productid=productid,X_name=X_name)
        request = scrapy.Request(url=comment_url, callback=self.goods_comment_price, meta={'item': item}, dont_filter=True)
       # time.sleep(8)
        yield request

    def goods_comment_price(self,response):
        item=response.meta['item']
        p_Name=item['p_Name']
        shop_name=item['shop_name']
        preid_1=item['preid_1']
        preid_2=item['preid_2']
        product_number=item['product_number']
        product_detail=item['product_detail']
        capacity=item['capacity']
        brand=item['brand']
        productid=item['productid']
        X_name=item['X_name']
        #time.sleep(6)
        sel=scrapy.Selector(response)

        commentcount_url="http://ss.gome.com.cn/item/v1/prdevajsonp/appraiseNew/"+str(preid_1)+"/1/all/0/10/flag/appraise"  #商品评论数链接
        price_url="http://ss.gome.com.cn/item/v1/d/m/store/unite/"+str(preid_1)+"/"+str(preid_2)+"/N/31180100/311801001/1/null/flag/item"   #商品价格链接

        #time.sleep(6)
        commentcount_web=requests.get(commentcount_url,timeout= 600).text
        try:
            bad_info=re.findall('"bad":\d+',commentcount_web)[0]
            PoorCount=bad_info.split(':')[-1]           #差评数
        except:
            PoorCount="0"
        try:
            good_info=re.findall('"good":\d+',commentcount_web)[0]
            GoodCount=good_info.split(':')[-1]          #好评数
        except:
            GoodCount="0"
        try:
            mid_info=re.findall('"mid":\d+',commentcount_web)[0]
            GeneralCount=mid_info.split(':')[-1]        #中评数
        except:
            GeneralCount="0"
        try:
            total_info=re.findall('"totalCount":\d+',commentcount_web)[0]
            CommentCount=total_info.split(':')[-1]     #评论总数
        except:
            CommentCount="0"
        #time.sleep(6)

        price_web = requests.get(price_url).text
        try:
            price_info = re.findall('"salePrice":".*?"', price_web)[0]
        except:
            try:
                price_info = re.findall('"salePrice":".*?"', price_web)[0]
            except:
                time.sleep(10)
                price_info = re.findall('"salePrice":".*?"', price_web)[0]
        price_1 = price_info.split(':')[-1]
        price_start = price_1.find('\"') + 1
        price_end = price_1.rfind('\"')
        price = price_1[price_start:price_end]         #价格
        PreferentialPrice=price[:]

        X_type="none"

        comment_web = sel.xpath(".//div[@class='adv-main']")
        try:
            #comment_num=comment_web.xpath(".//div[@class='adv-tlayer']/span[@class='adv-prdcount']/strong/text()").extract()[0]
            if int(CommentCount) == 0:  # 好评率
            # if int(comment_num)==0:          #好评率
                GoodRateShow="none"
            else:
                GoodRateShow=comment_web.xpath(".//div[@class='adv-goods']/div[@class='adv-gdsper']/span/text()").extract()[0]
        except:
            if int(CommentCount)!=0 and int(CommentCount)==int(GoodCount):
                GoodRateShow="100"
            else:
                # time.sleep(8)
                try:
                    # comment_num = comment_web.xpath( ".//div[@class='adv-tlayer']/span[@class='adv-prdcount']/strong/text()").extract()[0]
                    GoodRateShow = comment_web.xpath(".//div[@class='adv-goods']/div[@class='adv-gdsper']/span/text()").extract()[0]
                except:
                    if int(CommentCount)!=0:
                        goodpercent = round(int(GoodCount) / int(CommentCount) * 100)
                        generalpercent = round(int(GeneralCount) / int(CommentCount)* 100)
                        poorpercent = round(int(PoorCount) / int(CommentCount) * 100)
                        commentlist = [int(GoodCount), int(GeneralCount), int(PoorCount)]
                        percent_list = [goodpercent, generalpercent, poorpercent]
                        # 对不满百分之一的判定
                        for i in range(len(percent_list)):
                            if percent_list[i] == 0 and commentlist[i] != 0 and int(CommentCount) != 0:
                                percent_list[i] = 1
                        nomaxpercent = 0  # 定义为累计不是最大百分比数值
                        # 好评度计算url='http://res.suning.cn/project/review/js/reviewAll.js?v=20170823001'
                        if int(CommentCount) != 0:
                            maxpercent = max(goodpercent, generalpercent, poorpercent)
                            for each in percent_list:
                                if maxpercent != each:
                                    nomaxpercent += each
                            GoodRateShow = str(100 - nomaxpercent)
                        else:
                            GoodRateShow = "100"
                    else:
                        GoodRateShow="0"
                        # GoodRateShow="none"

        try:         #评论关键词
            comment_info=comment_web.xpath(".//div[@class='adv-recommend']/div[@class='w-recommend']/span/text()").extract()
            keyword=' '.join(comment_info)
        except:
            keyword="none"
        item = GomeItem(p_Name=p_Name, shop_name=shop_name, preid_1=preid_1, preid_2=preid_2, \
                        ProductID=preid_1, X_name=X_name, capacity=capacity,\
                        product_detail=product_detail,type=product_detail, brand=brand, productid=productid, \
                        GoodRateShow=GoodRateShow,keyword=keyword,PoorCount=PoorCount,\
                        GoodCount=GoodCount,GeneralCount=GeneralCount,CommentCount=CommentCount,\
                        price=price,PreferentialPrice=PreferentialPrice,X_type=X_type)

        yield item








