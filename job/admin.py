from django.contrib import admin

from job.models import SpiderBook, UserList

# 后台里面的认证和授权 可以隐藏掉
from django.contrib import admin
from django.contrib.auth.models import User, Group

# 取消注册 User 和 Group 模型
admin.site.unregister(User)
admin.site.unregister(Group)

# 设置管理后台的头部标题
admin.site.site_header = '图书后台管理'
# 设置管理后台在浏览器标签页中显示的标题
admin.site.site_title = '图书后台管理'
# 设置管理后台主页的标题
admin.site.index_title = '图书后台管理'





class UserListAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'pass_word')  # 列表中显示的字段
    search_fields = ('user_id', 'user_name')  # 可搜索的字段
    # 设置默认的排序方式，这里按照 id 字段进行排序
    ordering = ['user_id']
    # 允许编辑所有字段，包括主键
    fields = ('user_id', 'user_name', 'pass_word')

admin.site.register(UserList, UserListAdmin)


# Register your models here.
class SpiderBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_name', 'price', 'read_count', 'comment_count', 'rating', 'author', 'publisher', 'publish_date', 'word_count', 'category')
    search_fields = ('book_name', 'author', 'publisher', 'category')
    list_filter = ('category', 'publisher')
    # 设置默认的排序方式，这里按照 id 字段进行排序
    ordering = ['id']
    # 允许编辑所有字段
    fields = ('book_name', 'price', 'read_count', 'comment_count', 'rating', 'author', 'publisher', 'publish_date', 'word_count', 'category')
    # 点击哪些字段可以进入编辑页面
    list_display_links = ('id', 'book_name')
    # 每页显示的数量
    list_per_page = 50


admin.site.register(SpiderBook, SpiderBookAdmin)
