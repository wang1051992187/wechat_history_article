"""
    文章详细内容
"""
from bs4 import BeautifulSoup
from common import *
from RedisQueue import RedisQueue
from pypinyin import pinyin, lazy_pinyin, Style
from multiprocessing import Pool

q = RedisQueue('wechat_url')


def get_content(url):
    print(url)
    html = get_page_detail_get(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select('#js_content')[0].get_text().strip()
        content = content.replace("\xa0", "").replace("\u3000", "").replace("&quot;", "")
        return content, html
    else:
        return None


def get_article_info():
    return q.get()


def get_article_detail(i):
    print("当前为第{}个进程".format(i))
    while True:
        article = get_article_info()
        if article is None or article == "":
            break
        if q.qsize() < 2:
            quit()
        try:
            article_info = parse_page_index(article)
            print(article_info)
            url = article_info['content_url']
            if url == '':
                continue
            content, html = get_content(url)
            if content is not None:
                data = {
                    'nickname': article_info['nickname'].strip(),
                    'title': article_info['title'],
                    'digest': article_info['digest'],
                    'content_url': article_info['content_url'],
                    'datetime': article_info['datetime'],
                    'content': content,
                    'html': html
                }
                # 存储为名字的拼音
                nickname_pinyin = lazy_pinyin(article_info['nickname'].strip())
                nickname_pinyin = "".join(nickname_pinyin)
                save_to_mongodb(data, nickname_pinyin.strip())
            else:
                q.put(article)
        except Exception as e:
            print(e)
            q.put(article)


if __name__ == '__main__':
    pool = Pool(40)
    for i in range(40):
        pool.apply_async(get_article_detail, (i,))
        time.sleep(1)

    pool.close()  # 关闭进程池
    pool.join()   # 主进程在这里等待，只有子进程全部结束之后，在会开启主线程



