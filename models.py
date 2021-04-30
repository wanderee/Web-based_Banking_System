# -*- coding: utf-8 -*-

from peewee import MySQLDatabase, Model, CharField, BooleanField, IntegerField
import json
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import login_manager
from conf.config import config
import os

cfg = config[os.getenv('FLASK_CONFIG') or 'default']

db = MySQLDatabase(host=cfg.DB_HOST, user=cfg.DB_USER, passwd=cfg.DB_PASSWD, database=cfg.DB_DATABASE)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        # return str(r)
        return json.dumps(r, ensure_ascii=False)


# 管理员工号
class User(UserMixin, BaseModel):
    account_id = CharField()  # 账户id
    username = CharField()  # 用户名
    password = CharField()  # 密码
    fullname = CharField()  # 真实性名
    email = CharField()  # 邮箱
    authority = CharField()  # 账户权限
    money = CharField()  # 余额
    opener = CharField()  # 开户人
    status = BooleanField(default=True)  # 生效失效标识

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def gen_password(self, raw_password):
        self.password = generate_password_hash(raw_password)


# 通知人配置
class Flow(BaseModel):
    time = CharField()  # 时间
    send_id = CharField()  # 发送者账号id
    receive_id = CharField()  # 接受者账号id
    money = CharField()  # 转账金额
    status = BooleanField(default=True)  # 生效失效标识


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == int(user_id))


# 建表
def create_table():
    db.connect()
    db.create_tables([Flow, User])


if __name__ == '__main__':
    create_table()
