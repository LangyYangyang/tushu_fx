import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobRecommend.settings')
django.setup()

from job.models import SpiderBook
from collections import defaultdict

# 直接复制视图函数的逻辑来检查数据
book_data = SpiderBook.objects.all().values()

# 1. 评分区间数量分布（10分制）
rating_ranges = {
    '9.0分及以上:神作': 0,
    '8.5-8.9分:大师之作': 0,
    '8.0-8.4分:口碑之选': 0,
    '7.0-7.9分:有争议的佳作': 0,
    '6.0-6.9分:平庸之作': 0,
    '6.0分以下:烂书': 0,
    '尚未评分': 0
}
for book in book_data:
    if book['rating']:
        rating = float(book['rating'])
        if rating == 0:
            rating_ranges['尚未评分'] += 1
        elif rating >= 9.0:
            rating_ranges['9.0分及以上:神作'] += 1
        elif 8.5 <= rating < 9.0:
            rating_ranges['8.5-8.9分:大师之作'] += 1
        elif 8.0 <= rating < 8.5:
            rating_ranges['8.0-8.4分:口碑之选'] += 1
        elif 7.0 <= rating < 8.0:
            rating_ranges['7.0-7.9分:有争议的佳作'] += 1
        elif 6.0 <= rating < 7.0:
            rating_ranges['6.0-6.9分:平庸之作'] += 1
        elif rating < 6.0:
            rating_ranges['6.0分以下:烂书'] += 1
    else:
        rating_ranges['尚未评分'] += 1

print("=== 评分区间数据 ===")
for k, v in rating_ranges.items():
    print(f"  {k}: {v}")

# 2. 价格分布
price_ranges = {
    '0-5元': 0,
    '5-10元': 0,
    '10-20元': 0,
    '20-30元': 0,
    '30-40元': 0,
    '40-60元': 0,
    '60-80元': 0,
    '80-100元': 0,
    '100元以上': 0
}
for book in book_data:
    if book['price']:
        price = float(book['price'])
        if price <= 5:
            price_ranges['0-5元'] += 1
        elif 5 < price <= 10:
            price_ranges['5-10元'] += 1
        elif 10 < price <= 20:
            price_ranges['10-20元'] += 1
        elif 20 < price <= 30:
            price_ranges['20-30元'] += 1
        elif 30 < price <= 40:
            price_ranges['30-40元'] += 1
        elif 40 < price <= 60:
            price_ranges['40-60元'] += 1
        elif 60 < price <= 80:
            price_ranges['60-80元'] += 1
        elif 80 < price <= 100:
            price_ranges['80-100元'] += 1
        else:
            price_ranges['100元以上'] += 1

print("\n=== 价格分布数据 ===")
for k, v in price_ranges.items():
    print(f"  {k}: {v}")

# 3. 出版年份分布
year_ranges = defaultdict(int)
for book in book_data:
    if book['publish_date']:
        try:
            year = book['publish_date'].year
            year_ranges[str(year)] += 1
        except:
            pass
year_ranges = dict(sorted(year_ranges.items()))

print("\n=== 出版年份数据 ===")
for k, v in year_ranges.items():
    print(f"  {k}: {v}")

# 4. 热度最高Top10
hot_books = []
for book in book_data:
    if book['read_count']:
        book_name = book['book_name']
        if len(book_name) > 10:
            book_name = book_name[:10] + '...'
        hot_books.append({
            'book_name': book_name,
            'read_count': book['read_count'],
            'author': book['author']
        })
hot_books = sorted(hot_books, key=lambda x: x['read_count'], reverse=True)[:10]

print("\n=== 热度最高Top10 ===")
for book in hot_books:
    print(f"  {book['book_name']}: {book['read_count']}")
