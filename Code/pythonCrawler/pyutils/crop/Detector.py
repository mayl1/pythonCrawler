# -*- coding: utf-8 -*-
"""
    Cropman Library - Detector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements face detection functions.

    :copyright: (c) 2017 by Dongzhizhong
    :license: WTFPL (Do What the Fuck You Want to Public License).
"""

import cv2
import os

# ----------------------------------------------------------------------------

DEFAULT_DATA_FILENAME = os.path.join(
    os.path.split(os.path.realpath(__file__))[0],
    'config/haarcascade_frontalface_alt_tree.xml'
    )

class Detector(object):
    """Detector"""
    def __init__(self, data_filename = DEFAULT_DATA_FILENAME):
        super(Detector, self).__init__()
        self.face_cascade  = cv2.CascadeClassifier(data_filename)

    """
    void detectMultiScale(  
    2.    const Mat& image,  
    3.    CV_OUT vector<Rect>& objects,  
    4.    double scaleFactor = 1.1,  
    5.    int minNeighbors = 3,   
    6.    int flags = 0,  
    7.    Size minSize = Size(),  
    8.    Size maxSize = Size()  
    9.);  
    函数介绍：

    参数1：image--待检测图片，一般为灰度图像加快检测速度；

    参数2：objects--被检测物体的矩形框向量组；
    参数3：scaleFactor--表示在前后两次相继的扫描中，搜索窗口的比例系数。默认为1.1即每次搜索窗口依次扩大10%;
    参数4：minNeighbors--表示构成检测目标的相邻矩形的最小个数(默认为3个)。
            如果组成检测目标的小矩形的个数和小于 min_neighbors - 1 都会被排除。
            如果min_neighbors 为 0, 则函数不做任何操作就返回所有的被检候选矩形框，
            这种设定值一般用在用户自定义对检测结果的组合程序上；
    参数5：flags--要么使用默认值，要么使用CV_HAAR_DO_CANNY_PRUNING，如果设置为

            CV_HAAR_DO_CANNY_PRUNING，那么函数将会使用Canny边缘检测来排除边缘过多或过少的区域，

            因此这些区域通常不会是人脸所在区域；
    参数6、7：minSize和maxSize用来限制得到的目标区域的范围。
self.face_cascade.detectMultiScale(gray, scaleFactor = 1.15,
   minNeighbors = 2,
   minSize = (30,30)
    """

    def detect_faces(self, img):
        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray)
        return faces

# ----------------------------------------------------------------------------
