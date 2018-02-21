# -*- coding:utf-8 -*-

from django.db import models
from crawlerMeta.utils.dbutil import DBUtil

"""
    Class: GrabStarPhoto 演员照片表

    version: 1.0.0

    Date: 2017-11-28

    author: mayongliang

"""
class GrabStarPhoto(models.Model):

    # 序列id
    photoId = models.BigIntegerField(primary_key=True, db_column="PHOTO_ID", max_length=12)

    # 演员源id
    starSourceCode = models.CharField(db_column="STAR_SOURCE_CODE", max_length=32)

    # 源照片url
    photoUrl = models.CharField(db_column="PHOTO_URL", max_length=256)

    # 照片Ftpurl
    posterFtpUrl = models.CharField(db_column="POSTER_FTP_URL", max_length=256)

    # 显示状态 0不显示 1显示
    displayStatus = models.IntegerField(db_column="DISPLAY_STATUS", max_length=2)

    # 信息来源
    informationSources = models.IntegerField(db_column="INFORMATION_SOURCES", max_length=2)

    # 图片宽度
    photoWidth = models.IntegerField(db_column="PHOTO_WIDTH", max_length=4)

    # 图片高度
    photoHeight = models.IntegerField(db_column="PHOTO_HEIGHT", max_length=4)

    # 是否清洗
    cleanStatus = models.IntegerField(db_column="CLEAN_STATUS", max_length=2)

    # 抓取时间
    grabTime = models.CharField(db_column="GRAB_TIME", max_length=24)

    # 清洗时间
    cleanTime = models.CharField(db_column="CLEAN_TIME", max_length=24)

    # 清洗后id
    cleanAfterId = models.BigIntegerField(db_column="CLEAN_AFTER_ID", max_length=12)

    class Meta:
        db_table = "GRAB_STAR_PHOTO"

    def saveGrabStarPhoto(self, starId, strGrabStarCode, inforrationSources, webFileUrl, photoHeight,
                                  photoWidth, remoteFile, cleanAfterId, displayStatus):
        grabStarPhoto = GrabStarPhoto()
        grabStarPhoto.photoId = starId
        grabStarPhoto.starSourceCode = strGrabStarCode
        grabStarPhoto.informationSources = inforrationSources
        grabStarPhoto.posterFtpUrl = remoteFile
        grabStarPhoto.photoUrl = webFileUrl
        grabStarPhoto.photoHeight = photoHeight
        grabStarPhoto.photoWidth = photoWidth
        grabStarPhoto.grabTime = DBUtil().systemDateTime()
        grabStarPhoto.cleanStatus = 0
        grabStarPhoto.cleanAfterId = cleanAfterId
        grabStarPhoto.displayStatus = displayStatus
        grabStarPhoto.save(using="grab")
