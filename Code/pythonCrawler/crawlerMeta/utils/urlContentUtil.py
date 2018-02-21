import urllib.request,socket,re,sys,os
from pyutils.common.DateUtils import DateUtils
from pyutils.common.FtpUtils import FtpUtils
from crawlerMeta.utils.dbutil import DBUtil, ipDict, localIp
from meta.model.GrabStarPhoto import GrabStarPhoto
import requests
import time
url_separator = "/"
data_type_separator = "_"
data_type_1_star = "star"
data_type_1_meta = "meta"
data_type_2_clean = "clean"
data_type_2_grab = "grab"
#测试
ftpDict = {"ftpIp":"172.16.11.181",  "ftpUserName":"jhftpuser", "ftpPassWord": "jhftp0103"}
#正式
#ftpDict = {"ftpIp":"42.62.117.108",  "ftpUserName":"imageadvftp", "ftpPassWord": "BJTezhaWJyDq"}
#爱奇艺默认明星图片地址
iqiyi_default_star_photo = "http://www.qiyipic.com/common/fix/search_images/mx_default_195x260.jpg"
#豆瓣默认明星图片地址
douban_default_star_photo = "https://img3.doubanio.com/f/movie/63acc16ca6309ef191f0378faf793d1096a3e606/pics/movie/celebrity-default-large.png"

class UrlUtils:
    def getData(url) :
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
        }

        req = urllib.request.Request(url=url, headers=headers)

        res = urllib.request.urlopen(req)

        data = res.read();
        print(data);
        return data;

        # 根据图片外网地址获取要上传至FTP的地址
    def getRemoteFile(self, dataType, currentStamp, inforrationSources, headImgUrl):
        remoteFile = ""
        webFileUrl = headImgUrl
        if inforrationSources == 0:
            webFileUrl = headImgUrl.replace("s_ratio_celebrity", "l_ratio_celebrity")
        if dataType.split(data_type_separator)[0] == data_type_1_star and dataType.split(data_type_separator)[
            1] == data_type_2_grab:
            remoteFile = str(inforrationSources) + url_separator + str(ipDict[localIp]) + url_separator + data_type_1_star +  url_separator + str(
                currentStamp) + url_separator + DBUtil().find_last(webFileUrl, url_separator)
        elif dataType.split(data_type_separator)[0] == data_type_1_meta and dataType.split(data_type_separator)[
            1] == data_type_2_grab:
            remoteFile = str(inforrationSources) + url_separator + str(ipDict[localIp]) + url_separator + data_type_1_meta +  url_separator + str(
                currentStamp) + url_separator + DBUtil().find_last(webFileUrl, url_separator)
            #print("webFileUrl=", webFileUrl, "&remoteFile=", remoteFile)
        return remoteFile, webFileUrl


    #将外网图片上传至FTP并返回图片的高度和宽度
    def upLoadFtp(self, remoteFile, webFileUrl,inforrationSources):
        ftputil = FtpUtils()
        ftputil.connectFTP(ftpDict["ftpIp"], ftpDict["ftpUserName"], ftpDict["ftpPassWord"])
        if inforrationSources == 0 :
            # ipapi = requests.get(
            #     "http://dynamic.goubanjia.com/dynamic/get/d5d45bc51ed327b9ea1708aa20d3deb0.html?random=yes")
            # # print(ipapi)
            # ipapi.encoding = 'utf-8'
            # ipApiDataText = ipapi.text
            # ipApiData = ipApiDataText.strip("\n")
            # ipValue = "https://" + ipApiData
            # # 设置代理
            # if (ipapi):
            #     ipapi.close()
            # proxies = {
            #     "https": ipValue
            # }
           # ih, iw = ftputil.uploadWebImage(remoteFile, webFileUrl, referer = "https://www.douban.com/", proxies = proxies)
           ih, iw = ftputil.uploadWebImage(remoteFile, webFileUrl, referer="https://www.douban.com/")
        else:
            ih, iw = ftputil.uploadWebImage(remoteFile, webFileUrl)
        print(ih, "---", iw)
        return ih, iw


    def upLoadPhotoToFtp(self, starId, strGrabStarCode, inforrationSources, headImgUrl, cleanAfterId, upLoadCount, currentStamp, starIdList):
        try :
            if upLoadCount % 1000 == 0:
                currentStamp = DateUtils.getSysTimeSecond()
            # 明星_抓取
            dateType = data_type_1_star + data_type_separator + data_type_2_grab
            if (inforrationSources == 0 and headImgUrl and headImgUrl != douban_default_star_photo) or (inforrationSources == 2 and headImgUrl and headImgUrl != iqiyi_default_star_photo):
                remoteFile, webFileUrl = UrlUtils().getRemoteFile(dateType, currentStamp, inforrationSources, headImgUrl)
                photoHeight, photoWidth = UrlUtils().upLoadFtp(remoteFile, webFileUrl, inforrationSources)
                displayStatus = 1
                if (photoHeight != 0 and photoWidth != 0) :
                    upLoadCount += 1
                    GrabStarPhoto().saveGrabStarPhoto(starId, strGrabStarCode, inforrationSources, webFileUrl, photoHeight,
                                                      photoWidth, remoteFile, cleanAfterId, displayStatus)
                    starIdList.append(starId)

            else:
                remoteFile = ""
                webFileUrl = headImgUrl
                photoHeight, photoWidth = 0, 0
                displayStatus = 2
                GrabStarPhoto().saveGrabStarPhoto(starId, strGrabStarCode, inforrationSources, webFileUrl, photoHeight,
                                              photoWidth, remoteFile, cleanAfterId, displayStatus)
                starIdList.append(starId)
            if inforrationSources == 0:
                # time.sleep(1)
                pass
        except BaseException as e:
            print("e.message:", str(e), "上传来源" + str(inforrationSources) + " id为"+ str(starId) + "明星图片到FTP出现异常")
        return upLoadCount, currentStamp



