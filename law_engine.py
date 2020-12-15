# coding=utf-8

import os
import json
import re
import sys
import requests

from utils.log import NOTICE, log, ERROR, RECORD

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import time
import logging
from utils.parse_until import *
from config import CELERY_BROKER, CELERY_BACKEND, CRAWL_INTERVAL, NUM_STATIC, COUNT_NUM_STATIC, TRAIN_NUM_HEAD
from db_access import *

from utils.html_downloader import crawl, crawl_law_post
from bs4 import BeautifulSoup
from celery import Celery

# from multiprocessing import Pool, cpu_count

celery_app = Celery('law_engine', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

# websites = get_websites();
# train_nums = get_train_nums();
# train_stations = get_train_stations_n()
num_static1 = NUM_STATIC;
#运行方法标志
sign = "pkulaw";
#中央chl或地方lar
stype = "chl";
#关键字
keyword ="a";

#每页条
pagesize =10;

# -------日志-------------
logger = logging.getLogger()  # 不加名称设置root logger
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# 使用FileHandler输出到文件
fh = logging.FileHandler('log.out')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

# 使用StreamHandler输出到屏幕
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

# 添加两个Handler
logger.addHandler(ch)
logger.addHandler(fh)



# 获取到指定类别的所有信息
def get_useful_data(rc_data_html):
    local_res=[]
    datas=BeautifulSoup(rc_data_html,'html.parser').find_all('div',class_='block')
    for one in datas:
        oneData={}
        #在这里添加所需数据
        oneData["title"] =one.find('a').text

        local_res.append(oneData)
    return local_res
# 获取网页信息
def get_pku_law():
    print(keyword)
    index_num=0
    url = "https://www.pkulaw.com"
    chl_json_data={
        "Keywords":keyword,
        "PreviousLib": stype,
        "PreKeywords":keyword
    }
    rs_json_data={
        "Menu": "law",
        "RangeType": "Piece",
        "IsSynonymSearch": False,
        "LastLibForChangeColumn": "chl",
        "IsAdv": False,
        "OrderByIndex":4,
        "RecordShowType": "List",
        "Keywords":keyword,
        #匹配方式
        "MatchType": "Exact",
        "Library": "chl",
        "ClassFlag": "chl",
        "SearchKeywordType":"DefaultSearch",
        "PreviousLib": stype,
        "PreKeywords":keyword,
        "AfterSearch": True,
        "ClassCodeKey":"wq",
        "ShowType": "Default",
        "QueryOnClick": False,
        "Pager.PageIndex": 0,
        "GroupByIndex": 0,
        "OldPageIndex": 0,
        "Pager.PageSize": pagesize
    }
    datau="Menu=law&Keywords=old&PreKeywords="+keyword+"&SearchKeywordType=DefaultSearch&MatchType=Exact&RangeType=Piece&Library=chl&ClassFlag=chl&GroupLibraries=&QuerySearchCondition=DefaultSearch%2BExact%2BPiece%2B0&QueryOnClick=False&AfterSearch=True&RequestFrom=btnSearch&SearchInResult=&PreviousLib=chl&IsSynonymSearch=false&RecordShowType=List&ClassCodeKey=%2C%2C%2C%2C%2C&IsSearchErrorKeyword=&X-Requested-With=XMLHttpRequest"
    local_path="/law/chl"
    record_path="/law/search/RecordSearch"
    res={}
    try:
        # main_page=requests.post(url+local_path,headers=header,data=datau)
        data_hrml=crawl_law_post(url+local_path,chl_json_data)
        group_map={}
        group_html=BeautifulSoup(data_hrml,'html.parser').find_all('div',class_='grouping-title')
        #循环获取group 信息，包含名称和代号用于后续请求
        for group in group_html:
            group_map[group.find('a').text]=group.find('a').attrs.get('groupvalue')
        
        for name in group_map:
            page_index=0
            cur_map=[]
            #获取每一项的篇数
            cur_size=int(re.sub( "\D" , "", name))
            rs_json_data["GroupByIndex"]=page_index
            rs_json_data["Pager.PageIndex"]=page_index
            rs_json_data["ClassCodeKey"]=","+group_map[name]+",,,,"
            
            rc_data_html=crawl_law_post(url+record_path,rs_json_data)
            cur_map=get_useful_data(rc_data_html)
            cur_size-=pagesize
            #...
            while(cur_size>0):
                cur_size-=pagesize
                page_index+=1
                rs_json_data["GroupByIndex"]=page_index
                rs_json_data["Pager.PageIndex"]=page_index
                rc_data_html=crawl_law_post(url+record_path,rs_json_data)
                tem=get_useful_data(rc_data_html)
                cur_map+=tem
                # cur_map.extend(get_useful_data(rc_data_html))
            res[name]=cur_map
        # BeautifulSoup(data_hrml,'html.parser').find_all('div',class_='list-title');
        main_page=crawl(url);
    

    except Exception as e:
        # train_stations = train_stations[index_num:len(train_stations)]
        logger.warning(e)
        logger.error("异常终止" )
        # time.sleep(10 * CRAWL_INTERVAL)

# 刷新车站信息
# def gen_station():
#     text = crawl("https://www.12306.cn/index/script/core/common/station_name_v10037.js")
#     count = 0
#     global sign

#     while len(text) > 7:
#         # if count==0:
#         text = text[text.find("|") + 1:len(text)]

#         name = text[0:text.find("|")]
#         text = text[text.find("|") + 1:len(text)]

#         big_abbr = text[0:text.find("|")]
#         text = text[text.find("|") + 1:len(text)]

#         full_pinyin = text[0:text.find("|")]
#         text = text[text.find("|") + 1:len(text)]

#         small_abbr = text[0:text.find("|")]
#         text = text[text.find("|") + 1:len(text)]

#         station_info = {
#             'id': count,
#             'big_abbr': big_abbr,
#             'full_pinyin': full_pinyin,
#             'small_abbr': small_abbr,
#             'name': name
#         }
#         count += 1
#         res = create_station(**station_info)
#         if (not res["success"]):
#             logger.warning(res["msg"])
#         else:
#             logger.info(res["station"].name)
#         if (len(text) <=7):
#             sign='train_num'



if __name__ == '__main__':
    # while True:
        # if(sign=="train_num"):
        #     gen_train_num(num_static1, count_num_static1)
        # if(sign=="station"):
        #     gen_station()
        # if(sign=="station_num_relation"):
        #     gen_station_num_relation()
    if (sign == "pkulaw"):
        get_pku_law()

