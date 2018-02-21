# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabMediaInfo 媒资信息表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabMediaInfo(models.Model):

    # 媒资id
    mediaId = models.BigIntegerField(primary_key=True, db_column="MEDIA_ID", max_length=12)

    # 媒资数据源id
    mediaSourceCode = models.CharField(db_column="MEDIA_SOURCE_CODE", max_length=32)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 媒资数据源父id
    parentSourceCode = models.CharField(db_column="PARENT_SOURCE_CODE", max_length=32)

    # 媒资类型
    mediaType = models.CharField(db_column="MEDIA_TYPE", max_length=32)

    # 中文名
    cnName = models.CharField(db_column="CN_NAME", max_length=64)

    # 原名
    oldName = models.CharField(db_column="OLD_NAME", max_length=128)

    # 又名
    alternateName = models.CharField(db_column="ALTERNATE_NAME", max_length=256)

    # 发行年份
    mediaYear = models.IntegerField(db_column="MEDIA_YEAR", max_length=4)

    # 语言
    mediaLanguage = models.CharField(db_column="MEDIA_LANGUAGE", max_length=128)

    # 片长
    mediaTimes = models.IntegerField(db_column="MEDIA_TIMES", max_length=3)

    # 简介
    mediaIntro = models.CharField(db_column="MEDIA_INTRO", max_length=1024)

    # 影片类型
    subordinateType = models.CharField(db_column="SUBORDINATE_TYPE", max_length=128)

    # 制片国家/地区
    productionContry = models.CharField(db_column="PRODUCTION_CONTRY", max_length=128)

    # 总季数
    totalSeason = models.IntegerField(db_column="TOTAL_SEASON", max_length=2)

    # 当前季数
    currentSeason = models.IntegerField(db_column="CURRENT_SEASON", max_length=2)

    # 当前季的集数
    currentSeasonNumber = models.IntegerField(db_column="CURRENT_SEASON_NUMBER", max_length=3)

    # 海报url
    posterImgUrl = models.CharField(db_column="POSTER_IMG_URL", max_length=256)

    # 导演
    mediaDirector = models.CharField(db_column="MEDIA_DIRECTOR", max_length=256)

    # 演员
    mediaActor = models.CharField(db_column="MEDIA_ACTOR", max_length=256)

    # 标签
    mediaTag = models.CharField(db_column="MEDIA_TAG", max_length=256)

    # 上映时间
    releaseTime = models.CharField(db_column="RELEASE_TIME", max_length=256)

    # 拼音
    mediaPinyin = models.CharField(db_column="MEDIA_PINYIN", max_length=128)

    # 缩写
    mediaAbbreviation = models.CharField(db_column="MEDIA_ABBREVIATION", max_length=128)

    # 每集标题/本集看点
    episodeTitle = models.CharField(db_column="EPISODE_TITLE", max_length=512)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    #媒资页面code
    mediaWebCode = models.CharField(db_column="MEDIA_WEB_CODE", max_length=32)

    #协助媒资类型
    mediaAssistType = models.CharField(db_column="MEDIA_ASSIST_TYPE", max_length=32)

    #抓取页面URL
    grabWebUrl = models.CharField(db_column="GRAB_WEB_URL", max_length=256)
    #抓取页面URL
    cleanParentMediaId = models.CharField(db_column="CLEAN_PARENT_MEDIA_ID", max_length=256)

    class Meta:
        db_table = "GRAB_MEDIA_INFO"
