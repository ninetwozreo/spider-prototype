# --*-- coding: utf-8 --*--

import os
import json
import sys

from utils.log import NOTICE, log, ERROR, RECORD

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import time
import random
from config import CELERY_BROKER, CELERY_BACKEND, CRAWL_INTERVAL
from db_access import *
from utils.blacklist import blacklist_site, blacklist_company
from utils.content_process import complement_url, check_content
from utils.diff import diff_file
from utils.html_downloader import crawl
from bs4 import BeautifulSoup
from celery import Celery
# from multiprocessing import Pool, cpu_count

celery_app = Celery('info_engine', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

websites = get_websites();
train_nums = get_train_nums();
num_static1 = 1;
count_num_static1 = 5000;

#715 3880
# websites = get_websites_desc()

@celery_app.task
def extract(w_id):
    try:
        w = get_website(w_id)
        # log(NOTICE, "开始 #{id} {name} {site} ".format(id=w.id, name=w.company.name_cn, site=w.url))

        new_html_content = crawl(w.url)
        if not new_html_content:
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        if w.html_content:
            old_html_content = w.html_content.content
        else:
            save_html_content(w.id, new_html_content)
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        diff_text = diff_file(old_html_content, new_html_content)
        if not diff_text:
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        save_html_content(w.id, new_html_content)

        soup = BeautifulSoup(diff_text, 'lxml')
        items = soup.find_all('a')
        COUNT = 0
        if items:
            for a in items:
                if a.string:
                    url, text = a.get('href'), a.string
                    check_pass = check_content(url, text)
                    if check_pass:
                        url = complement_url(url, w.url)
                        if url:
                            result = save_info_feed(url, text, w.id, w.company.id)
                            if result:
                                COUNT += 1
                            # log(RECORD, "[name] [+] [{url}  {text}]".format(name=w.company.name_cn, url=url, text=text.strip()))
        if COUNT == 0:
            log(NOTICE, "#{id} {name} {site} 抓到更新 {count} 条".format(id=w.company.id, name=w.company.name_cn, site=w.url,
                                                                    count=COUNT))
        else:
            log(RECORD, "#{id} {name} {site} 抓到更新 {count} 条".format(id=w.company.id, name=w.company.name_cn, site=w.url,
                                                                    count=COUNT))

    except Exception as e:
        try:
            w = get_website(w_id)
            log(ERROR, "#{id} {name} {site} {err}".format(id=w.id, name=w.company.name_cn, site=w.url, err=str(e)))
        except Exception as e:
            log(ERROR, str(e))


def gen_info():
    # random.shuffle(websites)
    for w in websites[:]:
        if (w.url not in blacklist_site) and (w.company.name_cn not in blacklist_company):
            extract.delay(w.id)


# 刷新车站信息
def gen_station():
    text = crawl("https://www.12306.cn/index/script/core/common/station_name_v10037.js")
    count = 0
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
        # if(count>2868):
        #     print("""""")
        # id = int(text[0:text.find("@")])
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
            print(res["msg"])


# 刷新车次关系信息
def gen_station_num_relation():
    try:
        for train_num in train_nums[:]:
            url="https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no="
            url_parm_date="&leftTicketDTO.train_date="
            url_suffix="&rand_code="
            param_date=datetime.date.today()+ datetime.timedelta(days=1)
            text = crawl(url + train_num.train_no+url_parm_date+str(param_date)+url_suffix)
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
                        'station_no': relation['station_no']
                    }
                    res = create_train_relation_info(**relation_info)
                    print(res['msg'])
    except Exception as e:

        print(e)
        print("异常 已爬取到车次：" + str(train_num.train_code))
        time.sleep(60 * CRAWL_INTERVAL)

# 刷新车次信息
def gen_train_num(num_static, count_num_static):
    url = "https://search.12306.cn/search/v1/h5/search?callback=jQuery19108124885820364023_1567759292307&keyword="
    tran_num = "G"
    # tran_num = "K"
    global count_num_static1
    global num_static1
    num = num_static
    count_num = count_num_static

    while num < 9900:
        try:
            tran_num_u = tran_num + str(num)

            text = crawl(url + tran_num_u)

            if not text:
                count_num_static1 = count_num
                num_static1 = num
                print("中断 已爬取到车次：" + str(tran_num_u))
                print("数据主键已经到" + str(count_num))
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
                        print("已保存成功:" + str(count_num) + "条")
                        print(res['msg'])
                        count_num += 1
                    i += 1
            num += 1
        except Exception as e:
            count_num_static1 = count_num-1
            num_static1 = num
            print(e)
            print("异常 已爬取到车次：" + str(tran_num_u))
            print("数据主键已经到" + str(count_num))
            time.sleep(60 * CRAWL_INTERVAL)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
    #                     filename='new.log',
    #                     filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    #                     # a是追加模式，默认如果不写的话，就是追加模式
    #                     format=
    #                     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    #                     # 日志格式
    #                     )
    while True:
        # pool = Pool(processes=cpu_count())
        # pool.map(gen_train_num, num_static1)
        gen_train_num(num_static1, count_num_static1)
        # gen_station()
        # gen_station_num_relation()
        # gen_info()
        # time.sleep(60 * CRAWL_INTERVAL)
