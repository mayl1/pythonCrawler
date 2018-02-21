# -*- coding:utf-8 -*-

from django.db import models

"""
    Class: GrabStarRelation 明星关系表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabStarRelation(models.Model):

    # 关系id
    relationId = models.BigIntegerField(primary_key=True, db_column="RELATION_ID", max_length=12)

    # 演员源id
    starSourceCode = models.CharField(db_column="STAR_SOURCE_CODE", max_length=32)

    # 关系
    starRelation = models.CharField(db_column="STAR_RELATION", max_length=24)

    # 关系人源id
    relationSourceCode = models.CharField(db_column="RELATION_SOURCE_CODE", max_length=32)

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

    #清洗后演员源id
    cleanStarSouceId = models.BigIntegerField(db_column="CLEAN_STAR_SOURCE_ID", max_length=12)

    #清洗后关系人源id
    cleanStarRalationId = models.BigIntegerField(db_column="CLEAN_STAR_RELATION_ID", max_length=12)

    class Meta:
        db_table = "GRAB_STAR_RELATION"
