#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobRecommend.settings')
import django
django.setup()

from job import models

# 检查 SendList 表是否存在
print("检查 SendList 表结构:")
print(f"SendList 表名: {models.SendList._meta.db_table}")
print(f"SendList 字段: {[field.name for field in models.SendList._meta.fields]}")

# 检查 SendList 表中的数据
print("\n检查 SendList 表数据:")
send_list_data = models.SendList.objects.all()
print(f"SendList 数据量: {send_list_data.count()}")
for item in send_list_data:
    print(f"send_id: {item.send_id}, user_id: {item.user_id}, book_id: {item.book_id}")

# 检查 SpiderBook 表中的数据
print("\n检查 SpiderBook 表数据:")
book_data = models.SpiderBook.objects.all()
print(f"SpiderBook 数据量: {book_data.count()}")

# 检查 UserList 表中的数据
print("\n检查 UserList 表数据:")
user_data = models.UserList.objects.all()
print(f"UserList 数据量: {user_data.count()}")
for user in user_data:
    print(f"user_id: {user.user_id}, user_name: {user.user_name}")
