import requests
import time
from bs4 import BeautifulSoup
from django.db import connections
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict,sleepTimeLength,award_separator_1, award_separator_2,award_separator_3, award_separator_4
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils
from meta.model.GrabStarInfo import GrabStarInfo
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
from meta.model.GrabStarDynamic import GrabStarDynamic
from meta.analysis.doubanAnalysis import DoubanAnalysis
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_star, data_type_2_grab, douban_default_star_photo
from pyutils.common.DateUtils import DateUtils
import datetime

class DoubanStar :
    # 搜索索引初始
    search_start = 0
    # 按演职人员id访问api地址
    star_url = "https://api.douban.com/v2/movie/celebrity/starId?apikey=0fbfdca9eedf20c82f3f95fdcc9d6258"
    # 搜索索引初始
    star_start = 0
    #按演职人员id访问html地址
    star_html_url = "https://movie.douban.com/celebrity/starId/"
    #演员和作品关系地址
    media_star_url = 'https://movie.douban.com/celebrity/starId/movies?start=page&format=pic&sortby=time&'
    media_star_url_no = 'https://movie.douban.com/celebrity/starId/movies?start=0&format=pic&sortby=time&'
    # 演员奖项地址
    prize_star_url = 'https://movie.douban.com/celebrity/starId/awards/'
    #访问时间设置
    lengthAccess = 1
    htmlLengthAccess = 0.5

# 取得演职人员json数据
    def queryListStar(self):
        while True:
            #查询数据空最大演职人员id
            try:
                grabStar = GrabStarInfo.objects.using("grab").values("starSourceCode").extra(select={"starSourceCodeInt": "CAST(STAR_SOURCE_CODE AS UNSIGNED)"}).filter(informationSources=0).order_by('-starSourceCodeInt')[0]
                #判断是否查出数据
                if not grabStar :
                    #没有数据从0开始循环自增id 访问api
                    for i in range(9999999):
                        lastEndId = int(i)
                        #访问自增的id地址
                        listUrl = self.star_url.replace('starId', str(lastEndId))
                        # 设置接口访问时间为1s
                        time.sleep(self.lengthAccess)
                        print("自增-访问地址" + str(listUrl))
                        response = requests.get(listUrl)
                        code = response.status_code
                        print("自增-状态码"+str(code))
                        #通过返回状态码判断是否读取页面数据
                        if (code != 200):
                            pass
                        else:
                            # 获取访问的json格式内容
                            soup = BeautifulSoup(response.text)
                            # 解析演职人员详情页的内容
                            DoubanAnalysis().queryItemStar(soup)
                else :
                    #解析数据库返回数据解析最大id
                    lastStarId = grabStar["starSourceCode"]
                    countNo = 0
                    #按照最大id循环访问api
                    for i in range(9999999):
                        #最大值加循环次数访问地址api
                        lastEndId = int(lastStarId)+i
                        if HttpCrawlerUtils().isLocal(int(lastEndId)):
                            listUrl = self.star_url.replace('starId', str(lastEndId))
                            #设置接口访问时间为1s
                            time.sleep(self.lengthAccess)
                            print("数据库-访问地址" + str(listUrl))
                            response = requests.get(listUrl)
                            code = response.status_code
                            print("数据库-状态码" + str(code))
                            if (code != 200):
                                pass
                                countNo += 1
                                if (countNo > 10000):
                                    time.sleep(7200)
                                    break
                            else:
                                #获取访问的json格式内容
                                soup = BeautifulSoup(response.text, "html.parser")
                                #print(soup)
                                #解析演职人员详情页的内容
                                DoubanAnalysis().queryItemStar(soup)
            except BaseException as e:
                print("e.message:", str(e))
                raise

    # 补充演职人员信息
    def updateStar(self):
        #查询抓取演职人员表
        while True:
            try:
                cursor = connections["grab"].cursor()
                cursor.execute("SELECT STAR_SOURCE_CODE FROM GRAB_STAR_INFO WHERE CLEAN_STATUS != 2 AND INFORMATION_SOURCES = 0  AND mod(CAST(STAR_SOURCE_CODE AS UNSIGNED), %d) = %d ORDER BY (CAST(STAR_SOURCE_CODE AS UNSIGNED)) DESC  LIMIT 10" % (len(ipDict), ipDict[localIp]))
                resultTuple = cursor.fetchall()
                cursor.close()
                if resultTuple:
                    for id in resultTuple:
                        strgrabStarId = id[0]
                        print(strgrabStarId, type(strgrabStarId))
                        htmlUrl = self.star_html_url.replace('starId', str(strgrabStarId))
                        DoubanAnalysis().analyzeStarHtml(HttpCrawlerUtils().queryStarHtmldl(htmlUrl), strgrabStarId)
                        # print("暂停" + str(self.htmlLengthAccess)+ "秒 ")
                        time.sleep(self.htmlLengthAccess)
                    print("重新调用")
                else:
                    time.sleep(sleepTimeLength)
            except BaseException as e:
                print("e.message:", str(e))

    # 演职人员和作品关系信息
    def updateMediaStar(self):
        # 查询抓取演职人员表
        while True:
            try:
                grabStar = GrabMediaStarInfo.objects.using("grab").values("starSourceCode").extra(select={"starSourceCodeInt": "CAST(STAR_SOURCE_CODE AS UNSIGNED)"}).filter(informationSources=0).order_by('-starSourceCodeInt')[0]
                print(grabStar)
                lastStarId = grabStar["starSourceCode"]
                strgrabStarId = int(lastStarId) + 1
                for i in range(9999999):
                    # 最大值加循环次数访问地址
                    try:
                        if HttpCrawlerUtils().isLocal(int(str(strgrabStarId))):
                            htmlUrl = self.media_star_url_no.replace('starId', str(strgrabStarId))
                            htmlUrlList = self.media_star_url.replace('starId', str(strgrabStarId))
                            print(htmlUrl)
                            no = DoubanAnalysis().queryNo(HttpCrawlerUtils().queryStarHtmldl(htmlUrl))
                            if (int(no) % 10 == 0):
                                pageNo = int(no) // 10
                            else:
                                pageNo = int(no) // 10 + 1
                            # 循环翻页
                            for i in range(pageNo):
                                mediaStarUrl = htmlUrlList.replace('page', str(i * 10))
                                print(mediaStarUrl)
                                DoubanAnalysis().analyzeMediaStarHtml(HttpCrawlerUtils().queryStarHtmldl(mediaStarUrl), strgrabStarId)
                        strgrabStarId += 1
                    except BaseException as e:
                        print("e.message:", str(e))
            except BaseException as e:
                print("e.message:", str(e))

    # 演职人员获奖信息
    def updateStarPrize(self):
        while True:
            # 查询抓取演职人员表
            try:
                grabStar = GrabStarDynamic.objects.using("grab").values("starSourceCode").extra(select={"starSourceCodeInt": "CAST(STAR_SOURCE_CODE AS UNSIGNED)"}).filter(informationSources=0).order_by('-starSourceCodeInt')[0]
                print(grabStar)
                lastStarId = grabStar["starSourceCode"]
                strgrabStarId = int(lastStarId) + 1
                for i in range(9999999):
                    # 最大值加循环次数访问地址
                    try:
                        if HttpCrawlerUtils().isLocal(int(str(strgrabStarId))):
                            htmlUrlList = self.prize_star_url.replace('starId', str(strgrabStarId))
                            mediaStarUrl = htmlUrlList.replace('page', str(i * 10))
                            print(mediaStarUrl)
                            DoubanAnalysis().analyzeStarPrizeHtml(HttpCrawlerUtils().queryStarHtmldl(mediaStarUrl),strgrabStarId)
                        strgrabStarId += 1
                    except BaseException as e:
                        print("e.message:", str(e))
            except BaseException as e:
                print("e.message:", str(e))

    #抓取明星图片数据
    def grabStarPhoto(self):
        upLoadCount = 0
        # 当前时间戳秒
        currentStamp = 0
        print("调用抓取豆瓣明星图片时间是", datetime.datetime.now())
        while True :
            try:
                cursor = connections["grab"].cursor()
                cursor.execute(
                    "SELECT STAR_ID, STAR_SOURCE_CODE, INFORMATION_SOURCES, HEAD_IMG_URL, CLEAN_AFTER_ID FROM GRAB_STAR_INFO WHERE INFORMATION_SOURCES = 0 AND mod(STAR_ID, %d) = %d  AND STAR_ID IN (SELECT PHOTO_ID FROM GRAB_STAR_PHOTO WHERE INFORMATION_SOURCES = 0 AND PHOTO_HEIGHT = 0 AND DISPLAY_STATUS = 1) ORDER BY STAR_ID DESC" % (
                    len(ipDict), ipDict[localIp]))
                resultTuple = cursor.fetchall()
                cursor.close()
                if resultTuple :
                    starIdList = list()
                    for starInfoTuple in resultTuple:
                        upLoadCount, currentStamp = UrlUtils().upLoadPhotoToFtp(starInfoTuple[0], starInfoTuple[1], starInfoTuple[2], starInfoTuple[3], starInfoTuple[4], upLoadCount, currentStamp, starIdList)
                    if starIdList :
                        GrabStarInfo.objects.using("grab").filter(starId__in=starIdList).update(cleanStatus=3)
                    print("重新调用")
                else :
                    print("抓取豆瓣明星图片暂无数据当前时间是", datetime.datetime.now(), "休息", sleepTimeLength)
                    time.sleep(sleepTimeLength)
                    print("抓取豆瓣明星图片暂无数据休息后时间是", datetime.datetime.now())
            except BaseException as e:
                print("e.message:", str(e), "获取要抓取豆瓣明星图片出现异常")
                raise





if __name__ == '__main__' :
    pass
