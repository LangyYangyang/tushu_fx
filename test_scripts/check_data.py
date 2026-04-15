import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobRecommend.settings')
django.setup()

from job.models import SpiderBook

print('图书总数:', SpiderBook.objects.count())
print('有阅读人数的图书:', SpiderBook.objects.filter(read_count__gt=0).count())
print('有评分的图书:', SpiderBook.objects.filter(rating__gt=0).count())
print('有价格的图书:', SpiderBook.objects.filter(price__gt=0).count())
print('有出版日期的图书:', SpiderBook.objects.filter(publish_date__isnull=False).count())

# 显示前5本书的信息
print('\n前5本书的信息:')
for book in SpiderBook.objects.all()[:5]:
    print(f'书名: {book.book_name}, 评分: {book.rating}, 价格: {book.price}, 阅读人数: {book.read_count}')
