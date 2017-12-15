# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    #商品型号
    p_Name = scrapy.Field()
    #店铺名称
    shop_name = scrapy.Field()
    #商品ID
    ProductID = scrapy.Field()
    #正价
    price = scrapy.Field()
    #折扣价
    PreferentialPrice = scrapy.Field()
    #评论总数
    CommentCount = scrapy.Field()
    #好评度
    GoodRateShow = scrapy.Field()
    #好评
    GoodCount = scrapy.Field()
    #中评
    GeneralCount = scrapy.Field()
    #差评
    PoorCount = scrapy.Field()
    #评论关键字
    keyword = scrapy.Field()
    #类别
    type = scrapy.Field()
    #品牌
    brand = scrapy.Field()
    #外观样式
    X_type = scrapy.Field()
    #商品型号
    X_name = scrapy.Field()
    #控制方式
    control=scrapy.Field()
    # 温控方式
    temp_con=scrapy.Field()
    # 适用人数
    people=scrapy.Field()
    # 特色功能
    function=scrapy.Field()
    #产品尺寸
    size=scrapy.Field()
    #开门方式
    open_type=scrapy.Field()
    #容量
    capacity=scrapy.Field()
    #颜色
    color=scrapy.Field()
    product_url=scrapy.Field()
    #来源
    source=scrapy.Field()

