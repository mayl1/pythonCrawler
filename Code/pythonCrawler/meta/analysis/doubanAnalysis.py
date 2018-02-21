import requests
import time
import json
import re
from bs4 import BeautifulSoup
from django.db import connections
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict,sleepTimeLength,award_separator_1, award_separator_2,award_separator_3, award_separator_4
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils
from meta.model.MetaModel import MetaInfo
from meta.model.GrabStarInfo import GrabStarInfo
from meta.model.GrabMediaStarInfo import GrabMediaStarInfo
from meta.model.GrabStarDynamic import GrabStarDynamic
import datetime
from crawlerMeta.utils.urlContentUtil import UrlUtils

class DoubanAnalysis :
    # 搜索索引初始
    search_start = 0
    # 按演职人员id访问api地址
    star_url = "https://api.douban.com/v2/movie/celebrity/starId?apikey=0fbfdca9eedf20c82f3f95fdcc9d6258"
    # 搜索索引初始
    star_start = 0
    # 按演职人员id访问html地址
    star_html_url = "https://movie.douban.com/celebrity/starId/"
    # 演员和作品关系地址
    media_star_url = 'https://movie.douban.com/celebrity/starId/movies?start=page&format=pic&sortby=time&'
    media_star_url_no = 'https://movie.douban.com/celebrity/starId/movies?start=0&format=pic&sortby=time&'
    # 演员奖项地址
    prize_star_url = 'https://movie.douban.com/celebrity/starId/awards/'
    # 访问时间设置
    lengthAccess = 1
    htmlLengthAccess = 0.5
    upLoadCount = 0
    # 当前时间戳秒
    currentStamp = 0


    # 演职人员详情页信息
    def queryItemStar(self, soup):
        # 获取把html信息转成json
        js_dict = json.loads(soup.text)
        avatars = js_dict['avatars']
        # 获取演职人员头像
        img = avatars['large']
        # 获取演职人员名字
        name = js_dict['name']
        # 获取性别
        gender = js_dict['gender']
        # 获取演职人员豆瓣id
        grabStarId = js_dict['id']
        # 获取演职人员英文名字
        name_en = js_dict['name_en']
        # 获取演职人员国籍
        born_place = js_dict['born_place']
        # 演职人员性别转成需要代码（1是男0是女）
        if (gender == "男"):
            # 设置性别男为1
            sex = 1
        else:
            # 设置性别女为0
            sex = 0
        grabStarInfo = GrabStarInfo()
        # 设置演职人员code
        grabStarInfo.starSourceCode = grabStarId
        # 设置演职人员名字
        grabStarInfo.chName = str(name)
        # 设置演职人员英文名字
        grabStarInfo.enName = str(name_en)
        # 设置演职人员性别
        grabStarInfo.starSex = sex
        # 设置演职人员国籍
        grabStarInfo.starNationality = str(born_place)
        # 设置抓取的信息来源0代表豆瓣
        grabStarInfo.informationSources = 0
        # 设置抓取时间
        grabStarInfo.grabTime = DBUtil().systemDateTime()
        # 设置抓取清洗状态
        grabStarInfo.cleanStatus = 0
        # 设置清洗后id
        grabStarInfo.cleanAfterId = 0
        # 设置演职人员头像（能抓取的最大图）
        grabStarInfo.headImgUrl = str(img)
        try:
            # 保存数据库
            grabStarInfo.save(using="grab")
            print("入库")
            self.grabStarPhoto(grabStarId)
        except BaseException as e:
            print("e.message:", str(e))

    # 分析补充的演职人员html
    def analyzeStarHtml(self, data, grabStarId):
        try:
            if data is None:
                return
            # 获取演职人员基本信息
            xinxi = data.find(attrs={'class': 'info'}).find_all("ul")
            # 获取演职人员简介
            jianjie = data.find(attrs={'id': 'intro'}).find(attrs={'class': 'bd'})
            if jianjie.find(attrs={'class': 'all hidden'}):
                # 获取研制人眼更多简介
                jianjie = data.find(attrs={'id': 'intro'}).find(attrs={'class': 'bd'}).find(
                    attrs={'class': 'all hidden'})
                briefIntroduction = jianjie.text.replace(" ", "")
            else:
                # 获取演职人员简介
                briefIntroduction = jianjie.text.replace(" ", "")

            # 获取演职人员代表作品名称
            works = data.find(attrs={'class': 'list-s'}).find_all("img")
            representativeWorks = ""
            for k in works:
                try:
                    title = k['title']
                    representativeWorks += title + ";"
                except BaseException as e:
                    print("没有作品")

            for info in xinxi:
                # 解析用户基本信息
                names = info.find_all("li")
                #print(names)
                for li in names:
                    starSign = ""
                    # 演职人员出生日期
                    birthDate = ""
                    # 演职人员职业
                    starKariera = ""
                    # 演职人员更过英文名字
                    en_name = ""
                    # 演职人员更过中文名字
                    ch_name = ""
                    name = li.text
                    #print(name)
                    if ('星座' in name):
                        starSign = name.replace("星座:", "").strip().replace("\n", "").replace(" ", "")
                        #print(starSign)
                    if ('出生日期' in name):
                        birthDate = name.replace("出生日期:", "").strip().replace("\n", "").replace(" ", "")
                        #print(birthDate)
                    if ('职业' in name):
                        starKariera = name.replace("职业:", "").strip().replace("\n", "").replace(" ", "")
                        #print(starKariera)
                    if ('更多外文名' in name):
                        en_name = name.replace("更多外文名:", "").strip().replace("\n", "").replace(" ", "")
                        #print(en_name)
                    if ('更多中文名' in name):
                        ch_name = name.replace("更多中文名:", "").strip().replace("\n", "").replace(" ", "")
                        #print(ch_name)
                anotherName = ch_name + ";" + en_name
                if (anotherName == ";"):
                    anotherName = ''
                try:
                    # 更新此用户的信息
                    GrabStarInfo.objects.using("grab").filter(starSourceCode=grabStarId, informationSources=0).update(
                        starSign=starSign, birthDate=birthDate, starKariera=starKariera,
                        briefIntroduction=briefIntroduction, anotherName=anotherName,
                        representativeWorks=representativeWorks, cleanStatus=2)
                    print("修改成功")
                except BaseException as e:
                    print("修改出错")

        except BaseException as e:
            print("解析出错")

    def analyzeStarPrizeHtml(self, data, grabStarId):
        try:
            data = data.find_all(attrs={"class": "awards"})
            receivedAwards = ""
            for k in range(len(data)):
                nian = data[k].find("h2")
                receivedAwards = receivedAwards + str(nian.text) + award_separator_1
                val = data[k].find_all(attrs={"class": "award"})
                for i in range(len(val)):
                    list = val[i].find_all("li")
                    prize = ""
                    for a in list[0]:
                        prize += a.string
                    prizes = list[1].string
                    works = list[2].string
                    receivedAwards += prize + award_separator_2 + prizes + award_separator_2 + works
                    if i != len(val) - 1:
                        receivedAwards += award_separator_3
                if k != len(data) - 1:
                    receivedAwards += award_separator_4

            grabStarDynamic = GrabStarDynamic()
            # 设置演员原始code
            grabStarDynamic.starSourceCode = grabStarId
            # 设置抓取的信息来源
            grabStarDynamic.informationSources = 0
            # 设置抓取时间
            grabStarDynamic.grabTime = DBUtil().systemDateTime()
            # 设置抓取清洗状态
            grabStarDynamic.cleanStatus = 0
            # 设置清洗后id
            grabStarDynamic.cleanAfterId = 0
            # 设置奖项
            grabStarDynamic.receivedAwards = receivedAwards
            # 保存
            grabStar = GrabStarInfo.objects.using("grab").values("starId").filter(starSourceCode=grabStarId,
                                                                                  informationSources=0)
            if grabStar:
                grabStarDynamic.starId = grabStar[0]["starId"]
                grabStarDynamic.save(using="grab")
                print("保存或更新明星starId:", grabStarDynamic.starId, "奖项成功")
        except BaseException as e:
            print("e.message:", str(e))

    def analyzeMediaStarHtml(self, data, grabStarId):
        try:
            data = data.find(attrs={"id": "wrapper"}).find(attrs={"id": "content"}).find(
                attrs={"class": "article"}).find_all("h6")
            for info in data:
                name = info.find("a")
                nian = info.find_all("span")
                code = re.findall(r'(\w*[0-9]+)\w*', name["href"])[0]
                msType = nian[-1].text
                grabMediaStarInfo = GrabMediaStarInfo()
                # 设置媒资源code
                grabMediaStarInfo.mediaSourceCode = code
                # 设置演员源code
                grabMediaStarInfo.starSourceCode = grabStarId
                # 设置信息来源
                grabMediaStarInfo.informationSources = 0
                # 设置抓取时间
                grabMediaStarInfo.grabTime = DBUtil().systemDateTime()
                # 设置抓取清洗状态
                grabMediaStarInfo.cleanStatus = 0
                # 设置清洗后id
                grabMediaStarInfo.cleanAfterId = 0
                # 0导演1演员2编剧3制片4配音5作曲6自己
                try:
                    if ('导演' in msType):
                        #print("导演")
                        mediaStarType = 0
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('演员' in msType):
                        #print("演员")
                        mediaStarType = 1
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('编剧' in msType):
                        #print("编剧")
                        mediaStarType = 2
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('制片' in msType):
                        #print("制片")
                        mediaStarType = 3
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('配音' in msType):
                        #print("配音")
                        mediaStarType = 4
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('作曲' in msType):
                        #print("作曲")
                        mediaStarType = 5
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                    if ('自己' in msType):
                        #print("自己")
                        mediaStarType = 6
                        # 设置人物类型
                        grabMediaStarInfo.mediaStarType = mediaStarType
                        # 保存数据库
                        grabMediaStarInfo.save(using="grab")
                except BaseException as e:
                    print("e.message翻译类型:", str(e))
        except BaseException as e:
            print("e.message获取列表:", str(e))

    #  获取编码
    def queryNo(self, data):
        try:
            # print(data)
            if data.find(attrs={"id": "wrapper"}):
                NO = data.find(attrs={"id": "wrapper"}).find(attrs={"id": "content"}).find("h1")
                # print(NO)
                no = re.findall(r'(\w*[0-9]+)\w*', NO.text)[0]
                return no
        except BaseException as e:
            print("e.message解析条数:", str(e))
        return 0

#抓取明星图片数据
    def grabStarPhoto(self,starSourceCode):
        print("调用抓取豆瓣明星图片时间是", datetime.datetime.now())
        try:
            cursor = connections["grab"].cursor()
            cursor.execute("SELECT STAR_ID, STAR_SOURCE_CODE, INFORMATION_SOURCES, HEAD_IMG_URL, CLEAN_AFTER_ID FROM GRAB_STAR_INFO WHERE INFORMATION_SOURCES = 0 AND STAR_SOURCE_CODE = %s  ORDER BY STAR_ID DESC" % starSourceCode)
            resultTuple = cursor.fetchall()
            print(resultTuple)
            cursor.close()
            if resultTuple :
                starIdList = list()
                for starInfoTuple in resultTuple:
                    self.upLoadCount, self.currentStamp = UrlUtils().upLoadPhotoToFtp(starInfoTuple[0], starInfoTuple[1], starInfoTuple[2], starInfoTuple[3], starInfoTuple[4], self.upLoadCount, self.currentStamp, starIdList)
            else :
                print("抓取豆瓣明星图片暂无数据当前时间是", datetime.datetime.now(), "休息", sleepTimeLength)
                time.sleep(sleepTimeLength)
                print("抓取豆瓣明星图片暂无数据休息后时间是", datetime.datetime.now())
        except BaseException as e:
            print("e.message:", str(e), "获取要抓取豆瓣明星图片出现异常")
            raise