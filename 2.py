import concurrent.futures
import requests
from lxml import etree
import re
import pymysql
from pymysql.cursors import DictCursor

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://category.dangdang.com/pg3-cp98.00.00.00.00.00.html',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def get_HTML(url, session):
    """使用 session 发起请求"""
    try:
        response = session.get(url, timeout=10)
        print(f"{url} 访问成功")
        return response
    except Exception as e:
        print(f"访问失败: {e}")
        return None



def region(response):
    response.encoding = 'utf-8'
    obj = etree.HTML(response.text)
    url_x = obj.xpath('//p[@class="name"]/a/@href')
    new_links = []
    for link in url_x:
        match = re.search(r'/(\d+)\.html$', link)
        if match:
            product_id = match.group(1)
            new_link = f'https://e.dangdang.com/products/{product_id}.html'
            new_links.append(new_link)
        else:
            print(f"警告：无法从 '{link}' 中提取ID，已跳过")
    return new_links

def xq(link, session):
    """爬取详情页，使用传入的 session"""
    try:
        response = session.get(link, timeout=10)
        print(f"{link} 访问成功，状态码: {response.status_code}")
        response.encoding = 'utf-8'
        obj = etree.HTML(response.text)

        # 书名
        title = obj.xpath('//span[@class="title_words"]/text()')
        title = title[0].strip() if title else ''

        # 价格（字符串如 "¥49.80"）
        price = obj.xpath('//span[@class="price_out"]/text()')
        price_str = price[0].strip() if price else ''
        # 提取数字部分，转为浮点数（单位：元）
        price_num = 0.0
        if price_str:
            match = re.search(r'[\d.]+', price_str)
            if match:
                price_num = float(match.group())

        # 阅读人数（如 "已有1542人阅读"）
        popularity = obj.xpath('//div[@class="count_per"]/text()')
        pop_str = popularity[0] if popularity else ''
        read_count = 0
        if pop_str:
            match = re.search(r'(\d+)', pop_str)
            if match:
                read_count = int(match.group(1))

        # 评论数（从整个页面中找 "xxx人评论"）
        comment_match = re.search(r'(\d+)人评论', response.text)
        comment_count = int(comment_match.group(1)) if comment_match else 0

        # 评分（从 count_per 下的第二个 em）
        score = obj.xpath('//div[@class="count_per"]/em[2]/text()')
        rating = 0.0
        if score:
            try:
                rating = float(score[0].strip())
            except ValueError:
                rating = 0.0

        # 作者
        author = obj.xpath('//p[@dd_name="作者"]/span/a/text()')
        author = author[0].strip() if author else ''

        # 出版社
        publisher = obj.xpath('//p[@dd_name="出版社"]/span/a/text()')
        publisher = publisher[0].strip() if publisher else ''

        # 出版时间（格式 YYYY-MM-DD）
        time_match = re.search(r'出版时间：(\d{4}-\d{2}-\d{2})', response.text)
        publish_date = time_match.group(1) if time_match else None

        # 字数（单位：万字，如 "12.3万"）
        count_match = re.search(r'数：([\d.]+)万', response.text)
        word_count = 0
        if count_match:
            try:
                word_count = int(float(count_match.group(1)) * 10000)
            except ValueError:
                word_count = 0

        # 分类
        category = obj.xpath('//*[@id="productBookDetail"]/div[3]/p[5]/span[1]/a/text()')
        category = category[0].strip() if category else ''

        book_data = {
            'book_name': title,
            'price': price_num,
            'read_count': read_count,
            'comment_count': comment_count,
            'rating': rating,
            'author': author,
            'publisher': publisher,
            'publish_date': publish_date,
            'word_count': word_count,
            'category': category
        }
        return book_data
    except Exception as e:
        print(f"解析详情页 {link} 时出错: {e}")
        return None

def save_to_mysql(book_data, conn):
    """将单条数据插入MySQL，若已存在则跳过"""
    if not book_data:
        return False
    try:
        with conn.cursor() as cursor:
            # 先查询是否已存在相同书名的记录（可根据需要调整条件）
            select_sql = "SELECT id FROM spider_book WHERE book_name = %s"
            cursor.execute(select_sql, (book_data['book_name'],))
            result = cursor.fetchone()
            if result:
                print(f"书籍已存在，跳过插入: {book_data['book_name']}")
                return False

            # 不存在则插入
            insert_sql = """
                INSERT INTO spider_book 
                (book_name, price, read_count, comment_count, rating, author, publisher, publish_date, word_count, category)
                VALUES (%(book_name)s, %(price)s, %(read_count)s, %(comment_count)s, %(rating)s, %(author)s, %(publisher)s, %(publish_date)s, %(word_count)s, %(category)s)
            """
            cursor.execute(insert_sql, book_data)
        conn.commit()
        print(f"成功插入书籍: {book_data['book_name']}")
        return True
    except Exception as e:
        print(f"插入数据失败: {e}")
        conn.rollback()
        return False

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'book_gl',
        'charset': 'utf8mb4',
        'cursorclass': DictCursor
    }
    conn = None
    try:
        conn = pymysql.connect(**db_config)
        print("数据库连接成功")

        # 创建会话，复用连接
        session = requests.Session()
        session.headers.update(headers)

        for page in range(101):
            url = f'https://category.dangdang.com/pg{page}-cp98.00.00.00.00.00.html'
            response = get_HTML(url, session)
            if not response:
                continue

            new_links = region(response)
            # 使用线程池并发爬取详情页，最大并发数 5
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # 提交所有任务，限制每次最多爬前10本（可按需调整）
                future_to_link = {
                    executor.submit(xq, link, session): link
                    for link in new_links
                }
                for future in concurrent.futures.as_completed(future_to_link):
                    link = future_to_link[future]
                    try:
                        book_data = future.result()
                        if book_data:
                            save_to_mysql(book_data, conn)
                        else:
                            print(f"跳过 {link}")
                    except Exception as e:
                        print(f"处理 {link} 时出错: {e}")

    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        if conn:
            conn.close()
            print("数据库连接已关闭")

if __name__ == '__main__':
    main()