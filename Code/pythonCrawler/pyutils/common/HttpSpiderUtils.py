# -*- coding: utf-8 -*-

import random
import requests

import os

class HttpSpiderUtils(object):

    '''
    USER_AGENTS 随机头信息
    '''
    __USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    ]

    """
    #基于urllib库进行网络访问
    def spiderHtml(self, url, proxy_addr):
        try:
            #定义代理ip
            #proxy_addr = '114.247.94.102'#self.randomIP();

            #  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
            #  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'
            #  'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
            headerinfos = {'Accept': '*/*',
                       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                       'Accept-Encoding': 'gzip, deflate',
                       'Cache-Control': 'must-revalidate, no-cache, private',
                       'User-Agent': self.__USER_AGENTS[0],
                       'Connection': 'keep-alive',
                       'Referer': 'https://www.baidu.com/'
                       }

            #设置代理
            proxy = urllib.request.ProxyHandler({"http" : proxy_addr})

            #创建一个opener
            opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)

            #将opener安装为全局
            urllib.request.install_opener(opener)
            #用urlopen打开网页


            #创建一个请求
            req = urllib.request.Request(url, headers=headerinfos)
            requestData = urllib.request.urlopen(req, timeout = 600)
            data = requestData.read().decode('utf-8','ignore')
            print(data)
            if (requestData) :
                requestData.close()

            return data
        except BaseException as e:
            print(str(e))
        return None
    """

    """
    spliderHtmlUrl:根据url地址以及代理IP信息进行web访问
            proxies = {
                 "https": "https://101.81.106.155:9797"
            }
    """
    def spiderHtmlUrl(self, url, referer = None, proxies = None, timeout = 600):
        try:
            responseData = None

            userAgent = random.choice(self.__USER_AGENTS)
            headerinfos = {'Accept': '*/*',
                       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate',
                        'Cache-Control': 'must-revalidate, no-cache, private',
                       'User-Agent': userAgent,
                       'Connection': 'keep-alive',
                       'Referer': self.__get_referer(referer)
                       }

            #创建一个请求
            if proxies:
                responseData = requests.get(url, headers = headerinfos, proxies = proxies, timeout = timeout)
            else:
                responseData = requests.get(url, headers = headerinfos, timeout = timeout)

            if (responseData):
                responseData.encoding = 'utf-8'
                htmlText = responseData.text
                responseData.close()
                return htmlText
            else:
                return None

        except BaseException as e:
            print(str(e))
        return None

    def spiderImg(self, url, referer = None, proxies = None, timeout = 600):
        try:
            responseData = None
            userAgent = random.choice(self.__USER_AGENTS)
            headerinfos = {'Accept': '*/*',
                       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate',
                        'Cache-Control': 'must-revalidate, no-cache, private',
                       'User-Agent': userAgent,
                       'Connection': 'keep-alive',
                       'Referer': self.__get_referer(referer)
                       }

            #创建一个请求
            if proxies:
                responseData = requests.get(url, headers = headerinfos, proxies = proxies, timeout = timeout)
            else:
                responseData = requests.get(url, headers = headerinfos, timeout = timeout)

            if (responseData):
                responseData.encoding = 'utf-8'
                contentData = responseData.content
                responseData.close()
                return contentData
            else:
                print("responseData", responseData)
                return None

        except BaseException as e:
            print(str(e))
        return None

    """
    如果是目录，必须是\\或者/结束
    """
    def downloadImg2Local(self, webImgUrl, localPath, referer = None, proxies = None, timeout = 600):
        imgData = self.spiderImg(webImgUrl, referer, proxies, timeout)
        if (imgData):
            filePath, fileName = os.path.split(localPath)
            if filePath and filePath != "" and filePath != "/":
                if os.path.exists(filePath) == False:
                    os.makedirs(filePath)
            if fileName is None or fileName == "":
                _, fileName = os.path.split(webImgUrl)
                localPath = os.path.join(localPath, fileName)

            localFile = open(localPath, "wb")
            localFile.write(imgData)
            localFile.close()

    def __get_referer(self, referer):
        if referer:
            return referer
        else:
            return 'https://www.baidu.com/'


if __name__ == '__main__':
    httpSpiderUtils = HttpSpiderUtils()


    httpSpiderUtils.downloadImg2Local("http://img.xgo-img.com.cn/pics/1643/1642420.jpg", "d:\\aa\\")
        #print("我们（中国）（北京）".replace("（", "("))