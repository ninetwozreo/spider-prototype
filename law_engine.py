# coding=utf-8

import os
import json
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



# 获取坐标信息
def get_pku_law():
    print(keyword)
    index_num=0
    url = "https://www.pkulaw.com"
    json_data={
        "Keywords":keyword,
        "PreviousLib": stype,
        "PreKeywords":keyword
    }
    datau="Menu=law&Keywords=old&PreKeywords="+keyword+"&SearchKeywordType=DefaultSearch&MatchType=Exact&RangeType=Piece&Library=chl&ClassFlag=chl&GroupLibraries=&QuerySearchCondition=DefaultSearch%2BExact%2BPiece%2B0&QueryOnClick=False&AfterSearch=True&RequestFrom=btnSearch&SearchInResult=&PreviousLib=chl&IsSynonymSearch=false&RecordShowType=List&ClassCodeKey=%2C%2C%2C%2C%2C&IsSearchErrorKeyword=&X-Requested-With=XMLHttpRequest"
    local_path="/law/chl"
    data={""}
    try:
        # main_page=requests.post(url+local_path,headers=header,data=datau)
        data_hrml=crawl_law_post(url+local_path,json_data)
        # main_page=crawl(url);
        for station in train_stations:
            text = crawl(url + station.name + '火车站')
            json_train_station_msg = json.loads(text)
            if (json_train_station_msg['detail'].__contains__('pois')):
                point = json_train_station_msg['detail']['pois'][0]
            else:
                train_stations = train_stations[index_num+1:len(train_stations)]
                continue
            if(index_num==42):
                print("")
            point_info = {
                'point_x': point['pointx'],
                'point_y': point['pointy'],
                'station_id': station.id,
                'station_name': station.name
            }
            res=create_point_msg_info(**point_info)
            index_num += 1
            print(index_num)
            if not res['success']:
                logger.warning(res['msg'])
            else:
                logger.critical('保存成功第' + str(res['point'].id) + '条')

    except Exception as e:
        train_stations = train_stations[index_num:len(train_stations)]
        logger.warning(e)
        logger.error("异常终止" + str(station.name))
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

