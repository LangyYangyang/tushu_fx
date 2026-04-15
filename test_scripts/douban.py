import concurrent.futures
import json
import random
import time

import requests
from lxml import etree
import re
import pymysql
from pymysql.cursors import DictCursor

headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://read.douban.com',
    'priority': 'u=1, i',
    'referer': 'https://read.douban.com/category/1?sort=hot&page=6',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-csrf-token': '.eJwFwQEBwCAIBMAuJhiCvMSBH_SP4N0aILMb-CvcRU-ZBY_33qNtUQwplvAihm4GxQXly4ERuR5laBIW.aabJzQ.7eEDo13KclXNLWWPwglweGGq4HE',
    'x-requested-with': 'XMLHttpRequest',
}

def get_HTML(url, session,json_data,page):
    """使用 session 发起请求"""
    try:
        # print(url,json_data)
        response = session.post(url=url,json=json_data ,timeout=10)
        time.sleep(random.uniform(2, 5))
        print(f"{url} 访问成功")
        # print('**',response.text)
        data_dict = json.loads(response.text)
        return data_dict
    except Exception as e:
        print(f"访问失败: {e}::{page}")
        return None



def region(data_dict):
    url_xq = []
    for item in data_dict['list']:
        if 'url' in item:
            url = f'https://read.douban.com{item["url"]}?dcs=category'


            url_xq.append(url)
    print(url_xq)
    return url_xq
def xq(link, session):
    """爬取详情页，使用传入的 session"""
    try:
        response = session.get(link, timeout=10)
        time.sleep(random.uniform(1, 2))
        print(f"{link} 访问成功，状态码: {response.status_code}")

        obj = etree.HTML(response.text)

        # 书名
        title = obj.xpath('//h1[@class="article-title"]/text()')[0]
        title = title.strip() if title else ''

        # 价格
        price=obj.xpath('//span[contains(@class,"current-price-count")]/text()')
        price_str = price[0].strip() if price else ''
        # 提取数字部分，转为浮点数（单位：元）
        price_num = 0.0
        if price_str:
            match = re.search(r'[\d.]+', price_str)
            if match:
                price_num = float(match.group())

        # 阅读人数
        read_count = 0

        # 评论数
        comment_match = obj.xpath('//span[@class="amount"]/a/text()')
        comment_count = int(re.findall(r'\d+', comment_match[0])[0]) if comment_match else 0

        # 评分
        score = obj.xpath('//span[@class="score"]/text()')
        rating = 0.0
        if score:
            try:
                rating = float(score[0].strip())
            except ValueError:
                rating =0.0

        # 作者
        author = obj.xpath('//span[@class="labeled-text"]/a[@class="author-item"]/text()')
        author = author[0].strip() if author else ''

        # 出版社
        publisher = re.findall(r'<span class="label">出版社</span><span class="labeled-text"><span>(.*?)</span>',response.text)
        if publisher == []:
            publisher = obj.xpath('//span[@class="labeled-text"]/a/text()')
            publisher = publisher[1].strip() if publisher else ''
        else:
            publisher = publisher[0].strip() if publisher else ''

        # 出版时间（格式 YYYY-MM-DD）
        time_match = re.search(r'<span>(\d{4}-\d{2})</span></span></p><p class=""><span class="label">', response.text)
        publish_date = time_match.group(1) + '-01' if time_match else None

        # 字数（单位：万字，如 "12.3万"）
        count_match = re.findall(r'<span class="labeled-text">约 (\d+,\d+) 字</span>', response.text)[0]
        word_count = 0
        if count_match:
            try:
                word_count = int(count_match.replace(',', ''))
            except ValueError:
                word_count = 0

        category = obj.xpath('//ul[@class="tags"]/li[1]/a/span[1]/text()')
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
            select_sql = "SELECT id FROM book_data WHERE book_name = %s"
            cursor.execute(select_sql, (book_data['book_name'],))
            result = cursor.fetchone()
            if result:
                print(f"书籍已存在，跳过插入: {book_data['book_name']}")
                return False

            # 不存在则插入
            insert_sql = """
                INSERT INTO book_data 
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
        'database': 'recommend_job',
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

        for page in range(10,200):
            json_data = {
                'sort': 'hot',
                'page': page,
                'kind': 1,
                'query': '\n    query getFilterWorksList($works_ids: [ID!]) {\n      worksList(worksIds: $works_ids) {\n        \n    id\n    isOrigin\n    isEssay\n    isAudio\n    \n    title\n    cover(useSmall: false)\n    url\n    isBundle\n    coverLabel(preferVip: true)\n  \n    \n  url\n  title\n\n    \n  author {\n    name\n    url\n  }\n  origAuthor {\n    name\n    url\n  }\n  translator {\n    name\n    url\n  }\n\n    \n  ... on AudioWorks {\n    narrators\n    sourceAuthors\n  }\n\n    \n  abstract\n  authorHighlight\n  editorHighlight\n\n    \n    isOrigin\n    kinds {\n      \n    name @skip(if: true)\n    shortName @include(if: true)\n    id\n  \n    }\n    ... on WorksBase @include(if: true) {\n      wordCount\n      wordCountUnit\n    }\n    ... on WorksBase @include(if: false) {\n      inLibraryCount\n    }\n    ... on WorksBase @include(if: false) {\n      \n    isEssay\n    \n    ... on EssayWorks {\n      favorCount\n    }\n  \n    \n    \n    averageRating\n    ratingCount\n    url\n    isColumn\n    isFinished\n  \n  \n  \n    }\n    ... on EbookWorks @include(if: false) {\n      \n    ... on EbookWorks {\n      book {\n        url\n        averageRating\n        ratingCount\n      }\n    }\n  \n    }\n    ... on WorksBase @include(if: false) {\n      isColumn\n      isEssay\n      onSaleTime\n      ... on ColumnWorks {\n        updateTime\n      }\n    }\n    ... on WorksBase @include(if: true) {\n      isColumn\n      ... on ColumnWorks {\n        isFinished\n        finalizedCn\n      }\n    }\n    ... on EssayWorks {\n      essayActivityData {\n        \n    title\n    uri\n    tag {\n      name\n      color\n      background\n      icon2x\n      icon3x\n      iconSize {\n        height\n      }\n      iconPosition {\n        x y\n      }\n    }\n  \n      }\n    }\n    highlightTags {\n      name\n    }\n    ... on WorksBase @include(if: false) {\n      fanfiction {\n        tags {\n          id\n          name\n          url\n        }\n      }\n    }\n  \n    \n  ... on WorksBase {\n    copyrightInfo {\n      newlyAdapted\n      newlyPublished\n      adaptedName\n      publishedName\n    }\n  }\n\n    isInLibrary\n    ... on WorksBase @include(if: false) {\n      \n    fixedPrice\n    salesPrice\n    realPrice {\n      price\n      priceType\n    }\n  \n      \n    isOrigin\n    ... on ColumnWorks {\n      isAutoPricing\n    }\n  \n    }\n    ... on EbookWorks {\n      \n    fixedPrice\n    salesPrice\n    realPrice {\n      price\n      priceType\n    }\n  \n    }\n    ... on AudioWorks {\n      \n    fixedPrice\n    salesPrice\n    realPrice {\n      price\n      priceType\n    }\n  \n    }\n    ... on WorksBase @include(if: true) {\n      ... on EbookWorks {\n        id\n        isPurchased\n        isInWishlist\n      }\n    }\n    ... on WorksBase @include(if: false) {\n      fanfiction {\n        fandoms {\n          title\n          url\n        }\n      }\n    }\n    ... on WorksBase @include(if: false) {\n      fanfiction {\n        kudoCount\n      }\n    }\n  \n      }\n    }\n  ',
                'variables': {},
            }
            url = 'https://read.douban.com/j/kind/'
            response = get_HTML(url, session,json_data,page)
            if not response:
                continue

            new_links = region(response)
            # 使用线程池并发爬取详情页，最大并发数 5
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
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