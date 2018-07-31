import multiprocessing
import time
import pymysql
import datetime
# 当天数据备份在30天数据库

import pymongo
class copy_middle_db(object):
    def start_MySQL(self):
        conn = pymysql.connect(
            host='192.168.1.108',
            port=3306,
            user='Andlinks',
            passwd='Andlinks2017',
            db='bank_spider',
            charset='utf8')

        cur = conn.cursor()
        myConn_list = [conn, cur]
        return myConn_list

    def close_MySQL(self, cur, conn):
        cur.close()
        conn.close()

    # 讨论内容拷贝
    def copy_taolun(self):
        client = pymongo.MongoClient('192.168.1.108', connect=False)
        db = client['wechat_2']

        myConn_list = self.start_MySQL()
        cur = myConn_list[1]
        conn = myConn_list[0]

        for table in db.collection_names():
            if table != 'system.indexes':
                print('table name is ', table)
                collection = db[table]
                cursor = collection.find(no_cursor_timeout=True)
                for item in cursor:
                    sql = "INSERT INTO wechat_article(nickname,title,digest,datetime,content_url,content) VALUES ('{}', '{}', '{}', '{}', '{}','{}')".format(item['nickname'], item['title'], item['digest'], item['datetime'], item['content_url'], item['content'])
                    print(sql)
                    try:
                        cur.execute(sql)
                        conn.commit()
                    except Exception as e:
                        print(e)
                cursor.close()

        self.close_MySQL(cur, conn)


if __name__ == '__main__':
    c = copy_middle_db()
    c.copy_taolun()










