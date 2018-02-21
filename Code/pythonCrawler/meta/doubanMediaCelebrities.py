import requests
from bs4 import BeautifulSoup
import re
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
from crawlerMeta.utils.dbutil import DBUtil
from django.db import connections
import time
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
from meta.model.GrabMediaInfo import GrabMediaInfo
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
# 抓取豆瓣影片的影人信息
class DoubanMediaCelebrities :

    startStarId = 19900000
    # 按影片抓取演员信息地址
    star_html_url = "https://movie.douban.com/subject/starId/celebrities"
    #抓取影片中演员信息
    def mediaCelebrities(self, celebritiesId):
        listUrl = self.star_html_url.replace('starId', str(celebritiesId))
        httpSpiderUtils = HttpSpiderUtils()
        print(listUrl)
        # 获取接口中ip
        ipapi = requests.get(
            "http://dynamic.goubanjia.com/dynamic/get/d5d45bc51ed327b9ea1708aa20d3deb0.html?random=yes")
        #print(ipapi)
        ipapi.encoding = 'utf-8'
        ipApiDataText = ipapi.text
        ipApiData = ipApiDataText.strip("\n")
        ipValue = "https://" + ipApiData
        print(ipValue)
        # 设置代理
        if (ipapi):
            ipapi.close()
        proxies = {
            "https": ipValue
        }
        #抓影片演员信息
        htmlText = httpSpiderUtils.spiderHtmlUrl(listUrl, 'https://www.baidu.com/', proxies)
        if htmlText != None :
            try:
                #解析HTML
                htmlText = BeautifulSoup(htmlText, 'html.parser')

                data = htmlText.find_all(attrs={'class': 'list-wrapper'})

                for listWrapper in data :
                    # 获取人员类型
                    msType = listWrapper.find("h2").contents[0]

                    mediaStarType = DoubanMediaCelebrities().roleNameType(msType)

                    ulAll = listWrapper.find_all("ul")
                    #print(ulall)
                    for ul in ulAll :

                        liAll = ul.find_all(attrs={'class': 'celebrity'})
                        for li in liAll :
                            #print(li)
                            role = li.find(attrs={'class': 'role'})
                            roleName = None
                            if role != None :
                                roleName = role.text

                            code = re.findall(r'(\w*[0-9]+)\w*', li.find("a")["href"])[0]

                            grabMediaStarInfo = GrabMediaStarInfo()
                            #关联id
                            #grabMediaStarInfo.mediaStarId = DBUtil().createPK("GRAB_MEDIA_STAR_INFO")
                            #print(grabMediaStarInfo.mediaStarId)
                            # 设置媒资源code
                            grabMediaStarInfo.mediaSourceCode = celebritiesId
                            # 设置演员源code
                            grabMediaStarInfo.starSourceCode = code

                            grabMediaStarInfo.roleName = roleName
                            # 设置信息来源
                            grabMediaStarInfo.informationSources = 0
                            #设置类型
                            grabMediaStarInfo.mediaStarType = mediaStarType
                            # 设置抓取时间
                            grabMediaStarInfo.grabTime = DBUtil().systemDateTime()
                            # 设置抓取清洗状态
                            grabMediaStarInfo.cleanStatus = 0
                            # 设置清洗后id
                            grabMediaStarInfo.cleanAfterId = 0
                            grabMediaStarInfo.cleanStarSourceId = 0
                            grabMediaStarInfo.cleanMediaSourceId = 0
                            # 保存数据库
                            #grabMediaStarInfo.save(using="grab")
                            DoubanMediaCelebrities().saveMediaStarInfo(grabMediaStarInfo)
            except BaseException as e:
                print("e.message:", str(e))


    def saveMediaStarInfo(self, grabMediaStarInfo):
        try:
            cursor = connections["grab"].cursor()
            cursor.execute(
                "SELECT MEDIA_STAR_ID,ROLE_NAME,CLEAN_STATUS FROM GRAB_MEDIA_STAR_INFO WHERE MEDIA_SOURCE_CODE = %s AND STAR_SOURCE_CODE = %s  AND MEDIA_STAR_TYPE =%d AND INFORMATION_SOURCES = %d" % (
                    grabMediaStarInfo.mediaSourceCode, grabMediaStarInfo.starSourceCode, grabMediaStarInfo.mediaStarType ,grabMediaStarInfo.informationSources))
            resultTuple = cursor.fetchall()
            cursor.close()

            if resultTuple:
                grabMediaStarInfo.mediaStarId = resultTuple[0][0]
                if resultTuple[0][1] == None :
                    if resultTuple[0][2] != 1:
                        if grabMediaStarInfo.roleName != None :
                            GrabMediaStarInfo.objects.using("grab").filter(mediaStarId = resultTuple[0][0]).update(roleName = grabMediaStarInfo.roleName)

            else:
                grabMediaStarInfo.save(using="grab")

        except BaseException as e:
            print("e.message:", str(e), "查询开始明星id出现异常")
        return self.startStarId

    #判断类型
    def roleNameType(self, msType):
        mediaStarType = 0
        try:
            if ('导演' in msType):
                print("导演")
                mediaStarType = 0
                # 设置人物类型

            if ('演员' in msType):
                print("演员")
                mediaStarType = 1

            if ('编剧' in msType):
                print("编剧")
                mediaStarType = 2

            if ('制片' in msType):
                print("制片")
                mediaStarType = 3

            if ('配音' in msType):
                print("配音")
                mediaStarType = 4

            if ('作曲' in msType):
                print("作曲")
                mediaStarType = 5

            if ('自己' in msType):
                print("自己")
                mediaStarType = 6

        except BaseException as e:
            print("e.message翻译类型:", str(e))
        return mediaStarType

        # 获取每台服务器明星id开始值

        # 查询明星作品关系
    def queryMediaInfo(self):
            try:
                starId = self.queryMediaCode()
                if len(starId) == 0 :
                    time.sleep(120)
                #print("startStarId", starId)
                for i in range(len(starId)):

                    # 拼接完整的html地址
                    DoubanMediaCelebrities().mediaCelebrities(starId[i][0])#starId26787574 i[0]
                    #修改媒资状态为2
                    GrabMediaInfo.objects.using("grab").filter(mediaId = int(starId[i][1])).update(cleanStatus = 2)


                    time.sleep(1)
            except BaseException as e:
                print("e.message:", str(e), "查询开始id出错")
    #循环
    def querygrabMediaStar(self):
        for i in range(9999999):
            DoubanMediaCelebrities().queryMediaInfo()

    def queryMediaCode(self):
        resultTuple = 0
        try:
            cursor = connections["grab"].cursor()
            cursor.execute(
                "SELECT MEDIA_SOURCE_CODE,MEDIA_ID FROM GRAB_MEDIA_INFO  WHERE CLEAN_STATUS != 2 AND INFORMATION_SOURCES = 0")
            resultTuple = cursor.fetchall()
            cursor.close()
        except BaseException as e:
            print("e.message:", str(e), "查询开始明星id出现异常")
        return resultTuple
# localIp = DBUtil().getLocalIp()
# ipDict = {"10.168.60.122" : 0, "10.168.60.91" : 1, "10.168.60.81" : 2}
if __name__ == '__main__':
    doubanMediaCelebrities = DoubanMediaCelebrities()
    #doubanMediaCelebrities.queryMediaInfo();


