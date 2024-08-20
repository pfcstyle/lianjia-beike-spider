#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 小区信息的数据结构


class XiaoQu(object):
    def __init__(self, chinese_city, district, area, name, price, on_sale, type):
        self.chinese_city = chinese_city
        self.district = district
        self.area = area
        self.price = price
        self.name = name
        self.on_sale = on_sale
        self.type = type

    def text(self):
        return self.chinese_city + "," + \
            self.district + "," + \
            self.area + "," + \
            self.name + "," + \
            self.price + "," + \
            self.on_sale + "," + \
            self.type
