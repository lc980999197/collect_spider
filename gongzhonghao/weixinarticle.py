import random,json,os,time,re
import requests,lxml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

__author__ = "lz"
"""仅用于测试，勿用于非法图,代码中的谷歌驱动为chrome 74，其他版本chrome
对应驱动请自行下载https://chromedriver.storage.googleapis.com/index.html"""

class WeinxinArticle(object):
    def __init__(self,url):
        #配置无头浏览器
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('user-agent="%s"'%UserAgent().random) 
        self.broswer = webdriver.Chrome(executable_path="driver/chromedriver.exe",chrome_options=chrome_options)
        self.broswer.fullscreen_window()
        self.imgpath = "weixinimg"
        #创建公众号图片文件夹
        if not os.path.exists(self.imgpath):
            os.mkdir(self.imgpath)
        #初始化需要获取的公众号地址
        self.url = url
    def __del__(self):
        print("爬取结束，退出浏览器")
        self.broswer.quit()
    def send_request(self,url,rsp_type=0):
        """用于发送请求获取数据的方法rsp_type为0返回json，为1返回text,为2返回content"""
        res = requests.get(url,headers={"user-agent=":UserAgent().random})
        if rsp_type == 0:
            return res.json()
        elif rsp_type ==1:
            return res.text
        elif rsp_type ==2:
            return res.content
        else:
            raise TypeError("传入的响应类型错误")    
    def run(self):
        url = self.url
        self.broswer.get(url)
        #WebDriverWait(self.broswer,5).until(lambda x:x.find_element_by_id("js_content").is_displayed())#等待正文出现
        self.scroll()#模拟滚动条事件，加载公众号图片
        content = self.broswer.page_source
        #清洗数据
        content = self.clean_data(content)       
        with open('%s.html'%self.url.split("/")[-1],"w",encoding="utf-8") as file:
            file.write(content)

    def scroll(self):
        """滚动条加载,用于滚动条逐渐加载公众号图片"""
        for i in range(0,10000,500):
            while i<= 10000:
                print("持续下拉文章中，请稍后...")
                self.broswer.execute_script("window.scrollTo(0,%s)" %i)
                time.sleep(0.5)
                break

    def clean_data(self,content):
        """清洗无用dom"""
        content = re.sub(r"<script.*?script>","",content,count=0,flags=re.S)#清洗script标签
        content = re.sub(r'["|(](//)','"https://',content,count=0,flags=re.S)#清洗相对路径图片,ico,视频等
        content = re.sub(r'src="/mp/qrcode\?',\
            'src="https://mp.weixin.qq.com/mp/qrcode?',content,count=0,flags=re.S)#清洗右侧二维码
        content = content.replace('crossorigin="anonymous"','')#去除跨域属性，影响加载本地图片,项目中需评测该属性影响
        content = self.solve_image(content)#替换原公众号图片,解决防盗链
        return content

    def solve_image(self,dom):
        """传入dom结构，将图片缓存到本地然后返回替换后的dom"""
        soup = BeautifulSoup(dom,"lxml").select("img")
        title = self.url.split("/")[-1]
        if not os.path.exists("%s/%s" %(self.imgpath,title)):
            os.mkdir("%s/%s" %(self.imgpath,title)) 
        for index,val in enumerate(soup):
            if "src" in val.attrs and val.attrs['src'].startswith("https://mmbiz.qpic.cn"):#正文图片特征
                try:
                    img_file = self.send_request(val.attrs['src'],rsp_type=2)
                    img_ralate_path = "%s/%s/%s.jpeg" %(self.imgpath,title,index)
                    
                    with open(img_ralate_path,"wb") as file:
                        file.write(img_file)
                    dom = dom.replace(val.attrs['src'].replace("&","&amp;"),img_ralate_path,1)
                    print(val.attrs['src'])
                    print(img_ralate_path)
                    print("------------------")
                except Exception:
                    pass
        return dom
    def main(self):
        """主程序入口"""
        self.run()

if __name__ == "__main__":
    """传入单篇公众号地址进行爬取"""
    WeinxinArticle("https://mp.weixin.qq.com/s/qSXph5ZjF6y5i-KI_LMlGg").main()