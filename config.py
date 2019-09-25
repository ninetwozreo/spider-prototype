# --*-- coding: utf-8 --*--


# MYSQL配置
DB = {
    'HOST': '127.0.0.1',
    'PORT': 3306,
    'DB_NAME': 'db',
    # 'DB_NAME': '',
    'USER': 'root',
    'PASSWORD' : ''
}


# 异常休息时间(分钟)
CRAWL_INTERVAL = 0.5

# 车次主键
NUM_STATIC = 1

# 数据主键
COUNT_NUM_STATIC=1

# 车次头
TRAIN_NUM_HEAD='G'


# md5
MD5_SALT = "some random string"


# celery
CELERY_BROKER = 'redis://localhost:6379'
CELERY_BACKEND = 'redis://localhost:6379'


# 分页
ITEMS_NUM_PERPAGE = 50