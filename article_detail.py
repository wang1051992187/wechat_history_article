"""
    文章详细内容
"""
from bs4 import BeautifulSoup
from common import *
from RedisQueue import RedisQueue
from multiprocessing import Pool

q = RedisQueue('MzI0OTM1NzA4NA==')


def get_content(url):
    print(url)
    html = get_page_detail_get(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select('#js_content')[0].get_text().strip()
        content = content.replace("\xa0", "").replace("\u3000", "").replace("&quot;", "")
        name = soup.select('#js_name')[0].get_text().strip()
        return name, content, html
    else:
        return None


def get_article_info():
    return q.get()


def get_article_detail(i):
    """
    可多进程从Redis队列中获取到文章URL，从而得到具体文章数据
    :param i:
    :return:
    """
    print("当前为第{}个进程".format(i))
    while True:
        article = get_article_info()
        if article is None or article == "":
            break
        try:
            article_info = parse_page_index(article)
            print(article_info)
            url = article_info['content_url']
            if url == '':
                continue
            name, content, html = get_content(url)
            if content is not None:
                data = {
                    'nickname': name,
                    'title': article_info['title'],
                    'digest': article_info['digest'],
                    'content_url': article_info['content_url'],
                    'datetime': article_info['datetime'],
                    'content': content,
                    'html': html
                }
                save_to_mongodb(data, name.strip())
            else:
                q.put(article)
        except Exception as e:
            print(e)
            q.put(article)


if __name__ == '__main__':
    # 设置进程数量
    pool_num = 10
    pool = Pool(pool_num)
    for i in range(pool_num):
        pool.apply_async(get_article_detail, (i,))
        time.sleep(1)

    pool.close()  # 关闭进程池
    pool.join()   # 主进程在这里等待，只有子进程全部结束之后，在会开启主线程



