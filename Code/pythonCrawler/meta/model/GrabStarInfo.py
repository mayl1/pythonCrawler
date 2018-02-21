# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabStarInfo 演职人员表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabStarInfo(models.Model):

    # 影人id
    starId = models.BigIntegerField(primary_key=True, db_column="STAR_ID", max_length=12)

    # 影人信息源id
    starSourceCode = models.CharField(db_column="STAR_SOURCE_CODE", max_length=32)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 中文名
    chName = models.CharField(db_column="CH_NAME", max_length=64)

    # 英文名
    enName = models.CharField(db_column="EN_NAME", max_length=64)

    # 别名
    anotherName = models.CharField(db_column="ANOTHER_NAME", max_length=256)

    # 性别
    starSex = models.IntegerField(db_column="STAR_SEX", max_length=2)

    # 出生日期
    birthDate = models.CharField(db_column="BIRTH_DATE", max_length=24)

    # 国籍
    starNationality = models.CharField(db_column="STAR_NATIONALITY", max_length=24)

    # 职业
    starKariera = models.CharField(db_column="STAR_KARIERA", max_length=64)

    # 星座
    starSign = models.CharField(db_column="STAR_SIGN", max_length=24)

    # 民族
    starNation = models.CharField(db_column="STAR_NATION", max_length=24)

    # 头像url
    headImgUrl = models.CharField(db_column="HEAD_IMG_URL", max_length=256)

    # 简介
    briefIntroduction = models.CharField(db_column="BRIEF_INTRODUCTION", max_length=2048)

    # 代表作品
    representativeWorks = models.CharField(db_column="REPRESENTATIVE_WORKS", max_length=2048)

    # ta的标签
    taLabel = models.CharField(db_column="TA_LABEL", max_length=256)

    # 身高
    starHeight = models.IntegerField(db_column="STAR_HEIGHT", max_length=3)

    # 体重
    starWeight = models.IntegerField(db_column="STAR_WEIGHT", max_length=3)

    # 肤色
    skinColour = models.CharField(db_column="SKIN_COLOUR", max_length=16)

    # 兴趣爱好
    hobbiesInterests = models.CharField(db_column="HOBBIES_INTERESTS", max_length=256)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    class Meta:
        db_table = "GRAB_STAR_INFO"
