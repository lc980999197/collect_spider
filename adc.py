import requests
from bs4 import BeautifulSoup
from lxml import etree
import subprocess
from threading import Thread
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class AdcFilm(object):

    def __init__(self):
        self.domain = "https://www.adc000.com"
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        self.categories = {"自拍": f"{self.domain}/html/amateur/list_5_1.html",
                      "亚洲": f"{self.domain}/html/asia/list_4_1.html",
                      "剧情": f"{self.domain}/html/story/list_7_1.html",
                      "欧美": f"{self.domain}/html/west/list_6_1.html",
                      "动漫": f"{self.domain}/html/hentai/list_8_1.html",
                      }
    def get_film_list(self, url):
        """获取每个分页的视频列表"""
        # url = "https://adc006.com/html/amateur/list_5_2.html"
        print("解析分页数据，生成视频列表中....")
        response = requests.get(url, headers=self.headers, verify=False)
        soups = BeautifulSoup(response.text, "lxml").select(".col-sm-6 .list-item a")
        print("视频列表生成完毕....")
        return [f"{self.domain}{soup.attrs['href']}" for soup in soups]

    def get_film(self, url):
        """下载视频详情页视频"""
        # url = "https://adc006.com/html/amateur/28.html"
        response = requests.get(url, headers = self.headers, verify=False)
        title = BeautifulSoup(response.text, "lxml").select_one("title").text
        print(f"开始下载:{title}.mp4，请耐心等待...")
        cmd_download = f"you-get -O {title.replace(' ','_')} -o anime --skip-existing-file-size-check {url}"
        try:
            res = subprocess.run(cmd_download, shell=True, stdout=subprocess.PIPE, timeout=30*60)
            res = res.stdout.decode("utf-8")
            if "100%" in res:
                print(f"{title}下载完成...")
            else:
                print(f"{title}下载失败，提示:{res}")
        except Exception:
            pass

    def get_url(self, url):
        """获取该分类下所有的url"""
        print("获取分页数据....")
        url_split = url.split("_")
        res = requests.get(url, headers = self.headers, verify=False)
        xpath_list = etree.HTML(res.text).xpath("//a[text()='末页']")
        all_pages = int(xpath_list[0].attrib["href"].split("_")[-1].split(".")[0])
        return [f'{url_split[0]}_{url_split[1]}_{page}.html' for page in range(1,all_pages+1)]

if __name__ == '__main__':
    adc = AdcFilm()
    ulr_list = adc.get_url(adc.categories['动漫'])
    for url in ulr_list:
        film_list = adc.get_film_list(url)
        for film in film_list:
            adc.get_film(film)
