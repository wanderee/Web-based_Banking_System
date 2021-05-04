from app import get_logger, get_config
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
from app.models import User, Flow
from app.main.forms import OpenAccountForm, CloseAccountForm, TransferAccountForm
from . import main

logger = get_logger(__name__)
cfg = get_config()
authority_dict = {'0': '超级管理员',
                  '1': '职员',
                  '2': '客户'}


def create_account(form, view):
    if form.validate_on_submit():
        if current_user.authority == '2':
            flash('您没有权限开户')
        else:
            new_user = User()
            error = utils.open_account(form, new_user, int(current_user.authority), current_user.id)
            if error == 0:
                flash('开户成功,账号:' + str(new_user.account_id))
            elif error == 1:
                flash('用户名重复')
            else:
                flash('开户失败')
    else:
        utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


def cancellation_account(form, view):
    if form.validate_on_submit():
        account_id = form.account_id.data
        delete_user = User.get_or_none(User.account_id == account_id)
        if delete_user is not None:
            if int(current_user.authority) < int(delete_user.authority):
                delete_user.delete_instance()
                flash('销户成功')
            else:
                flash('您没有权限注销该用户')
        else:
            flash('没有该用户')
    else:
        utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


def transfer_money(form, view):
    if form.validate_on_submit():
        if current_user.account_id == form.account_id.data:
            flash('不能转账给自己')
        else:
            receive_user = User.get(User.account_id == form.account_id.data)
            if receive_user is not None:
                flow = Flow()
                if utils.transfer_money(current_user, receive_user, form.money_change.data):
                    utils.flow_save(flow, current_user.account_id, receive_user.account_id, form.money_change.data)
                    flash('转账成功')
                else:
                    flash('余额不足')
            else:
                flash('没有该用户')
    return render_template(view, form=form, current_user=current_user)


# 根目录跳转
@main.route('/', methods=['GET'])
@login_required
def root():
    return redirect(url_for('main.index'))


# 首页
@main.route('/index', methods=['GET'])
@login_required
def index():
    user_count, flow_count = utils.transaction_count(current_user.account_id)
    base_info = {'my_account': current_user.account_id,
                 'my_authority': authority_dict[current_user.authority],
                 'user_count': user_count,
                 'flow_count': flow_count}
    return render_template('index.html', base_info=base_info, current_user=current_user)


# 开户
@main.route('/open_account', methods=['GET', 'POST'])
@login_required
def open_account():
    return create_account(OpenAccountForm(), 'open_account.html')


# 销户
@main.route('/close_account', methods=['GET', 'POST'])
@login_required
def close_account():
    return cancellation_account(CloseAccountForm(), 'close_account.html')


# 查余额
@main.route('/search_money', methods=['GET', 'POST'])
@login_required
def search_money():
    return render_template('search_money.html', money=current_user.money, current_user=current_user)


# 转账
@main.route('/transfer_account', methods=['GET', 'POST'])
@login_required
def transfer_account():
    return transfer_money(TransferAccountForm(), 'transfer_account.html')


# 查流水
@main.route('/search_flow', methods=['GET', 'POST'])
@login_required
def search_flow():
    flow_list = utils.get_flow_list(current_user.account_id)
    return render_template('search_flow.html', flow_list=flow_list,current_user=current_user)
