#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬虫基类
# 爬虫名常量，用来设置爬取哪个站点

import threading
import requests
from lib.zone.city import lianjia_cities, beike_cities
from lib.utility.date import *
import lib.utility.version
import random

thread_pool_size = 6
proxy_pool_url = 'http://127.0.0.1:5010'  # 参考proxy_pool项目，本地搭建的代理池地址

# 防止爬虫被禁，随机延迟设定
# 如果不想delay，就设定False，
# 具体时间可以修改random_delay()，由于多线程，建议数值大于10
RANDOM_DELAY = True
LIANJIA_SPIDER = "lianjia"
BEIKE_SPIDER = "ke"
# SPIDER_NAME = LIANJIA_SPIDER
SPIDER_NAME = BEIKE_SPIDER


class BaseSpider(object):
    @staticmethod
    def random_delay():
        if RANDOM_DELAY:
            time.sleep(random.randint(0, 15))

    def __init__(self, name):
        self.name = name
        if self.name == LIANJIA_SPIDER:
            self.cities = lianjia_cities
        elif self.name == BEIKE_SPIDER:
            self.cities = beike_cities
        else:
            self.cities = None
        # 准备日期信息，爬到的数据存放到日期相关文件夹下
        self.date_string = get_date_string()
        print('Today date is: %s' % self.date_string)

        self.total_num = 0  # 总的小区个数，用于统计
        print("Target site is {0}.com".format(SPIDER_NAME))
        self.mutex = threading.Lock()  # 创建锁

    def create_prompt_text(self):
        """
        根据已有城市中英文对照表拼接选择提示信息
        :return: 拼接好的字串
        """
        city_info = list()
        count = 0
        for en_name, ch_name in self.cities.items():
            count += 1
            city_info.append(en_name)
            city_info.append(": ")
            city_info.append(ch_name)
            if count % 4 == 0:
                city_info.append("\n")
            else:
                city_info.append(", ")
        return 'Which city do you want to crawl?\n' + ''.join(city_info)

    def get_chinese_city(self, en):
        """
        拼音拼音名转中文城市名
        :param en: 拼音
        :return: 中文
        """
        return self.cities.get(en, None)
    
    @staticmethod
    def get_proxy(isHttps: bool):
        return requests.get(f"{proxy_pool_url}/get?type={'https' if isHttps else 'http'}").json()

    @staticmethod
    def delete_proxy(proxy):
        requests.get(f"{proxy_pool_url}/delete?proxy={proxy}")
    
    @staticmethod
    def request_get(url: str, timeout=10, headers=None):
        if proxy_pool_url is None:
            return requests.get(url, timeout=timeout, headers=headers)
        proxy = BaseSpider.get_proxy(url.startswith('https://')).get("proxy")
        retry_count = 3
        while retry_count > 0:
            
            try:
                response = requests.get(url, timeout=timeout, headers=headers, proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"}, verify=False)
                # 使用代理访问
                return response
            except Exception as e:
                retry_count -= 1
        # 无效代理， 删除代理池中代理
        BaseSpider.delete_proxy(proxy)
        return None