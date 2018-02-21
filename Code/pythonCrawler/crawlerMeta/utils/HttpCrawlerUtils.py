# -*- coding: utf-8 -*-

import urllib.request
import random
import requests
from bs4 import BeautifulSoup
import time
import re
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
from sys import getrefcount
import gc

class HttpCrawlerUtils(object):
    gc.enable()
    gc.set_threshold(700, 10, 5)
    index = 0
    vcode = 20495023
    proxies = ["https://218.241.234.48:8080",
               "https://119.57.112.130:8080",
               "https://119.57.112.181:8080",
               "https://119.57.144.253:8080",
               "https://106.3.240.237:8080",
               "https://106.3.240.209:8080"]

    agentsList = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0"
    ]

    def queryStarHtml(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/60.0.3112.101 Safari/537.36'}
        try:
            req = urllib.request.Request(url=url, headers=headers)
            res = urllib.request.urlopen(req)
            html = res.read()
            # 获取html页面信息
            data = BeautifulSoup(html, 'html.parser')
            #print(data)
            # 关闭链接
            res.close()
            return data
        except BaseException as e:
            print("e.message:", str(e))
            print("出现问题等待")
            #time.sleep(3600)
        return None



    def queryStarHtmldl(self, url):
        try:
            user_Agent = random.choice(self.agentsList)
            headerinfos = {'Accept': '*/*',
                           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Accept-Encoding': 'gzip, deflate',
                           'Cache-Control': 'must-revalidate, no-cache, private',
                           'User-Agent': user_Agent,
                           'Connection': 'keep-alive',
                           'Referer': 'https://www.baidu.com/'}
            #print(user_Agent)
            #随机获取本地设置好的ip
            #ipvalue = random.choice(self.proxies)
            #获取接口中ip
            ipapi = requests.get( "http://dynamic.goubanjia.com/dynamic/get/d5d45bc51ed327b9ea1708aa20d3deb0.html?random=yes")
            #print(ipapi)
            ipapi.encoding = 'utf-8'
            ipApiDataText = ipapi.text
            ipApiData = ipApiDataText.strip("\n")
            ipValue = "https://"+ipApiData
            # 设置代理
            if (ipapi):
                ipapi.close()
            proxies = {
                "https": ipValue
            }
            # 创建一个请求
            responseData = requests.get(url, headers=headerinfos, proxies=proxies ,timeout=10)
            responseData.encoding = 'utf-8'
            data = responseData.text
            data = BeautifulSoup(data, 'html.parser')

            if (responseData):
                responseData.close()

            return data
        except BaseException as e:
            print(str(e))
            print("访问出现问题等待")
            time.sleep(5)
            raise
        return None



        # 是否是本机要处理的数据
    def isLocal(self, starId: object) -> object:
        if ipDict:
            if localIp in ipDict:
                if starId % len(ipDict) == ipDict[localIp]:
                    return True
                else:
                    print("该starId", starId, "不是", localIp, "要处理的数据")
                    return False
            else:
                print("本机ip", localIp, "不在ip字典中")
                return False
        else:
            print("没有要处理数据的服务器")
            return False



if __name__ == '__main__':
    httpCrawlerUtils = HttpCrawlerUtils();
    while(True) :
        httpCrawlerUtils.crawlerUrl("https://movie.douban.com/subject/%d/?from=showing" % (httpCrawlerUtils.vcode))
        httpCrawlerUtils.index = httpCrawlerUtils.index + 1
        httpCrawlerUtils.vcode = httpCrawlerUtils.vcode + 1