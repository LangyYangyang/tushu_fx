import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='recommend_job'
)

# 创建游标
cursor = conn.cursor()

# 检查spider_book表数据量
try:
    cursor.execute('SELECT COUNT(*) FROM spider_book')
    spider_book_count = cursor.fetchone()[0]
    print('spider_book表数据量:', spider_book_count)
except Exception as e:
    print('spider_book表不存在或查询失败:', e)

# 检查book_data表数据量
try:
    cursor.execute('SELECT COUNT(*) FROM book_data')
    book_data_count = cursor.fetchone()[0]
    print('book_data表数据量:', book_data_count)
except Exception as e:
    print('book_data表不存在或查询失败:', e)

# 关闭连接
cursor.close()
conn.close()
