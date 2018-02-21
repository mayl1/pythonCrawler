# -*- coding:utf-8 -*-
"""crawlerMeta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from meta import views
urlpatterns = [
    url(r'^queryDouban/$', views.doubanList),
    url(r'^doubanSearch/$', views.doubanSearch),
    url(r'^queryStar/$', views.doubanStarList),
    url(r'^updateStar/$', views.doubanUpdateStarList),
    url(r'^queryIqiyiMeta/$', views.iqiyiMetaList),
    url(r'^updateMediaStar/$', views.doubanMediaStarList),
    url(r'^saveIQiYiStarList/$', views.iqiyiSaveStarList),
    url(r'^updateIQiYiStarList/$', views.iqiyiUpdateStarList),
    url(r'^updateStarPrize/$', views.doubanMediaStarPrize),
    url(r'^grabIQiYiStarPhoto/$', views.grabIQiYiStarPhoto),
    url(r'^grabDoubanStarPhoto/$', views.grabDoubanStarPhoto),
    url(r'^queryListMeta/$', views.grabDoubanMedia),
    url(r'^queryDoubanMediaList/$', views.doubanMediaList),
    url(r'^queryDoubanMediaWinningList/$', views.doubanMediaWinningList),
    url(r'^queryIqyiMedia/$', views.iqyiMediaList),
    url(r'^readyZeroQueryListMeta/$', views.readyZeroGrabDoubanMedia),
    url(r'^queryYKMediaList/$', views.YKMediaList),
]




