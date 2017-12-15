import requests
import json

ProductID="1900415"
comment_web = "https://sclub.jd.com/comment/productPageComments.action?productId=" + str(ProductID) + "&score=0&sortType=5&page=0&pageSize=10"
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

print(keyword)
print(CommentCount)
print(GoodRateShow)

ProductID="1900415"
price_web = "https://p.3.cn/prices/mgets?pduid=1508741337887922929012&skuIds=J_" + str(ProductID)
print("价格：", price_web)
price_webs = requests.get(price_web, timeout=1000).text
price_json = json.loads(price_webs)[0]
PreferentialPrice = price_json['p']
price = price_json['m']
print(price,PreferentialPrice)