from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict, award_separator_1, award_separator_2,award_separator_3, award_separator_4, award_result_separator_left, award_result_separator_right, sleepTimeLength
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils
from meta.model.GrabStarInfo import GrabStarInfo
from meta.model.GrabStarRelation import GrabStarRelation
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
from meta.model.GrabStarDynamic import GrabStarDynamic
from meta.model.GrabStarPhoto import GrabStarPhoto
from django.db import connections
import time
import datetime
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_star, data_type_2_grab, iqiyi_default_star_photo
from pyutils.common.DateUtils import DateUtils
class IQiYiMeta :

    #明星id从200000105开始以后依次增加100
    startStarId = 200000105
    # 按演职人员id访问html地址
    star_html_url = "http://www.iqiyi.com/lib/s_%d.html"
    upLoadCount = 0
    # 当前时间戳秒
    currentStamp = 0

    #获取每台服务器明星id开始值
    def queryStartStarId(self) :
        try:
            cursor = connections["grab"].cursor()
            cursor.execute(
                "SELECT STAR_SOURCE_CODE FROM GRAB_STAR_INFO WHERE INFORMATION_SOURCES = 2 AND mod(CAST(SUBSTR(STAR_SOURCE_CODE, 1, 7) AS UNSIGNED), %d) = %d ORDER BY (CAST(STAR_SOURCE_CODE AS UNSIGNED)) DESC  LIMIT 1" % (
                len(ipDict), ipDict[localIp]))
            resultTuple = cursor.fetchall()
            cursor.close()
            if resultTuple :
                self.startStarId = int(resultTuple[0][0]) + 100
        except BaseException as e :
            print("e.message:", str(e), "查询开始明星id出现异常")
        return self.startStarId


    #查询明星详情及明星作品关系和明星相关人员关系信息
    def queryStarInfo(self):
        while True :
            try:
                countNum = 0
                starId = self.queryStartStarId()
                #print("startStarId", starId)
                for i in range(9999999) :
                    # 拼接完整的html地址
                    star_html_all_url = self.star_html_url % starId
                    #判断是否是本机要处理的数据
                    if HttpCrawlerUtils().isLocal(int(str(starId)[0:7])) :
                        print("iqiyiHtml=", star_html_all_url)
                        countNum = self.analyzeStarHtml(HttpCrawlerUtils().queryStarHtml(star_html_all_url), starId, False, countNum)
                        if countNum >= 100 :
                            time.sleep(sleepTimeLength)
                            break
                        # sleepTimeLength = random.randint(10, 60)
                        # print("暂停%d秒" % sleepTimeLength)
                        # time.sleep(sleepTimeLength)
                    starId += 100
                    print("countNum", countNum)
            except BaseException as e :
                print("e.message:", str(e), "查询开始id出错")

    # 分析补充的演职人员html
    def analyzeStarHtml(self, data, grabStarId, isUpdate, countNum):
        try:
            if data is None:
                countNum += 1
                return countNum
            allH1 = data.find(attrs={"class": "result_detail"}).find_all("h1")
            for h1 in allH1:
                starName = h1.text
                print("starName", starName)
                if starName :
                    self.analyzeStarInfoAndSave(data, str(grabStarId), starName, isUpdate)
                    #self.analyzeMediaStarInfoAndSave(data, str(grabStarId))
                    self.analyzeStarRelationAndSave(data, str(grabStarId), isUpdate)
                    self.analyzeStarAwardAndSave(data, str(grabStarId), isUpdate)
                    countNum = 0
                else:
                    countNum += 1
                return countNum
        except BaseException as e :
            print("e.message:", str(e), "解析明星姓名出现异常")
            countNum += 1
            return countNum

    #解析明星详情数据并保存至数据库
    def analyzeStarInfoAndSave(self, data, grabStarId, starName, isUpdate):
        grabStarInfo = GrabStarInfo()
        try:
            # 设置演职人员code
            grabStarInfo.starSourceCode = grabStarId
            # 设置演职人员名字
            grabStarInfo.chName = str(starName)
            # 设置抓取的信息来源2代表爱奇艺
            grabStarInfo.informationSources = 2
            # 设置抓取时间
            grabStarInfo.grabTime = DBUtil().systemDateTime()
            # 设置抓取清洗状态
            grabStarInfo.cleanStatus = 0
            # 设置清洗后id
            grabStarInfo.cleanAfterId = 0
            #设置头像url
            grabStarInfo.headImgUrl = data.find(attrs={"class": "result_pic"}).find("img")["src"]
            #print("headImgUrl=", grabStarInfo.headImgUrl)
            # starKariera = ""
            # 身高和体重默认为0
            starHeight = 0
            grabStarInfo.starHeight = starHeight
            starWeight = 0
            grabStarInfo.starWeight = starWeight
            starWeightHtml = data.find(attrs={"class": "mx_topic-item"}).find(attrs={"class": "clearfix"}).find(
                attrs={"itemprop": "weight"}).text.replace("体重：", "").strip()
            if (not DBUtil().isBlank(starWeightHtml) and starWeightHtml != "-"):
                starWeight = int(starWeightHtml.replace("kg", ""))
                grabStarInfo.starWeight = starWeight
            grabStarInfo.starKariera = data.find(attrs={"class": "mx_topic-item"}).find(
                attrs={"class": "clearfix"}).find(attrs={"itemprop": "jobTitle"}).text.replace("职业：", "").strip().replace("\n", "").replace(" ", "")
            #print("starWeight=", grabStarInfo.starWeight, "&starKariera=", grabStarInfo.starKariera)
            # 获取演职人员推荐作品名称
            if data.find(attrs={"class": "works-title textOverflow"}):
                works = data.find(attrs={"class": "site-piclist site-piclist-13777"}).find_all("li")
                #print("works", works)
                representativeWorks = ""
                for work in works :
                    workName = work.find(attrs={"class": "site-piclist_info"}).find(attrs={"class": "site-piclist_info_title"}).find("a")["title"]
                    representativeWorks += workName + ";"
                #print("representativeWorks", representativeWorks)
                grabStarInfo.representativeWorks = representativeWorks[0: len(representativeWorks) - 1]
            #获取简介
            introduceInfo = data.find(attrs={"class": "introduce-info"}).text.replace(" ", "")
            #print("introduceInfo", introduceInfo)
            grabStarInfo.briefIntroduction = introduceInfo
            leftBasicInfoValues = data.find(attrs={"class": "basicInfo-block basicInfo-left"}).find_all("dd")
            for i in range(len(leftBasicInfoValues)) :
                if i == 0 :
                    grabStarInfo.enName = leftBasicInfoValues[i].text.strip()
                if i == 1 :
                    if leftBasicInfoValues[i].text.strip() == "男" :
                        grabStarInfo.starSex = 1
                    else:
                        grabStarInfo.starSex = 0
                if i == 2 :
                    starHeightHtml = leftBasicInfoValues[i].text.strip()
                    if (not DBUtil().isBlank(starHeightHtml) and starHeightHtml != "-") :
                        starHeight = starHeightHtml.replace("cm", "")
                        grabStarInfo.starHeight = starHeight
                if i == 3 :
                    grabStarInfo.birthDate = leftBasicInfoValues[i].text.strip()
            #print("enName=", grabStarInfo.enName, "&starSex=", grabStarInfo.starSex, "&starHeight=", grabStarInfo.starHeight, "&birthDate=", grabStarInfo.birthDate)
            rightBasicInfoValues = data.find(attrs={"class": "basicInfo-block basicInfo-right"}).find_all("dd")
            for i in range(len(rightBasicInfoValues)) :
                if i == 0 :
                    #设置别名
                    grabStarInfo.anotherName = rightBasicInfoValues[i].text.strip()
                if i == 2 :
                    #设置国籍
                    grabStarInfo.starNationality = rightBasicInfoValues[i].text.strip()
                if i == 3 :
                    #设置星座
                    grabStarInfo.starSign = rightBasicInfoValues[i].text.strip()
                if i == 6 :
                    #设置兴趣爱好
                    grabStarInfo.hobbiesInterests = rightBasicInfoValues[i].text.strip()
            # print("anotherName=", grabStarInfo.anotherName, "&starNationality=", grabStarInfo.starNationality, "&starSign=",
            #       grabStarInfo.starSign, "&hobbiesInterests=", grabStarInfo.hobbiesInterests)
        except  BaseException as e :
            print("e.message:", str(e), "解析明星详情出现异常")
        #插入数据库
        try:
            if isUpdate :
                GrabStarInfo.objects.using("grab").filter(starSourceCode=grabStarId, informationSources=2).update(headImgUrl=grabStarInfo.headImgUrl, starHeight=grabStarInfo.starHeight, starWeight=grabStarInfo.starWeight,
                                                                                            starKariera=grabStarInfo.starKariera, representativeWorks=grabStarInfo.representativeWorks, briefIntroduction=grabStarInfo.briefIntroduction,
                                                                                            enName=grabStarInfo.enName, starSex=grabStarInfo.starSex, birthDate=grabStarInfo.birthDate, anotherName=grabStarInfo.anotherName,
                                                                                            starNationality=grabStarInfo.starNationality, starSign=grabStarInfo.starSign, hobbiesInterests=grabStarInfo.hobbiesInterests, cleanStatus=2)
                print("更新明星详情成功")
            else:
                # 保存数据库
                grabStarInfo.save(using="grab")
                print("保存明星详情成功")
            self.grabStarPhotoByCodeAndSource(grabStarId, 2)
        except BaseException as e:
            print("e.message:", str(e), "保存明星详情出现异常")



    # 解析明星作品关联数据并保存至数据库
    def analyzeMediaStarInfoAndSave(self, data, grabStarId):
        try :
            workTypes = data.find(attrs={"id": "block-F"}).find_all(attrs={"class": "piclist-scroll piclist-scroll-h203"})
            #print("workTypes=", type(workTypes), workTypes)
            for workType in workTypes:
                #全部都是演员（0导演1演员2编剧）
                mediaStarType = 1
                workInfos = workType.find(attrs={"class": "wrapper-cols"}).find(attrs={"class": "wrapper-piclist"}).find(attrs={"class": "site-piclist site-piclist-155203"}).find_all("li")
                #print("workInfosli", workInfos)
                for workInfo in workInfos:
                    try:
                        metaHref = workInfo.find(attrs={"class": "site-piclist_pic"}).find("a")["href"]
                        # roleName = workInfo.find(attrs={"class": "site-piclist_info"}).find(attrs={"class": "site-piclist_info_describe"}).find_all("span")[1].text
                        # print("roleName", roleName)
                        if "/lib/m_" in metaHref :
                            mediaSourceCode = self.getMiddleStr(metaHref, "http://www.iqiyi.com/lib/m_", ".html")
                            #print("mediaSourceCode=", mediaSourceCode)
                            grabMediaStarInfo = GrabMediaStarInfo()
                            grabMediaStarInfo.starSourceCode = grabStarId
                            # 设置抓取的信息来源2代表爱奇艺
                            grabMediaStarInfo.informationSources = 2
                            # 设置抓取时间
                            grabMediaStarInfo.grabTime = DBUtil().systemDateTime()
                            # 设置抓取清洗状态
                            grabMediaStarInfo.cleanStatus = 0
                            # 设置清洗后id
                            grabMediaStarInfo.cleanAfterId = 0
                            # 设置媒资类型
                            grabMediaStarInfo.mediaStarType = mediaStarType
                            # 设置媒资code
                            grabMediaStarInfo.mediaSourceCode = mediaSourceCode
                            # 设置清洗后演员源id (yff0127add)
                            grabMediaStarInfo.cleanStarSourceId = 0
                            # 设置清洗后媒资数据源id
                            grabMediaStarInfo.cleanMediaSourceId = 0
                            grabMediaStarInfo.save(using="grab")
                    except BaseException as e:
                        print("e.message:", str(e), "解析明星媒资关联媒资code或保存至数据库出现异常")
        except BaseException as e:
            print("e.message:", str(e), "解析明星媒资关联媒资类型出现异常")

    # 解析明星人物关系数据并保存至数据库
    def analyzeStarRelationAndSave(self, data, grabStarId, isUpdate):
        try :
            if data.find(attrs={"class": "center-star"}) :
                relations = data.find(attrs={"class": "center-star"}).find_all("p")
                #print("relations", type(relations), relations)
                #从第二个开始，因为第一个是本人
                for i in range(1, len(relations)) :
                    try :
                        relationCode = ""
                        if i == 1 :
                            relationCode = data.find(attrs={"class": "sub-star left-top-star"}).find("a")["href"][27:36]
                        if i == 2 :
                            relationCode = data.find(attrs={"class": "sub-star right-top-star"}).find("a")["href"][27:36]
                        if i == 3 :
                            relationCode = data.find(attrs={"class": "sub-star right-center-star"}).find("a")["href"][27:36]
                        if i == 4 :
                            relationCode = data.find(attrs={"class": "sub-star right-bottom-star"}).find("a")["href"][27:36]
                        if i == 5 :
                            relationCode = data.find(attrs={"class": "sub-star left-bottom-star"}).find("a")["href"][27:36]
                        if i == 6 :
                            relationCode = data.find(attrs={"class": "sub-star left-center-star"}).find("a")["href"][27:36]
                        #print("relationCode", relationCode)
                        grabStarRelation = GrabStarRelation()
                        grabStarRelation.starSourceCode = grabStarId
                        grabStarRelation.starRelation = relations[i].text
                        # 设置抓取的信息来源2代表爱奇艺
                        grabStarRelation.informationSources = 2
                        # 设置抓取时间
                        grabStarRelation.grabTime = DBUtil().systemDateTime()
                        # 设置抓取清洗状态
                        grabStarRelation.cleanStatus = 0
                        # 设置清洗后id
                        grabStarRelation.cleanAfterId = 0
                        # 设置清洗后演员源id(yff0127add)
                        grabStarRelation.cleanStarSouceId = 0
                        # 设置清洗后关系人源id
                        grabStarRelation.cleanStarRalationId = 0
                        grabStarRelation.relationSourceCode = relationCode
                        #print("starRelation=", grabStarRelation.starRelation, "&relationCode=", grabStarRelation.relationSourceCode)
                        if isUpdate :
                            count = GrabStarRelation.objects.using("grab").filter(starSourceCode=grabStarId, relationSourceCode=relationCode, informationSources=2).count()
                            if count > 0 :
                                GrabStarRelation.objects.using("grab").filter(starSourceCode=grabStarId, relationSourceCode=relationCode, informationSources=2).update(starRelation=grabStarRelation.starRelation, cleanStatus=2)
                            else :
                                grabStarRelation.save(using="grab")
                        else:
                            grabStarRelation.save(using="grab")
                    except BaseException as e:
                        print("e.message:", str(e), "解析明星人物关系code出现异常")
            else:
                if data.find(attrs={"class" : "relateStar_list relateStar_hidePopUl clearfix"}) :
                    relationInfos = data.find(attrs={"class" : "relateStar_list relateStar_hidePopUl clearfix"}).find_all("li")
                    for relationInfo in relationInfos :
                        try:
                            #这里href的值是""//www.iqiyi.com/lib/s_206307105.html""这种格式,没有带http:
                            relationCode = relationInfo.find(attrs={"class", "relateStar_info"}).find(attrs={"class", "relateStar_title relateStar_relationNam"}).find("a")["href"][22:31]
                            starRelation = relationInfo.find(attrs={"class", "relateStar_info"}).find(attrs={"class", "relateStar_title relateStar_relationNam"}).find("span").find_all("em")[1].text
                            grabStarRelation = GrabStarRelation()
                            grabStarRelation.starSourceCode = grabStarId
                            grabStarRelation.starRelation = starRelation
                            # 设置抓取的信息来源2代表爱奇艺
                            grabStarRelation.informationSources = 2
                            # 设置抓取时间
                            grabStarRelation.grabTime = DBUtil().systemDateTime()
                            # 设置抓取清洗状态
                            grabStarRelation.cleanStatus = 0
                            # 设置清洗后id
                            grabStarRelation.cleanAfterId = 0
                            grabStarRelation.relationSourceCode = relationCode
                            # 设置清洗后演员源id(yff0127add)
                            grabStarRelation.cleanStarSouceId = 0
                            # 设置清洗后关系人源id
                            grabStarRelation.cleanStarRalationId = 0
                            # print("相关明星starRelation=", grabStarRelation.starRelation, "&relationCode=",
                            #       grabStarRelation.relationSourceCode)
                            if isUpdate:
                                count = GrabStarRelation.objects.using("grab").filter(starSourceCode=grabStarId,
                                                                                      relationSourceCode=relationCode, informationSources=2).count()
                                if count > 0:
                                    GrabStarRelation.objects.using("grab").filter(starSourceCode=grabStarId,
                                                                                  relationSourceCode=relationCode, informationSources=2).update(
                                        starRelation=grabStarRelation.starRelation, cleanStatus=2)
                                else:
                                    grabStarRelation.save(using="grab")
                            else:
                                grabStarRelation.save(using="grab")
                        except BaseException as e:
                            print("e.message:", str(e), "解析相关明星信息出现异常")
        except BaseException as e:
            print("e.message:", str(e), "解析明星人物关系类型出现异常")

    # 解析明星获奖信息并保存至数据库
    def analyzeStarAwardAndSave(self, data, grabStarId, isUpdate):
        try:
            if data.find(attrs={"class": "m-getPrice-tab j-starAward-all"}):
                receivedAwards = ""
                allAwards = data.find(attrs={"class": "m-getPrice-tab j-starAward-all"}).find_all(attrs={"class": "getPrice-detail-cont"})
                for i in range(len(allAwards)) :
                    year = allAwards[i].find(attrs={"class": "getPrice-tab-title"}).find("span").text
                    receivedAwards = receivedAwards + year + award_separator_1
                    sameAwardInfos = allAwards[i].find_all(attrs={"class": "getPrice-info-table"})
                    for k in range(len(sameAwardInfos)) :
                        awardInfos = sameAwardInfos[k].find_all("li")
                        for j in range(len(awardInfos)) :
                            tabPrResult = ""
                            tabPrTime = awardInfos[j].find(attrs={"class": "tabPr-time"}).text
                            tabPrName = awardInfos[j].find(attrs={"class": "tabPr-name"}).text
                            tabPrProj = awardInfos[j].find(attrs={"class": "tabPr-proj"}).text
                            if awardInfos[j].find(attrs={"class": "tabPr-result tabPr-result"}) :
                                tabPrResult = awardInfos[j].find(attrs={"class": "tabPr-result tabPr-result"}).text
                            elif awardInfos[j].find(attrs={"class": "tabPr-result tabPr-succes"}):
                                tabPrResult = awardInfos[j].find(attrs={"class": "tabPr-result tabPr-succes"}).text
                            receivedAwards = receivedAwards + tabPrTime + tabPrName + award_separator_2 + tabPrProj + award_result_separator_left + tabPrResult + award_result_separator_right
                            if k != len(sameAwardInfos) - 1 or j != len(awardInfos) - 1 :
                                receivedAwards += award_separator_3
                    if i != len(allAwards) - 1:
                        receivedAwards += award_separator_4
                #print("receivedAwards=", receivedAwards)
                grabStarDynamic = GrabStarDynamic()
                grabStarDynamic.starSourceCode = grabStarId
                # 设置抓取的信息来源2代表爱奇艺
                grabStarDynamic.informationSources = 2
                # 设置抓取时间
                grabStarDynamic.grabTime = DBUtil().systemDateTime()
                # 设置抓取清洗状态
                grabStarDynamic.cleanStatus = 0
                # 设置清洗后id
                grabStarDynamic.cleanAfterId = 0
                grabStarDynamic.receivedAwards = receivedAwards
                grabStar = GrabStarInfo.objects.using("grab").values("starId", "cleanAfterId").filter(starSourceCode=grabStarId,
                                                                                      informationSources=2)
                if grabStar:
                    if isUpdate:
                        grabStarDynamic.cleanStatus = 2
                        grabStarDynamic.cleanAfterId = grabStar[0]["cleanAfterId"]
                        #print("cleanAfterId", grabStarDynamic.cleanAfterId)
                    grabStarDynamic.starId = grabStar[0]["starId"]
                    grabStarDynamic.save(using="grab")
                    print("保存或更新明星starId:", grabStarDynamic.starId, "奖项成功")
        except BaseException as e:
            print("e.message:", str(e), "解析明星奖项出现异常")

    # 替换
    def getMiddleStr(self, content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]


    def updateStarInfo(self):
        print("调用更新爱奇艺明星图片时间是", datetime.datetime.now())
        while True :
            try:
                cursor = connections["grab"].cursor()
                cursor.execute(
                    "SELECT  STAR_SOURCE_CODE FROM GRAB_STAR_INFO WHERE CLEAN_STATUS != 2 AND INFORMATION_SOURCES = 2  AND mod(CAST(SUBSTR(STAR_SOURCE_CODE, 1, 7) AS UNSIGNED), %d) = %d ORDER BY (CAST(STAR_SOURCE_CODE AS UNSIGNED)) DESC  LIMIT 10" % (
                    len(ipDict), ipDict[localIp]))
                resultTuple = cursor.fetchall()
                cursor.close()
                if resultTuple :
                    for idTuple in resultTuple:
                        strGrabStarCode = idTuple[0]
                        #print(strgrabStarId, type(strgrabStarId))
                        star_html_all_url = self.star_html_url % int(strGrabStarCode)
                        print("iqiyiUpdateHtml=", star_html_all_url)
                        self.analyzeStarHtml(HttpCrawlerUtils().queryStarHtml(star_html_all_url), strGrabStarCode, True, 0)
                    print("重新调用")
                else :
                    print("更新爱奇艺明星信息暂无数据当前时间是", datetime.datetime.now(), "休息", sleepTimeLength)
                    time.sleep(sleepTimeLength)
                    print("更新爱奇艺明星信息暂无数据休息后时间是", datetime.datetime.now())
            except BaseException as e:
                print("e.message:", str(e), "获取要更新的明星code出现异常")

    #根据明星code和来源抓取明星图片信息
    def grabStarPhotoByCodeAndSource(self, grabStarId, informationSources) :
        grabStar = GrabStarInfo.objects.using("grab").values("starId", "headImgUrl", "cleanAfterId").filter(starSourceCode=grabStarId,
                                                                              informationSources=informationSources)
        if grabStar:
            self.upLoadCount, self.currentStamp = UrlUtils().upLoadPhotoToFtp(grabStar[0]["starId"], grabStarId , informationSources, grabStar[0]["headImgUrl"], grabStar[0]["cleanAfterId"], self.upLoadCount, self.currentStamp, list())

    #抓取明星图片数据
    def grabStarPhoto(self):
        upLoadCount = 0
        # 当前时间戳秒
        currentStamp = 0
        print("调用抓取爱奇艺明星图片时间是", datetime.datetime.now())
        while True :
            try:
                cursor = connections["grab"].cursor()
                cursor.execute(
                    "SELECT STAR_ID, STAR_SOURCE_CODE, INFORMATION_SOURCES, HEAD_IMG_URL, CLEAN_AFTER_ID FROM GRAB_STAR_INFO WHERE CLEAN_STATUS != 3 AND  INFORMATION_SOURCES = 2 AND mod(STAR_ID, %d) = %d ORDER BY STAR_ID DESC LIMIT 10" % (
                    len(ipDict), ipDict[localIp]))
                resultTuple = cursor.fetchall()
                cursor.close()
                if resultTuple :
                    starIdList = list()
                    for starInfoTuple in resultTuple:
                        upLoadCount, currentStamp = UrlUtils().upLoadPhotoToFtp(starInfoTuple[0], starInfoTuple[1],
                                                                                starInfoTuple[2], starInfoTuple[3],
                                                                                starInfoTuple[4], upLoadCount,
                                                                                currentStamp, starIdList)
                    if starIdList:
                        GrabStarInfo.objects.using("grab").filter(starId__in=starIdList).update(cleanStatus=3)
                    print("重新调用")
                else :
                    print("抓取爱奇艺明星图片暂无数据当前时间是", datetime.datetime.now(), "休息", sleepTimeLength)
                    time.sleep(sleepTimeLength)
                    print("抓取爱奇艺明星图片暂无数据休息后时间是", datetime.datetime.now())
            except BaseException as e:
                print("e.message:", str(e), "获取要抓取爱奇艺明星图片出现异常")
                raise









