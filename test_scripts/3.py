import json
import re
from pymysql.cursors import DictCursor
import pymysql
import requests
from lxml import etree


def lieSpider(key_word, all_page):
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'recommend_job',
        'charset': 'utf8mb4',
        'cursorclass': DictCursor
    }
    conn = pymysql.connect(**db_config)
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

    try:
        for page_num in range(1, int(all_page) + 1):
            url = f'https://e.dangdang.com/media/api.go?action=searchMedia&enable_f=1&promotionType=1&keyword={key_word}&deviceSerialNo=html5&macAddr=html5&channelType=html5&permanentId=20250519165519291328838381674184745&returnType=json&channelId=70000&clientVersionNo=6.8.0&platformSource=DDDS-P&fromPlatform=106&deviceType=pconline&token=&stype=media&mediaTypes=1,2&start={10 * page_num - 10}&end={page_num * 10}'
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, headers=headers, timeout=10)
            data_dict = json.loads(response.text)
            print(f"正在爬取第{page_num}页: {url}")
            print(data_dict)

            # 检查是否有数据
            if 'data' not in data_dict or 'searchMediaPaperList' not in data_dict['data']:
                print(f"第{page_num}页没有数据")
                continue

            book_list = data_dict['data']['searchMediaPaperList']
            if not book_list:
                print(f"第{page_num}页图书列表为空")
                continue

            for book_item in book_list:
                try:
                    book_id = book_item['saleId']

                    # 书名
                    title = book_item['title']
                    title = title.strip() if title else ''

                    # 价格
                    price_num = float(book_item['lowestPrice']) if book_item.get('lowestPrice') else 0.0

                    # 作者
                    author = book_item.get('author', '')
                    author = author.strip() if author else ''

                    # 出版社
                    publisher = book_item.get('publisher', '')
                    publisher = publisher.strip() if publisher else ''

                    url_l = f'https://e.dangdang.com/products/{book_id}.html'
                    print(f"正在获取详情: {url_l}")

                    response1 = requests.get(url=url_l, headers=headers, timeout=10)
                    obj = etree.HTML(response1.text)

                    # 阅读人数
                    popularity = obj.xpath('//div[@class="count_per"]/text()')
                    pop_str = popularity[0] if popularity else ''
                    read_count = 0
                    if pop_str:
                        match = re.search(r'(\d+)', pop_str)
                        if match:
                            read_count = int(match.group(1))
                            if '万' in pop_str:
                                read_count = read_count * 10000

                    # 评论数
                    comment_match = re.search(r'(\d+)人评论', response1.text)
                    comment_count = int(comment_match.group(1)) if comment_match else 0

                    # 评分
                    score = obj.xpath('//div[@class="count_per"]/em[2]/text()')
                    rating = 0.0
                    if score:
                        try:
                            rating = float(score[0].strip())
                        except ValueError:
                            rating = 0.0

                    # 出版时间（格式 YYYY-MM-DD）
                    publish_date = re.findall(r'<p>出版时间：(\d{4}-\d{2}-\d{2})</p>', response1.text)
                    publish_date = publish_date[0].strip() if publish_date else ''

                    # 字数（单位：万字，如 "12.3万"）
                    count_match = re.search(r'数：([\d.]+)万', response1.text)
                    word_count = 0
                    if count_match:
                        try:
                            word_count = int(float(count_match.group(1)) * 10000)
                        except ValueError:
                            word_count = 0

                    # 类型
                    category = obj.xpath('//*[@id="productBookDetail"]/div[3]/p[5]/span[1]/a/text()')
                    category = category[0].strip() if category else ''

                    print(f"处理图书: {title}, 阅读人数: {read_count}")

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
                    print(book_data)

                    if not book_data['book_name']:
                        print("图书名称为空，跳过")
                        continue

                    with conn.cursor() as cursor:
                        # 先查询是否已存在相同书名的记录
                        select_sql = "SELECT id FROM book_data WHERE book_name = %s"
                        cursor.execute(select_sql, (book_data['book_name'],))
                        result = cursor.fetchone()
                        if result:
                            print(f"书籍已存在，跳过插入: {book_data['book_name']}")
                            continue

                        # 不存在则插入
                        insert_sql = """
                               INSERT INTO book_data 
                               (book_name, price, read_count, comment_count, rating, author, publisher, publish_date, word_count, category)
                               VALUES (%(book_name)s, %(price)s, %(read_count)s, %(comment_count)s, %(rating)s, %(author)s, %(publisher)s, %(publish_date)s, %(word_count)s, %(category)s)
                           """
                        cursor.execute(insert_sql, book_data)
                    conn.commit()
                    print(f"成功插入书籍: {book_data['book_name']}")

                except Exception as e:
                    print(f"处理单本图书时出错: {e}")
                    continue

        print("爬虫执行完成")
        return 0  # 返回0表示成功

    except Exception as e:
        print(f"爬虫执行出错: {e}")
        conn.rollback()
        return 1  # 返回1表示失败
    finally:
        conn.close()


if __name__ == '__main__':
    lieSpider('凡人', 1)
