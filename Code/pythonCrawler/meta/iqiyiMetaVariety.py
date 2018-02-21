import requests
from bs4 import BeautifulSoup
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
import re
import json
import time
from meta.model.GrabMediaInfo import GrabMediaInfo
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_meta, data_type_2_grab, iqiyi_default_star_photo
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
from django.db import connections
from pyutils.common.DateUtils import DateUtils
from meta.model.GrabMediaDynamic import  GrabMediaDynamic
from meta.model.GrabPoster import GrabPoster
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils

class IqiyiMetaVariety:
    # 图片上传数量
    imageUploadNum = 0

    # 媒资来源=爱奇艺
    informationSources = 2

    # 集数
    currentSeasonNumber = 1

    # 生成图片的时间
    currentStamp = 0

    meta_start = 0

    # 按影片抓取演员信息地址
    media_html_url = "http://so.iqiyi.com/intent?if=video&type=list?p=10&p1=101&mode=11&threeCategory=&platform=web&pageNum=PageNum&intentActionType=0&pageSize=10&ctgName=%E7%BA%AA%E5%BD%95%E7%89%87&dataType=json&method=POST&firstFilter=&secondFilter=&termParams=%2526ctgname%253D%2525E7%2525BA%2525AA%2525E5%2525BD%252595%2525E7%252589%252587%2526graph_type%253D1_1_0_-1%2526real_query%253D%2525E8%2525AE%2525B0%2525E5%2525BD%252595%2525E7%252589%252587&pos=1"

    def iqyiMediaGrab(self ,pageNum):
        listUrl = self.media_html_url.replace('PageNum', str(pageNum))
        httpSpiderUtils = HttpSpiderUtils()
        print(listUrl)
        # 获取接口中ip
        ipapi = requests.get(
            "http://dynamic.goubanjia.com/dynamic/get/d5d45bc51ed327b9ea1708aa20d3deb0.html?random=yes")
        # print(ipapi)
        ipapi.encoding = 'utf-8'
        ipApiDataText = ipapi.text
        ipApiData = ipApiDataText.strip("\n")
        ipValue = "https://" + ipApiData

        # 设置代理
        if (ipapi):
            ipapi.close()
        proxies = {
            "https": ipValue
        }
        # 抓影片演员信息
        htmlText = httpSpiderUtils.spiderHtmlUrl(listUrl, 'https://www.baidu.com/', proxies)
        json_dict = json.loads(htmlText)
        # 解析HTML
        #htmlText = BeautifulSoup(htmlText, 'html.parser')

        json_dict = json.loads(htmlText)
        media_source_code = json_dict['data']

        mediaSourceCodeHtml = BeautifulSoup(media_source_code, 'html.parser')

        data = mediaSourceCodeHtml.find_all(attrs={'class': 'site-piclist_pic'})
        mediaWebCode = 0
        for i in range(len(data)) :
            href = data[i].find("a").get('href')
            #href = "http://www.iqiyi.com/a_19rrhb9oml.html"
            if "a_" in href:
                try :

                    # 保存媒资主表
                    mediaInfo = {"mediaWebCode": mediaWebCode, "grabWebUrl": href, "director": []}

                    htmlDetail = httpSpiderUtils.spiderHtmlUrl(href, 'https://www.baidu.com/', proxies)
                    htmlDetail = BeautifulSoup(htmlDetail, 'html.parser')

                    currentSeasonNumber = self.parseCurrentSeasonNumber(htmlDetail)

                    mediaInfo["currentSeasonNumber"] = currentSeasonNumber
                    #媒资code
                    mediaSourceCode = IqiyiMetaVariety().parseMediaSourceCode(htmlDetail)
                    mediaInfo["mediaSourceCode"] = mediaSourceCode

                    #评分
                    score = IqiyiMetaVariety().parseScore(mediaSourceCode)
                    mediaInfo["mediaScore"] = score
                    # 媒资图片
                    imgUrl = IqiyiMetaVariety().parseImage(htmlDetail)
                    #上传图片
                    ftpUrl, photoHeight, photoWidth = self.parseImageUpload(imgUrl)
                    mediaInfo["posterFtpUrl"] = ftpUrl
                    mediaInfo["posterHeight"] = photoHeight
                    mediaInfo["posterWidth"] = photoWidth

                    mediaInfo["mediaWebCode"] = pageNum

                    mediaInfo["posterImgUrl"] = imgUrl
                    #中文名称
                    cnName = IqiyiMetaVariety().parseCnName(htmlDetail)
                    mediaInfo["cnName"] = cnName
                    #年份
                    mediaYear = IqiyiMetaVariety().parseMediaYear(htmlDetail)
                    if (mediaYear == "") :
                        mediaYear = None
                    mediaInfo["mediaYear"] = mediaYear
                    #语言
                    inLanguage = IqiyiMetaVariety().parseInLanguage(htmlDetail)
                    mediaInfo["mediaLanguage"] = inLanguage
                    #标签
                    mediaTag = IqiyiMetaVariety().parseGenre(htmlDetail)
                    mediaInfo["mediaType"] = mediaTag
                    # 媒资类型
                    mediaInfo["mediaType"] = IqiyiMetaVariety().parseMediaTypeName(htmlDetail)
                    #简介
                    description =  IqiyiMetaVariety().parseDescription(htmlDetail)
                    mediaInfo["mediaIntro"] = description
                    # 演员列表
                    starList, protagonist = self.parseStarList(mediaSourceCodeHtml, mediaSourceCode)
                    mediaInfo["starList"] = starList
                    mediaInfo["protagonist"] = protagonist

                    #main_title
                    IqiyiMetaVariety().saveIqiyiMedia(mediaInfo)
                except BaseException as e:
                    print("e.message:", str(e), "保存错误")
               #IqiyiMetaVariety().iqyiMediaDetailsGrab(htmlDetail)

    def iqyiMediaDetailsGrab(self, htmlDetail):

        data = htmlDetail.find_all(attrs={'class': 'album-head-info'})
        #print(data)

    def parseMediaYear(self,htmlDetail):
        mediaYear = ""
        htmlDetail = htmlDetail.find_all(attrs={'itemprop': 'datePublished'})
        if (len(htmlDetail) > 1) :
            mediaYear = htmlDetail[1].text

        return  mediaYear
    #简介
    def parseDescription(self,htmlDetail):
        mediaYear = ""
        htmlDetail = htmlDetail.find_all(attrs={'itemprop': 'description'})


        if (len(htmlDetail) > 1) :
            if (len(htmlDetail) == 2) :

                description = htmlDetail[1]

            else :
                description = htmlDetail[2]
            span = description.find("span")

            if (span is not None):

                description = span.text
            else:
                description = htmlDetail[1].text

        return  description

    def parseInLanguage(self,htmlDetail):
        inLanguage = ""
        htmlDetail = htmlDetail.find_all(attrs={'itemprop': 'inLanguage'})
        if (len(htmlDetail) > 1) :
            inLanguage = htmlDetail[1].find("a").text

        return  inLanguage

    def parseCnName(self, htmlDetail):
        htmlDetail = htmlDetail.find_all(attrs={'itemprop': 'name'})
        cnName = htmlDetail[1].find("a").text
        return cnName
    #类型
    def parseGenre(self, htmlDetail):
        htmlDetail = htmlDetail.find_all(attrs={'itemprop': 'genre'})
        genreEm = htmlDetail[0].find("em")
        if (genreEm is None) :
            genre = htmlDetail[0].find_all("a")
            if (len(genre) == 0) :
                return ""
            else :
                return genre[0].text
        else :
            genre = genreEm.find_all("a")
            if (len(genre) == 0):
                return ""
            else:
                return genre[0].text


    def parseMediaTypeName(self,data):

        # 媒资类型
        mediaType = data.find(attrs={"class": 'channelTag'}) #mediaType = self.parseMediaType(
        if mediaType is None :
            mediaType = "documentary"
        else :
            mediaType = self.parseMediaType(mediaType.text)


        return mediaType
    # 解析媒资code
    def parseMediaSourceCode(self, data):


        spans = data.find_all("span")

        for i in range(len(spans)):

            mediaSourceCode = spans[i].get("data-score-tvid")


            if mediaSourceCode is not None :
                return mediaSourceCode

        return None

    # 解析评分
    def parseScore(self, mediaSourceCode):
        # tvid不为空，调用评价接口，查询评分
        if (mediaSourceCode is not None):
            url = "http://score-video.iqiyi.com/beaver-api/get_sns_score?qipu_ids=" + mediaSourceCode + "&appid=21&tvid=" + mediaSourceCode + "&pageNo=1"
            jsonStr = HttpSpiderUtils().spiderHtmlUrl(url)
            jsonObj = json.loads(jsonStr)
            data = jsonObj['data']

            # 解析评分
            if len(data) > 0 :
                score = jsonObj['data'][0]['sns_score']
                return score
        return None

    # 解析图片
    def parseImage(self, data):
        img = data.find_all('meta', attrs={'itemprop': 'image'})

        if (len(img) > 0) :
            imgUrl = img[0].attrs['content']
            # 小列表图转为260*360
            imgUrl = imgUrl.replace('180_101.jpg', '260_360.jpg')
            return imgUrl
        return None;

    def parseMediaType(self, mediaType):
        if mediaType == '电影':
            return 'movie'
        elif mediaType == '电视剧':
            return 'tv'
        elif mediaType == '动漫':
            return 'manga'
        elif mediaType == '综艺':
            return 'variety'
        elif mediaType == '纪录片':
            return 'documentary'
            # 保存媒资信息
    def saveIqiyiMedia(self, mediaInfo):
        try:

            try :
                # 保存媒资主表
                grabMediaInfo = GrabMediaInfo()
                # 媒资主表ID
                mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")
                grabMediaInfo.mediaId = mediaId
                grabMediaInfo.mediaSourceCode = mediaInfo.get("mediaSourceCode")
                grabMediaInfo.informationSources = self.informationSources
                grabMediaInfo.mediaType = mediaInfo.get("mediaType")
                grabMediaInfo.cnName = mediaInfo.get("cnName")
                grabMediaInfo.grabWebUrl = mediaInfo.get("grabWebUrl")
                grabMediaInfo.mediaWebCode = mediaInfo.get("mediaWebCode")
                if mediaInfo.get("alternateName") is not None:
                    grabMediaInfo.alternateName = mediaInfo.get("alternateName")
                if mediaInfo.get("mediaYear") is not None:

                    grabMediaInfo.mediaYear = int(mediaInfo.get("mediaYear"))
                else:
                    grabMediaInfo.mediaYear = 0
                if mediaInfo.get("mediaLanguage") is not None:
                    grabMediaInfo.mediaLanguage = mediaInfo.get("mediaLanguage")
                if mediaInfo.get("mediaTimes") is not None:
                    grabMediaInfo.mediaTimes = int(mediaInfo.get("mediaTimes"))
                else:
                    grabMediaInfo.mediaTimes = 0
                if mediaInfo.get("mediaIntro") is not None:
                    grabMediaInfo.mediaIntro = mediaInfo.get("mediaIntro")
                if mediaInfo.get("subordinateType") is not None:
                    grabMediaInfo.subordinateType = mediaInfo.get("subordinateType")
                if mediaInfo.get("productionContry") is not None:
                    grabMediaInfo.productionContry = mediaInfo.get("productionContry")
                if mediaInfo.get("currentSeasonNumber") is not None:
                    grabMediaInfo.currentSeasonNumber = int(mediaInfo.get("currentSeasonNumber"))
                else:
                    grabMediaInfo.currentSeasonNumber = 1
                if mediaInfo.get("posterImgUrl") is not None:
                    grabMediaInfo.posterImgUrl = mediaInfo.get("posterImgUrl")
                if mediaInfo.get("mediaDirector") is not None:
                    grabMediaInfo.mediaDirector = mediaInfo.get("mediaDirector")
                if mediaInfo.get("protagonist") is not None:
                    grabMediaInfo.mediaActor = str(mediaInfo.get("protagonist"))
                if mediaInfo.get("releaseTime") is not None:
                    grabMediaInfo.releaseTime = mediaInfo.get("releaseTime")
                grabMediaInfo.totalSeason = 1
                grabMediaInfo.currentSeason = 1
                grabMediaInfo.grabTime = DBUtil().systemDateTime()
                grabMediaInfo.cleanStatus = 0
                grabMediaInfo.cleanAfterId = 0
                grabMediaInfo.cleanParentMediaId = 0
                grabMediaInfo.save(using="grab", force_insert=True)
                IqiyiMetaVariety().parseSubset(mediaInfo.get("mediaSourceCode"))
            except BaseException as e:
                print("e.message:", str(e), "保存媒资信息出现异常")

            # 保存媒资动态信息
            grabMediaDynamic = GrabMediaDynamic()
            grabMediaDynamic.mediaId = grabMediaInfo.mediaId
            grabMediaDynamic.mediaSourceCode = grabMediaInfo.mediaSourceCode
            grabMediaDynamic.informationSources = grabMediaInfo.informationSources
            if mediaInfo.get("mediaScore") is not None:
                grabMediaDynamic.mediaScore = mediaInfo.get("mediaScore")
            else:
                grabMediaDynamic.mediaScore = 0
            grabMediaDynamic.receivedAwards = str(mediaInfo.get("receivedAwards"))
            grabMediaDynamic.grabTime = DBUtil().systemDateTime()
            grabMediaDynamic.cleanStatus = 0
            grabMediaDynamic.cleanAfterId = 0
            grabMediaDynamic.receivedAwards = ""
            grabMediaDynamic.mediaMoney = 0
            grabMediaDynamic.save(using="grab", force_insert=True)
            # 保存图片
            self.saveMediaPoster(mediaInfo)
            # 保存媒资与影人关系
            self.saveMediaStarInfo(mediaInfo.get("starList"))

        except BaseException as e:
            print("e.message:", str(e), "保存媒资信息出现异常")
        return

    # 图片上传
    def parseImageUpload(self, webUrl):
        ftpUrl = ''
        photoHeight = 0
        photoWidth = 0
        if self.imageUploadNum % 1000 == 0 and self.currentStamp == 0:
            self.currentStamp = DateUtils.getSysTimeSecond()
        dateType = data_type_1_meta + data_type_separator + data_type_2_grab
        print("currentStamp:", self.currentStamp, ",imageUploadNum:", self.imageUploadNum,
              ",self.imageUploadNum % 1000 == 0:", self.imageUploadNum % 1000 == 0)
        # 取得FTP上传后地址
        ftpUrl, webFileUrl = UrlUtils().getRemoteFile(dateType, self.currentStamp, self.informationSources, webUrl)
        # 上传图片到FTP,返回图片尺寸
        photoHeight, photoWidth = UrlUtils().upLoadFtp(ftpUrl, webFileUrl, self.informationSources)
        self.imageUploadNum += 1
        return ftpUrl, photoHeight, photoWidth


    # 解析媒资与影人关系列表
    def parseStarList(self, data, mediaCode):
        # 演员列表
        starList = []
        # 主要演员
        protagonist = []
        # 相关明星节点
        starListNode = data.find_all("div", attrs={"class": "headImg-wrap", "itemtype": "//schema.org/Person"})
        if len(starListNode) == 0:
            return starList, protagonist
        # 解析结点
        dataListNode = None;

        # 明星节点不为空，查询明星列表
        if (len(starListNode) > 1):
            # 展开后
            dataListNode = starListNode[1]
        elif (len(starListNode) == 1):
            # 展开前
            dataListNode = starListNode[0]
        # 明星节点不为空,
        if (dataListNode is not None):
            starDataList = dataListNode.find_all("li")
            for i in range(len(starDataList)):
                starDict = {"starSourceCode": None, "mediaSourceCode": mediaCode, "mediaStarType": 1, "roleName": None,
                            "informationSources": 2}
                # 获取明星链接，通过链接地址，取得明星CODE
                starUrl = starDataList[i].find("p", class_="headImg-bottom-title").find('a').get('href')
                starDict["starSourceCode"] = re.findall(r'\d+', starUrl)[0]
                # 剧中角色
                roleNameNode = starDataList[i].select('p[class="headImg-bottom-describe"]')
                if (len(roleNameNode) > 0):
                    starDict["roleName"] = roleNameNode[0].text.replace('饰', '').strip().replace('\n', '')
                starList.append(starDict)
            protagonistNode = starListNode[0].find_all("li")
            for i in range(len(protagonistNode)):
                protagonist.append(starDataList[i].select('p[class="headImg-bottom-title"]')[0].select('a')[0].text)
        # 媒资导演
        directorNode = data.select('p[class="episodeIntro-director"]')
        for direIndex in range(len(directorNode)) :
            starDict = {"starSourceCode": None, "mediaSourceCode": mediaCode, "mediaStarType": 0, "roleName": None,
                        "informationSources": 2}
            # 判断是否有导演
            if directorNode[direIndex].find('a') is not None :
                starUrl = directorNode[direIndex].find('a').get('href')
                starDict["starSourceCode"] = re.findall(r'\d+', starUrl)[0]
                starList.append(starDict)
        return starList, protagonist


    # 保存媒资图片
    def saveMediaPoster(self, mediaInfo):
        try:
            grabPoster = GrabPoster()
            grabPoster.posterId = DBUtil().createPK("GRAB_POSTER")
            grabPoster.mediaSourceCode = mediaInfo.get("mediaSourceCode")
            grabPoster.informationSources = self.informationSources
            grabPoster.posterUrl = mediaInfo.get("posterImgUrl")
            grabPoster.posterWidth = mediaInfo.get("posterWidth")
            grabPoster.posterHeight = mediaInfo.get("posterHeight")
            grabPoster.posterFtpUrl = mediaInfo.get("posterFtpUrl")
            grabPoster.displayStatus = 1
            grabPoster.cleanStatus = 0
            grabPoster.cleanAfterId = 0
            grabPoster.grabTime = DBUtil().systemDateTime()
            grabPoster.save(using="grab", force_insert=True)
        except BaseException as e:
            print("e.message:", str(e), "保存媒资图片出错")

    # 保存媒资与演员关系
    def saveMediaStarInfo(self, starList):
        for index in range(len(starList)) :
            try:
                grabMediaStarInfo = GrabMediaStarInfo()
                mediaStrarDict = starList[index]
                # 查询关系是否存在starDict = {"starCode": None, "mediaCode": mediaCode, "mediaStarType": 1, "roleName": None,"informationSources": 2}
                grabMediaStarInfoList = GrabMediaStarInfo.objects.using("grab")\
                    .filter(mediaSourceCode=mediaStrarDict.get("mediaSourceCode"), starSourceCode=mediaStrarDict.get("starSourceCode")
                            , mediaStarType=mediaStrarDict.get("mediaStarType"), informationSources=mediaStrarDict.get("informationSources"))
                if len(grabMediaStarInfoList) > 0 :
                    grabMediaStarInfo = grabMediaStarInfoList[0]

                    # 更新演员角色名称为空的数据
                    if (mediaStrarDict.get("mediaStarType") ==1) and (grabMediaStarInfo.roleName is None or len(grabMediaStarInfo.roleName) == 0) :
                        grabMediaStarInfo.roleName = mediaStrarDict.get("roleName")
                        grabMediaStarInfo.save(using="grab")
                else:
                    grabMediaStarInfo.mediaSourceCode = mediaStrarDict.get("mediaSourceCode")
                    grabMediaStarInfo.starSourceCode = mediaStrarDict.get("starSourceCode")
                    grabMediaStarInfo.informationSources = mediaStrarDict.get("informationSources")
                    grabMediaStarInfo.mediaStarType = mediaStrarDict.get("mediaStarType")
                    grabMediaStarInfo.roleName = mediaStrarDict.get("roleName")
                    grabMediaStarInfo.grabTime = DBUtil().systemDateTime()
                    grabMediaStarInfo.cleanStatus = 0
                    grabMediaStarInfo.cleanAfterId = 0
                    grabMediaStarInfo.cleanStarSourceId = 0
                    grabMediaStarInfo.cleanMediaSourceId = 0
                    grabMediaStarInfo.save(using="grab", force_insert=True)

            except BaseException as e:
                print("e.message:", str(e), "保存媒资与演员关系异常")
        return

    def parseCurrentSeasonNumber(self, data):

        emAll = data.find_all("em")

        for em in emAll :

            if ( "集数" in em.text) :
                currentSeasonNumbers = em.text.split("/")
                if (len(currentSeasonNumbers) > 1) :
                    currentSeasonNumber = re.sub("\D", "", currentSeasonNumbers[1])
                    return currentSeasonNumber
                else :
                    currentSeasonNumber = re.sub("\D", "", em.text)
                    return currentSeasonNumber
            if ( "集数" in em.text) :
                currentSeasonNumbers = em.text.split("/")
                if (len(currentSeasonNumbers) > 1) :
                    currentSeasonNumber = re.sub("\D", "", currentSeasonNumbers[1])
                    return currentSeasonNumber
                else :
                    currentSeasonNumber = re.sub("\D", "", em.text)
                    return currentSeasonNumber

        return 1
    # 请求记录片
    def queryMetaVariety(self):
        self.meta_start = self.queryMetaIndex()

        for i in range(99999999) :
            IqiyiMetaVariety().iqyiMediaGrab(self.meta_start)

            self.meta_start = self.meta_start + 1

    def parseSubset(self, mediaSourceCode):
        try:
            url = "http://cache.video.iqiyi.com/jp/sdvlst/3/"+str(mediaSourceCode)+"/?categoryId=3&sourceId=" + str(mediaSourceCode)
            print(url)
            jsonStr = HttpSpiderUtils().spiderHtmlUrl(url)
            jsonObj = json.loads(jsonStr.split("=")[1])
            data = jsonObj['data']
            if (data == None) :
                print(data)

            for i in  range(len(data)) :
                subset = data[i]
                try:
                    if (subset is not None) :
                        # 保存媒资主表
                        grabMediaInfo = GrabMediaInfo()
                        # 媒资主表ID
                        mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")
                        grabMediaInfo.mediaId = mediaId
                        tvYear = subset["tvYear"]
                        if (tvYear is not None) :
                            grabMediaInfo.mediaYear = tvYear[0:4]
                        else :
                            tvYear = 0

                        grabMediaInfo.releaseTime = tvYear
                        grabMediaInfo.mediaSourceCode = subset["tvId"]
                        grabMediaInfo.informationSources = self.informationSources
                        grabMediaInfo.mediaType = ""


                        tvSbtitle = subset["tvSbtitle"]
                        grabMediaInfo.cnName = tvSbtitle
                        aDesc = subset["aDesc"]
                        grabMediaInfo.mediaIntro = aDesc

                        timeLength = subset["timeLength"]
                        grabMediaInfo.mediaLanguage = timeLength
                        #父集id
                        faqipuid = subset["faqipuid"]
                        grabMediaInfo.parentSourceCode = faqipuid
                        grabMediaInfo.episodeTitle = subset["tvFocus"] #tvFocus
                        mActors = subset["mActors"]
                        grabMediaInfo.mediaActor = mActors
                        grabMediaInfo.grabWebUrl = url
                        grabMediaInfo.totalSeason = 1
                        grabMediaInfo.currentSeason = 1
                        grabMediaInfo.grabTime = DBUtil().systemDateTime()
                        grabMediaInfo.cleanStatus = 0
                        grabMediaInfo.cleanAfterId = 0
                        grabMediaInfo.cleanParentMediaId = 0
                        grabMediaInfo.posterImgUrl = ""
                        grabMediaInfo.mediaTag = ""

                        grabMediaInfo.save(using="grab", force_insert=True)
                except BaseException as e:
                    print("e.message:", str(e), "保存子集失败")
        except BaseException as e:
            print("e.message:", str(e), "保存子集失败")

# 获取媒资开始抓取的初始ID
    def queryMetaIndex(self):
        try:
            cursor = connections["grab"].cursor()
            cursor.execute(
                "SELECT MEDIA_WEB_CODE FROM GRAB_MEDIA_INFO WHERE CLEAN_STATUS < 2 AND INFORMATION_SOURCES = 2  AND MEDIA_TYPE = 'documentary' AND MOD ( CAST( LEFT (MEDIA_WEB_CODE, 7) AS UNSIGNED ), %d ) = %d ORDER BY ( CAST( MEDIA_WEB_CODE AS UNSIGNED )) DESC LIMIT 1" % (
                    len(ipDict), ipDict[localIp]))
            resultTuple = cursor.fetchall()
            cursor.close()
            # 查询结果为空，返回初始值
            if not cursor.fetchall():
                print(len(resultTuple))
                if len(resultTuple) == 0 :
                    return self.meta_start
                for id in resultTuple:
                    return int(id[0]) + 1

        except BaseException as e:
            print("queryStarIndex.message:", str(e))
            raise
    def isProcess(self, metaCode):
        # 将媒资code 去掉最后2位‘14’后再进行验证是否本机执行
        metaId = metaCode
        return HttpCrawlerUtils().isLocal(metaId)
if __name__ == '__main__':
    IqiyiMetaVariety().parseSubset()