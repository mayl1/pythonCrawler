# -*- coding:utf-8 -*-
import urllib.request
from bs4 import BeautifulSoup
from django.db import connections
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict, award_separator_1, award_separator_2,award_separator_3, award_separator_4
import time
def get_html(url):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/60.0.3112.101 Safari/537.36'}
    req = urllib.request.Request(url=url,headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read()
    soup = BeautifulSoup(html,'html.parser')
    data = soup.find(attrs={'class': 'info'}).find_all("ul")
    #print(data)
    return data

def get_all(data):
    print("111")
    for info in data:
        #print(str(info))
        names = (info.find("li"))
        dd = names.replace(' ', '')
        cc = dd.rstrip()+'\n'
        print(cc)
        #aa = GetMiddleStr(dd, '< li>< span>星座</span>:', '</li>')
        #print(aa)

        # names = info.find("a")
        # bb = str(info)
        # zhiwei = re.findall(u'[\\[\u4e00-\u9fa5\\]]+', bb)
        # #print(names)
        # mzid = re.sub("\D", "", str(names))
        # #links = re.findall('"((http|ftp)s?://.*?)"', str(names))
        # print(mzid)
        # name = names.get_text()

def GetMiddleStr(content,startStr,endStr):
  startIndex = content.index(startStr)
  if startIndex>=0:
    startIndex += len(startStr)
  endIndex = content.index(endStr)
  return content[startIndex:endIndex]


# if __name__ == '__main__':
#     url='https://movie.douban.com/celebrity/1274477/'
#     get_all(get_html(url))

def testException():
    varStr = "a123"
    try:
        varInt = int(varStr)
        print("varInt=", varStr)
        return varStr
    except BaseException as e:
        print("e.message:", str(e))
    print("varStr=" + varStr)
    return varStr
starId = 202285005
print("starId = ", type(str(starId)[0:7]), str(starId)[0:7], int(str(starId)[0:7]) % 3 == 0)
#print(testException())

# starStr = """演员
#                                                                             /
#                                                                                                         导演
#                                                                             /
#                                                                                                         制片人
#                                                                             /"""
starStr = ""
print("starStr=", starStr, "&starRlace=", starStr.replace("\n", "").replace(" ", ""))

#starAwardStr = "2012年:第64届艾美奖/喜剧类剧集最佳男主角(提名);2010年:第62届艾美奖/喜剧类剧集最佳男主角(提名);2006年:第58届艾美奖/喜剧类剧集最佳男主角(提名),第63届美国金球奖/音乐喜剧类剧集最佳男主角(提名);1994年:第46届艾美奖/喜剧类剧集最佳编剧(提名);1993年:第45届艾美奖/喜剧类剧集最佳编剧(提名);1992年:第44届艾美奖/喜剧类剧集最佳编剧(提名);1991年:第43届艾美奖/喜剧类剧集最佳编剧(提名);"
starAwardStr ="1982年:第9届土星奖/最佳男配角(提名)"
starAwardList = starAwardStr.split(award_separator_4)
print("starAwardStr=", starAwardStr)
print("starAwardList=", starAwardList, len(starAwardList))
for starAward in starAwardList :
    print(starAward)
    a = starAward.split(award_separator_1)
    for i in range(len(a)) :
        print(a[i])
        if i == 1 :
            for j in a[i].split(award_separator_3) :
                print(j)
                for k in j.split(award_separator_2) :
                    print(k)

print(1000 % 3000)













