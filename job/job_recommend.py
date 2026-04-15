#!/usr/bin/python3.9.10
# -*- coding: utf-8 -*-
# @Time    : 2023/2/18 9:41
# @File    : job_recommend.py
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "JobRecommend.settings"
import django

django.setup()
from job import models
from math import sqrt, pow
import operator
from django.db.models import Subquery, Q, Count
import random


# 计算相似度
def similarity(book1_id, book2_id):
    book1_set = models.SendList.objects.filter(book=book1_id)
    # book1的收藏用户数
    book1_sum = book1_set.count()
    # book2的收藏用户数
    book2_sum = models.SendList.objects.filter(book=book2_id).count()
    # 两者的交集
    common = models.SendList.objects.filter(user__in=Subquery(book1_set.values('user')), book=book2_id).values(
        'user').count()
    # 没有人收藏当前图书
    if book1_sum == 0 or book2_sum == 0:
        return 0
    similar_value = common / sqrt(book1_sum * book2_sum)  # 余弦计算相似度
    return similar_value


# 基于物品
def recommend_by_item_id(user_id, k=9):
    try:
        # 获取用户设置的图书类型
        current_user = models.UserList.objects.get(user_id=user_id)
        if current_user.userexpect_set.count() != 0:
            user_expect = list(models.UserExpect.objects.filter(user=user_id).values("key_word", "category"))[0]
            # print(user_expect)
            # 处理多个category值的情况
            category_list = user_expect['category'].split(',') if user_expect['category'] else []
            # 构建查询条件
            from django.db.models import Q
            query = Q()
            if category_list:
                # 使用Q对象构建多个category的查询条件
                category_query = Q()
                for category in category_list:
                    category = category.strip()
                    if category == '其他':
                        # 如果用户选择了"其他"，则推荐category为空或者数量较少的类型
                        category_query |= Q(category='')
                        category_query |= Q(category__in=['中国', '互联网', '人生', '传记', '创作', '励志', '历史', '哲学', '商业', '回忆', '回忆录', '奇幻', '婚姻', '学术', '小说', '强强', '心理', '心理学', '思维', '惊悚', '成长', '投资', '推理', '教材', '教育学', '文化', '文学', '日本', '明朝', '期刊/杂志', '治愈', '漫画', '爱情', '狗血', '知识', '研究', '社会学', '科幻', '科普', '经典', '经济', '经济学', '美国', '美国文学', '职场', '自传', '英国文学', '言情', '计算机', '诗歌', '诺贝尔文学奖', '进口书', '都市', '金融', '长篇小说', '限时特价', '随笔', '青春', '非虚构'])
                    else:
                        category_query |= Q(category__icontains=category)
                query &= category_query
            book_list = list(models.SpiderBook.objects.filter(query).values())  # 从用户设置的意向中选
            try:
                book_list = random.sample(book_list, 9)
            except ValueError:
                book_list = book_list[:]  # 或者其他适当的处理方式
                print(book_list)
        else:
            # 如果用户没有设置图书类型，则随机推荐
            book_list = list(models.SpiderBook.objects.all().values())  # 从全部的图书中选
            try:
                book_list = random.sample(book_list, 9)
            except ValueError:
                book_list = book_list[:]  # 或者其他适当的处理方式
    except models.UserList.DoesNotExist:
        # 如果用户不存在，则随机推荐
        book_list = list(models.SpiderBook.objects.all().values())  # 从全部的图书中选
        try:
            book_list = random.sample(book_list, 9)
        except ValueError:
            book_list = book_list[:]  # 或者其他适当的处理方式
    # print('from here')
    # print(book_list)
    return book_list


if __name__ == '__main__':
    # similarity(1, 2)
    recommend_by_item_id(1)
