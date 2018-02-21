# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabMediaDynamic 影片动态信息表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabMediaDynamic(models.Model):

    # 影片id
    mediaId = models.BigIntegerField(primary_key=True, db_column="MEDIA_ID", max_length=12)

    # 媒资数据源id
    mediaSourceCode = models.CharField(db_column="MEDIA_SOURCE_CODE", max_length=32)

    # 评分
    mediaScore = models.FloatField(db_column="MEDIA_SCORE")
    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 曾获奖项
    receivedAwards = models.CharField(db_column="RECEIVED_AWARDS", max_length=1024)

    # 票房
    mediaMoney = models.CharField(db_column="MEDIA_MONEY", max_length=32)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 最后更新时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    class Meta:
        db_table = "GRAB_MEDIA_DYNAMIC"
