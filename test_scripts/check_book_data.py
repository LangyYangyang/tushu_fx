import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobRecommend.settings')
django.setup()

# 导入模型
from job.models import SpiderBook

# 检查图书数据
print("检查图书数据...")
book_count = SpiderBook.objects.count()
print(f"总图书数量: {book_count}")

# 检查有发布日期的图书数量
books_with_date = SpiderBook.objects.filter(publish_date__isnull=False).count()
print(f"有发布日期的图书数量: {books_with_date}")

# 检查前10本图书的发布日期
print("\n前10本图书的发布日期:")
books = SpiderBook.objects.all()[:10]
for book in books:
    print(f"书名: {book.book_name}, 发布日期: {book.publish_date}")

# 检查每年的图书数量
print("\n每年的图书数量:")
yearly_counts = {}
for book in SpiderBook.objects.filter(publish_date__isnull=False):
    if book.publish_date:
        year = book.publish_date.year
        if year in yearly_counts:
            yearly_counts[year] += 1
        else:
            yearly_counts[year] = 1

for year, count in sorted(yearly_counts.items()):
    print(f"{year}年: {count}本")
