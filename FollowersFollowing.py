# _*_ coding:utf-8 _*_
import requests
import sys
import time
import re
import datetime
from bs4 import BeautifulSoup

from logger import Logger
from mongodb import Mongo,Mongo_1,Mongo_2
from proxy_pool import get_IP
from extractor import extract_followers_following, extract_last_followers

reload(sys)
sys.setdefaultencoding('utf8')

class FollowersFollowing:

    def __init__(self, fileNum):
        self.user_id = None
        self.user_url = 'https://www.zhihu.com/people/' + str(self.user_id) +'/following'
        self.topic_url = self.user_url + '/topics'
        self.is_del = False
        # self.proxy = None
        self.userID_list = []
        self.fileNum = fileNum
        self.file = None
        self.start = None
        self.end = None
        self.type = None
        self.state = False
        self.following_type = None
        self.following_id_list = []
        self.user_id_list = None

        self.mongo = Mongo_2()
        self.mongo1 = Mongo()

        self.current_proxy = None
        self.content = None
        self.headers = {
            'Accept': 'textml,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Referer': 'http://www.zhihu.com/',
            'Cookie': None,
            'x-udid':None,
        }

        self.get_following()

    def parser(self, url, logger):

        while 1:
            try:
                r = requests.get(url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                time.sleep(3)
                logger.info('请求状态码' + str(r.status_code))
                if r.status_code == 404:
                    logger.warning('该用户被删！无法获得用户信息!!!')
                    self.is_del = True
                    break
                if r.status_code == 200:
                    self.content = BeautifulSoup(r.content, "lxml")
                    break
            except Exception as e:
                logger.error('请求出错！' + str(e))
                self.current_proxy = get_IP()
                logger.warning('切换ip代理!中断3秒！')
                time.sleep(3)
                continue

    def get_following(self):
        self.copycookies()
        self.get_createpoint()
        items = self.mongo.db.PM_question_followers_finalsample.find()
        for item in items:
            self.userID_list.append(item.get('user_id'))
        self.current_proxy = get_IP()
        self.get_cookie()
        # self.user_id_list = extract_last_followers()
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.state = False
            self.user_id = self.userID_list[i]
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d')))
            News = self.type + ','+ str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            logfielname = '/log/' + dt + 'followers_' + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                        logname='正在爬取第' + str(i + 1) + '个用户的关注了').getlog()

            following_url = 'https://www.zhihu.com/api/v4/members/' + str(self.user_id) + '/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={0}&limit=20'
            following_count = 0

            # self.following_id_list = extract_followers_following(self.user_id, self.user_id_list)
            # if len(self.following_id_list) == 0:
            #     self.following_type = 0
            # else:
            #     self.following_type = 1

            while 1:
                try:
                    r = requests.get(following_url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                    time.sleep(3)
                    logger.info('第一次请求状态码' + str(r.status_code))
                    if r.status_code == 200:
                        j = r.json()
                        following_count = j['paging']['totals']
                    elif r.status_code == 404:
                        self.is_del = True
                        logger.info('!!!该用户被删!!!')
                        self.delLogger(logger)
                        break
                    elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/followers_following_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            return
                        else:
                            self.change_cookie()
                            with open('User/followers_following_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                    else:
                        self.delLogger(logger)
                        return


                except Exception, e:
                    logger.error('查看回答数出错！' + str(e))
                    self.current_proxy = get_IP()
                    logger.warning('切换ip代理!中断3秒！')
                    time.sleep(3)
                    continue

                else:
                    # 没有关注者的用户也要保存一下
                    if following_count == 0:
                        logger.warning('用户没有关注者！')
                        self.delLogger(logger)
                        data_plus = {'user_id': self.user_id, "following_count": following_count}
                        self.mongo.db.FR_followers_following.insert(data_plus)
                        break
                    elif self.following_type == 0 and following_count >= 4000:
                        logger.warning('用户关注了数大于4000！')
                        self.delLogger(logger)
                        data_plus = {'user_id': self.user_id, "following_count": following_count}
                        self.mongo.db.FR_followers_following.insert(data_plus)
                        break
                    else:
                        offset = 0
                        while 1:
                            try:
                                soup = requests.get(following_url.format(str(offset)), headers=self.headers, timeout=5, proxies=self.current_proxy)
                                time.sleep(3)
                                logger.info('请求状态码' + str(soup.status_code))
                            except Exception, e:
                                logger.error('请求关注者出错！' + str(e))
                                self.current_proxy = get_IP()
                                logger.warning('切换ip代理!中断3秒！')
                                time.sleep(3)
                                continue
                            else:
                                following_data = soup.json()
                                data = following_data.get('data')
                                logger.info('is_end?' + str(following_data['paging']['is_end']))
                                if following_data['paging']['is_end']:
                                    following_list = []
                                    for i in range(0, len(data)):
                                        following_id = data[i]['url_token']  # 用户ID
                                        following_info = data[i]  # 全部信息

                                        info = {
                                        "following_id": following_id,
                                        "following_info": following_info
                                        }
                                        following_list.append(info)
                                    data_plus = {
                                    'user_id': self.user_id,
                                    "following_count": following_count,
                                    # "follower_type":self.following_type,
                                    "following": following_list
                                    }
                                    self.mongo.db.FR_followers_following.insert(data_plus)

                                    logger.info('已获得所有关注了用户！')
                                    logger.info('成功保存数据！')
                                    self.delLogger(logger)
                                    break
                                else:
                                    offset = offset + 20
                                    following_list = []
                                    for i in range(0, len(data)):
                                        following_id = data[i]['url_token']  # 用户ID
                                        # if following_id in self.following_id_list:
                                        #     self.state = True
                                        following_info = data[i]  # 全部信息

                                        info = {
                                        "following_id": following_id,
                                        "following_info": following_info
                                        }
                                        following_list.append(info)
                                    data_plus = {
                                    'user_id': self.user_id,
                                    "following_count": following_count,
                                    # "follower_type":self.following_type,
                                    "following": following_list
                                    }
                                    self.mongo.db.FR_followers_following.insert(data_plus)
                                    # if self.state:
                                    #     self.delLogger(logger)
                                    #     break
                        self.delLogger(logger)
                        self.mongo.client.close()
                        break

    def copycookies(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/followers_following_cookies.txt','a+') as f_a:
            Lines1 = f_a.readlines()
            if len(Lines1) == 0:
                for line in Lines:
                    f_a.write(line)

    def change_cookie(self):
        with open('Cookies/followers_following_cookies.txt', "r") as f:
            Lines = f.readlines()
            dict = eval(Lines[0])
            self.type = dict['type']
            self.headers['Cookie'] = dict['Cookie']
            self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/followers_following_cookies.txt', "w") as f_w:
            for line in Lines[1:]:
                f_w.write(line)

    def get_cookie(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
            for line in Lines:
                dict = eval(line)
                if self.type == dict['type']:
                    self.headers['Cookie'] = dict['Cookie']
                    self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/followers_following_cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/followers_following_cookies.txt', "w") as f_w:
            for line in Lines:
                if self.type != eval(line)['type']:
                    f_w.write(line)

    def get_createpoint(self):
        self.file = open('CreatePoint/followers_following_createpoint_' + str(self.fileNum) + '.txt','a+')
        Lines = self.file.readlines()
        if len(Lines) == 0:
            print '请输入爬取的Cookie编号、起始点和终止点：'
            Input = raw_input()
            self.type = Input.split(',')[0]
            self.start = int(Input.split(',')[1])
            self.end = int(Input.split(',')[2].strip('\n'))
            self.file.write(Input + '\n')
        else:
            self.type = Lines[-1].split(',')[0]
            self.start = int(Lines[-1].split(',')[1])
            self.end = int(Lines[-1].split(',')[2].strip('\n'))

    def delLogger(self, myLogger):
        for myHandler in myLogger.handlers:
            myHandler.close()
            myLogger.removeHandler(myHandler)