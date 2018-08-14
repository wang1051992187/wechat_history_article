from RedisQueue import RedisQueue
from common import *
from pypinyin import pinyin, lazy_pinyin, Style
import re

begin_url = '''
https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzI0OTM1NzA4NA==&f=json&offset=100&count=10&is_ok=1&scene=124&uin=MTMzMDE2MDc0NA%3D%3D&key=1d3570e9b8c452382d517f3e2889bc1f29b398b9da29306ab893f2e0882ce5e3cdd5a656005759b8999e2687643e12d64662895f5d7afb9a99c3e1e8ceac7493505451f0421ae81ddc99e55f888b68b2&pass_ticket=R2a9ORnMqp%2FOkNppjTPEUO9LrQPkvhp1%2BAeOLtKQfI4%2FJGzEA9GrP0DganZUFeGq&wxtoken=&appmsg_token=967_%252FjNoCH%252FQtbeHjm7aS5IwKH_dXkPlKeI3BwcrYg~~&x5=0&f=json
'''

# 替换 url中的offset
begin_url = re.sub(r'offset=.*?&', 'offset={}&', begin_url)
print(begin_url)
# 以URL中的biz做当前公众号唯一标识
biz = re.findall(r'biz=(.*?)&', begin_url)[0]


def get_all_url(url, biz):
    """
    根据URL解析JSON,得到文章信息保存到Redis队列中
    :param url:
    :param biz:
    :return:
    """
    if biz is None:
        print("空")
        return
    q = RedisQueue(biz.strip())
    json_str = get_page_detail(url)
    json_re = parse_page_index(json_str)
    general_msg_list = parse_page_index(json_re['general_msg_list'])
    for list_re in general_msg_list['list']:
        print("当前biz为", biz)
        datetime = list_re['comm_msg_info']['datetime']
        try:
            title = list_re['app_msg_ext_info']['title']
            digest = list_re['app_msg_ext_info']['digest']
            content_url = list_re['app_msg_ext_info']['content_url']
            author = list_re['app_msg_ext_info']['author']
            print(url)
            # content = get_content(content_url)
            data1 = {
                'title': title,
                'digest': digest,
                'datetime': datetime,
                'content_url': content_url,
                'author': author
                # 'content': content
            }
            data1 = json.dumps(data1)
            q.put(data1)
            print(data1)

            for multi_app_msg_item_list in list_re['app_msg_ext_info']['multi_app_msg_item_list']:
                title = multi_app_msg_item_list['title']
                digest = multi_app_msg_item_list['digest']
                content_url = multi_app_msg_item_list['content_url']
                print(content_url)

                author = multi_app_msg_item_list['author']
                data2 = {
                    'title': title,
                    'digest': digest,
                    'datetime': datetime,
                    'content_url': content_url,
                    'author': author
                    # 'content': content
                }
                data2 = json.dumps(data2)
                q.put(data2)
                print(data2)
        except KeyError as e:
            print("error", e)

    # 获取 next_offset
    if len(general_msg_list['list']) < 10:
        return None
    return json_re['next_offset']


def url_circulate(next_offset):
    """
    递归爬取所有的JSON的URL
    :param next_offset:
    :return:
    """
    next_url = begin_url.format(next_offset)
    print(next_url)
    next_offset = get_all_url(next_url, biz)
    time.sleep(3)
    if next_offset is not None:
        url_circulate(next_offset)


if __name__ == '__main__':
    url_circulate(0)
