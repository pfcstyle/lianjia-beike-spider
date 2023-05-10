#!/usr/bin/env python
# coding=utf-8

from lib.spider.ershou_spider import *
from csv import reader
import json
import os


def list_and_sort_sub_dirs(root: str, filter):
    sub_dirs = [d for d in os.listdir(
        root) if os.path.isdir(os.path.join(root, d)) and filter(d)]
    return sorted(sub_dirs)


class ErshouPriceTracker:
    def __init__(self, city, start_date):
        self.city = city
        self.start_date = start_date
        # {"$houseid": {"city":"","district":"","area":"","house_id":"","prices":[],"dates":[]}}
        self.house_prices = {}

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
                        district, area, house_id, price = row[1], row[2], row[3], row[5]
                        ershou_price_dict[house_id] = (
                            district, area, price, ",".join(row))

        return ershou_price_dict

    def start(self):
        city_path = create_city_path("{0}/ershou".format(SPIDER_NAME), city)
        dates = list_and_sort_sub_dirs(
            city_path, lambda x: x >= self.start_date)
        print("City is {}, Time Series: {}".format(city, dates))

        for date in dates:
            houses = self.load_ershou_data(city, date)
            for house_id, (district, area, price, row) in houses.items():
                house_info = self.house_prices.get(house_id, None)
                if house_info is None:
                    self.house_prices[house_id] = {
                        "district": district, "area": area, "prices": [price], "dates": [date], "link": ErShouSpider.get_house_url(self.city, house_id), "row": row}
                else:
                    prices = self.house_prices[house_id].get("prices", [])
                    if len(prices) == 0 or prices[-1] != price:
                        self.house_prices[house_id].get("dates").append(date)
                        self.house_prices[house_id].get("prices").append(price)
                        self.house_prices[house_id]['row'] = row

        price_ts_file = "ershou_timeseries_prices.csv"
        houses = []
        for house_id, house_info in self.house_prices.items():
            houses.append(house_info)
        houses = sorted(houses, key=lambda house: (house['district'], house['area'], - len(
            house['prices']),  float(house['prices'][-1].split('万')[0])))
        with open(price_ts_file, "w") as outfile:
            for house_info in houses:
                outfile.write("{}, {}, {}, {}".format(
                    house_info['prices'], house_info['dates'], house_info['link'], house_info['row']))
                outfile.write('\n')

        print("save price time-series data to : " + price_ts_file)


if __name__ == "__main__":
    city = "bj"
    # 允许用户通过命令直接指定
    if len(sys.argv) == 1:
        print("Wait for your choice.")
        # 让用户选择爬取哪个城市的二手房小区价格数据
        start_date = input("开始日期: ")
    elif len(sys.argv) == 2:
        start_date = str(sys.argv[1])
        print("City is: {0}, Date from {1} ".format(city,
              start_date))
    else:
        print("At most accept one parameter.")
        exit(1)

    tracker = ErshouPriceTracker(city, start_date)
    tracker.start()
