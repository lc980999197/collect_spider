#!/usr/bin/python
#仅为研究代码调试，勿用于其他非法用途 ,不可描述
import requests
from bs4 import BeautifulSoup
import lxml
import random
import time
import re
import os
from urllib import parse
import gevent
import urllib
from gevent import monkey
from queue import Queue
import threading
monkey.patch_all(thread=False)
def get_headers():
    headers_explore = random.choice(['firefox','chrome','opera','sarafi','other'])
    if(headers_explore == 'firefox'):
        headers1 = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        headers2 = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}
        headers = random.choice([headers1,headers2])
    elif(headers_explore == 'chrome'):
        headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3236.0 Safari/537.36'}
    else:
        headers = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41'}
    headers['refer'] = "https://www.qipa10.com/"
    headers['Accept-Encoding'] = 'gzip'
    return headers

class Qipa(object):
    def __init__(self):
        #初始化下载的文件夹
        if not os.path.exists("qipavideo"):
            os.mkdir("qipavideo")
        self.save_path = "qipavideo"
        self.headers = get_headers()
        self.baseurl = 'https://www.qipa10.com/videos?page='
        self.domain = 'https://www.qipa10.com'
        self.q = Queue()
    def get_video_url(self,page):
        urls = self.baseurl+str(page)
        url_list = []
        res = requests.get(urls,headers=self.headers,verify=False)
        soup = BeautifulSoup(res.text,'lxml')
        pre = soup.select('.well-sm a')
        for i in pre:
            vi = self.domain + i.attrs['href']
            url_list.append(vi)
        for i in url_list:
            dict_list = {}
            title = re.split(r'/',i,flags=0)[-1]
            res2 = requests.get(i,headers=self.headers)
            soup2 = BeautifulSoup(res2.text,'lxml')
            try:
                last = soup2.select('video source')[-1].attrs['src']
                if "http" not in last:#简单判断URL，不符合则跳过
                    continue
                dict_list[title] = last
                path = "%s/%s.mp4" %(self.save_path,title)              
                print("视频%s.mp4地址获取成功，已放入列队" %title)
                self.q.put(dict_list)
            except Exception:
                print("发生未知异常，已忽略")
                pass
        print("第%s页解析完成,持续下载中......" %page)
    def download_video(self,num):
        print("线程%s启动！"%num)
        while True:#开始下载文件，若60S*5内没有取到新增数据则退出程序
            try:
                mp4 = self.q.get(block=True,timeout=60*5)
                for k in mp4:
                    path = "%s/%s.mp4" %(self.save_path,k)
                    if(os.path.exists(path)):#跳过已存在文件
                        print("文件%s已存在，已忽略" %k)
                        continue               
                    print("开始写入%s" %path)
                    with open(path,"wb") as file:
                        file.write(requests.get(mp4[k]).content)
                    print('%s下载完成!' %path)
            except Exception:
                exit("全部下载完成，退出程序")
    def thread_start(self):
        for i in range(4):
            t = threading.Thread(target=self.download_video,args=(i,))
            t.start()
    def gevent_start(self,start,end):
        if start < 1:
            exit("下载页码过小，程序退出")
        job = [ gevent.spawn(self.get_video_url(page)) for page in range(start,end) ]
        gevent.joinall(job)
    def run(self,start=1,end=40):
        print("开始解析，请稍等......")
        #启动获取链接线程
        thread_spider_url = threading.Thread(target=self.gevent_start,args=(start,end,))
        thread_spider_url.start()
        print("开始同步进行下载视频")
        #启动多线程下载
        self.thread_start()
Qipa().run(1,40)#此参数设置下载的页码

#to do  关闭线程
