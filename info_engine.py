# --*-- coding: utf-8 --*--

import os
import json
import sys

from utils.log import NOTICE, log, ERROR, RECORD

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import time
import logging
from utils.parse_until import *
from config import CELERY_BROKER, CELERY_BACKEND, CRAWL_INTERVAL, NUM_STATIC, COUNT_NUM_STATIC, TRAIN_NUM_HEAD
from db_access import *

from utils.html_downloader import crawl
from bs4 import BeautifulSoup
from celery import Celery

# from multiprocessing import Pool, cpu_count

celery_app = Celery('info_engine', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

# websites = get_websites();
train_nums = get_train_nums();
train_stations = get_train_stations_n()
num_static1 = NUM_STATIC;
#运行方法标志
sign = "station";
count_num_static1 = COUNT_NUM_STATIC;

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
# logger.addHandler(fh)


# --------------------
# 715 3880
# websites = get_websites_desc()






# 获取坐标信息
def get_points():

    index_num=0
    global train_stations
    url = "https://apis.map.qq.com/jsapi?qt=poi&wd="
    try:
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
        logger.warning("异常 已爬取到车站：" + str(station.name))
        time.sleep(10 * CRAWL_INTERVAL)

# 刷新车站信息
def gen_station():
    text = crawl("https://www.12306.cn/index/script/core/common/station_name_v10037.js")
    count = 0
    global sign
    if (len(text) <=7):
        sign='train_num'
    while len(text) > 7:
        # if count==0:
        text = text[text.find("|") + 1:len(text)]

        name = text[0:text.find("|")]
        text = text[text.find("|") + 1:len(text)]

        big_abbr = text[0:text.find("|")]
        text = text[text.find("|") + 1:len(text)]

        full_pinyin = text[0:text.find("|")]
        text = text[text.find("|") + 1:len(text)]

        small_abbr = text[0:text.find("|")]
        text = text[text.find("|") + 1:len(text)]

        station_info = {
            'id': count,
            'big_abbr': big_abbr,
            'full_pinyin': full_pinyin,
            'small_abbr': small_abbr,
            'name': name
        }
        count += 1
        res = create_station(**station_info)
        if (not res["success"]):
            logger.warning(res["msg"])
        else:
            logger.info(res["station"].name)

# 刷新车次关系信息
def gen_station_num_relation():
    index_num = 0
    global train_nums
    global sign
    try:
        if(len(train_nums)<=0):
            sign="points"
        for train_num in train_nums[:]:
            url = "https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no="
            url_parm_date = "&leftTicketDTO.train_date="
            url_suffix = "&rand_code="
            param_date = datetime.date.today() + datetime.timedelta(days=3)
            text = crawl(url + train_num.train_no + url_parm_date + str(param_date) + url_suffix)
            # if (train_num.train_no == '0300000K4009'):
            json_train_msg = json.loads(text)
            if ((json_train_msg['data']['data'] is not None)):
                for relation in json_train_msg['data']['data']:
                    relation_info = {
                        'arrive_time': relation['arrive_time'],
                        'train_code': relation['station_train_code'],
                        'running_time': relation['running_time'],
                        'start_time': relation['start_time'],
                        'station_name': relation['station_name'],
                        'arrive_day_diff': relation['arrive_day_diff'],
                        'station_no': relation['station_no'],
                        'train_no': train_num.train_no
                    }
                    res = create_train_relation_info(**relation_info)
                    logger.info('this is info message')
                    if not res['success']:
                        logger.warning(res['msg'])
                    else:
                        logger.critical('保存成功第' + str(res['trainNumStationRelation'].id) + '条' + str(index_num))
            else:
                train_num.useful = 'F'
                res = train_num_update(**to_dict(train_num))
                if (res['success']):
                    logger.critical('已更新状态' + str(train_num.train_code))

            index_num += 1
    except Exception as e:
        train_nums = train_nums[index_num:len(train_nums)]
        logger.warning(e)
        logger.warning("异常 已爬取到车次：" + str(train_num.train_code))
        time.sleep(10 * CRAWL_INTERVAL)


# 刷新车次信息
def gen_train_num(num_static, count_num_static):
    url = "https://search.12306.cn/search/v1/h5/search?callback=jQuery19108124885820364023_1567759292307&keyword="
    tran_num = TRAIN_NUM_HEAD
    # tran_num = "K"
    global sign
    global count_num_static1
    global num_static1
    num = num_static
    count_num = count_num_static
    if (num >=10000):
        sign="station_num_relation"
    while num < 10000:
        try:
            tran_num_u = tran_num + str(num)

            text = crawl(url + tran_num_u)

            if not text:
                count_num_static1 = count_num
                num_static1 = num
                logger.info("中断 已爬取到车次：" + str(tran_num_u) + "数据主键已经到" + str(count_num))
                break
            # text = crawl("https://search.12306.cn/search/v1/h5/search?callback=jQuery110201481886827579022_1567752183819&keyword=" + tran_num_u + "&suorce=&action=&_=1567752183845")
            json_train = json.loads(text[text.find("(") + 1:text.find(")")])
            # print(json_train)

            i = 0
            if ((json_train['data'] is not None)):
                while (json_train['data'] is not None) & (i < len(json_train['data'])):
                    if json_train['data'][i]['params']['station_train_code'] == tran_num_u:
                        info = json_train['data'][i]['params']
                        tran_num_info = {
                            'id': count_num,
                            'total_station_num': info['total_num'],
                            'useful': 'T',
                            'train_no': info['train_no'],
                            'train_code': info['station_train_code'],
                            'from_station': info['from_station'],
                            'to_station': info['to_station']
                        }
                        res = create_train_num(**tran_num_info)
                        logger.critical("已保存成功:" + str(count_num) + "条" + res['msg'])
                        count_num += 1
                    i += 1
            num += 1
        except Exception as e:
            count_num_static1 = count_num - 1
            num_static1 = num
            logger.warning(e)
            logger.warning("异常 已爬取到车次：" + str(tran_num_u) + "数据主键已经到" + str(count_num))
            time.sleep(60 * CRAWL_INTERVAL)



if __name__ == '__main__':
    while True:
        if(sign=="train_num"):
            gen_train_num(num_static1, count_num_static1)
        if(sign=="station"):
            gen_station()
        if(sign=="station_num_relation"):
            gen_station_num_relation()
        if (sign == "points"):
            get_points()

