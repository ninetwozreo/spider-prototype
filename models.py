# --*-- coding: utf-8 --*--
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from config import DB
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Sequence
from sqlalchemy import func
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8'.format(
    USERNAME=DB['USER'],
    PASSWORD=DB['PASSWORD'],
    HOST=DB['HOST'],
    PORT=DB['PORT'],
    DB_NAME=DB['DB_NAME'],
), convert_unicode=True, echo=False)

DBSession = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = DBSession.query_property()

Base = declarative_base()


def init_db(db_engine):
    Base.metadata.create_all(bind=db_engine)
    # Base.metadata.tables["log"].create(bind=db_engine)


# 火车车次车站关联关系

class TrainNumStationRelation(Base):
    """
    id 到达时间 车次名 真车次名 运行时间  开车时间 站中文名 是否是第二天（0，1） 该车次的第几站 车次主键 车站主键
    """

    __tablename__ = 'train_num_station_relation'
    id = Column(Integer, primary_key=True)
    arrive_time = Column(String(32))
    train_code = Column(String(64))
    train_no = Column(String(64))
    running_time = Column(String(5))
    start_time = Column(String(5))
    station_name=Column(String(64))
    arrive_day_diff=Column(String(64))
    station_no=Column(Integer)
    train_id=Column(Integer)
    station_id=Column(Integer)

# 经纬度 坐标信息
class Point(Base):
    """
        id X坐标 Y坐标 对应站id  站名
        """

    __tablename__ = 'point_msg'
    id = Column(Integer, primary_key=True)
    point_x = Column(String(64))
    point_y = Column(String(64))
    station_id = Column(Integer)
    station_name = Column(String(64))
# 火车车次
class TrainNum(Base):
    """
    id 车次名 是否在用 站数  保留字段 起始站 终点站
    """


    __tablename__ = 'train_num'
    id = Column(Integer, primary_key=True)
    train_code = Column(String(256))
    total_station_num = Column(Integer)
    useful = Column(String(5))
    train_no=Column(String(64))
    from_station=Column(String(64))
    to_station=Column(String(64))
    station_type=Column(String(4))

    # full_pinyin = Column(String(256))


# 火车站
class Station(Base):
    """
    id 小写缩写 大写缩写 中文名 全拼 保留筛选字段
    """

    __tablename__ = 'train_station'
    id = Column(Integer, primary_key=True)
    small_abbr = Column(String(1024))
    big_abbr = Column(Text)
    name = Column(String(256))
    full_pinyin = Column(String(256))
    update_keep=Column(String(256))

class CrawlerLOG(Base):
    __tablename__ = 'log'
    id = Column(Integer, Sequence('log_id_seq'), primary_key=True)
    level = Column(Integer)
    text = Column(Text)
    create_at = Column(DateTime(timezone=True), default=func.now())


if __name__ == '__main__':
    init_db(engine)
    # pass
