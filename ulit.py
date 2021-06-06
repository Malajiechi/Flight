# coding: utf-8
import datetime
import pymysql


def con_db():
    return pymysql.connect(host='127.0.0.1', port=3306, db='flaskshoupiaosys', user='root', passwd='123456',
                           charset='utf8mb4')

def timesf(data):
    """
    格式化时间
    :param data:
    :return:
    """
    for i in data:
        for k, v in i.items():
            if isinstance(v, datetime.datetime):
                i[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, datetime.date):
                i[k] = v.strftime('%Y-%m-%d')