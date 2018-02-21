# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabMediaStarInfo 影片影人关联表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabMediaStarInfo(models.Model):

    # 关联id
    mediaStarId = models.BigIntegerField(primary_key=True, db_column="MEDIA_STAR_ID", max_length=12)

    # 媒资数据源id
    mediaSourceCode = models.CharField(db_column="MEDIA_SOURCE_CODE", max_length=32)

    # 影人信息源id
    starSourceCode = models.CharField(db_column="STAR_SOURCE_CODE", max_length=32)

    #角色名称
    roleName = models.CharField(db_column="ROLE_NAME", max_length=64)

    # 类型
    mediaStarType = models.IntegerField(db_column="MEDIA_STAR_TYPE", max_length=2)

    # 演员的角色名称
    roleName = models.CharField(db_column="ROLE_NAME", max_length=64)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    # 清洗后演员源id
    cleanStarSourceId = models.BigIntegerField(db_column="CLEAN_STAR_SOURCE_ID", max_length=12)

    # 清洗后媒资数据源id
    cleanMediaSourceId = models.BigIntegerField(db_column="CLEAN_MEDIA_SOURCE_ID", max_length=12)

    class Meta:
        db_table = "GRAB_MEDIA_STAR_INFO"
