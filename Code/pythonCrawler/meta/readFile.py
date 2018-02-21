import urllib.request,socket,re,sys,os
from crawlerMeta.utils.urlContentUtil import getData
def getMetadata() :
    # 网址
    url = "http://list.iqiyi.com/www/2/-------------11-1-1-iqiyi--.html"
    data = getData(url);

    print("1111111111111");
    for link, t in set(re.findall(r'(https:[^s]*?(jpg|png|gif))', str(data))):
        print(link)

def dataProcess() :
    # 网址
    url = "https://www.douban.com/"

if __name__ == "__main__":
    getMetadata();