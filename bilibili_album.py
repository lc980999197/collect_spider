#用于测试获取bilibili相册，勿用于商业或其他非法用途
__author__ = "lz"

import random,requests,json,os,threading,urllib3
from queue import Queue,Empty
import gevent
from gevent import monkey
monkey.patch_all(thread=False)
#移除控制台verify=False造成的报错
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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
    headers['refer'] = "https://h.bilibili.com/eden/draw_area"
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    #headers['host'] = 'api.vc.bilibili.com'
    return headers

class Album(object):
    def __init__(self):
        #Bilibili相册api基础链接
        self.url = "https://api.vc.bilibili.com/link_draw/v2/Doc/list?category=all&type=hot&page_size=20&page_num="
        #存放所有相册的列队
        self.q = Queue()
        #初始化下载的文件夹
        if not os.path.exists("bilibili_album"):
            os.mkdir("bilibili_album")
        self.dir = "bilibili_album"
    def send_request(self,url,rsp_type=0):
        """用于发送请求获取数据的方法rsp_type为0返回json，为1返回text,为2返回content"""
        res = requests.get(url,headers=get_headers(),verify=False)
        if rsp_type == 0:
            return res.json()
        elif rsp_type ==1:
            return res.text
        elif rsp_type ==2:
            return res.content
        else:
            raise TypeError("传入的响应类型错误")
    def collect_url(self,page):
        """用于解析收集所有相册,传入单条分页，获取数据插入列队"""
        url = self.url + str(page)
        try:
            json_data = self.send_request(url,rsp_type=0)
            data = json_data['data']['items']
            for i in data:
                my_dict = {}
                my_dict['author'] = i['user']['name']
                my_dict['title'] = i['item']['title']
                my_dict['upload_time'] = i['item']['upload_time']
                my_dict['pics'] = i['item']['pictures']
                self.q.put(my_dict)
                print("相簿\"%s\"解析完成" %my_dict['title'])
        except Exception:
            print("发生未知异常，请检查网络或者接口是否可通信")
    def save_thread(self):
        """线程任务，用于存储单张图片"""
        t = threading.Thread(target=self.get_pic)
        t.start()
        t.join()
    def get_pic(self):
        """用于下载图片"""
        try:
            while True:
                #阻塞模式取图，判断10s无法获取则无数据，终止程序
                pic = self.q.get(block=True,timeout=10)
                print("开始下载相簿\"%s\"" %pic['title'])
                for idx,val in enumerate(pic['pics']):
                    ext = val['img_src'].split(".")[-1]
                    pic_path = "%s/%s%s.%s" %(self.dir,pic['title'],str(idx),ext)
                    pic_content = self.send_request(val['img_src'],rsp_type=2)
                    with open(pic_path,"wb") as file:
                        file.write(pic_content)
        except Empty:
            print("全部下载完成")
            exit()
    def run(self,total):
        """Link Start！传入想要获取的总分页，截止2019/06/01总计24页"""
        collect_job = [ gevent.spawn(self.collect_url(page)) for page in range(0,total)]
        gevent.joinall(collect_job)
        #同时开始缓存图片
        self.save_thread()
if __name__ == "__main__":
    Album().run(24)#传入获取的总分页

#to do 加入多线程/多进程下载图片  流量不够不进行尝试了ORZ