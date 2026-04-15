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

# 删除现有的外键约束
try:
    cursor.execute('ALTER TABLE send_list DROP FOREIGN KEY send_list_book_id_a9779146_fk_spider_book_id')
    print('删除现有外键约束成功')
except Exception as e:
    print('删除现有外键约束失败:', e)

# 修改book_id字段的引用
try:
    cursor.execute('ALTER TABLE send_list ADD CONSTRAINT send_list_book_id_a9779146_fk_book_data_id FOREIGN KEY (book_id) REFERENCES book_data (id)')
    print('创建新外键约束成功')
except Exception as e:
    print('创建新外键约束失败:', e)

# 关闭连接
cursor.close()
conn.close()
