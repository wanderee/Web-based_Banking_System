# -*- coding: utf-8 -*-

import html
import json
import datetime
import collections
from urllib.parse import unquote
import peewee
from flask import Response, flash
import random
import time
from models import User

## 字符串转字典
from app.models import Flow


def str_to_dict(dict_str):
    if isinstance(dict_str, str) and dict_str != '':
        new_dict = json.loads(dict_str)
    else:
        new_dict = ""
    return new_dict


## URL解码
def urldecode(raw_str):
    return unquote(raw_str)


# HTML解码
def html_unescape(raw_str):
    return html.unescape(raw_str)


## 键值对字符串转JSON字符串
def kvstr_to_jsonstr(kvstr):
    kvstr = urldecode(kvstr)
    kvstr_list = kvstr.split('&')
    json_dict = {}
    for kvstr in kvstr_list:
        key = kvstr.split('=')[0]
        value = kvstr.split('=')[1]
        json_dict[key] = value
    json_str = json.dumps(json_dict, ensure_ascii=False, default=datetime_handler)
    return json_str


# 字典转对象
def dict_to_obj(dict, obj, exclude=None):
    for key in dict:
        if exclude:
            if key in exclude:
                continue
        setattr(obj, key, dict[key])
    return obj


# peewee转dict
def obj_to_dict(obj, exclude=None):
    dict = obj.__dict__['_data']
    if exclude:
        for key in exclude:
            if key in dict: dict.pop(key)
    return dict


# peewee转list
def query_to_list(query, exclude=None):
    list = []
    for obj in query:
        dict = obj_to_dict(obj, exclude)
        list.append(dict)
    return list


# 封装HTTP响应
def jsonresp(jsonobj=None, status=200, errinfo=None):
    if status >= 200 and status < 300:
        jsonstr = json.dumps(jsonobj, ensure_ascii=False, default=datetime_handler)
        return Response(jsonstr, mimetype='application/json', status=status)
    else:
        return Response('{"errinfo":"%s"}' % (errinfo,), mimetype='application/json', status=status)


# 通过名称获取PEEWEE模型
def get_model_by_name(model_name):
    if model_name == 'notifies':
        DynamicModel = Flow
    else:
        DynamicModel = None
    return DynamicModel


# JSON中时间格式处理
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError("Unknown type")


# wtf表单转peewee模型
def form_to_model(form, model):
    for wtf in form:
        model.__setattr__(wtf.name, wtf.data)
    return model


def transaction_count(account_id):
    r1, r2 = Flow.select().where(Flow.send_id == '000000'), Flow.select().where(Flow.receive_id == '000000')
    flow_count = r1.count() + r2.count()
    user_count = []
    for flow_row in r1:
        user_count.append(flow_row.receive_id)
    for flow_row in r2:
        user_count.append(flow_row.send_id)
    user_count = len(collections.Counter(user_count).keys())
    return user_count, flow_count


def open_account(form, model, authority, opener):
    """
    :param form:
    :param model:
    :param authority:
    :param opener:
    :return:    0:success
                1:用户名重复
    """

    new_account_id = str(random.randint(1, 999999)).zfill(6)
    while User.get_or_none(User.account_id == new_account_id) is not None:
        new_account_id = str(random.randint(1, 999999)).zfill(6)
    model.account_id = new_account_id
    if User.get_or_none(User.username == form.username.data) is not None:
        return 1
    model.username = form.username.data
    model.gen_password(form.password.data)
    model.fullname = form.fullname.data
    model.email = form.email.data
    model.money = form.money.data
    model.authority = str(authority + 1)
    model.opener = opener
    model.save()
    return 0


def flow_save(flow, send_id, receive_id, money):
    localtime = time.asctime(time.localtime(time.time()))
    flow.time = localtime
    flow.send_id = send_id
    flow.receive_id = receive_id
    flow.money = money
    flow.save()


def transfer_money(send_user, receive_user, money):
    my_money = float(send_user.money)
    receive_money = float(receive_user.money)
    money_change = float(money)
    if my_money < money_change:
        return False
    else:
        my_money -= money_change
        receive_money += money_change
        send_user.money = my_money
        print('{} send {} to {}'.format(my_money, money_change, receive_money))
        receive_user.money = receive_money
        send_user.save()
        receive_user.save()
        return True


def get_flow_list(account_id):
    return Flow.select().where((Flow.send_id == account_id) | (Flow.receive_id == account_id))


# peewee模型转表单
def model_to_form(model, form):
    dict = obj_to_dict(model)
    form_key_list = [k for k in form.__dict__]
    for k, v in dict.items():
        if k in form_key_list and v:
            field = form.__getitem__(k)
            field.data = v
            form.__setattr__(k, field)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("字段 [%s] 格式有误,错误原因: %s" % (
                getattr(form, field).label.text,
                error
            ))
