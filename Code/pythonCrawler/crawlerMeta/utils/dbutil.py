# -*- coding:utf-8 -*-
from django.db import connections, transaction
import socket


#poolMeta = PooledDB(pymysql, 5, host='124.127.46.36', user='cibn_write', passwd='bQ^PFJWnc^I=^9UQ',db='cibn_meta', port=3306, charset="utf8")
#pool = PooledDB(pymysql, 5, host='124.127.46.36', user='cibn_write', passwd='bQ^PFJWnc^I=^9UQ',db='cibn_meta', port=3306, charset="utf8")
#poolOms = PooledDB(pymysql, 5, host='124.127.46.36', user='cibn_write', passwd='bQ^PFJWnc^I=^9UQ',db='cibn_meta', port=3306, charset="utf8")
#poolBehavior = PooledDB(pymysql, 5, host='124.127.46.36', user='cibn_write', passwd='bQ^PFJWnc^I=^9UQ',db='cibn_meta', port=3306, charset="utf8")
award_separator_1 = ":"
award_separator_2 = "/"
award_separator_3 = ","
award_separator_4 = ";"
award_result_separator_left = "("
award_result_separator_right = ")"
#更新查出无数据时睡眠时间（单位：秒）
sleepTimeLength = 2 * 60 * 60
class DBUtil:

    #实例方法，类内部定义的没有装饰器且第一个参数为self的函数
    def createPK(self, tablename):
        cursor = connections['grab'].cursor()
        cursor.execute("SELECT getPKID('{0}') AS PKVALUE".format(tablename))
        row = cursor.fetchone()
        return row[0]

    def createPKByStep(self, tablename, pkstep):
        cursor = connections['grab'].cursor()
        cursor.execute("SELECT getPKIDByStep('{0}', {1}) AS PKVALUE".format(tablename, pkstep))
        row = cursor.fetchone()
        return row[0]

    def systemDateTime(self):
        cursor = connections['grab'].cursor()
        cursor.execute("SELECT date_format(sysdate(), '%Y-%m-%d %H:%I:%S') AS curDate")
        row = cursor.fetchone()
        #print("当前时间：" + row[0])
        return row[0]

    def isBlank(self, param):
        if (param == None or len(param) == 0):
            return  True
        return False

    #获取本机ip
    def getLocalIp(self):
        # 获取本机电脑名
        myname = socket.getfqdn(socket.gethostname())
        # 获取本机ip
        myaddr = socket.gethostbyname(myname)
        return myaddr

    def getLinuxIp(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('www.baidu.com', 0))
            ip = s.getsockname()[0]
        except:
            ip = "x.x.x.x"
        finally:
            s.close()
        return ip

    #获取subStr在str中最后一次出现的index之后的字符串
    def find_last(self, str, subStr):
        last_position = -1
        while True:
            position = str.find(subStr, last_position + 1)
            if position == -1:
                return str[last_position + 1:]
            last_position = position

localIp = DBUtil().getLocalIp()
ipDict = {"10.168.60.122" : 0, "10.168.60.91" : 1, "10.168.60.81" : 2}

# localIp = DBUtil().getLinuxIp()
# ipDict = {"42.62.117.117" : 0, "42.62.117.118" : 1, "42.62.117.119" : 2}




