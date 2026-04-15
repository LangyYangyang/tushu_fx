import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobRecommend.settings')
django.setup()

from job.models import SpiderBook
from collections import defaultdict

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

# 评分区间数据转换为ECharts需要的格式
rating_data = []
for range_name, count in rating_ranges.items():
    rating_data.append({'value': count, 'name': range_name})

print("=== 评分区间JSON数据 ===")
print(json.dumps(rating_data, ensure_ascii=False))
