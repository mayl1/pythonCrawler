import requests
import time
import json
import re
import pymysql
from bs4 import BeautifulSoup
from django.db import connections
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
from crawlerMeta.utils.dbutil import DBUtil
# from selenium import webdriver
# from selenium.webdriver.common.by import By
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
from pyutils.common.DateUtils import DateUtils
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_meta, data_type_2_grab, iqiyi_default_star_photo
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils
from meta.model.GrabMediaInfo import GrabMediaInfo
from meta.model.GrabMediaDynamic import  GrabMediaDynamic
from meta.model.GrabPoster import GrabPoster
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
class IqiyiMeta:

    # 按演职人员id访问api地址
    meta_url = "http://www.iqiyi.com/lib/m_%d.html"

    # 搜索索引初始
    meta_start = 200000114

    # 图片上传数量
    imageUploadNum = 0

    # 媒资来源=爱奇艺
    informationSources = 2

    # 集数
    currentSeasonNumber = 1

    # 生成图片的时间
    currentStamp = 0

    def queryMetaItemMeta(self, itemUrl, mediaWebCode):
        htmlText = HttpSpiderUtils().spiderHtmlUrl(itemUrl)
        if htmlText is None:
            return
        else:
            data = BeautifulSoup(htmlText, 'html.parser')
            if (len(data.select('div[class="info-intro"]')) == 0):
                return None
            mediaInfo = {"mediaWebCode": mediaWebCode, "grabWebUrl": itemUrl, "director" : []}
            intro = data.select('div[class="info-intro"]')[0]
            # 解析媒资code
            mediaSourceCode = self.parseMediaSourceCode(data)
            mediaInfo["mediaSourceCode"] = mediaSourceCode
            # 媒资类型
            mediaType = self.parseMediaType(intro.select('a[class="channelTag"]')[0].text)
            mediaInfo["mediaType"] = mediaType
            # 分集介绍
            parsePlot = []
            if (mediaType is not None):
                # 综艺
                if mediaType == 'variety':
                    mediaData = self.parseVarietyMedia(data)
                    mediaInfo.update(mediaData)
                elif mediaType == 'movie':
                    mediaInfo.update(self.parseMovieMedia(data))
                elif mediaType == 'tv' or mediaType == 'manga':
                    mediaInfo.update(self.parseTvMedia(data))
                    tvPlotList = self.parsePlot(data, mediaSourceCode)
                    mediaInfo["tvPlotList"] = tvPlotList
            # 评分
            score = self.parseScore(mediaSourceCode)
            mediaInfo["mediaScore"] = score
            # 媒资图片
            imgUrl = self.parseImage(data)
            mediaInfo["posterImgUrl"] = imgUrl
            # 图片上传
            ftpUrl, photoHeight, photoWidth = self.parseImageUpload(imgUrl)
            mediaInfo["posterFtpUrl"] = ftpUrl
            mediaInfo["posterHeight"] = photoHeight
            mediaInfo["posterWidth"] = photoWidth
            # 演员列表
            starList, protagonist = self.parseStarList(data, mediaSourceCode)
            mediaInfo["starList"] = starList
            mediaInfo["protagonist"] = protagonist
            # 获奖信息
            receivedAwards = self.parseReceivedAwards(data)
            mediaInfo["receivedAwards"] = receivedAwards
            # 保存媒资信息
            self.saveIqiyiMedia(mediaInfo)
        return None

    # 保存媒资信息
    def saveIqiyiMedia(self, mediaInfo):
        try:
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
            if mediaInfo.get("alternateName") is not None :
                grabMediaInfo.alternateName = mediaInfo.get("alternateName")
            if mediaInfo.get("mediaYear") is not None :
                grabMediaInfo.mediaYear = int(mediaInfo.get("mediaYear"))
            else:
                grabMediaInfo.mediaYear = 0
            if mediaInfo.get("mediaLanguage") is not None :
                grabMediaInfo.mediaLanguage = mediaInfo.get("mediaLanguage")
            if mediaInfo.get("mediaTimes") is not None :
                grabMediaInfo.mediaTimes = int(mediaInfo.get("mediaTimes"))
            else:
                grabMediaInfo.mediaTimes = 0
            if mediaInfo.get("mediaIntro") is not None :
                grabMediaInfo.mediaIntro = mediaInfo.get("mediaIntro")
            if mediaInfo.get("subordinateType") is not None :
                grabMediaInfo.subordinateType = mediaInfo.get("subordinateType")
            if mediaInfo.get("productionContry") is not None :
                grabMediaInfo.productionContry = mediaInfo.get("productionContry")
            if mediaInfo.get("currentSeasonNumber") is not None :
                grabMediaInfo.currentSeasonNumber = int(mediaInfo.get("currentSeasonNumber"))
            else:
                grabMediaInfo.currentSeasonNumber = 1
            if mediaInfo.get("posterImgUrl") is not None :
                grabMediaInfo.posterImgUrl = mediaInfo.get("posterImgUrl")
            if mediaInfo.get("mediaDirector") is not None  :
                grabMediaInfo.mediaDirector = mediaInfo.get("mediaDirector")
            if mediaInfo.get("protagonist") is not None :
                grabMediaInfo.mediaActor = str(mediaInfo.get("protagonist"))
            if mediaInfo.get("releaseTime") is not None :
                grabMediaInfo.releaseTime = mediaInfo.get("releaseTime")
            grabMediaInfo.totalSeason = 1
            grabMediaInfo.currentSeason = 1
            grabMediaInfo.grabTime = DBUtil().systemDateTime()
            grabMediaInfo.cleanStatus = 0
            grabMediaInfo.cleanAfterId = 0
            grabMediaInfo.save(using="grab", force_insert=True)
            # 保存媒资动态信息
            grabMediaDynamic = GrabMediaDynamic()
            grabMediaDynamic.mediaId = grabMediaInfo.mediaId
            grabMediaDynamic.mediaSourceCode = grabMediaInfo.mediaSourceCode
            grabMediaDynamic.informationSources = grabMediaInfo.informationSources
            if mediaInfo.get("mediaScore") is not None :
                grabMediaDynamic.mediaScore = mediaInfo.get("mediaScore")
            else:
                grabMediaDynamic.mediaScore = 0
            grabMediaDynamic.receivedAwards = str( mediaInfo.get("receivedAwards"))
            grabMediaDynamic.grabTime = DBUtil().systemDateTime()
            grabMediaDynamic.cleanStatus = 0
            grabMediaDynamic.cleanAfterId = 0
            grabMediaDynamic.save(using="grab", force_insert=True)
            # 保存图片
            self.saveMediaPoster(mediaInfo)
            # 保存媒资与影人关系
            self.saveMediaStarInfo(mediaInfo.get("starList"))
            # 电视剧和动漫保存剧集信息
            self.saveTvPlotList(mediaInfo.get("tvPlotList"))
        except BaseException as e:
            print("e.message:", str(e), "保存媒资信息出现异常")
        return

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

    # 电视剧和动漫保存剧集信息
    def saveTvPlotList(self, plotList):
        if plotList is None:
            return
        try:
            for index in range(len(plotList)) :
                plotDict = plotList[index]
                grabMediaInfo = GrabMediaInfo()
                grabMediaInfo.mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")
                grabMediaInfo.grabTime = DBUtil().systemDateTime()
                grabMediaInfo.mediaSourceCode = plotDict.get("mediaSourceCode")
                grabMediaInfo.cnName = plotDict.get("cnName")
                grabMediaInfo.currentSeasonNumber = plotDict.get("currentSeasonNumber")
                grabMediaInfo.episodeTitle = plotDict.get("episodeTitle")
                grabMediaInfo.informationSources = plotDict.get("informationSources")
                grabMediaInfo.parentSourceCode = plotDict.get("parentSourceCode")
                grabMediaInfo.cleanStatus = 0
                grabMediaInfo.cleanAfterId = 0
                grabMediaInfo.mediaYear = 0
                grabMediaInfo.mediaTimes = 0
                grabMediaInfo.totalSeason = 1
                grabMediaInfo.currentSeason = 1
                grabMediaInfo.save(using="grab", force_insert=True)
        except BaseException as e:
            print("e.message:", str(e), "保存电视剧集出错")

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
                    print("grabMediaStarInfo", grabMediaStarInfo)
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

    # 解析综艺媒资
    def parseVarietyMedia(self, data):
        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = ''
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0):
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = ''
        if (len(alternateNameNode) > 0):
            alternateName = alternateNameNode[0].text.replace('别名：', '')
        # 上映时间
        releaseTime = intro.select('p[class="episodeIntro-time"]')[0].select('span')[0].text
        # 语言MEDIA_LANGUAGE
        language = ''
        languageSoup = intro.select('p[itemprop=inLanguage]')
        if len(languageSoup) > 0:
            language = languageSoup[0].select('a')[0].text
        # 简介
        mediaIntro = ""
        mediaIntroSoup = intro.select('span[class="briefIntroTxt"]')
        if len(mediaIntroSoup) > 0 :
            mediaIntro = mediaIntroSoup[0].text
            if mediaIntro.endswith('...') and len(mediaIntroSoup) > 1 :
                mediaIntro = mediaIntroSoup[1].text
        # 影片类型
        subordinateType = ''
        subordinateNode = intro.select('p[class="episodeIntro-type"]')[0].select('a')
        # 多个影片类型用分号分隔
        if (len(subordinateNode) > 0):
            for index in range(len(subordinateNode)):
                if (index > 0):
                    subordinateType = subordinateType + ";"
                subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text
        # 导演
        director = []
        directorNode = data.select('p[class="episodeIntro-director"]')
        if directorNode is not None:
            for direIndex in range(len(directorNode)):
                if directorNode[direIndex].find('a') is not None:
                    director.append(directorNode[direIndex].find('a').text.strip().replace('\n', ''))
        # 返回数据
        resultDict = {}
        resultDict["cnName"] = cnName
        resultDict["alternateName"] = alternateName
        resultDict["releaseTime"] = releaseTime
        resultDict["mediaLanguage"] = language
        resultDict["mediaIntro"] = mediaIntro
        resultDict["subordinateType"] = subordinateType
        resultDict["productionContry"] = productionContry
        resultDict["currentSeasonNumber"] = self.currentSeasonNumber
        resultDict["mediaDirector"] = str(director)
        return resultDict

    # 解析电影媒资
    def parseMovieMedia(self, data):

        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = None
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0):
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = None
        if (len(alternateNameNode) > 0):
            alternateName = alternateNameNode[0].text.replace('别名：', '').strip().replace("\n", "")
        # 如果有英文名追加到别名中
        enNameNode = intro.select('p[class="info-title-english"]')
        if len(enNameNode) > 0:
            if alternateName is None:
                alternateName = enNameNode[0].text.strip().replace("\n", "")
            else:
                alternateName = alternateName + ";" + enNameNode[0].text.strip().replace("\n", "")
        # 上映时间
        releaseTime = intro.select('p[class="episodeIntro-wordplay"]')[0].select('span')[0].text.strip().replace("\n",
                                                                                                                 "")
        # 电影时长
        mediaTimes = intro.select('p[class="episodeIntro-time"]')[0].select('span')[0].text
        mediaTimes = re.sub(r'\D', "", mediaTimes).strip().replace("\n", "")
        # 语言MEDIA_LANGUAGE
        language = ''
        languageSoup = intro.select('p[class="episodeIntro-lang"]')
        if len(languageSoup) > 0:
            language = languageSoup[0].select('span')[0].text.strip().replace("\n", "")
        # 简介
        mediaIntro = ''
        mediaIntroSoup = data.select('span[class="briefIntroTxt"]')
        if len(mediaIntroSoup) > 1 :
            mediaIntro = mediaIntroSoup[1].text
            if (mediaIntro.endswith('...') and (len(data.select('span[class="briefIntroTxt"]')) > 2)):
                mediaIntro = mediaIntroSoup[2].text
        elif len(mediaIntroSoup) == 1 :
            mediaIntro = mediaIntroSoup[0].text
        # 影片类型.find_all("span", class_= ["movPr-time", "movPr-hidde"])
        subordinateType = ''
        subordinateNode = intro.find_all("p", class_=["episodeIntro-type", "maxw-info-type"])
        if len(subordinateNode) > 0 :
            subordinateNode = subordinateNode[0].select('a')
            # 多个影片类型用分号分隔
            if (len(subordinateNode) > 0):
                for index in range(len(subordinateNode)):
                    if (index > 0):
                        subordinateType = subordinateType + ";"
                        subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text.strip().replace('\n', '')
        # 导演
        director = []
        directorNode = data.select('p[class="episodeIntro-director"]')
        for direIndex in range(len(directorNode)):
            if directorNode[direIndex].find('a') is not None :
                director.append(directorNode[direIndex].find('a').text.strip().replace('\n', ''))
        # 返回数据
        resultDict = {}
        resultDict["cnName"] = cnName
        resultDict["alternateName"] = alternateName
        resultDict["releaseTime"] = releaseTime
        resultDict["mediaLanguage"] = language
        resultDict["mediaIntro"] = mediaIntro
        resultDict["subordinateType"] = subordinateType
        resultDict["productionContry"] = productionContry
        resultDict["mediaTimes"] = mediaTimes
        resultDict["mediaDirector"] = str(director)
        resultDict["currentSeasonNumber"] = self.currentSeasonNumber
        return resultDict

    # 解析电视剧、动漫媒资
    def parseTvMedia(self, data):
        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = None
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0):
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = None
        if (len(alternateNameNode) > 0):
            alternateName = alternateNameNode[0].text.replace('别名：', '').strip().replace("\n", "")
        # 如果有英文名追加到别名中
        enNameNode = intro.select('p[class="info-title-english"]')
        if len(enNameNode) > 0:
            if alternateName is None:
                alternateName = enNameNode[0].text.strip().replace("\n", "")
            else:
                alternateName = alternateName + ";" + enNameNode[0].text.strip().replace("\n", "")
        # 上映时间
        mediaYear = intro.select('p[class="episodeIntro-time"]')[0].select('span')[0].text.strip().replace("\n", "")
        # 语言MEDIA_LANGUAGE
        language = ''
        languageSoup = intro.select('p[class="episodeIntro-lang"]')
        if len(languageSoup) > 0:
            language = languageSoup[0].select('span')[0].text.strip().replace("\n", "")

        # 简介
        mediaIntro = ''
        mediaIntroSoup = data.select('span[class="briefIntroTxt"]')
        if len(mediaIntroSoup) > 1:
            mediaIntro = mediaIntroSoup[1].text
            if (mediaIntro.endswith('...') and (len(data.select('span[class="briefIntroTxt"]')) > 2)):
                mediaIntro = mediaIntroSoup[2].text
        elif len(mediaIntroSoup) == 1:
            mediaIntro = mediaIntroSoup[0].text
        # 影片类型
        subordinateType = ''
        subordinateNode = data.find(attrs={"class": "episodeIntro-type"})
        if subordinateNode is not None :
            subordinateNode = subordinateNode.select('a')
            # 多个影片类型用分号分隔
            if (len(subordinateNode) > 0):
                for index in range(len(subordinateNode)):
                    if (index > 0):
                        subordinateType = subordinateType + ";"
                    subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text.strip().replace('\n', '')
        # 导演
        director = []
        directorNode = data.select('p[class="episodeIntro-director"]')
        for direIndex in range(len(directorNode)):
            if directorNode[direIndex].find('a') is not None :
                director.append(directorNode[direIndex].find('a').text.strip().replace('\n', ''))
        # 媒资集数
        currentSeasonNumberSoup = data.find('span', attrs={"class": "title-update-progress"})
        if currentSeasonNumberSoup is not None:
            numberList = re.findall(r'\d+', currentSeasonNumberSoup.text)
            self.currentSeasonNumber = numberList[len(numberList) - 1]
        # 返回数据
        resultDict = {}
        resultDict["cnName"] = cnName
        resultDict["alternateName"] = alternateName
        resultDict["mediaYear"] = mediaYear
        resultDict["mediaLanguage"] = language
        resultDict["mediaIntro"] = mediaIntro
        resultDict["subordinateType"] = subordinateType
        resultDict["productionContry"] = productionContry
        resultDict["mediaDirector"] = str(director)
        resultDict["currentSeasonNumber"] = self.currentSeasonNumber
        return resultDict

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

    # 解析媒资code
    def parseMediaSourceCode(self, data):
        scoreHtml = data.findAll("div", attrs={"data-score-tvid": True})
        mediaSourceCode = None
        for score in scoreHtml:
            mediaSourceCode = score.attrs['data-score-tvid']
        return mediaSourceCode

    # 解析评分
    def parseScore(self, mediaSourceCode):
        # tvid不为空，调用评价接口，查询评分
        if (mediaSourceCode is not None):
            url = "http://score-video.iqiyi.com/beaver-api/get_sns_score?qipu_ids=" + mediaSourceCode + "&appid=21&tvid=" + mediaSourceCode + "&pageNo=1"
            jsonStr = HttpSpiderUtils().spiderHtmlUrl(url)
            jsonObj = json.loads(jsonStr)
            # 解析评分
            score = jsonObj['data'][0]['sns_score']
            return score
        return None

    # 解析图片
    def parseImage(self, data):
        img = data.find_all('img', attrs={'id': 'j-album-img'})
        if (img is not None):
            imgUrl = img[0].attrs['src']
            # 小列表图转为260*360
            imgUrl = imgUrl.replace('180_236.jpg', '260_360.jpg')
            return imgUrl
        return None;

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

    # 获奖信息 RECEIVED_AWARDS
    def parseReceivedAwards(self, data):
        receivedAwards = []
        awardsData = data.find(attrs={"class": "moviePrice-cont j-movieaward-all"})
        # 判断是否有获奖信息
        if (awardsData is None):
            return json.dumps(receivedAwards, ensure_ascii=False);
        allAwards = awardsData.find_all(attrs={"class": "moviePrice-tab-title"})
        # 判断是否有获奖信息
        for i in range(len(allAwards)):
            year = allAwards[i].text
            awardsDict = {'awardsYear': year}
            reListNode = allAwards[i]
            detailNode = reListNode.find_next().find_all(attrs={"class": "movPr-info-line"})
            awardsInfoList = []
            for detailIndex in range(len(detailNode)):
                # 第几届
                awardsTime = detailNode[detailIndex].find("span", class_=["movPr-time", "movPr-hidde"]).text
                # 奖项名称
                awardsName = detailNode[detailIndex].find("a", class_=["movPr-name"]).text
                # 奖项内容
                awardsProj = detailNode[detailIndex].find("span", class_=["movPr-proj"]).text
                # 奖项结果
                awardsResult = detailNode[detailIndex].find("span", class_=["movPr-result", "movPr-succes"]).text
                awardsInfo = {"awardsTime": awardsTime, "awardsName": awardsName, "awardsProj": awardsProj,
                              "awardsResult": awardsResult, "awardsStar": ""}
                awardsInfoList.append(awardsInfo)
            awardsDict["awardsInfoList"] = awardsInfoList
            receivedAwards.append(awardsDict)
        return json.dumps(receivedAwards, ensure_ascii=False);

    # 剧集介绍
    def parsePlot(self, data, parentCode):
        plotList = []
        nodeSoup = data.find_all(class_=["episodePlot-list"])
        if nodeSoup is None :
            return plotList
        for nodeIndex in range(len(nodeSoup)):
            plotSoup = nodeSoup[nodeIndex].find_all('li')
            for plotIndex in range(len(plotSoup)):
                plotNumSoup = plotSoup[plotIndex].find("a",class_="plotNum")
                # 判断是否有剧集
                if plotNumSoup is not None :
                    plotNum = plotNumSoup.text
                    plotNum = re.findall(r'\d+', plotNum)[0]
                    episodeTitle = plotSoup[plotIndex].find("p", class_="plotBody").text
                    plotDict = {"mediaSourceCode": parentCode + "_" + plotNum,
                                "currentSeasonNumber": int(plotNum), "episodeTitle": episodeTitle,
                                "informationSources":self.informationSources, "parentSourceCode":parentCode,
                                "cnName":plotNumSoup.text}
                    plotList.append(plotDict)
        return plotList

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

    def queryListMeta(self):
        '''
        itemUrl = "http://www.iqiyi.com/lib/m_215434414.html"
        self.queryMetaItemMeta(itemUrl, "215434414")
        return
        '''
        self.meta_start = self.queryMetaIndex()
        for i in range(999999):
            if self.isProcess(self.meta_start) :
                itemUrl = "http://www.iqiyi.com/lib/m_" + str(self.meta_start) + ".html"
                print(self.meta_start)
                try:
                    self.queryMetaItemMeta(itemUrl, str(self.meta_start))
                except BaseException as e:
                    print("except:" +itemUrl, "_________", str(e))

            self.meta_start = self.meta_start + 100


    # 获取媒资开始抓取的初始ID
    def queryMetaIndex(self):
        try:
            cursor = connections["grab"].cursor()
            cursor.execute(
                "SELECT MEDIA_WEB_CODE FROM GRAB_MEDIA_INFO WHERE CLEAN_STATUS < 2 AND INFORMATION_SOURCES = 2 AND MOD ( CAST( LEFT (MEDIA_WEB_CODE, 7) AS UNSIGNED ), %d ) = %d ORDER BY ( CAST( MEDIA_WEB_CODE AS UNSIGNED )) DESC LIMIT 1" % (
                    len(ipDict), ipDict[localIp]))
            resultTuple = cursor.fetchall()
            cursor.close()
            # 查询结果为空，返回初始值
            if not cursor.fetchall():
                print(len(resultTuple))
                if len(resultTuple) == 0 :
                    return self.meta_start
                for id in resultTuple:
                    return int(id[0]) + 100

        except BaseException as e:
            print("queryStarIndex.message:", str(e))
            raise

    def isProcess(self, metaCode):
        # 将媒资code 去掉最后2位‘14’后再进行验证是否本机执行
        metaId = int(str(metaCode)[0:-2])
        return HttpCrawlerUtils().isLocal(metaId)
