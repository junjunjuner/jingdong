import sys
import urllib
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver

# #整体橱柜
# url = 'https://search.jd.com/Search?keyword=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&enc=utf-8&wq=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&pvid=a7933b8c1eb341849cebc6e466f1bd74'
# # url="https://list.jd.com/list.html?cat=737,738,747"   #取暖器
# driver = webdriver.Chrome('/home/260199/chrome/chromedriver') # 创建一个driver用于打开网页，记得找到brew安装的chromedriver的位置，在创建driver的时候指定这个位置
# driver.get(url) # 打开网页

# # 搜索
# driver.find_element_by_id("kw").send_keys("selenium")
# driver.find_element_by_id("su").click()
# time.sleep(3)
def get_url(url):
    # 将页面滚动条拖到底部
    js = "var q=document.documentElement.scrollTop=10000"
    driver.execute_script(js)
    time.sleep(3)

    # 搜索
    soup = BeautifulSoup(driver.page_source, 'lxml')
    productid_info=soup.find_all('li',class_='gl-item')
    print(len(productid_info))
    if len(productid_info)==30:
        print("未翻页")
        js = "var q=document.documentElement.scrollTop=10000"
        driver.execute_script(js)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        productid_info = soup.find_all('li', class_='gl-item')
        print(len(productid_info))

    for pro in productid_info:
        productid=re.findall('data-sku=\"(.*?)\"',str(pro))[0]
        price=re.findall('<em>￥</em><i>(.*?)</i>',str(pro))[0]
        # print(productid,price)
    # productid_list=driver.find_elements_by_class_name("gl-item")
    # print(len(productid_list))
    # for p in productid_list:
        # print(p.find_elements_by_xpath('//@sku-id'))
        # print(len(p.text))
    # driver.find_element_by_id("su").click()
    time.sleep(3)
    next_page = driver.find_element_by_xpath(".//div[@class='page clearfix']/div/span[@class='p-num']/a[@class='pn-next']").click()
    try:
        get_url(next_page)
        time.sleep(2)
    except:
        driver.quit()

#整体橱柜
url = 'https://search.jd.com/Search?keyword=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&enc=utf-8&wq=%E6%95%B4%E4%BD%93%E6%A9%B1%E6%9F%9C&pvid=a7933b8c1eb341849cebc6e466f1bd74'
driver = webdriver.Chrome('/home/260199/chrome/chromedriver') # 创建一个driver用于打开网页，记得找到brew安装的chromedriver的位置，在创建driver的时候指定这个位置
driver.get(url) # 打开网页
get_url(url)
# next_page=driver.find_element_by_xpath(".//div[@class='page clearfix']/div/span[@class='p-num']/a[@class='pn-next']").click()
# driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click() # selenium的xpath用法，找到包含“下一页”的a标签去点击
# # 将滚动条移动到页面的顶部
# js = "var q=document.documentElement.scrollTop=0"
# driver.execute_script(js)
# time.sleep(3)

# name_counter = 1
# page = 0;
# while page < 50: # 共50页，这里是手工指定的
# soup = BeautifulSoup(driver.page_source, "html.parser")
# current_names = soup.select('div.ranking-table') # 选择器用ranking-table css class，可以取出包含本周、上周的两个table的div标签
# for current_name_list in current_names:
# # print current_name_list['data-cat']
# if current_name_list['data-cat'] == 'thisWeek': # 这次我只想抓取本周，如果想抓上周，改一下这里为lastWeek即可
# names = current_name_list.select('td.star-name > a') # beautifulsoup选择器语法
# counter = 0;
# for star_name in names:
# counter = counter + 1;
# print star_name.text # 明星的名字是a标签里面的文本，虽然a标签下面除了文本还有一个与文本同级别的img标签，但是.text输出的只是文本而已
# name_counter = name_counter + 1;
# driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click() # selenium的xpath用法，找到包含“下一页”的a标签去点击
# page = page + 1
# time.sleep(2) # 睡2秒让网页加载完再去读它的html代码
#
# print name_counter # 共爬取得明星的名字数量
# driver.quit()