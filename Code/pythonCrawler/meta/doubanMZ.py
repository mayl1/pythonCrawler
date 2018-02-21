import requests
import time
from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
from bs4 import BeautifulSoup
from meta.analysis.doubanMZAnalysis import DoubanMZAnalysis
from meta.model.GrabMediaInfo import GrabMediaInfo
from crawlerMeta.utils.HttpCrawlerUtils import HttpCrawlerUtils

class DoubanMeta :


    # 按媒资id访问api地址
    meta_url = "https://api.douban.com/v2/movie/subject/metaId?apikey=0fbfdca9eedf20c82f3f95fdcc9d6258"


    # 取得媒资数据json数据
    '''
    豆瓣媒资 id  间隔比较大countNo 应该设置1W -10W 之间10W 比较稳妥
    '''
    def queryListMeta(self):
        while True:
            print("------------------------")
            try:
                grabMedia = GrabMediaInfo.objects.using("grab").values("mediaSourceCode").extra(select={"mediaSourceCodeInt": "CAST(MEDIA_SOURCE_CODE AS UNSIGNED)"}).filter(informationSources=0).order_by('-mediaSourceCodeInt')
                print(len(grabMedia))
                grabMediaNo = len(grabMedia)
                if grabMediaNo > 0:
                    csid = grabMedia[0]["mediaSourceCode"]
                    print(csid)
                    # 查询数据空最大媒资id
                    countNo = 0
                    for i in range(9999999):
                        metaId = int(csid) + i
                        if HttpCrawlerUtils().isLocal(int(metaId)):
                            listUrl = self.meta_url.replace('metaId', str(metaId))
                            print(listUrl)
                            response = HttpSpiderUtils().spiderHtmlUrl(listUrl)
                            time.sleep(0.3)
                            if response == None :
                                pass
                                countNo += 1
                                print(metaId,"没有数据")
                                if (countNo > 10000):
                                    time.sleep(7200)
                                    break
                            else:
                                pass
                                DoubanMZAnalysis().queryItemMata(response)
                else:
                    countNo = 0
                    for i in range(9999999):
                        csid = 3073647
                        metaId = int(csid) + i
                        if HttpCrawlerUtils().isLocal(int(metaId)):
                            listUrl = self.meta_url.replace('metaId', str(metaId))
                            response = HttpSpiderUtils().spiderHtmlUrl(listUrl)
                            time.sleep(0.3)
                            if response == None :
                                pass
                                countNo += 1
                                print(metaId, "没有数据")
                                if (countNo > 10000):
                                    time.sleep(7200)
                                    break
                            else:
                                DoubanMZAnalysis().queryItemMata(response)
            except BaseException as e:
                print("e.message:", str(e))
                raise


    # 取得媒资数据json数据
    '''
    豆瓣媒资 id  间隔比较大countNo 应该设置1W -10W 之间10W 比较稳妥
    '''
    def readyZeroQueryListMeta(self):
        while True:
            print("------------------------")
            try:
                countNo = 0
                for i in range(9999999):
                    csid = 3073647
                    metaId = int(csid) + i
                    if HttpCrawlerUtils().isLocal(int(metaId)):
                        listUrl = self.meta_url.replace('metaId', str(metaId))
                        response = HttpSpiderUtils().spiderHtmlUrl(listUrl)

                        if response == None :
                            time.sleep(0.3)
                            countNo += 1
                            print(metaId, "没有数据")
                            if (countNo > 10000):
                                time.sleep(7200)
                                break
                        else:
                            time.sleep(0)
                            DoubanMZAnalysis().queryItemMata(response)
            except BaseException as e:
                print("e.message:", str(e))
                raise



if __name__ == '__main__' :
    doubanMeta = DoubanMeta()
    doubanMeta.queryListMeta()
