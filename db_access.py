# --*-- coding: utf-8 --*--

import datetime
import hashlib
from sqlalchemy import desc
from config import MD5_SALT
from models import *


session = DBSession()

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)




def get_train_stations():
    train_stations = session.query(Station).all()
    return train_stations

def get_train_stations_n():
    train_stations = session.query(Station).filter_by(update_keep='NO').all()
    return train_stations

def get_train_nums():
    train_nums = session.query(TrainNum).all()
    return train_nums

#创建经纬度坐标点

def create_point_msg_info(**kwargs):

    try:
        res = {"success": False, "msg": "", 'point': None}
        point = session.query(Point).filter_by(point_x=kwargs["point_x"],point_y=kwargs["point_y"],).first()
        if point:
            res["msg"] = "关系已存在"
            return res
        session.add(
            Point( station_name=kwargs["station_name"],station_id=kwargs["station_id"],
                   point_x=kwargs["point_x"], point_y=kwargs["point_y"]))
        # session.commit()
        session.flush()
        point = session.query(Point).filter_by(point_x=kwargs["point_x"]).first()
        res["success"] = True
        res["point"] = point
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res
#创建车次与车站的关联关系'id': count_num,

def create_train_relation_info(**kwargs):

    try:
        res = {"success": False, "msg": "", 'station': None}
        trainNumStationRelation = session.query(TrainNumStationRelation).filter_by(train_no=kwargs["train_no"],station_name=kwargs["station_name"]).first()
        if trainNumStationRelation:
            res["msg"] = "关系已存在"
            return res
        session.add(
            TrainNumStationRelation( arrive_time=kwargs["arrive_time"],train_no=kwargs["train_no"],
                     train_code=kwargs["train_code"], running_time=kwargs["running_time"],
                      start_time=kwargs["start_time"], station_name=kwargs["station_name"],
                      arrive_day_diff=kwargs["arrive_day_diff"],station_no=kwargs["station_no"]))
        # session.commit()
        session.flush()
        trainNumStationRelation = session.query(TrainNumStationRelation).filter_by(train_code=kwargs["train_code"],station_name=kwargs["station_name"]).first()
        res["success"] = True
        res["trainNumStationRelation"] = trainNumStationRelation
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res
#更新车次'id': count_num,
def train_num_update(**kwargs):
        try:
            res = {"success": False, "msg": ""}
            trainNum = session.query(TrainNum).filter_by(id=kwargs["id"]).first()
            # profile = session.query(CompanyProfle).filter_by(company_id=kwargs["company_id"]).first()
            if kwargs["useful"] != trainNum.useful:
                trainNum.useful = kwargs["useful"]

            if kwargs["from_station"] != trainNum.from_station:
                trainNum.from_station = kwargs["from_station"]

            if kwargs["to_station"] != trainNum.to_station:
                trainNum.to_station = kwargs["to_station"]

            if kwargs["total_station_num"] != trainNum.total_station_num:
                trainNum.total_station_num = kwargs["total_station_num"]

            if kwargs["train_code"] != trainNum.train_code:
                trainNum.train_code = kwargs["train_code"]

            if kwargs["train_no"] != trainNum.train_no:
                trainNum.train_no = kwargs["train_no"]

            # session.commit()
            session.flush()
            res["success"] = True
            return res
        except Exception as e:
            # print(str(e))
            # session.rollback()
            res["msg"] = "更新出错"
            return res


#创建车次'id': count_num,

def create_train_num(**kwargs):
    try:
        res = {"success": False, "msg": "", 'station': None}
        trainNum = session.query(TrainNum).filter_by(train_code=kwargs["train_code"]).first()
        if trainNum:
            res["msg"] = "车次已存在"
            return res
        session.add(
            TrainNum(id=kwargs["id"], total_station_num=kwargs["total_station_num"],
                     train_code=kwargs["train_code"], train_no=kwargs["train_no"],
                     from_station=kwargs["from_station"], to_station=kwargs["to_station"],
                     useful=kwargs["useful"]))
        # session.commit()
        session.flush()
        trainNum = session.query(TrainNum).filter_by(train_code=kwargs["train_code"]).first()
        res["success"] = True
        res["trainNum"] = trainNum
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res
#创建车站
def create_station(**kwargs):
    try:
        res = {"success": False, "msg": "", 'station': None}
        station = session.query(Station).filter_by(big_abbr=kwargs["big_abbr"]).first()
        if station:
            res["msg"] = "车站已存在"
            return res
        session.add(Station( small_abbr=kwargs["small_abbr"], big_abbr=kwargs["big_abbr"], name=kwargs["name"], full_pinyin=kwargs["full_pinyin"]))
        # session.commit()
        session.flush()
        station = session.query(Station).filter_by(big_abbr=kwargs["big_abbr"]).first()
        res["success"] = True
        res["station"] = station
        return res
    except Exception as e:
        print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res

























def log2db(level, msg):
    try:
        session.add(CrawlerLOG(level=level, text=msg))
        session.flush()
    except:
        pass