# encoding=utf-8

import datetime
from mongodb import Mongo_1,Mongo_2

class Adder:

    def __init__(self):
        self.followers_list = []
        self.followers_list_old = []
        self.mongo = Mongo_2()


    def followers_difference(self):
        temp = self.mongo.db.followers.find({})
        for l in temp:
            self.followers_list.append(l.get('user_id'))
        print len(set(self.followers_list))
        temps = self.mongo.db.followers_old.find({})
        for l in temps:
            self.followers_list_old.append(l.get('user_id'))
        print len(set(self.followers_list_old))
        ret_list = list(set(self.followers_list).difference(set(self.followers_list_old)))
        print len(ret_list)
        for i in range(len(ret_list)):
            data = {'user_id':ret_list[i]}
            self.mongo.db.followers_new.insert(data)
        self.mongo.client.close()
        print '新增关注者抽取完毕...'


    def commenters_difference(self):
        temp = self.mongo.db.commenters.find({})
        for l in temp:
            self.followers_list.append(l.get('user_id'))
        print len(set(self.followers_list))
        temps = self.mongo.db.commenters_old.find({})
        for l in temps:
            self.followers_list_old.append(l.get('user_id'))
        print len(set(self.followers_list_old))
        ret_list = list(set(self.followers_list).difference(set(self.followers_list_old)))
        print len(ret_list)
        for i in range(len(ret_list)):
            data = {'user_id':ret_list[i]}
            self.mongo.db.commenters_new.insert(data)
        self.mongo.client.close()
        print '新增评论者抽取完毕...'

    def voters_difference(self):
        temp = self.mongo.db.voters.find({})
        for l in temp:
            self.followers_list.append(l.get('user_id'))
        print len(set(self.followers_list))
        temps = self.mongo.db.voters_old.find({})
        for l in temps:
            self.followers_list_old.append(l.get('user_id'))
        print len(set(self.followers_list_old))
        ret_list = list(set(self.followers_list).difference(set(self.followers_list_old)))
        print len(ret_list)
        for i in range(len(ret_list)):
            data = {'user_id':ret_list[i]}
            self.mongo.db.voters_new.insert(data)
        self.mongo.client.close()
        print '新增点赞者抽取完毕...'

    def answerers_difference(self):
        lists = self.mongo.db.answerers.find({})
        for l in lists:
            self.followers_list.append(l.get('user_id'))
        print len(set(self.followers_list))
        temps = self.mongo.db.answerers_old.find({})
        for l in temps:
            self.followers_list_old.append(l.get('user_id'))
        print len(set(self.followers_list_old))
        ret_list = list(set(self.followers_list).difference(set(self.followers_list_old)))
        print len(ret_list)
        for i in range(len(ret_list)):
            data = {'user_id': ret_list[i]}
            self.mongo.db.answerers_new.insert(data)
        self.mongo.client.close()
        print '新增回答者抽取完毕...'

    def editors_difference(self):
        lists = self.mongo.db.editors.find({})
        for l in lists:
            self.followers_list.append(l.get('user_id'))
        print len(set(self.followers_list))
        temps = self.mongo.db.editors_old.find({})
        for l in temps:
            self.followers_list_old.append(l.get('user_id'))
        print len(set(self.followers_list_old))
        ret_list = list(set(self.followers_list).difference(set(self.followers_list_old)))
        print len(ret_list)
        for i in range(len(ret_list)):
            data = {'user_id': ret_list[i]}
            self.mongo.db.editors_new.insert(data)
        self.mongo.client.close()
        print '新增编辑者抽取完毕...'

if __name__ == "__main__":

    begin = datetime.datetime.now()
    #创建对象
    add = Adder()

    # 新增关注者
    # add.followers_difference()

    # 新增评论者
    # add.commenters_difference()

    # 新增点赞者
    # add.voters_difference()

    # 新增回答者
    # add.answerers_difference()

    # 新增编辑者
    add.editors_difference()

    end = datetime.datetime.now()

    print '用时：' + str(end - begin)