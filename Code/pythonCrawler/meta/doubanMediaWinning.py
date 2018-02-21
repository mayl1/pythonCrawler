import requests
from bs4 import BeautifulSoup
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
import re
import json
import time
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
from django.db import connections
from meta.model.GrabMediaDynamic import  GrabMediaDynamic
# 抓取豆瓣影片的影人信息
class DoubanMediaWinning :
    # 按影片抓取演员信息地址
    grab_html_url = "https://movie.douban.com/subject/mediaSourceCode/awards/"

    # 抓取影片中演员信息
    def mediaWinning(self, mediaId, mediaSourceCode):
        print(mediaId)
        listUrl = self.grab_html_url.replace('mediaSourceCode', str(mediaSourceCode))
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
        print(ipValue)
        # 设置代理
        if (ipapi):
            ipapi.close()
        proxies = {
            "https": ipValue
        }
        # 抓影片演员信息
        htmlText = httpSpiderUtils.spiderHtmlUrl(listUrl, 'https://www.baidu.com/', proxies)
        if htmlText != None:
            receivedAwards = DoubanMediaWinning().doubanAnalysis(htmlText)
            grabMediaDynamic = GrabMediaDynamic()
            grabMediaDynamic.mediaId = mediaId
            grabMediaDynamic.receivedAwards = str( receivedAwards)
            grabMediaDynamic.mediaSourceCode = mediaSourceCode
            #更改获取奖项信息
            DoubanMediaWinning().updateMediaDynamicInfo(grabMediaDynamic)

    # 解析HTML
    def doubanAnalysis(self, htmlText):
        try:
            # 解析HTML
            htmlText = BeautifulSoup(htmlText, 'html.parser')

            article = htmlText.find(attrs={'class': 'article'})
            # print(article)
            awards = article.find_all(attrs={'class': 'awards'})
            # print(awards)
            awardsInfoList = []
            receivedAwards = []
            for award in awards:
                # print(award)
                h2 = award.find("h2")
                year = h2.find("span").text
                year = year[2:][:-1]
                awardsDict = {'awardsYear': year}
                # 第几届
                awardsTime = "第" + re.sub("\D", "", h2.find("a").contents[0]) + "届"

                awardsName = h2.find("a").contents[0]
                awardsName = awardsName[len(awardsTime):]

                ulALL = award.find_all("ul")
                # print(ulALL)

                for ul in ulALL:
                    liAll = ul.find_all("li")

                    # 奖项内容
                    awardsProj = liAll[0].contents[0]
                    result = "(提名)" in awardsProj
                    if result:
                        awardsResult = "提名"
                        awardsProj = awardsProj[:-4]
                    else:
                        awardsResult = "获奖"
                    # print(result)
                    # 获奖人
                    awardees = liAll[1].find_all("a")
                    awardsStar = ""
                    if len(awardees) > 0:
                        for awardee in awardees:
                            awardsStar = awardsStar + awardee.contents[0] + " "

                    awardsInfo = {"awardsTime": awardsTime, "awardsProj": awardsProj, "awardsName": awardsName,
                                  "awardsResult": awardsResult, "awardsStar": awardsStar}
                    awardsInfoList.append(awardsInfo)
                # print(awardsInfoList)
                awardsDict["awardsInfoList"] = awardsInfoList
                receivedAwards.append(awardsDict)
            return json.dumps(receivedAwards, ensure_ascii=False)


        except BaseException as e:
            print("e.message:", str(e))

    #更改获奖信息
    def updateMediaDynamicInfo(self,grabMediaDynamic):
        try:
            GrabMediaDynamic.objects.using("grab").filter(mediaId=grabMediaDynamic.mediaId).update(
                receivedAwards=grabMediaDynamic.receivedAwards,cleanStatus = 2)
        except BaseException as e:
            print("e.message:", str(e), "查询开始明星id出现异常")

    #查询数据库已有曾获奖项
    def queryMediaDynamicInfo(self):
        for i in range(9999999):
            try:
                cursor = connections["grab"].cursor()
                cursor.execute(
                    "SELECT MEDIA_SOURCE_CODE,MEDIA_ID FROM GRAB_MEDIA_DYNAMIC WHERE INFORMATION_SOURCES = 0 AND CLEAN_STATUS !=2 LIMIT 100")
                resultTuple = cursor.fetchall()
                cursor.close()
                print(len(resultTuple))
                if resultTuple:
                    for i in range(len(resultTuple)) :
                        print(resultTuple[i][0])
                        print(resultTuple[i][1])
                        DoubanMediaWinning().mediaWinning(resultTuple[i][1],resultTuple[i][0])
                else:
                    time.sleep(120)

            except BaseException as e:
                print("e.message:", str(e), "查询开始明星id出现异常")
        return self.startStarId

if __name__ == '__main__':
    doubanMediaWinning = DoubanMediaWinning()
    doubanMediaWinning.mediaWinning(26611804)

