from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
from app.models import User, Flow
from app.main.forms import OpenAccountForm, CloseAccountForm, TransferAccountForm
from . import main

logger = get_logger(__name__)
cfg = get_config()


def create_account(DynamicModel, form, view):
    if form.validate_on_submit():
        model = DynamicModel()
        utils.open_account_form_to_model(form, model, int(current_user.authority), current_user.id)
        model.save()
        flash('开户成功,账号:' + str(model.account_id))
    else:
        utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


def cancellation_account(DynamicModel, form, view):
    if form.validate_on_submit():
        account_id = form.account_id.data
        DynamicModel.get(DynamicModel.account_id == account_id).delete_instance()
        flash('销户成功')
    else:
        utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


def transfer_money(DynamicModel, form, view):
    my_count_id = current_user.account_id
    if form.validate_on_submit():
        if my_count_id == form.account_id.data:
            flash('不能转账给自己')
        else:
            try:
                accept_user = DynamicModel.get(DynamicModel.account_id == form.account_id.data)
            except:
                flash('没有该用户')
                return render_template(view, form=form, current_user=current_user)
            my_money = float(current_user.money)
            acceptor_money = float(accept_user.money)
            money_change = float(form.money_change.data)
            if my_money < money_change:
                flash('余额不足')
            else:
                my_money -= money_change
                acceptor_money += money_change
                current_user.money = my_money
                accept_user.money = acceptor_money
                current_user.save()
                accept_user.save()
                flash('转账成功')
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
    return render_template('index.html', current_user=current_user)


# 开户
@main.route('/open_account', methods=['GET', 'POST'])
@login_required
def open_account():
    return create_account(User, OpenAccountForm(), 'open_account.html')


# 销户
@main.route('/close_account', methods=['GET', 'POST'])
@login_required
def close_account():
    return cancellation_account(User, CloseAccountForm(), 'close_account.html')


# 查余额
@main.route('/search_money', methods=['GET', 'POST'])
@login_required
def search_money():
    return render_template('search_money.html', money=current_user.money, current_user=current_user)


# 查余额
@main.route('/transfer_account', methods=['GET', 'POST'])
@login_required
def transfer_account():
    return transfer_money(User, TransferAccountForm(), 'transfer_account.html')
