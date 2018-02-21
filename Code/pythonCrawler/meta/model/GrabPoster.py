# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabPoster 影片海报表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabPoster(models.Model):

    # 序列id
    posterId = models.BigIntegerField(primary_key=True, db_column="POSTER_ID", max_length=12)

    # 影片源id
    mediaSourceCode = models.CharField(db_column="MEDIA_SOURCE_CODE", max_length=32)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 海报url
    posterUrl = models.CharField(db_column="POSTER_URL", max_length=256)

    # 海报FTP
    posterFtpUrl = models.CharField(db_column="POSTER_FTP_URL", max_length=256)

    # 图片宽度
    posterWidth = models.IntegerField(db_column="POSTER_WIDTH", max_length=4)

    # 图片高度
    posterHeight = models.IntegerField(db_column="POSTER_HEIGHT", max_length=4)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    # 显示状态
    displayStatus = models.BigIntegerField(db_column="DISPLAY_STATUS", max_length=2)

    class Meta:
        db_table = "GRAB_POSTER"
