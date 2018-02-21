from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict
import json
import time
from crawlerMeta.utils.dbutil import DBUtil, localIp, ipDict,sleepTimeLength,award_separator_1, award_separator_2,award_separator_3, award_separator_4
from crawlerMeta.utils.urlContentUtil import UrlUtils, data_type_separator, data_type_1_star, data_type_2_grab, douban_default_star_photo, data_type_1_meta
from bs4 import BeautifulSoup
from meta.model.GrabMediaInfo import GrabMediaInfo
from meta.model.GrabPoster import GrabPoster
from meta.model.GrabMediaDynamic import GrabMediaDynamic
from meta.doubanMediaCelebrities import DoubanMediaCelebrities

from pyutils.common.DateUtils import DateUtils

class DoubanMZAnalysis :
    # 图片上传数量
    imageUploadNum = 0
   # 媒资来源 = 豆瓣
    informationSources = 0

    # 图片上传
    def parseImageUpload(self, webUrl):
        ftpUrl = ''
        photoHeight = 0
        photoWidth = 0
        dateType = data_type_1_meta + data_type_separator + data_type_2_grab
        if self.imageUploadNum % 1000 == 0:
            currentStamp = DateUtils.getSysTimeSecond()
        # 取得FTP上传后地址
        ftpUrl, webFileUrl = UrlUtils().getRemoteFile(dateType, currentStamp, self.informationSources, webUrl)
        # 上传图片到FTP,返回图片尺寸
        photoHeight, photoWidth = UrlUtils().upLoadFtp(ftpUrl, webFileUrl, self.informationSources)
        self.imageUploadNum += 1
        return ftpUrl, photoHeight, photoWidth

    # 媒资详情页信息
    def queryItemMata(self, response):
        try:
            json_dict = json.loads(response)
            media_source_code = json_dict['id']
            cn_name = json_dict['title']
            genresNo = len(json_dict['genres'])
            if genresNo > 0:
                subordinate_type = json_dict['genres']
            else:
                subordinate_type = ""
            akaNo = len(json_dict['aka'])
            if akaNo > 0:
                alternate_name = json_dict['aka']
            else:
                alternate_name = ""
            subtypeNo = len(json_dict['subtype'])
            if subtypeNo > 0:
                media_type = json_dict['subtype']
            else:
                media_type = ""
            poster_img_url = json_dict['images']['large']
            media_intro = json_dict['summary']
            media_year = json_dict['year']
            if media_year == "" or media_year == None:
                media_year = 0
            grab_web_url = json_dict['share_url']
            pingfen = json_dict['rating']['average']
            total_season = json_dict['seasons_count']
            if total_season == "" or total_season == None:
                total_season = "1"
            current_season = json_dict['current_season']
            if current_season == "" or current_season == None:
               current_season = "1"
            current_season_number = json_dict['episodes_count']
            if current_season_number == "" or current_season_number is None:
                current_season_number = "1"
            directorsNo = len(json_dict['directors'])
            if directorsNo > 0:
                dy = []
                for n in range(directorsNo):
                    media_director = json_dict['directors'][n]['name']
                    dy.append(media_director)
            else:
                dy = ""
            zy = []
            castsNo = len(json_dict['casts'])
            if castsNo > 0:
                for i in range(castsNo):
                    media_actor = json_dict['casts'][i]['name']
                    zy.append(media_actor)
            else:
                zy = ""
            countriesNo = len(json_dict['countries'])
            if countriesNo > 0:
                production_contry = json_dict['countries'][0]
            else:
                production_contry = ''

            # -----保存媒资基础信息------
            grabMediaInfo = GrabMediaInfo()
            #设置主键id
            grabMediaInfo.mediaId = DBUtil().createPK("GRAB_MEDIA_INFO")
            # 媒资数据源id
            grabMediaInfo.mediaSourceCode = media_source_code
            # 信息来源
            grabMediaInfo.informationSources = 0
            #媒资父id 豆瓣没有剧集默认值为0
            grabMediaInfo.parentSourceCode = 0
            #
            grabMediaInfo.cleanParentMediaId = 0
            # 媒资类型
            grabMediaInfo.mediaType = media_type
            # 中文名
            grabMediaInfo.cnName = cn_name
            # 又名
            grabMediaInfo.alternateName = alternate_name
            # 发行年份
            grabMediaInfo.mediaYear = media_year
            # 简介
            grabMediaInfo.mediaIntro = media_intro
            # 影片类型
            grabMediaInfo.subordinateType = subordinate_type
            # 制片国家/地区
            grabMediaInfo.productionContry = production_contry
            # 总季数
            grabMediaInfo.totalSeason = int(total_season)
            # 当前季数
            grabMediaInfo.currentSeason = int(current_season)
            # 当前季的集数
            grabMediaInfo.currentSeasonNumber = int(current_season_number)
            # 海报url
            grabMediaInfo.posterImgUrl = poster_img_url
            # 导演
            grabMediaInfo.mediaDirector = dy
            # 演员
            grabMediaInfo.mediaActor = str(zy)
            # 是否清洗
            grabMediaInfo.cleanStatus = 0
            # 清洗后id
            grabMediaInfo.cleanAfterId = 0
            # 抓取时间
            grabMediaInfo.grabTime = DateUtils.getSysTimeFormat("%Y-%m-%d %H:%M:%S")
            # 抓取页面URL
            grabMediaInfo.grabWebUrl = grab_web_url
            if (media_type  == 'tv'):
                if ('真人秀' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'variety'
                elif ('音乐' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'variety'
                elif ('歌舞' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'variety'
                elif ('脱口秀' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'variety'
                elif ('动画' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'manga'
                elif ('儿童' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'manga'
                elif ('纪录片' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'documentary'
                else:
                    grabMediaInfo.mediaAssistType = 'tv'
            else:
                if ('纪录片' in subordinate_type):
                    # 协助媒资类型
                    grabMediaInfo.mediaAssistType = 'documentary'
                else:
                    grabMediaInfo.mediaAssistType = 'movie'
            # 保存数据库
            grabMediaInfo.save(using="grab", force_insert=True)
            # -----保存媒资图片------
            ftpUrl, photoHeight, photoWidth = DoubanMZAnalysis().parseImageUpload(poster_img_url)
            self.addMataImg(media_source_code, poster_img_url, ftpUrl, photoWidth, photoHeight)
            # -----保存媒资评分------
            self.addMataPF(media_source_code, grabMediaInfo.mediaId, pingfen)
            #-------保存媒资演员信息-------
            #DoubanMediaCelebrities().mediaCelebrities(media_source_code)
        except BaseException as e:
            print("e.message:", str(e))
            time.sleep(10)

    # 媒资图片信息
    def addMataImg(self, media_source_code,poster_img_url,ftpUrl,photoWidth,photoHeight):
        try:
            grabPoster = GrabPoster()
            # 序列id
            grabPoster.posterId = DBUtil().createPK("GRAB_POSTER")
            # 影片源id
            grabPoster.mediaSourceCode = media_source_code
            # 信息来源
            grabPoster.informationSources = 0
            # 海报url
            grabPoster.posterUrl = poster_img_url
            # 海报FTP
            grabPoster.posterFtpUrl = ftpUrl
            # 图片宽度
            grabPoster.posterWidth = photoWidth
            # 图片高度
            grabPoster.posterHeight = photoHeight
            # 抓取时间
            grabPoster.grabTime = DateUtils.getSysTimeFormat("%Y-%m-%d %H:%M:%S")
            # 清洗状态
            grabPoster.cleanStatus = 0
            # 清洗后id
            grabPoster.cleanAfterId = 0
            # 图片显示状态
            grabPoster.displayStatus = 1
            grabPoster.save(using="grab", force_insert=True)
        except BaseException as e:
            print("e.message:", str(e))

    # 媒资评分
    def addMataPF(self, media_source_code,mediaId,pingfen):
        try:
            grabMediaDynamic = GrabMediaDynamic()
            # 影片id
            grabMediaDynamic.mediaId = mediaId
            # 媒资数据源id
            grabMediaDynamic.mediaSourceCode = media_source_code
            # 评分
            grabMediaDynamic.mediaScore = pingfen
            # 信息来源
            grabMediaDynamic.informationSources = 0
            # 清洗状态
            grabMediaDynamic.cleanStatus = 0
            # 清洗后id
            grabMediaDynamic.cleanAfterId = 0
            # 抓取时间
            grabMediaDynamic.grabTime = DateUtils.getSysTimeFormat("%Y-%m-%d %H:%M:%S")
            grabMediaDynamic.save(using="grab", force_insert=True)
        except BaseException as e:
            print("e.message:", str(e))