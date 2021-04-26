#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:xjl
# datetime:2019/12/30 19:39
# software: PyCharm
"""自己手动实现一个下载目标urld的自愿的代码
    1 找到目标的网址
    2 在本地新建文件夹
    3 保存到文件夹中
    存在的问题是下载下来的图片是打不开的什么原因
"""
import requests
import urllib
from urllib.request import urlretrieve
import re
import os
from bs4 import BeautifulSoup


#输出地址
outputdir = os.getcwd()+"/tdir/"
#目标url
turl = "https://www.kancloud.cn/zlt2000/microservices-platform/919412";
#拼接用
clear_url = "https://www.kancloud.cn/zlt2000/microservices-platform/";
 # 设置请求头，字典格式
form_header = {"cookie": "_ga=GA1.2.516440153.1614065539; _aihecong_chat_visitorId=603747d512b69258a2f15f90; PHPSESSID=0u7u9g2j4nlh24lfco7sdt1erc; __yjs_duid=1_95b542c333bb084f7843c4644658d9461617706833493; __cfduid=d19de4ceacf4acb3036d76b458ea51ad51618882593; _gid=GA1.2.2015901827.1619314659; remember_cc248a61b22205317666319f4fffa9146988fb4b=552879%7C64JQnT04udAN4Z9cLGTGEFByGBB656lm15E56SOkB97gtNMjMGbKqwNgEVBu; _aihecong_chat_visitorCookie=%7B%22last%22%3Afalse%2C%22visitormarkId%22%3A%226084c7ef97944538279e561a%22%2C%22visitorId%22%3A%22603747d512b69258a2f15f90%22%2C%22lastTime%22%3A1619331344715%7D; _aihecong_chat_visibility=false; _gat_web=1"}

file_content={}
link_list=[]
  # 保存url指定内容
def file_down(url,file_name,short_href):
     
    html = requests.get(url, headers=form_header).text  # 获取网页内容
    # 这里由于有些图片可能存在网址打不开的情况，加个5秒超时控制。
    # data-objurl="http://pic38.nipic.com/20140218/17995031_091821599000_2.jpg"获取这种类型链接
    # tsoup = BeautifulSoup(html, 'html.parser', from_encoding='utf8')

    # html= html.replace(short_href, short_href+'.html')

    file_content[file_name]=str(html)
    link_list.append(short_href)
    # with open(file_name, 'w',encoding='utf-8') as f:
    #     f.write(file_content[file_name])
    #     f.close()
   
 
# 下载list内容
def get_list(URL):
    html = requests.get(URL).text  # 获取网页内容   

    
    
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf8')
    # # ^abc.*?qwe$
    li_list = soup.find('div',class_='catalog').find_all('li')
    # # pic_url = re.findall('"https://cdn.pixabay.com/photo/""(.*?)",',html,re.S)
    
    for tab in li_list:
        short_href = tab.find('a').attrs['href']
        name = tab.find('a').text
        name=name.replace('/','-')
        file_down(clear_url+short_href,outputdir+name+".html",short_href)
        print(name)


 
 
# 下载目标 到本地
def downlocal():
    for k in file_content:
        with open(k, 'w',encoding='utf8') as f:
            f.write(file_content[k])
            f.close()
    # urlretrieve(IMAGE_URL, './image2.png')
 
 
# 处理list中的url
def handle_list():
    for k in file_content:
        cus=file_content[k]
        for num in link_list:
            cus=cus.replace(num,num+".html")
        file_content[k]=cus
 
# # 下载目标网站的资源
# def zip_down(url):
#     filename = "./tomcat.zip"
#     try:
#         urlretrieve(url, filename)
#     except urllib.ContentTooShortError:
#         print('Network conditions is not good.Reloading.')
#         zip_down(url, filename)
 
 
if __name__ == '__main__':
   
    get_list(turl)
    handle_list()
    downlocal()

    # file_down(turl,outputdir+"919412"+".html")
