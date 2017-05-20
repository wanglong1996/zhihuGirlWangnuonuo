#coding:utf8

import json
import time

import pymongo
import requests
from requests.exceptions import RequestException

from zhihuGirlWangnuonuo.config import *

client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB]


#将cookies转换为字典形式
raw_cookies = 'q_c1=96d602e1204b40d49abb907f108f2dee|1494986921000|1494986921000; r_cap_id="MGRhZGFkYzRhZjBlNDk4ZmI2MGQ4OTA4YTQ2ODg5ZDI=|1495246016|4621ebaf75b1a883ba30e6e2d4e0e6a346cb1f8a"; cap_id="NmNkMTI1MTRmNmMwNDVjYmIwYTE2YmZmZTQ5N2EzZTc=|1495246016|066585db2766be279580820f85b177ec71a6d984"; __utma=155987696.65231980.1495268443.1495268443.1495268443.1; __utmz=155987696.1495268443.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); d_c0="ACDCuJD6yAuPTkUzswiWNJgX4-udGcLNYCg=|1495246018"; _zap=7c54351a-a90b-4841-9d43-f127a75848a2; capsion_ticket="2|1:0|10:1495274733|14:capsion_ticket|44:NTdhYTVhZTJiMzBiNDZmZWJlMjYzNDFiMTE0NTU1OWU=|57d607246c1ab2854f35c6cf2a25701d4437e274c51da0c9242215f9bb10878d"; _xsrf=a3795d11294418f45ae06f5b70d5de89; aliyungf_tc=AQAAAAF0jRm7PAsA3EtQMU8jvgVodNRE; acw_tc=AQAAAB5VWQE1kQ0A3EtQMYjg9TJCOTn/; __utmc=155987696; z_c0="2|1:0|10:1495274752|4:z_c0|92:Mi4wQUFDQVVGRWJBQUFBSU1LNGtQcklDeVlBQUFCZ0FsVk5BS0pIV1FDVzlqczZPWHNLYXB4RkQ2MGdzLVRJdnBleFNB|c2f96a474b66b33b13c546626f523bd013dc519a0a0a0ecb72689de37b2f4929"'
cookies = {}
for line in raw_cookies.split(';'):
    key,value = line.split('=',1)
    cookies[key]=value
header = {
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Lannguage': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',

}


def get_page_index(offset):

    url = 'https://www.zhihu.com/api/v4/members/{}/answers?include=data[*].is_normal,is_collapsed,collapse_reason,suggest_edit,comment_count,can_comment,content,voteup_count,reshipment_settings,comment_permission,mark_infos,created_time,updated_time,relationship.is_authorized,voting,is_author,is_thanked,is_nothelp,upvoted_followees;data[*].author.badge[?(type=best_answerer)].topics&offset={}&limit=20&sort_by=created'
    url = url.format(zhihuID,str(offset))
    #如果不模拟登录，会出现访问错误
    try:
        response = requests.get(url,cookies=cookies,headers=header)
        response.encoding ='utf-8'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错！')
        return None
def parse_page(html):
    data = json.loads(html)
    for item in data['data']:
        content = item['content']
        title = item['question']['title']
        updated_time = item['question']['updated_time']
        updated_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updated_time))
        voteup = item['voteup_count']
        create_time =item['created_time']
        create_time = e=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time))
        result = {
            'create_time':create_time,
            'updated_time':updated_time,
            'title':title,
            'content':content,
            'voteup_count': voteup,

        }
        save_to_mongo(result)

def save_to_mongo(result):
    i = 0
    if db[MONGODB_TABLE].insert(result):
        print('save {}to db OK'.format(str(i)))
        i += 1

    else:
        print('save to db error')


def main():
    groups = [x*20 for x in range(0,answer_page_number)]
    for i in groups:
        parse_page(get_page_index(i))




if __name__ == "__main__":
    main()