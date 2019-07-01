import requests
import lxml
import json
from bs4 import BeautifulSoup
from pathlib import Path
class Qishuwang(object):
    def __init__(self):
        """初始化网站域名，编码格式，分类信息"""
        self.domain = "http://www.qishu.cc"
        self.encoding = "GB2312"
        self.cate_file_name = "qishuwang_novel_caterory.txt"
        self.categories = self.__get_novel_category()

    def __get_novel_category(self):
        """初始化小说分类方法"""
        category_file = self.get_cache(self.cate_file_name)
        try:
            if category_file:
                return category_file
            else:
                #requests抓取首页分类数据
                res_text = Qishuwang.http_requests(self.domain,self.encoding) 
                soup = BeautifulSoup(res_text,"lxml").select("#globalNavUL a")[1:]#切片去除首页
                category_dict = {}
                for i in soup:
                    category_dict[i.text] = [f"{self.domain}{i.attrs['href']}",0]
                #字典添加分类的总分页信息
                category_dict = self.aio_requests(category_dict)
                self.write_cache(category_dict,self.cate_file_name)
                return category_dict
        except Exception as e:
            exit("系统异常，退出程序,异常为",e)   
    def generator_pages(self,category):
        """根据分类返回该分类所有分页"""
        if category not in self.categories:
            return []
        else:
            base_url = self.categories[category][0].split("_")[0]
            return (f"{base_url}_{i}.html" for i in range(1,int(self.categories[category][1])))

    def aio_requests(self,url_dict):
        """异步请求解析分类数据，添加总分页到数据"""
        import asyncio
        from aiohttp import ClientSession
        async def get_result(category,url):
            async with ClientSession() as session:
                async with session.get(url) as response:
                    print(f"{category}解析完成")
                    res_text = await response.text(encoding=self.encoding,errors="ignore")
                    url_dict[category][1] = BeautifulSoup(res_text,"lxml").select("code")[0].select("a")[-1].text if res_text else 0
        loop = asyncio.get_event_loop()
        tasks = []
        for category in url_dict:
            task = asyncio.ensure_future(get_result(category,url_dict[category][0]))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        return url_dict

    @staticmethod
    def get_cache(file_name):
        """获取json序列化缓存的文件，没有或异常False"""
        abs_file = Path(Path(__file__).cwd()/file_name)  
        if abs_file.is_file():
            with abs_file.open() as f:
                try:
                    return json.load(f) 
                except Exception:
                    return False 
        else:
            return False 

    @staticmethod
    def write_cache(data,file_name):
        """json序列化写入缓存文件，已存在则抛出异常，入参为数据和文件名"""
        abs_file = Path(Path(__file__).cwd()/file_name)
        if abs_file.is_file():
            raise FileExistsError("该文件已存在")
        else:
            with open(abs_file,"w") as f:
                json.dump(data,f)     

    @staticmethod
    def http_requests(url,encoding):
        try:
            res = requests.get(url,timeout=3)
            res.encoding=encoding 
            return res.text 
        except Exception:
            print(f"链接{url}请求失败")
            return False 

if __name__ == "__main__":
    """简单测试，需要添加批量获取小说和下载地址等功能"""
    g = Qishuwang().generator_pages("玄幻奇幻")
    for i in g:
        print(i)