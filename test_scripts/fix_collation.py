import pymysql

# 连接到MySQL数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='recommend_job',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # 检查数据库排序规则
        cursor.execute("SELECT @@character_set_database, @@collation_database;")
        db_charset = cursor.fetchone()
        print(f"Database charset: {db_charset['@@character_set_database']}")
        print(f"Database collation: {db_charset['@@collation_database']}")
        
        # 禁用外键约束
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        print("\nDisabled foreign key checks")
        
        # 检查spider_book表的排序规则
        cursor.execute("SHOW TABLE STATUS LIKE 'spider_book';")
        table_status = cursor.fetchone()
        if table_status:
            print(f"\nspider_book table collation: {table_status['Collation']}")
        
        # 修改spider_book表的排序规则为utf8mb4_general_ci
        cursor.execute("ALTER TABLE spider_book CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        print("Modified spider_book table collation to utf8mb4_general_ci")
        
        # 检查其他相关表的排序规则
        tables = ['send_list', 'user_expect', 'user_list', 'spider_info']
        for table in tables:
            cursor.execute(f"SHOW TABLE STATUS LIKE '{table}';")
            table_status = cursor.fetchone()
            if table_status:
                print(f"\n{table} table collation: {table_status['Collation']}")
                # 修改表的排序规则
                try:
                    cursor.execute(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
                    print(f"Modified {table} table collation to utf8mb4_general_ci")
                except Exception as e:
                    print(f"Error modifying {table} table: {e}")
                    # 如果修改失败，尝试只修改表的默认排序规则
                    cursor.execute(f"ALTER TABLE {table} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
                    print(f"Modified {table} table default collation to utf8mb4_general_ci")
        
        # 重新启用外键约束
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("\nEnabled foreign key checks")
        
    conn.commit()
    print("\nAll tables have been updated successfully!")
finally:
    conn.close()
