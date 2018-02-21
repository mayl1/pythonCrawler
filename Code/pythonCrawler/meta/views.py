# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections, transaction
import json
import _thread
from  meta.douban import DoubanStar
from  meta.doubanMZ import DoubanMeta
from  meta.iqiyiMeta import IqiyiMeta
from crawlerMeta.utils.dbutil import DBUtil
from meta.iqiyi import IQiYiMeta
from meta.doubanMediaCelebrities import DoubanMediaCelebrities
from meta.doubanMediaWinning import DoubanMediaWinning
from meta.iqiyiMetaVariety import IqiyiMetaVariety
from meta.youkuMedia import YoukuMedia
import time
# Create your views here.

'''豆瓣自动抓取功能'''
def doubanList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        _thread.start_new_thread(DoubanMeta().queryListMeta())
        data["resultCode"] = "1"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


'''豆瓣关键字搜索'''
def doubanSearch(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    key = request.GET.get("key")
    if (DBUtil().isBlank(key)):
        data["resultDesc"] = "缺少参数"
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

    # 调用豆瓣自动抓取函数
    print(DoubanMeta().searchMetaByKey(key))
    try:
        DoubanMeta().searchMetaByKey(key)
        data["resultCode"] = "1"
    except:
        print("Error: 豆瓣搜索错误")

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

'''豆瓣自动抓取演职人员信息'''
def doubanStarList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用豆瓣自动抓取函数
    try:
        DoubanStar().queryListStar()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"

    except BaseException as e:
        print("e.message:", str(e))
        print("Error: 豆瓣自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

'''豆瓣自动补充抓取演职人员信息'''
def doubanUpdateStarList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用豆瓣自动抓取函数
    try:
        DoubanStar().updateStar()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

'''爱奇艺媒资view'''
def iqiyiMetaList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用豆瓣自动抓取函数
    try:
        IqiyiMeta().queryListMeta()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 爱奇艺自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#豆瓣补充演员和作品信息
def doubanMediaStarList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        DoubanStar().updateMediaStar()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#爱奇艺自动抓取演职人员信息
def iqiyiSaveStarList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用爱奇艺自动抓取函数
    try:
        IQiYiMeta().queryStarInfo()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 爱奇艺自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


#爱奇艺自动更新演职人员信息以及作品关系和任务关系
def iqiyiUpdateStarList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用爱奇艺自动抓取函数
    try:
        IQiYiMeta().updateStarInfo()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 爱奇艺自动更新无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#豆瓣补充演员获奖信息
def doubanMediaStarPrize(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        DoubanStar().updateStarPrize()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#抓取爱奇艺明星图片信息
def grabIQiYiStarPhoto(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        IQiYiMeta().grabStarPhoto()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except:
        print("Error: 爱奇艺明星图片自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

'''豆瓣自动抓取功能'''
def doubanMediaList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        _thread.start_new_thread(DoubanMediaCelebrities().querygrabMediaStar())
        data["resultCode"] = "1"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")
'''豆瓣自动抓取功能'''
def doubanMediaWinningList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        _thread.start_new_thread(DoubanMediaWinning().queryMediaDynamicInfo())
        data["resultCode"] = "1"
    except:
        print("Error: 豆瓣自动抓取无法启动线程")
'''爱奇艺'''
def iqyiMediaList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        _thread.start_new_thread(IqiyiMetaVariety().queryMetaVariety())
        data["resultCode"] = "1"
    except:
        print("Error: 爱奇艺自动抓取无法启动线程")
'''爱奇艺'''
def YKMediaList(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        _thread.start_new_thread(YoukuMedia().queryYKMediaGrab())
        data["resultCode"] = "1"
    except:
        print("Error: 爱奇艺自动抓取无法启动线程")

#抓取豆瓣明星图片信息
def grabDoubanStarPhoto(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}
    # 调用豆瓣自动抓取函数
    try:
        DoubanMeta().grabStarPhoto()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except BaseException as e:
        print(str(e), "Error: 豆瓣明星图片自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#豆瓣媒资
def grabDoubanMedia(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        DoubanMeta().queryListMeta()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except BaseException as e:
        print("e.message:", str(e))
        print("Error: 豆瓣明星图片自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

#豆瓣媒资
def readyZeroGrabDoubanMedia(request):
    data = {"resultCode": "0", "resultDesc": "", "total": "", "dataList": []}

    # 调用豆瓣自动抓取函数
    try:
        DoubanMeta().readyZeroQueryListMeta()
        data["resultCode"] = "1"
        data["resultDesc"] = "成功"
    except BaseException as e:
        print("e.message:", str(e))
        print("Error: 豆瓣明星图片自动抓取无法启动线程")
        data["resultCode"] = "0"
        data["resultDesc"] = "失败"

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")

