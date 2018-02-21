# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabStarDynamic 演员动态信息表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabStarDynamic(models.Model):

    # 影人id
    starId = models.BigIntegerField(primary_key=True, db_column="STAR_ID", max_length=12)

    # 影人源id
    starSourceCode = models.CharField(db_column="STAR_SOURCE_CODE", max_length=32)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 曾获奖项
    receivedAwards = models.CharField(db_column="RECEIVED_AWARDS", max_length=2048)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    class Meta:
        db_table = "GRAB_STAR_DYNAMIC"
