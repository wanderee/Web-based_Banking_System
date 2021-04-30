from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, InputRequired, Email, Regexp, EqualTo, NumberRange


class OpenAccountForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='输入4~16位的用户名'), Length(4, 16, message='长度不正确')])
    password = PasswordField('密码', validators=[DataRequired(message='输入6~36位的密码'), Length(6, 36, message='长度不正确')])
    confirm = PasswordField('确认密码', validators=[InputRequired(message='请输入密码'), EqualTo('password', '两次密码要一致')])
    fullname = StringField('真实姓名')
    email = StringField('邮箱')
    money = StringField('初始金额', validators=[DataRequired(message='输入初始金额的数字'),
                                            Length(0, 64, message='长度不正确')])
    submit = SubmitField('开户')


class CloseAccountForm(FlaskForm):
    account_id = StringField('账号', validators=[DataRequired(message='请输入6位的账号'), Length(6, 6, message='长度不正确')])
    submit = SubmitField('销户')


class TransferAccountForm(FlaskForm):
    account_id = StringField('接收账号', validators=[DataRequired(message='请输入6位的账号'), Length(6, 6, message='长度不正确')])
    money_change = StringField('接收账号', validators=[DataRequired(message='请输入金额'), Length(0, 16, message='长度不正确')])
    submit = SubmitField('转账')


class TestForm(FlaskForm):
    name = StringField('What is your name', validators=[DataRequired()])
    submit = SubmitField('Submit')
