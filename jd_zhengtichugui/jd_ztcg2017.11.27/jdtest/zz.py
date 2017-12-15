from bs4 import BeautifulSoup

import requests
from  lxml.etree import HTML
import json
import re
# url="https://item.jd.com/5720885.html"
# urls=requests.get(url).text
# url=HTML(urls)
# guige1=url.xpath(".//div[@class='Ptable']/div[1]/dl/dd[@class=None]/text()")
# print(guige1)

url="https://item.jd.com/5720885.html"
# url="https://item.jd.com/4939815.html"
a=requests.get(url).text
s=BeautifulSoup(a,'lxml')
# print (a)
guige=s.find('div',class_='Ptable')
guige1=guige.find_all('div',class_='Ptable-item')
x={}
for gg in guige1:
    guige2=gg.find_all('dt',class_=None)
    guige3=gg.find_all('dd',class_=None)
    for i in range(len(guige2)):
        dt=re.findall(">(.*?)<",str(guige2[i]))
        dd=re.findall(">(.*?)<",str(guige3[i]))
        x.setdefault(dt[0],dd[0])
print(x)