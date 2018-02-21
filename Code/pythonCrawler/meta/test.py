import requests
import time
import json
import re
import pymysql
from bs4 import BeautifulSoup
from django.db import connections
from crawlerMeta.utils.dbutil import DBUtil
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_meta, data_type_2_grab, iqiyi_default_star_photo
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils
from pyutils.common.DateUtils import DateUtils
class testIqiyi:
    # 图片上传数量
    imageUploadNum = 0
    # 媒资来源=爱爱奇艺
    informationSources =2
    currentSeasonNumberSoup = 1
    def queryMetaItemMeta(self, itemUrl, mediaCode):
        htmlText = HttpSpiderUtils().spiderHtmlUrl(itemUrl)
        if htmlText is None:
            return
        else:
            data = BeautifulSoup(htmlText, 'html.parser')
            if (len(data.select('div[class="info-intro"]')) == 0) :
                return None
            intro = data.select('div[class="info-intro"]')[0]
            # 解析媒资code
            mediaSourceCode = self.parseMediaSourceCode(data)
            # 评分
            score = self.parseScore(mediaSourceCode)
            # 媒资图片
            imgUrl = self.parseImage(data)
            # 图片上传
            #ftpUrl, photoHeight, photoWidth =self.parseImageUpload(imgUrl)
            # 媒资类型
            mediaType = self.parseMediaType(intro.select('a[class="channelTag"]')[0].text)
            mediaInfo = None
            # 分集介绍
            parsePlot = []
            if (mediaType is not None):
                # 综艺
                if mediaType == 'variety':
                    mediaInfo = self.parseVarietyMedia(data, mediaInfo)
                elif mediaType == 'movie' :
                    mediaInfo = self.parseMovieMedia(data, mediaInfo)
                elif mediaType == 'tv' or mediaType == 'manga':
                    mediaInfo = self.parseTvMedia(data, mediaInfo)
                    parsePlot = self.parsePlot(data, mediaSourceCode)

            # 演员列表
            starList, protagonist = self.parseStarList(data, mediaSourceCode)
            # 获奖信息
            receivedAwards = self.parseReceivedAwards(data)
            return None

    def parseVarietyMedia(self, data, mediaInfo):
        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = None
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0) :
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = None
        if (len(alternateNameNode) > 0) :
            alternateName = alternateNameNode[0].text.replace('别名：', '')
        # 上映时间
        releaseTime = intro.select('p[class="episodeIntro-time"]')[0].select('span')[0].text
        # 语言MEDIA_LANGUAGE
        language = None
        languageSoup = intro.select('p[itemprop=inLanguage]')
        if len(languageSoup) > 0:
            language = languageSoup[0].select('a')[0].text
        # 简介
        mediaIntro = intro.select('span[class="briefIntroTxt"]')[0].text
        if mediaIntro.endswith('...'):
            mediaIntro = intro.select('span[class="briefIntroTxt"]')[1].text
        # 影片类型
        subordinateType = ''
        subordinateNode = intro.select('p[class="episodeIntro-type"]')[0].select('a')
        # 多个影片类型用分号分隔
        if (len(subordinateNode) > 0) :
            for index in range(len(subordinateNode)) :
                if (index > 0) :
                    subordinateType = subordinateType + ";"
                subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text

        return cnName, alternateName, releaseTime, language, mediaIntro, subordinateType, productionContry

    def parseMovieMedia(self, data, mediaInfo):
        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = None
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0) :
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = None
        if (len(alternateNameNode) > 0) :
            alternateName = alternateNameNode[0].text.replace('别名：', '').strip().replace("\n", "")
        # 如果有英文名追加到别名中
        enNameNode = intro.select('p[class="info-title-english"]')
        if len(enNameNode) > 0:
            if alternateName is None:
                alternateName = enNameNode[0].text.strip().replace("\n", "")
            else:
                alternateName = alternateName + ";" + enNameNode[0].text.strip().replace("\n", "")
        # 上映时间
        releaseTime = intro.select('p[class="episodeIntro-wordplay"]')[0].select('span')[0].text.strip().replace("\n", "")
        # 电影时长
        mediaTimes = intro.select('p[class="episodeIntro-time"]')[0].select('span')[0].text
        mediaTimes = re.sub(r'\D', "", mediaTimes).strip().replace("\n", "")
        # 语言MEDIA_LANGUAGE
        language = ''
        languageSoup = intro.select('p[class="episodeIntro-lang"]')
        if len(languageSoup) > 0:
            language = languageSoup[0].select('span')[0].text.strip().replace("\n", "")
        # 简介
        mediaIntro = data.select('span[class="briefIntroTxt"]')[1].text
        if (mediaIntro.endswith('...') and (len(data.select('span[class="briefIntroTxt"]')) > 2) ):
            mediaIntro = data.select('span[class="briefIntroTxt"]')[2].text
        # 影片类型.find_all("span", class_= ["movPr-time", "movPr-hidde"])
        subordinateType = ''
        subordinateNode = intro.find_all("p", class_= ["episodeIntro-type", "maxw-info-type"])[0].select('a')
        # 多个影片类型用分号分隔
        if (len(subordinateNode) > 0) :
            for index in range(len(subordinateNode)) :
                if (index > 0) :
                    subordinateType = subordinateType + ";"
                subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text.strip().replace('\n','')
        # 导演
        director = intro.select('p[class="episodeIntro-director"]')[0].select('a')[0].text.strip().replace('\n','')

        return cnName, alternateName, releaseTime, language, mediaIntro, subordinateType, productionContry, mediaTimes, director

    def parseTvMedia(self, data, mediaInfo):
        intro = data.select('div[class="info-intro"]')[0]
        # 中文名
        cnName = None
        cnName_node = intro.select('span[class="info-intro-title"]')
        if (len(cnName_node) > 0) :
            cnName = cnName_node[0].text
        else:
            cnName_node = intro.select('a[class="info-intro-title"]')
            if (len(cnName_node) > 0):
                cnName = cnName_node[0].text
        # 别名
        alternateNameNode = intro.select('span[class="info-intro-title-s"]')
        alternateName = None
        if (len(alternateNameNode) > 0) :
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
        mediaIntro = intro.select('span[class="briefIntroTxt"]')[0].text
        if (mediaIntro.endswith('...') and (len(intro.select('span[class="briefIntroTxt"]'))>1)):
            mediaIntro = intro.select('span[class="briefIntroTxt"]')[1].text
        # 影片类型
        subordinateType = ''
        subordinateNode = intro.select('p[class="episodeIntro-type"]')[0].select('a')
        # 多个影片类型用分号分隔
        if (len(subordinateNode) > 0) :
            for index in range(len(subordinateNode)) :
                if (index > 0) :
                    subordinateType = subordinateType + ";"
                subordinateType = subordinateType + (subordinateNode[index].text)
        # 地区
        productionContry = intro.select('p[class="episodeIntro-area"]')[0].select('a')[0].text.strip().replace('\n','')
        # 导演
        director = intro.select('p[class="episodeIntro-director"]')[0].select('a')[0].text.strip().replace('\n','')
        # 媒资集数
        currentSeasonNumberSoup = data.find('span', attrs={"class": "title-update-progress"})
        if currentSeasonNumberSoup is not None:
            print(currentSeasonNumberSoup.text)
            self.currentSeasonNumber = re.findall(r'\d+', currentSeasonNumberSoup.text)[0]
        return cnName, alternateName, mediaYear, language, mediaIntro, subordinateType, productionContry, director, self.currentSeasonNumber

    def parseMediaType(self, mediaType):
        if mediaType == '电影':
            return 'movie'
        elif mediaType == '电视剧':
            return 'tv'
        elif mediaType == '动漫':
            return 'manga'
        elif mediaType == '综艺':
            return 'variety'

    # 解析媒资code
    def parseMediaSourceCode(self, data) :
        scoreHtml = data.findAll("div", attrs={"data-score-tvid": True})
        mediaSourceCode = None
        for score in scoreHtml:
            mediaSourceCode = score.attrs['data-score-tvid']
        return mediaSourceCode

    # 解析评分
    def parseScore(self, mediaSourceCode):
        #tvid不为空，调用评价接口，查询评分
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

    # 解析演员列表
    def parseStarList(self, data, mediaCode):
        # 演员列表
        starList = []
        # 主要演员
        protagonist = []
        # 相关明星节点
        starListNode = data.find_all("div", attrs={"class": "headImg-wrap","itemtype":"//schema.org/Person"})
        if len(starListNode) == 0 :
            return starList, protagonist
        # 解析结点
        dataListNode = None;

        # 明星节点不为空，查询明星列表
        if (len(starListNode) > 1) :
            # 展开后
            dataListNode = starListNode[1]
        elif (len(starListNode) == 1) :
            # 展开前
            dataListNode = starListNode[0]
        # 明星节点不为空,
        if (dataListNode is not None):
            starDataList =  dataListNode.find_all("li")
            for i in range(len(starDataList)) :
                starDict = {"starCode":None, "mediaCode":mediaCode, "mediaStarType":1, "roleName":None, "informationSources":2}
                # 获取明星链接，通过链接地址，取得明星CODE
                starUrl = starDataList[i].find("p", class_="headImg-bottom-title").find('a').get('href')
                starDict["starCode"] = re.findall(r'\d+', starUrl)[0]
                # 剧中角色

                roleNameNode = starDataList[i].select('p[class="headImg-bottom-describe"]')
                if (len(roleNameNode) > 0) :
                    starDict["ROLE_NAME"] = roleNameNode[0].text.replace('饰', '').strip().replace('\n', '')
                starList.append(starDict)
            protagonistNode =starListNode[0].find_all("li")
            for i in range(len(protagonistNode)) :
                protagonist.append(starDataList[i].select('p[class="headImg-bottom-title"]')[0].select('a')[0].text)
            #演员列表不为空，返回
            if (len(starList) > 0) :
                return starList, protagonist

        return starList, protagonist

    # 获奖信息 RECEIVED_AWARDS
    def parseReceivedAwards(self, data):
        receivedAwards = []
        awardsData = data.find(attrs={"class": "moviePrice-cont j-movieaward-all"})
        # 判断是否有获奖信息
        if (awardsData is None) :
            return json.dumps(receivedAwards, ensure_ascii=False);
        allAwards = awardsData.find_all(attrs={"class": "moviePrice-tab-title"})
        # 判断是否有获奖信息
        for i in range(len(allAwards)):
            year = allAwards[i].text
            awardsDict = {'awardsYear':year}
            reListNode = allAwards[i]
            detailNode = reListNode.find_next().find_all(attrs={"class": "movPr-info-line"})
            awardsInfoList = []
            for detailIndex in range(len(detailNode)):
                # 第几届
                awardsTime = detailNode[detailIndex].find("span", class_= ["movPr-time", "movPr-hidde"]).text
                # 奖项名称
                awardsName = detailNode[detailIndex].find("a", class_= ["movPr-name"]).text
                # 奖项内容
                awardsProj = detailNode[detailIndex].find("span",class_= ["movPr-proj"]).text
                # 奖项结果
                awardsResult = detailNode[detailIndex].find("span", class_= ["movPr-result", "movPr-succes"]).text
                awardsInfo = {"awardsTime":awardsTime, "awardsName":awardsName, "awardsProj":awardsProj, "awardsResult":awardsResult, "awardsStar":""}
                awardsInfoList.append(awardsInfo)
            awardsDict["awardsInfoList"] = awardsInfoList
            receivedAwards.append(awardsDict)
        return json.dumps(receivedAwards, ensure_ascii=False);

    # 剧集介绍
    def parsePlot(self, data, parentCode):
        currentSeasonNumber = 0
        plotList = []
        nodeSoup = data.find_all(class_= ["episodePlot-list"])
        for nodeIndex in range(len(nodeSoup)) :
            plotSoup = nodeSoup[nodeIndex].find_all('li')
            for plotIndex in range(len(plotSoup)) :
                currentSeasonNumber += 1
                episodeTitle = plotSoup[plotIndex].find("p", class_="plotBody").text
                plotDict = {"mediaSourceCode" : parentCode + "_" + str(currentSeasonNumber), "currentSeasonNumber": currentSeasonNumber, "episodeTitle":episodeTitle}
                plotDict["informationSources"] = 2
                plotDict["parentSourceCode"] = parentCode
                plotList.append(plotDict)
        return plotList

    # 图片上传
    def parseImageUpload(self, webUrl) :
        ftpUrl = ''
        photoHeight = 0
        photoWidth = 0
        dateType = data_type_1_meta + data_type_separator + data_type_2_grab
        if self.imageUploadNum % 1000 == 0:
            currentStamp = DateUtils.getSysTimeSecond()
        # 取得FTP上传后地址
        ftpUrl, webFileUrl = UrlUtils().getRemoteFile(dateType, currentStamp, self.informationSources, webUrl)
        # 上传图片到FTP,返回图片尺寸
        photoHeight, photoWidth = UrlUtils().upLoadFtp(ftpUrl, webFileUrl, self.informationSources)
        return ftpUrl, photoHeight, photoWidth

if __name__ == "__main__":
    # 早期国内综艺 女人帮
    #itemUrl = "http://www.iqiyi.com/lib/m_200000114.html"
    # 早期外国综艺 柯南秀
    #itemUrl = "http://www.iqiyi.com/lib/m_204762414.html"
    # 近期综艺 亲爱的客栈
    itemUrl = "http://www.iqiyi.com/lib/m_214913614.html"
    #私人定制
    itemUrl = "http://www.iqiyi.com/lib/m_216487014.html"
    # 电影早期倩女幽魂
    itemUrl = "http://www.iqiyi.com/lib/m_200167414.html?src=search"
    itemUrl = "http://www.iqiyi.com/lib/m_211141114.html?src=search"
    # 电视剧 凤囚凰
    itemUrl = "http://www.iqiyi.com/lib/m_215238014.html?src=search"
    itemUrl = "http://www.iqiyi.com/lib/m_200877514.html?src=search"
    # 外国
    itemUrl = "http://www.iqiyi.com/lib/m_203112814.html?src=search"
    # 动漫黑色四叶草 http://www.iqiyi.com/lib/m_216384214.html
    itemUrl = "http://www.iqiyi.com/lib/m_213208414.html"
    itemUrl = "http://www.iqiyi.com/lib/m_212911214.html?src=search"
    #process = testIqiyi();
    #process.queryMetaItemMeta(itemUrl, 123)
    htmlText = HttpSpiderUtils().spiderHtmlUrl(itemUrl)
    data = BeautifulSoup(htmlText, 'html.parser')
    currentSeasonNumber = 0
    plotList = []
    nodeSoup = data.find_all(class_=["episodePlot-list"])
    # 媒资集数
    currentSeasonNumberSoup = data.find('span', attrs={"class": "title-update-progress"})
    if currentSeasonNumberSoup is not None:
        numberList = re.findall(r'\d+', currentSeasonNumberSoup.text)
        currentSeasonNumber = numberList[len(numberList) - 1]
        print(currentSeasonNumber)



