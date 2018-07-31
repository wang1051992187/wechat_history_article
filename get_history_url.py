from article_detail import *
from RedisQueue import RedisQueue
from pypinyin import pinyin, lazy_pinyin, Style

begin_url = '''
https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MjM5MzU4NDkzOA==&f=json&offset={}&count=10&is_ok=1&scene=124&uin=MTMzMDE2MDc0NA%3D%3D&key=1d3570e9b8c45238b8a0db7cf4c40e4f105b365727bd0ddf56a2cb43aa4513c77f9f39dfe9a1244ce41bc9cd3619aa33c477af77276e55e0ba8d07aa64020fba92ee242f1a58e56740c5c669893938fc&pass_ticket=qf07TCU8fHwcY0KEmh14RExqCSginGN%2BfzUIgMYpfoZ9GyEsHlch5bSOaK8hptp2&wxtoken=&appmsg_token=967_z86Ewlm2ub6hzQuCiP8MfKC_GzehTglYPZDJfQ~~&x5=0&f=json%0A
'''


def get_all_url(url, nickname):
    nickname_pinyin = lazy_pinyin(nickname)
    nickname_pinyin = "".join(nickname_pinyin)
    if nickname is None:
        print("空")
        return
    q = RedisQueue('wechat_url_'+ nickname_pinyin)
    json_str = get_page_detail(url)
    json_re = parse_page_index(json_str)
    general_msg_list = parse_page_index(json_re['general_msg_list'])
    print(len(general_msg_list['list']))
    for list_re in general_msg_list['list']:
        # print(list_re['app_msg_ext_info'])
        datetime = list_re['comm_msg_info']['datetime']
        try:
            title = list_re['app_msg_ext_info']['title']
            digest = list_re['app_msg_ext_info']['digest']
            content_url = list_re['app_msg_ext_info']['content_url']
            print(url)
            # content = get_content(content_url)
            data1 = {
                'nickname': nickname,
                'title': title,
                'digest': digest,
                'datetime': datetime,
                'content_url': content_url,
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
                # content = get_content(content_url)
                data2 = {
                    'nickname': nickname,
                    'title': title,
                    'digest': digest,
                    'datetime': datetime,
                    'content_url': content_url,
                    # 'content': content
                }
                data2 = json.dumps(data2)
                q.put(data2)
                print(data2)
        except KeyError as e:
            print("error",e)

    # 获取 next_offset
    if len(general_msg_list['list']) < 10:
        return None
    return json_re['next_offset']


def url_circulate(next_offset):
    nickname = " 南京银行无锡分行"
    next_url = begin_url.format(next_offset)
    print(next_url)
    next_offset = get_all_url(next_url,nickname)
    time.sleep(3)
    if next_offset is not None:
        url_circulate(next_offset)


if __name__ == '__main__':
    url_circulate(0)
