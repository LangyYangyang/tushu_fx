#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "JobRecommend.settings"
import django
django.setup()
from job import models
from collections import defaultdict

# 模拟 book_analysis 函数的逻辑
print("测试书籍维度分析数据生成...")

# 获取所有图书数据
book_data = models.SpiderBook.objects.all().values()
print(f"获取到 {len(book_data)} 条图书数据")

# 1. 评分区间数量分布
print("\n1. 评分区间数量分布:")
rating_ranges = {
    '9.0分及以上:神作': 0,
    '8.5-8.9分:大师之作': 0,
    '8.0-8.4分:口碑之选': 0,
    '7.0-7.9:有争议的佳作': 0,
    '6.0-6.9:平庸之作': 0,
    '6.0分以下不包括0:烂书': 0,
    '0:尚未评分': 0
}
for book in book_data:
    if book['rating']:
        rating = float(book['rating'])
        if rating >= 9.0:
            rating_ranges['9.0分及以上:神作'] += 1
        elif 8.5 <= rating < 9.0:
            rating_ranges['8.5-8.9分:大师之作'] += 1
        elif 8.0 <= rating < 8.5:
            rating_ranges['8.0-8.4分:口碑之选'] += 1
        elif 7.0 <= rating < 8.0:
            rating_ranges['7.0-7.9:有争议的佳作'] += 1
        elif 6.0 <= rating < 7.0:
            rating_ranges['6.0-6.9:平庸之作'] += 1
        elif rating > 0 and rating < 6.0:
            rating_ranges['6.0分以下不包括0:烂书'] += 1
    else:
        rating_ranges['0:尚未评分'] += 1
print(rating_ranges)

# 2. 价格分布
print("\n2. 价格分布:")
price_ranges = {
    '0-5': 0,
    '5-10': 0,
    '10-20': 0,
    '20-30': 0,
    '30-40': 0,
    '40-60': 0,
    '60-80': 0,
    '80-100': 0,
    '100以上': 0
}
for book in book_data:
    if book['price']:
        price = float(book['price'])
        if price < 5:
            price_ranges['0-5'] += 1
        elif 5 <= price < 10:
            price_ranges['5-10'] += 1
        elif 10 <= price < 20:
            price_ranges['10-20'] += 1
        elif 20 <= price < 30:
            price_ranges['20-30'] += 1
        elif 30 <= price < 40:
            price_ranges['30-40'] += 1
        elif 40 <= price < 60:
            price_ranges['40-60'] += 1
        elif 60 <= price < 80:
            price_ranges['60-80'] += 1
        elif 80 <= price < 100:
            price_ranges['80-100'] += 1
        else:
            price_ranges['100以上'] += 1
print(price_ranges)

# 3. 出版年份分布
print("\n3. 出版年份分布:")
year_ranges = {}
for book in book_data:
    if book['publish_date']:
        try:
            year = book['publish_date'].year
            year_str = str(year)
            if year_str in year_ranges:
                year_ranges[year_str] += 1
            else:
                year_ranges[year_str] = 1
        except:
            pass
# 按年份排序
year_ranges = dict(sorted(year_ranges.items()))
print(year_ranges)

# 4. 热度最高top10
print("\n4. 热度最高top10:")
hot_books = []
for book in book_data:
    if book['read_count']:
        hot_books.append((book['book_name'], book['read_count']))
# 排序并取前10
hot_books = sorted(hot_books, key=lambda x: x[1], reverse=True)[:10]
print(hot_books)

print("\n测试完成！")
