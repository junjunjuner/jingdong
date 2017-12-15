import pandas as pd

df = pd.read_csv("jdtest_柜式items_2017-11-09 15:06:14.csv", encoding='utf-8')
df1=df.set_index('ProductID')
df2=pd.read_csv("jdtest_capacity_2017-11-14 08:58:55.csv", encoding='utf-8')
df3=df2.set_index('ProductID')
df1['capacity']=df3['capacity']
df1.to_csv('new.csv',encoding='utf-8')





FIELDS_TO_EXPORT = [
    'p_Name',
    'shop_name',
    'ProductID',
    'price',
    'PreferentialPrice',
    'CommentCount',
    'GoodRateShow',
    'GoodCount',
    'GeneralCount',
    'PoorCount',
    'keyword',
    'type',         #核心参数
    'brand',        #品牌
    'X_name',       #型号
    'control',      #控制方式
    'X_type',       #外观样式
    'capacity',     #容量
    'temp_con',     #温控方式
    'people',       #适用人数
    'function',     #特色功能
    'color',        #颜色
    'size',         #产品尺寸
    'open_type',    #开门方式
    'source'
]