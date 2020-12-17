# coding=utf-8

import xlwt
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
#输出地址
outputdir = os.getcwd()
#运行方法标志
sign = "pkulaw";
#中央chl或地方lar
stype = "lar";
# stype = "chl";
#关键字
keyword ="老旧小区";
#每页条
pagesize =100;

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
        a=one.find('a');
        oneData["title"] =a.text
        oneData["href"] =a.attrs.get('href')
        local_res.append(oneData)
    return local_res
# 获取网页信息
def get_pku_law():
    print(keyword)
    #创建excel文件
    execl = xlwt.Workbook()

    index_num=0
    url = "https://www.pkulaw.com"
    group_json_data={
        "library": stype,
        "className": "EffectivenessDic",
        # classCodeKeys: 
        # QueryBase64Request: eyJGaWVsZE5hbWUiOm51bGwsIlZhbHVlIjpudWxsLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjowLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoyLCJDaGlsZE5vZGVzIjpbeyJGaWVsZE5hbWUiOiJLZXl3b3JkU2VhcmNoVHJlZSIsIlZhbHVlIjpudWxsLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjowLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoxLCJDaGlsZE5vZGVzIjpbeyJGaWVsZE5hbWUiOiJEb2N1bWVudE5PIiwiVmFsdWUiOiLogIHml6flsI/ljLoiLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjoxLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoyLCJDaGlsZE5vZGVzIjpbXSwiQW5hbHl6ZXIiOiJpa19tYXhfd29yZCIsIkJvb3N0IjpudWxsLCJNaW5pbXVtX3Nob3VsZF9tYXRjaCI6bnVsbH0seyJGaWVsZE5hbWUiOiJUaXRsZSIsIlZhbHVlIjoi6ICB5pen5bCP5Yy6IiwiUnVsZVR5cGUiOjQsIk1hbnlWYWx1ZVNwbGl0IjoiXHUwMDAwIiwiV29yZE1hdGNoVHlwZSI6MSwiV29yZFJhdGUiOjAsIkNvbWJpbmF0aW9uVHlwZSI6MiwiQ2hpbGROb2RlcyI6W10sIkFuYWx5emVyIjoiaWtfbWF4X3dvcmQiLCJCb29zdCI6bnVsbCwiTWluaW11bV9zaG91bGRfbWF0Y2giOm51bGx9XSwiQW5hbHl6ZXIiOm51bGwsIkJvb3N0IjpudWxsLCJNaW5pbXVtX3Nob3VsZF9tYXRjaCI6bnVsbH1dLCJBbmFseXplciI6bnVsbCwiQm9vc3QiOm51bGwsIk1pbmltdW1fc2hvdWxkX21hdGNoIjpudWxsfQ==
        "keyword": keyword,
        # advDic: 
        # SearchInResult: 
        "ClassFlag": stype,
        "KeywordType": "DefaultSearch",
        "MatchType": "Exact"
    }
    chl_json_data={
        "Keywords":keyword,
        "PreviousLib": stype,
        "PreKeywords":keyword,
        "Library": stype,
        "RecordShowType": "List",
        "ClassFlag": stype,
        "PreviousLib": stype
    }
    
    rs_json_data={
        "Menu": "law",
        "RangeType": "Piece",
        "IsSynonymSearch": False,
        "LastLibForChangeColumn": stype,
        "IsAdv": False,
        "OrderByIndex":4,
        "RecordShowType": "List",
        "Keywords":keyword,
        #匹配方式
        "MatchType": "Exact",
        "Library": stype,
        "ClassFlag": stype,
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
    local_path="/law/chl"
    group_get_path="/Tool/SingleClassResult"
    record_path="/law/search/RecordSearch"
    res={}
    try:
        # main_page=requests.post(url+local_path,headers=header,data=datau)
        #map中key为代码，value为名字
        group_map=json.loads( crawl_law_post(url+group_get_path,group_json_data))
        # group_map={}
        # group_html=BeautifulSoup(data_hrml,'html.parser').find_all('div',class_='grouping-title')
        # #循环获取group 信息，包含名称和代号用于后续请求
        # for group in group_html:
        #     group_map[group.find('a').text]=group.find('a').attrs.get('groupvalue')
        
        for group in group_map:
            page_index=0
            cur_map=[]
            #获取每一项的篇数
            cur_size=int(re.sub( "\D" , "", group.get('value')))
            rs_json_data["GroupByIndex"]=page_index
            rs_json_data["Pager.PageIndex"]=page_index
            rs_json_data["ClassCodeKey"]=","+group.get('key')+",,,,"
            
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
            res[group.get('value')]=cur_map
        #处理获取到的数据到excel
        sheet = execl.add_sheet("测试表名",cell_overwrite_ok=True)

        for group_name in res: 
            sheet = execl.add_sheet(group_name,cell_overwrite_ok=True)

            sheet.write(1,0,group_name)
            i=1
            cur_data=res[group_name]
            for one in cur_data:
                sheet.write(i,0,one.get("title")) 
                i+=1
        # os.mknod("a.xlsx") 
        execl.save(outputdir+keyword)
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

