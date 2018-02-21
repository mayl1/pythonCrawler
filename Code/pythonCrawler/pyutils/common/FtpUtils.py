# -*- coding: utf-8 -*-
"""
    FTP Library - FTPUtils
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by Dongzhizhong
    :license: WTFPL (Do What the Fuck You Want to Public License).
"""
import os
import requests
from ftplib import FTP, error_perm

from pyutils.common.HttpSpiderUtils import HttpSpiderUtils
from pyutils.crop.Cropper import Cropper
"""
ftp登陆连接
from ftplib import FTP            #加载ftp模块
ftp=FTP()                         #设置变量
ftp.set_debuglevel(2)             #打开调试级别2，显示详细信息
ftp.connect("IP","port")          #连接的ftp sever和端口
ftp.login("user","password")      #连接的用户名，密码
print ftp.getwelcome()            #打印出欢迎信息
ftp.cmd("xxx/xxx")                #进入远程目录
bufsize=1024                      #设置的缓冲区大小
filename="filename.txt"           #需要下载的文件
file_handle=open(filename,"wb").write #以写模式在本地打开文件
ftp.retrbinaly("RETR filename.txt",file_handle,bufsize) #接收服务器上文件并写入本地文件
ftp.set_debuglevel(0)             #关闭调试模式
ftp.quit()                        #退出ftp
 
ftp相关命令操作
ftp.cwd(pathname)                 #设置FTP当前操作的路径
ftp.dir()                         #显示目录下所有目录信息
ftp.nlst()                        #获取目录下的文件
ftp.mkd(pathname)                 #新建远程目录
ftp.pwd()                         #返回当前所在位置
ftp.rmd(dirname)                  #删除远程目录
ftp.delete(filename)              #删除远程文件
ftp.rename(fromname, toname)#将fromname修改名称为toname。
ftp.storbinaly("STOR filename.txt",file_handel,bufsize)  #上传目标文件
ftp.retrbinary("RETR filename.txt",file_handel,bufsize)  #下载FTP文件
"""

"""
Python函数：open()

1：作用：打开一个文件


2：语法：

open(file[, mode[, buffering[, encoding[, errors[, newline[, closefd=True]]]]]])


3：参数说明：
file：              要打开的文件名，需加路径(除非是在当前目录)。唯一强制参数
mode：        文件打开的模式
buffering：    设置buffer（取值为0,1,>1）
encoding：  返回数据的编码（一般为UTF8或GBK）
errors：        报错级别（一般为strict，ignore）
newline：      用于区分换行符(只对文本模式有效，可以取的值有None,'\n','\r','','\r\n')
closefd：      传入的file参数类型（缺省为True）

常用的是file，mode和encoding这三个参数

4：参数详细说明：
4.1.mode：文件打开的模式。有如下几种模式
'r'： 以只读模式打开（缺省模式）（必须保证文件存在）
'w'：以只写模式打开。若文件存在，则会自动清空文件，然后重新创建；若文件不存在，则新建文件。使用这个模式必须要保证文件所在目录存在，文件可以不存在。该模式下不能使用read*()方法 
'a'：以追加模式打开。若文件存在，则会追加到文件的末尾；若文件不存在，则新建文件。该模式不能使用read*()方法。

下面四个模式要和上面的模式组合使用
'b'：以二进制模式打开
't'： 以文本模式打开（缺省模式）
'+'：以读写模式打开
'U'：以通用换行符模式打开

常见的mode组合
'r'或'rt'：    默认模式，文本读模式
'w'或'wt'：  以文本写模式打开（打开前文件会被清空）
'rb'：          以二进制读模式打开
'ab'：        以二进制追加模式打开
'wb'：        以二进制写模式打开（打开前文件会被清空）
'r+'：        以文本读写模式打开，可以写到文件任何位置；默认写的指针开始指在文件开头, 因此会覆写文件
'w+'：        以文本读写模式打开（打开前文件会被清空）。可以使用read*()
'a+'：        以文本读写模式打开（写只能写在文件末尾）。可以使用read*()
'rb+'：      以二进制读写模式打开
'wb+'：    以二进制读写模式打开（打开前文件会被清空）

'ab+'：      以二进制读写模式打开

 


4.2.buffering：设置buffer
0：    代表buffer关闭（只适用于二进制模式）
1：    代表line buffer（只适用于文本模式）
>1：  表示初始化的buffer大小

4.3.errors：报错级别
strict：    字符编码出现问题时会报错
ignore：  字符编码出现问题时程序会忽略而过，继续执行下面的程序

4.4.closefd：
True：  传入的file参数为文件的文件名
False：  传入的file参数只能是文件描述符
Ps：      文件描述符，就是一个非负整数，在Unix内核的系统中，打开一个文件，便会返回一个文件描述符。

注意：使用open打开文件后一定要记得关闭文件对象


5：实例：
存在文件 test.txt ，文件内容如下
'''
hello good boy

how are you?

I am fine.
'''

5.1：以默认的方式打开

>>> f = open('test.txt')
>>> print f.read()
hello good boy

how are you?

I am fine.
>>> f.close()

5.2：以只写的方式打开

>>> f = open('test.txt','w')
>>> f.read()
Traceback (most recent call last):
  File "<pyshell#9>", line 1, in <module>
    f.read()
IOError: File not open for reading
>>> f.write('good bye!\n')
>>> f.close()

>>> f = open('test.txt')
>>> print f.read()
good bye!

>>> f.close()

5.3：以追加的方式打开

>>> f = open('test.txt','a')
>>> f.write('see you tomorrow!\n')
>>> f.close()

>>> f = open('test.txt','r')
>>> print f.read()
good bye!
see you tomorrow!

>>> f.close()

5.4：判断文件是否被关闭

>>> try:
 all_the_text = f.read()
finally:
 f.close()

>>> f.read()
Traceback (most recent call last):
  File "<pyshell#60>", line 1, in <module>
    f.read()
ValueError: I/O operation on closed file

注：不能把open语句放在try块里，因为当打开文件出现异常时，文件对象file_object无法执行close()方法。

6：其他：
file()与open()
相同点： 两者都能够打开文件，对文件进行操作，用法和参数也相似

不同点：
file 打开文件，相当于这是在构造文件类

open 打开文件，是用python的内建函数来操作
"""
class FtpUtils(object):

    __bufsize = 4096
    __defaultDir = "/"

    def connectFTP(self, host, username, password, port = 21, timeout = 600):
        self.ftp = FTP()
        # ftp.set_debuglevel(2)
        self.ftp.connect(host, port, timeout)
        self.ftp.login(username, password)
        self.ftp.encoding = 'UTF-8'
        self.__defaultDir = self.ftp.pwd()

    # 从ftp下载文件 ftputil.downloadFile("b.jpg", "D:\\face\\ftp_b.jpg")返回为1表示成功，0表示失败
    def downloadFile(self, remoteFile, localFile):
        try:
            remoteFilePath, remoteFileName = os.path.split(remoteFile)
            if remoteFilePath and remoteFilePath != "" and remoteFilePath != "/":
                self.ftp.cwd(remoteFilePath)

            fp = open(localFile, 'wb')
            self.ftp.retrbinary('RETR ' + remoteFileName, fp.write, self.__bufsize)
            self.ftp.set_debuglevel(0)
            fp.close()
            return 1
        except BaseException as e:
            print(str(e))
            return 0

    # 从本地上传文件到ftp  ftputil.uploadFile("b.jpg", "D:\\face\\d.jpg") 返回为1表示成功，0表示失败
    def uploadFile(self, remoteFile, localFile):
        try:
            remoteFilePath, remoteFileName = os.path.split(remoteFile)
            if remoteFilePath and remoteFileName != "" and remoteFileName != "/":
                self.makeDirs(remoteFilePath)

            if remoteFileName is None or remoteFileName == "":
                _, remoteFileName = os.path.split(localFile)

            fp = open(localFile, 'rb')

            self.ftp.storbinary('STOR ' + remoteFileName, fp, self.__bufsize)
            self.ftp.set_debuglevel(0)
            fp.close()
            return 1
        except BaseException as e:
            print(str(e))
            return 0

    # 把内容上传文件到ftp  ftputil.uploadFile("b.jpg", "aaaaaa") 返回为1表示成功，0表示失败
    #content为bytes类型， 如果是字符串可以通过bytes(context, "utf-8")进行处理
    def uploadFileContent(self, remoteFile, content):
        try:
            if content is None:
                return 0
            remoteFilePath, remoteFileName = os.path.split(remoteFile)
            if remoteFilePath and remoteFileName != "" and remoteFileName != "/":
                self.makeDirs(remoteFilePath)

            ftpsend = self.ftp.transfercmd('STOR ' + remoteFileName)
            ftpsend.sendall(content)
            ftpsend.close()

            self.ftp.set_debuglevel(0)
            return 1
        except BaseException as e:
            print(str(e))
            return 0

    # 把内容上传文件到ftp  ftputil.uploadFile("b.jpg", "aaaaaa") 返回图片的尺寸:高度，宽度
    def uploadWebImage(self, remoteFile, webFileUrl, referer = None, proxies = None, timeout = 6000):

        httpSpiderUtils = HttpSpiderUtils()
        webData = httpSpiderUtils.spiderImg(webFileUrl, referer, proxies, timeout)

        if self.uploadFileContent(remoteFile, webData) == 1:
            cropper = Cropper()
            return cropper.getImageSize(webData)
        else:
            return 0, 0

    # 把内容上传文件根据感知人脸检测算法进行处理，然后上传到ftp
    def uploadCopFaceWebImage(self, remoteFile, webFileUrl, target_width, target_height, referer = None, proxies = None, timeout = 6000):

        cropper = Cropper()
        cropper.cropFaceWebImg(webFileUrl, "d:\\face\web.jpg", target_width, target_height, referer, proxies, timeout)
        return self.uploadFile(remoteFile, "d:\\face\web.jpg")


    # 把内容上传文件根据感知人脸检测算法进行处理，然后上传到ftp
    def uploadCopFaceWebImage1(self, remoteFile, webFileUrl, target_width, target_height, referer = None, proxies = None, timeout = 6000):

        cropper = Cropper()
        img = cropper.getCropFaceWebImg(webFileUrl, target_width, target_height)
        return self.uploadFile(remoteFile, img)

    def closeFTP(self):
        if self.ftp:
            self.ftp.close()

    def uploadDir(self, remoteDir, localDir):
        try:
            if os.path.isdir(localDir) == False:
                return 0
            localNames = os.listdir(localDir)

            self.makeDirs(remoteDir)
            for localName in localNames:
                src = os.path.join(localDir, localName)
                if os.path.isdir(src):
                    self.uploadDir(localName, src)
                    self.ftp.cwd("..")
                else:
                    self.uploadFile("/", src)
            return 1
        except BaseException as e:
            print(str(e))
            return 0

    def downloadDir(self, remoteDir, localDir):
        try:
            if os.path.isdir(localDir) == False:
                os.makedirs(localDir)
            self.ftp.cwd(remoteDir)
            remoteNames = self.getFileList(".")
            for remoteFile in remoteNames:
                localPath = os.path.join(localDir, remoteFile[1])
                if remoteFile[0] == "dir":
                    self.downloadDir(remoteFile[1], localPath)
                    self.ftp.cwd("..")
                else:
                    self.downloadFile(remoteFile[1], localPath)
            return 1
        except BaseException as e:
            print(str(e))
            return 0

    def getFileList(self, remoteName):
        dir_res = []
        file_res = []
        self.ftp.dir(remoteName, dir_res.append)
        for dirresource in dir_res:
            fileinfo = dirresource.split(" ")
            if (dirresource.startswith("d")):
                file_res.append(["dir", fileinfo[-1]])
            else:
                file_res.append(["file", fileinfo[-1]])
        return file_res


    def changeDir(self, dir):
        self.ftp.cwd(dir)

    def changeRootDir(self):
        self.changeDir(self.__defaultDir)

    def getCurrentDir(self):
        return self.ftp.pwd()

    def makeDirs(self, remoteDirs):
        try:
            self.ftp.cwd(remoteDirs)
        except error_perm:
            try:
                dirList = remoteDirs.split("/")
                for dirName in dirList:
                    self.makeDir(dirName)

            except BaseException as e:
                print (str(e))

    def makeDir(self, remoteDir):
        try:
            self.ftp.cwd(remoteDir)
        except error_perm:
            self.ftp.mkd(remoteDir)
            self.ftp.cwd(remoteDir)

if __name__ == "__main__":
    ftputil = FtpUtils()
    ftputil.connectFTP("172.16.11.181", "jhftpuser", "jhftp0103")
    #ftputil.uploadFile("cc/bb/b.jpg", "D:\\face\\d.jpg")
    #ftputil.uploadFile("cc/bb", "D:\\face\\d.jpg")
    #ftputil.uploadFile("b.jpg", "D:\\face\\d.jpg")
    #ftputil.uploadDir("batcha/img/", "D:\\face\\file")
    #ftputil.uploadFileContent("cc/bb/b.txt", "D:\\face\\d.jpg")

    ih, iw = ftputil.uploadWebImage("cc1/bb/1642420.jpg", "http://img.xgo-img.com.cn/pics/1643/1642420.jpg")
    print(ih,"---", iw)


    #ih, iw = ftputil.uploadWebImage("cc/bb/1642420.jpg", "http://img.xgo-img.com.cn/pics/1643/1642420.jpg")
    #print(ih,"---", iw)
    # proxies = {
    #     "https": "https://101.81.106.155:9797"
    # }
    #ftputil.uploadCopFaceWebImage("cc/bb/100_200.webp", "http://res.cloudinary.com/demo/image/upload/w_300/sample.webp", 100, 200)
    #ftputil.uploadCopFaceWebImage1("cc/bb/200_200.jpg", "http://img.xgo-img.com.cn/pics/1643/1642420.jpg", 100, 200)
    #ipapi = requests.get("http://dynamic.goubanjia.com/dynamic/get/d5d45bc51ed327b9ea1708aa20d3deb0.html?random=yes")
    # print(ipapi)
    # ipapi.encoding = 'utf-8'
    # ipApiDataText = ipapi.text
    # ipApiData = ipApiDataText.strip("\n")
    # ipValue = "https://" + ipApiData
    # # 设置代理
    # if (ipapi):
    #     ipapi.close()
    # proxies = {
    #     "https": ipValue
    # }
    # ih, iw = ftputil.uploadWebImage("0/0/1516008497/pJ6qulXxhPNocel_avatar_uploaded1513167429.56.jpg",
    #                                 "https://img3.doubanio.com/view/celebrity/l_ratio_celebrity/public/pJ6qulXxhPNocel_avatar_uploaded1513167429.56.jpg",
    #                                 "https://www.douban.com/", proxies)
    ih, iw =ftputil.uploadWebImage("0/1/1516476016/p1407158073.93.jpg", "https://img3.doubanio.com/view/celebrity/l_ratio_celebrity/public/p1407158073.93.jpg")
    print(ih, "---", iw)

    #ftputil.uploadDir("batchb/img/", "D:\\face\\file")
    #ftputil.changeRootDir()
    #ftputil.downloadFile("b.jpg", "D:\\face\\ftp_b.jpg")
    #ftputil.downloadFile("cc/bb/b.jpg", "D:\\face\\ftp_cc_bb_b.jpg")
    #ftputil.downloadDir("batchb/img/haibao", "D:\\ftp")
    #ftputil.downloadFile("cc/bb/100_200.jpg", "D:\\face\\100_200.jpg")
    #ftputil.downloadFile("cc/bb/1642420.jpg", "D:\\face\\ftp_1642420.jpg")

    ftputil.closeFTP()
