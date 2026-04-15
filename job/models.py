from django.db import models

class SpiderBook(models.Model):
    id = models.AutoField(primary_key=True)
    book_name = models.CharField('图书名字', max_length=255, blank=False, null=False)
    price = models.DecimalField('图书价格', max_digits=10, decimal_places=2, blank=True, null=True)
    read_count = models.IntegerField('阅读人数', default=0, blank=True, null=True)
    comment_count = models.IntegerField('评论数', default=0, blank=True, null=True)
    rating = models.DecimalField('评分', max_digits=3, decimal_places=2, blank=True, null=True)
    author = models.CharField('作者', max_length=255, blank=False, null=False)
    publisher = models.CharField('图书出版社', max_length=255, blank=True, null=True)
    publish_date = models.DateField('出版时间', blank=True, null=True)
    word_count = models.IntegerField('总字数（单位：万字）', blank=True, null=True)
    category = models.CharField('类型', max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'book_data'
        verbose_name = "图书信息"
        verbose_name_plural = "图书信息"

class SendList(models.Model):
    send_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(SpiderBook, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UserList', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'send_list'

class SpiderInfo(models.Model):
    spider_id = models.AutoField(primary_key=True)
    spider_name = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'spider_info'

class UserExpect(models.Model):
    expect_id = models.AutoField(primary_key=True)
    key_word = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('UserList', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_expect'

class UserList(models.Model):
    user_id = models.CharField('用户ID', primary_key=True, max_length=11)  # 用户ID，主键
    user_name = models.CharField('用户名', max_length=255, blank=True, null=True)  # 用户名
    pass_word = models.CharField('密码', max_length=255, blank=True, null=True)  # 密码

    class Meta:
        managed = True  # 是否由Django管理
        db_table = 'user_list'  # 数据库表名
        verbose_name = "前台用户"
        verbose_name_plural = "前台用户"