#!/usr/bin/env python
# coding=utf-8
# author: Zeng YueTian
# 此代码仅供学习与交流，请勿用于商业用途。
# 获得指定城市的二手房数据

from lib.spider.ershou_spider import *
from csv import reader
import json


class ErshouTrending:
    def __init__(self, city, start_date, end_date):
        self.city = city
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def load_ershou_data(city: str, date: str):
        ershou_price_dict = {}
        date_path = create_date_path(
            "{0}/ershou".format(SPIDER_NAME), city, date)
        for root, dirs, files in os.walk(date_path, topdown=False):
            for name in files:
                csv_file = os.path.join(root, name)
                with open(csv_file, 'r') as read_obj:
                    csv_reader = reader(read_obj)
                    for row in csv_reader:
                        house_id, price, pic = row[3], row[5], row[7]
                        ershou_price_dict[house_id] = (
                            price, pic, ",".join(row))

        return ershou_price_dict

    def start(self):
        start_prices = self.load_ershou_data(self.city, self.start_date)
        end_prices = self.load_ershou_data(self.city, self.end_date)

        price_up = {}
        price_down = {}
        xiajia_houses = {}  # 下架房源
        shangjia_houses = {}  # 上架房源

        pic_to_houses = {}
        for house_id, (end_price, pic, csv_row) in end_prices.items():
            # print("house_id: {}, end_price: {}\n".format(house_id, end_price))
            if start_prices.get(house_id, None) is None:
                shangjia_houses[house_id] = csv_row

        for house_id, (start_price, pic, csv_row) in start_prices.items():
            if end_prices.get(house_id, None) is None:
                xiajia_houses[house_id] = csv_row
                continue

            end_price, pic, _ = end_prices.get(house_id)
            start_price_f = float(start_price.split("万")[0])
            end_price_f = float(end_price.split("万")[0])
            if end_price_f > start_price_f:
                price_up[house_id] = (start_price, end_price)
            elif end_price_f < start_price_f:
                price_down[house_id] = (start_price, end_price)

        print("新增房源数量: {}".format(len(shangjia_houses)))
        print("下架房源数量: {}".format(len(xiajia_houses)))
        print("降价房源数量: {}".format(len(price_down)))
        print("涨价房源数量: {}".format(len(price_up)))

        trending_path = create_date_path(
            "{0}/ershou_trending".format(SPIDER_NAME), city, "")
        trending_csv_file = trending_path + \
            "{}-{}.csv".format(start_date, end_date)
        with open(trending_csv_file, "w") as f:
            for house_id, (start_price, end_price) in price_down.items():
                _, pic, csv_row = end_prices.get(house_id)
                f.write("降价房源: {}📉{} {} {}\n".format(
                    start_price, end_price, ErShouSpider.get_house_url(city, house_id), csv_row))
            for house_id, (start_price, end_price) in price_up.items():
                _, pic, csv_row = end_prices.get(house_id)
                f.write("涨价房源: {}💹{} {} {}\n".format(
                    start_price, end_price, ErShouSpider.get_house_url(city, house_id), csv_row))
            for house_id, csv_row in shangjia_houses.items():
                f.write("✅上架房源: {} {}\n".format(
                    ErShouSpider.get_house_url(city, house_id), csv_row))
            for house_id, csv_row in xiajia_houses.items():
                f.write("⛔️下架房源: {} {}\n".format(
                    ErShouSpider.get_house_url(city, house_id), csv_row))

        print("save trending data to : " + trending_csv_file)


if __name__ == "__main__":
    city = "bj"
    # 允许用户通过命令直接指定
    if len(sys.argv) == 1:
        print("Wait for your choice.")
        # 让用户选择爬取哪个城市的二手房小区价格数据
        start_date = input("开始日期: ")
        end_date = input("截止日期: ")
    elif len(sys.argv) == 3:
        start_date = str(sys.argv[1])
        end_date = str(sys.argv[2])
        print("City is: {0}, Date from {1} - {2}".format(city,
              start_date, end_date))
    else:
        print("At most accept one parameter.")
        exit(1)

    trending = ErshouTrending(city, start_date, end_date)
    trending.start()
