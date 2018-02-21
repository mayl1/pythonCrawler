# -*- coding: utf-8 -*-
"""
    Cropman Library - Cropper
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements face-ware image cropping functions.

    :copyright: (c) 2017 by Dongzhizhong
    :license: WTFPL (Do What the Fuck You Want to Public License).
"""
import os
import sys

import cv2
import numpy
import requests

from pyutils.crop.Detector import Detector


# ----------------------------------------------------------------------------

class Cropper(object):
    """Cropper"""
    def __init__(self):
        super(Cropper, self).__init__()
        self.detector  = Detector()

    """
    dataframe_target_size : 图片大小的数据集合，包括宽度和高度，0列是宽度，1列是高度
    """
    def batchDataFrameCropFaceLocalImg(self, inputImgFile, outLocalImgDir, dataframe_target_size):
        input_image = cv2.imread(inputImgFile)
        # 取文件后缀  os.path.splitext("/root/a.py")  ('/root/a', '.py')
        #取目录与文件名os.path.split("/root/a.py") ('/root', 'a.py')
        _, input_imageExt = os.path.splitext(inputImgFile)
        print(dataframe_target_size)
        for index, target_size in dataframe_target_size.iterrows():
            outLocalImgFile = outLocalImgDir + "%d.%d%s" % (target_size[0], target_size[1], input_imageExt)
            self.cropFaceImg(input_image, outLocalImgFile, target_size[0], target_size[1])

    """
    cropper.batchCropFaceWebImg(input_filename, "D:\\face\\", [100, 400, 500], [200, 100, 400])
    target_widths : [100, 400, 500]
    target_heights : [200, 100, 400]
    
    如果通过dataframe进行处理：
    imageSize = pandas.DataFrame([[100,200],[400,100],[500,400]])
    print(imageSize[0])
    print(imageSize[1])
    cropper.batchCropFaceLocalImg(input_filename, "D:\\face\\", imageSize[0], imageSize[1])

    """
    def batchCropFaceLocalImg(self, inputImgFile, outLocalImgDir, target_widths, target_heights):
        input_image = cv2.imread(inputImgFile)
        # 取文件后缀  os.path.splitext("/root/a.py")  ('/root/a', '.py')
        #取目录与文件名os.path.split("/root/a.py") ('/root', 'a.py')
        _, input_imageExt = os.path.splitext(inputImgFile)
        for target_width, target_height in zip(target_widths, target_heights):
            outLocalImgFile = outLocalImgDir + "%d.%d%s" % (target_width, target_height, input_imageExt)
            self.cropFaceImg(input_image, outLocalImgFile, target_width, target_height)

    def batchCropFaceWebImg(self, inputWebImgFile, outLocalImgDir, target_widths, target_heights):
        input_image = self.webImage(inputWebImgFile)
        # 取文件后缀  os.path.splitext("/root/a.py")  ('/root/a', '.py')
        #取目录与文件名os.path.split("/root/a.py") ('/root', 'a.py')
        _, input_imageExt = os.path.splitext(inputWebImgFile)
        for target_width, target_height in zip(target_widths, target_heights):
            outLocalImgFile = outLocalImgDir + "%d.%d%s" % (target_width, target_height, input_imageExt)
            self.cropFaceImg(input_image, outLocalImgFile, target_width, target_height)

    def batchCropLocalImg(self, inputImgFile, outLocalImgDir, target_widths, target_heights):
        input_image = cv2.imread(inputImgFile)
        # 取文件后缀  os.path.splitext("/root/a.py")  ('/root/a', '.py')
        #取目录与文件名os.path.split("/root/a.py") ('/root', 'a.py')
        _, input_imageExt = os.path.splitext(inputImgFile)
        for target_width, target_height in zip(target_widths, target_heights):
            outLocalImgFile = outLocalImgDir + "%d.%d%s" % (target_width, target_height, input_imageExt)
            self.cropImg(input_image, outLocalImgFile, target_width, target_height)

    def batchCropWebImg(self, inputWebImgFile, outLocalImgDir, target_widths, target_heights):
        input_image = self.webImage(inputWebImgFile)
        # 取文件后缀  os.path.splitext("/root/a.py")  ('/root/a', '.py')
        #取目录与文件名os.path.split("/root/a.py") ('/root', 'a.py')
        _, input_imageExt = os.path.splitext(inputWebImgFile)
        for target_width, target_height in zip(target_widths, target_heights):
            outLocalImgFile = outLocalImgDir + "%d.%d%s" % (target_width, target_height, input_imageExt)
            self.cropImg(input_image, outLocalImgFile, target_width, target_height)

    def cropFaceLocalImg(self, inputImgFile, outLocalImgFile, target_width, target_height):
        input_image = cv2.imread(inputImgFile)
        return self.cropFaceImg(input_image, outLocalImgFile, target_width, target_height)

    def cropFaceWebImg(self, inputWebImgFile, outLocalImgFile, target_width, target_height):
        input_image = self.webImage(inputWebImgFile)
        return self.cropFaceImg(input_image, outLocalImgFile, target_width, target_height)

    def cropLocalImg(self, inputImgFile, outLocalImgFile, target_width, target_height):
        input_image = cv2.imread(inputImgFile)
        return self.cropImg(input_image, outLocalImgFile, target_width, target_height)

    def cropWebImg(self, inputWebImgFile, outLocalImgFile, target_width, target_height):
        input_image = self.webImage(inputWebImgFile)
        return self.cropImg(input_image, outLocalImgFile, target_width, target_height)

    def webImage(self, inputWebImgFile, timeout = 600):
        webImg = requests.get(inputWebImgFile, timeout)
        inputImgFile = numpy.asarray(bytearray(webImg.content), dtype="uint8")
        webImg.close()

        #inputImgFile = numpy.asarray(bytearray(HttpCrawlerUtils().crawlerImgUrl(inputWebImgFile)), dtype="uint8")
        return cv2.imdecode(inputImgFile, cv2.IMREAD_COLOR)

    def getImageSize(self, imgContent):
        inputImgContent = numpy.asarray(bytearray(imgContent), dtype="uint8")
        imgObj = cv2.imdecode(inputImgContent, cv2.IMREAD_COLOR)
        return imgObj.shape[:2]

    def getLocalImageSize(self, imgFileName):
        imgObj = cv2.imread(imgFileName)
        return imgObj.shape[:2]

    def cropImg(self, input_image, outLocalImgFile, target_width, target_height):
        if input_image is None:
           print('FAILED: Invalid input image. Please check .')
           return False
        else:
            target_image = self.crop(input_image, target_width, target_height)
            if target_image is None:
                print('FAILED: Cropping failed.')
                return False
            else:
                cv2.imwrite(outLocalImgFile, target_image)
                print('\nSUCCESS: Result: %s' % outLocalImgFile)
                return True

    def cropFaceImg(self, input_image, outLocalImgFile, target_width, target_height):
        if input_image is None:
           print('FAILED: Invalid input image. Please check.')
           return False
        else:
            target_image = self.cropFace(input_image, target_width, target_height)
            if target_image is None:
                print('FAILED: Cropping failed.')
                return False
            else:
                cv2.imwrite(outLocalImgFile, target_image)
                print('\nSUCCESS: Result: %s' % outLocalImgFile)
                return True

    @staticmethod
    def _bounding_rect(faces):
        top, left  =  sys.maxsize,  sys.maxsize
        bottom, right = -sys.maxsize, -sys.maxsize
        for (x, y, w, h) in faces:
            if x < left:
                left = x
            if x + w > right:
                right = x + w
            if y < top:
                top = y
            if y + h > bottom:
                bottom = y + h
        return top, left, bottom, right

    def cropFace(self, img, target_width, target_height):
        original_height,  original_width  = img.shape[:2]

        faces = self.detector.detect_faces(img)
        if len(faces) == 0: # no detected faces
            #print("--------------------0----------------")
            sizeLv = target_width / original_width
            if (sizeLv < target_height/original_height):
                sizeLv = target_height / original_height

            size = (int(original_width * sizeLv), int(original_height * sizeLv))
            img = cv2.resize(img, size, interpolation = cv2.INTER_AREA)

            target_center_x = original_width * sizeLv / 2
            target_center_y = original_height * sizeLv / 2
        else:
            #print("--------------------len(faces)----------------", len(faces))
            top, left, bottom, right  = self._bounding_rect(faces)
            #print("----left---", left, "----top---", top, "----right---", right, "-----bottom----", bottom)
            target_center_x = (left + right) / 2
            target_center_y = (top + bottom) / 2
        target_left = target_center_x - target_width / 2
        target_right = target_left + target_width
        target_top = target_center_y - target_height / 2
        target_bottom = target_top + target_height
        if target_top < 0:
            delta = abs(target_top)
            target_top += delta
            target_bottom += delta
            if target_bottom > original_height:
                target_bottom = original_height
        if target_left < 0:
            delta = abs(target_left)
            target_left += delta
            target_right += delta
            if target_right > original_width:
                target_right = original_width

        return img[int(target_top):int(target_bottom), int(target_left):int(target_right)]

    def crop(self, img, target_width, target_height):
        original_height,  original_width  = img.shape[:2]

        sizeLv = target_width / original_width
        if (sizeLv < target_height/original_height):
            sizeLv = target_height / original_height

        size = (int(original_width * sizeLv), int(original_height * sizeLv))
        img = cv2.resize(img, size, interpolation = cv2.INTER_AREA)

        target_center_x = original_width * sizeLv / 2
        target_center_y = original_height * sizeLv / 2

        target_left = target_center_x - target_width / 2
        target_right = target_left + target_width
        target_top = target_center_y - target_height / 2
        target_bottom = target_top + target_height
        if target_top < 0:
            delta = abs(target_top)
            target_top += delta
            target_bottom += delta
            if target_bottom > original_height:
                target_bottom = original_height
        if target_left < 0:
            delta = abs(target_left)
            target_left += delta
            target_right += delta
            if target_right > original_width:
                target_right = original_width

        return img[int(target_top):int(target_bottom), int(target_left):int(target_right)]

# ----------------------------------------------------------------------------
