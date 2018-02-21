import requests
from bs4 import BeautifulSoup
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
import re
import json
from meta.model.GrabMediaInfo import GrabMediaInfo
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict

class YoukuMedia :
    media_html_url = "http://list.youku.com/category/show/c_97.html?spm=a2h1n.8251845.filterPanel.5~1~3!2~A"
    media_subset_url = "http://list.youku.com/show/point?id=mediaSourceCode&stage=reload_showid&callback=jQuery"
    media_type_url = "http://list.youku.com/show/module?id=mediaSourceCode&tab=point&callback=jQuery"
    def iqyiMediaGrab(self ):
        htmlText = self.parsResultHtml(self.media_html_url)
        #获取分类
        filterPanel = htmlText.find(attrs={'id': 'filterPanel'})

        filterPanelDiv =filterPanel.find_all("div")

        yearDiv = filterPanelDiv[3]

        ulAll = yearDiv.find("ul")
        liall = ulAll.find_all("li")
        for i in range(len(liall)):
            a = liall[i].find("a")
            if (a is not None) :
                url = "http:"+ str(a.get("href"))
                html = self.parsResultHtml(url)
                self.parsListalso(html)


        #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    #获取页面列表中详情页Url地址
    def parsListalso(self, html):
        ykColAll = html.find_all(attrs={'class': 'yk-col4 mr1'})


        for ykCol in ykColAll :
            ykPlayUrl = ykCol.find("a")["href"]
            ulAll = ykCol.find_all(attrs={'class': 'p-info pos-bottom'})
            span = ulAll[0].find("span")
            ykType = span.text

            if "http" not in ykPlayUrl:
                ykPlayUrl = "http:" + ykPlayUrl
            if ("资料" in ykType) :
                ykDetailsUrl = ykPlayUrl
            else :

                ykPlayHtml = self.parsResultHtml(ykPlayUrl)
                basicTitle = ykPlayHtml.find(attrs={'id': 'module_basic_title'})
                ykDetailsUrl = basicTitle.find(attrs={'class': 'desc-link'})["href"]
                if "http" not in ykDetailsUrl:
                    ykDetailsUrl = "http:" + ykDetailsUrl
            #获取节目集详情页信息
            ykDetailsHtml = self.parsResultHtml(ykDetailsUrl)
            grabMediaInfo = self.parsYkDetailsContext(ykDetailsHtml, ykDetailsUrl)
            self.parsSubsetId(ykDetailsHtml,grabMediaInfo)



            #print("-----------------------------------------------------------------", ykDetailsUrl)

    #获取详情页基础信息
    def parsYkDetailsContext(self, ykDetailsHtml, ykDetailsUrl):
        # 主演
        protagonist = []


        url =ykDetailsUrl.split("/")
        mediaSourceCode = url[len(url)-1].split(".")[0].split("_")[1]
        basicData = ykDetailsHtml.find(attrs={'class': 'mod mod-new'})
        # 获取子集信息
        basicSubsetData = ykDetailsHtml.find(attrs={'class': 'mod-area-left'})

        mediaDirector , productionContry ,subordinateType = self.parsMediaDirector(basicData)
        #获取图片地址
        imgDiv = basicData.find(attrs={'class': 'yk-pack p-list'})
        img = imgDiv.find("img")
        imgUrl = img["src"]
        baseContext = basicData.find("ul")
        title = baseContext.find(attrs={'class': 'p-row p-title'})
        types = title.find_all("a")[0].text
        mediaType = self.parseMediaType(types)
        name = title.text.split("：")[1][:-6]
        # 发行年份
        mediaYear = title.text.split("：")[1][:-2][-4 :]

        #又名
        alternateName = baseContext.find(attrs={'class': 'p-alias'}).text
        #上映时间
        releaseTimes = baseContext.find_all(attrs={'class': 'pub'})
        #评分
        mediaScore = 0
        if len(releaseTimes) > 1:
            releaseTime = releaseTimes[1].text[5:]
        else:
            releaseTime = ""
        mediaScoreHtml = baseContext.find(attrs={'class': 'star-num'})
        if mediaScoreHtml == None:
            mediaScore = 0
        else :
            mediaScore = mediaScoreHtml.text
        #获取主演
        mediaActorLi =  baseContext.find(attrs={'class': 'p-performer'})
        if mediaActorLi is not None :
            #获取a标签内容
            mediaActorALL = mediaActorLi.find_all("a")
            for mediaActorA in mediaActorALL :
                actor =  mediaActorA.text
                protagonist.append(actor)
            mediaActor = protagonist

        #获取简介
        mediaIntroData = basicData.find(attrs={'class': 'p-row p-intro'})

        mediaIntro = mediaIntroData.find_all("span")[1].text

        try:
            # 保存媒资主表
            grabMediaInfo = GrabMediaInfo()
            # 媒资主表ID
            mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")

            grabMediaInfo.mediaId = mediaId
            grabMediaInfo.mediaSourceCode = mediaSourceCode
            grabMediaInfo.informationSources = 1
            grabMediaInfo.mediaType = mediaType
            grabMediaInfo.cnName = name
            grabMediaInfo.grabWebUrl = ykDetailsUrl
            grabMediaInfo.mediaWebCode = ""
            grabMediaInfo.alternateName = alternateName
            grabMediaInfo.mediaYear = mediaYear
            grabMediaInfo.mediaLanguage = ""
            grabMediaInfo.mediaTimes = 0
            grabMediaInfo.mediaIntro = mediaIntro
            grabMediaInfo.subordinateType = subordinateType
            grabMediaInfo.productionContry = productionContry
            #未处理
            grabMediaInfo.currentSeasonNumber = 1
            grabMediaInfo.posterImgUrl = imgUrl
            grabMediaInfo.mediaDirector = mediaDirector
            grabMediaInfo.mediaActor = mediaActor
            grabMediaInfo.releaseTime = releaseTime
            grabMediaInfo.totalSeason = 1
            grabMediaInfo.currentSeason = 1
            grabMediaInfo.grabTime = DBUtil().systemDateTime()
            grabMediaInfo.cleanStatus = 0
            grabMediaInfo.cleanAfterId = 0
            grabMediaInfo.cleanParentMediaId = 0

            grabMediaInfo.save(using="grab", force_insert=True)
            # 获取影人信息
            self.parsMediaFilmHtml(ykDetailsHtml)

        except BaseException as e:
            print("e.message:", str(e), "保存媒资信息出现异常")
        return grabMediaInfo



    #获取影人详情页Url 地址
    def parsMediaFilmHtml(self,ykDetailsHtml):
        divRight = ykDetailsHtml.find(attrs={'class': 'mod-area-right'})
        filmUrlAll = divRight.find_all(attrs={'class': 'c555 f13'})
        for filmUrl in filmUrlAll :
            url = filmUrl["href"]
            if "http" not in url:
                url = "http:" + url
            ykFilmhtml = self.parsResultHtml(url)
            self.parsMediaFilmDetailsHtml(ykFilmhtml)


    #获取影人详情页信息
    def parsMediaFilmDetailsHtml(self, ykFilmhtml):
        divStar = ykFilmhtml.find(attrs={'class': 'box-star'})
        print(divStar)
        imgUrl = divStar.find("img")["src"]
        cname = divStar.find("dt").text
        info = divStar.find(attrs={'class': 'info'})
        spanAll = info.find_all("span")
        #中文名称
        chName = ""
        #英文名称
        enName = ""
        #别名
        anotherName = ""
        #性别
        starSex = ""
        # 国籍
        starNationality = ""
        # 出生日期
        birthDate = ""
        #星座
        starSign = ""
        # 职业
        starKariera = ""
        #来源
        informationSources = 1
        #j奖项
        receivedAwards = ""


        for span in spanAll :
            if "性别：" in str(span) :
                starSex = span.text.split("：")[1]
                print(starSex)
            if "别名：" in str(span) :
                text = span.text
                anotherName = text.split("：")[1]
                print(anotherName)
            if "地区：" in str(span) :
                starNationality = span.text.split("：")[1]
                print(starNationality)
            if "生日：" in str(span) :
                birthDate = span.text.split("：")[1]
                print(birthDate)
            if "星座" in str(span) :
                starSign = span.text.split("：")[1]
                print(starSign)
            if "职业：" in str(span) :
                starKariera = span.text.split("：")[1]
                print(starKariera)
        #获取简介
        briefIntroductionSpan = divStar.find(attrs={'class': 'long noshow'})
        briefIntroduction = briefIntroductionSpan.text
        #奖项
        awardsDD = divStar.find(attrs={'class': 'awards'})
        aAll = awardsDD.find("p").find_all("a")
        print(aAll)
        prize = aAll[0].text
        content = awardsDD.text.split(prize)
        year = re.sub("\D", "", content[0])
        mediaName = aAll[1].text
        AwardName = content[1].split(mediaName)[0]

        receivedAwards = year+":"+ prize+"/"+AwardName+"/"+mediaName
        print(receivedAwards)
        print(imgUrl,cname,starKariera,starSign,birthDate,starNationality,anotherName,starSex,briefIntroduction)

    #获取子集信息
    def parsSubsetId(self,ykDetailsHtml,grabMediaInfo):
        ykScripts = ykDetailsHtml.find_all("script")

        for ykScript in ykScripts :
            if "videoId" in str(ykScript):
                scriptStr = ykScript.text[17:][:-1]
                scriptStrs = scriptStr.split(",")
                for scriptStr in scriptStrs :
                    if "showid:" in scriptStr:
                        #获取子集集数分类（如果电视剧：1-40 、综艺 201801）

                        showid =re.sub("\D", "", scriptStr)

                        listUrl = self.media_subset_url.replace('mediaSourceCode', str(showid))
                        print(listUrl)
                        jsonStr = HttpSpiderUtils().spiderHtmlUrl(listUrl)
                        jsonStr = jsonStr[24:][:-2]
                        jsonObj = json.loads(str(jsonStr))
                        divDate = jsonObj['html']
                        self.parsSubset(divDate ,grabMediaInfo)




    # 获取子集集数分类（如果电视剧：1-40 、综艺 201801）
    def parsMediaSubsetType(self,showid):
        listUrl = self.media_type_url.replace('mediaSourceCode', str(showid))
        print(listUrl)
        jsonStr = HttpSpiderUtils().spiderHtmlUrl(listUrl)
        jsonStr = jsonStr[24:][:-2]
        jsonObj = json.loads(str(jsonStr))
        divDate = jsonObj['html']
        divDate = BeautifulSoup(divDate, 'html.parser')
        liAll = divDate.find_all("li")
        return liAll

    #获取子集信息
    def parsSubset(self, divDate,grabMediaInfo):
        divDate = str(divDate)
        divDate = BeautifulSoup(divDate, 'html.parser')
        divAll = divDate.find_all(attrs={'class': 'p-item-info'})
        for divitem in divAll :
            itemA = divitem.find(attrs={'class': 'item-title'}).find("a")
            print(itemA)
            cName = itemA.text
            itemUrl = itemA["href"]
            itemStr = itemUrl[:len(itemUrl) - 1].split(".")
            pSourceCode = grabMediaInfo.mediaSourceCode
            grabMediaInfo.parentSourceCode = pSourceCode
            grabMediaInfo.cnName = cName
            grabMediaInfo.grabWebUrl = itemUrl
            grabMediaInfo.mediaIntroData = itemStr

            mediaSourceCode = 0
            for item in itemStr :

                if "id" in item :
                    mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")
                    grabMediaInfo.mediaId = mediaId
                    mediaSourceCode = item.split("_")[2]
                    grabMediaInfo.mediaSourceCode = mediaSourceCode
            currentSeasonNumber = re.sub("\D", "", cName)
            grabMediaInfo.currentSeason = currentSeasonNumber
            print(mediaSourceCode,itemUrl,cName,currentSeasonNumber)

    # 获取导演\地区
    def parsMediaDirector(self, basicData):
        liAll = basicData.find_all("li")
        # 导演
        mediaDirectorList = []
        productionContry = ""
        subordinateType = []
        for li in liAll :
            #print(li.text)

            if "导演" in li.text :
                aAll = li.find_all("a")
                for a in aAll :
                    mediaDirectorList.append(a.text)
            if "地区" in li.text :
                a = li.find("a")
                productionContry = a.text
            if "类型" in li.text :
                aAll = li.find_all("a")
                for a in aAll:
                    subordinateType.append(a.text)


        return mediaDirectorList , productionContry , subordinateType

    # 获取html 页面内容
    def parsResultHtml(self, listUrl):

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
        # 解析HTML
        htmlText = BeautifulSoup(htmlText, 'html.parser')

        return htmlText

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
        else:
            return mediaType

    def queryYKMediaGrab(self):
        YoukuMedia().iqyiMediaGrab()


if __name__ == '__main__':
    YoukuMedia().iqyiMediaGrab()

