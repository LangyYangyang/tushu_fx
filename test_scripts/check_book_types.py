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

# 检查数据库中的图书类型
try:
    cursor.execute('SELECT DISTINCT category FROM book_data')
    categories = cursor.fetchall()
    print('数据库中的图书类型:')
    for category in categories:
        print(f'  - {category[0]}')
except Exception as e:
    print('查询图书类型失败:', e)

# 检查每种类型的图书数量
try:
    cursor.execute('SELECT category, COUNT(*) as count FROM book_data GROUP BY category')
    category_counts = cursor.fetchall()
    print('\n每种类型的图书数量:')
    for category, count in category_counts:
        print(f'  - {category}: {count}本')
except Exception as e:
    print('查询图书数量失败:', e)

# 检查用户设置的图书类型
try:
    cursor.execute('SELECT key_word, category FROM user_expect')
    user_expects = cursor.fetchall()
    print('\n用户设置的图书类型:')
    for key_word, category in user_expects:
        print(f'  - key_word: {key_word}, category: {category}')
except Exception as e:
    print('查询用户设置失败:', e)

# 关闭连接
cursor.close()
conn.close()
