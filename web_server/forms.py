from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from web_server.models import User


# 注册表单
class RegistrationForm(FlaskForm):
    # 用户名校验，数据校验及长度校验
    username = StringField("昵称", validators=[DataRequired(message="虽然英雄无名，但还请留下点什么！"),
                                             Length(min=2, max=21, message="昵称要在2到21个")])
    # 邮箱校验，数据及邮箱校验 WTForms版本在2.2.1才能执行此代码
    email = StringField("邮箱/Email",
                        validators=[DataRequired(message="英雄，留个联系方式呗！"), Email(message="邮箱的格式是：name@163.com")])
    # 密码校验
    password = PasswordField("密码", validators=[DataRequired(message="我勒个去，没密码这活没法干了！")])
    # 验证信息字母小写，一定注意
    confirm_password = PasswordField("密码确认", validators=[DataRequired(message="我勒个去，没密码这活没法干了！"),
                                                         EqualTo("password", message="英雄，咱能把密码输入一致不！")])
    # 提交
    submit = SubmitField("点击注册")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("用户名已存在，换一个试试？")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email已存在，换一个试试？")


# 用户数据更新
class UpdateAccountForm(FlaskForm):
    # 用户名校验，数据校验及长度校验
    username = StringField("昵称", validators=[DataRequired(message="虽然英雄无名，但还请留下点什么！"),
                                             Length(min=2, max=21, message="昵称要在2到21个")])
    # 邮箱校验，数据及邮箱校验 WTForms版本在2.2.1才能执行此代码
    email = StringField("邮箱/Email",
                        validators=[DataRequired(message="英雄，留个联系方式呗！"), Email(message="邮箱的格式是：name@163.com")])
    # 用户提交图片校验
    picture = FileField("点击上传头像", validators=[FileAllowed(["jpg", "png"], message="目前仅支持jpg与png格式")])
    # 提交
    submit = SubmitField("点击更新")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("用户名已存在，换一个试试？")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email已存在，换一个试试？")


# 登录
class LoginForm(FlaskForm):
    email = StringField("邮箱/Email", validators=[DataRequired(message="你是来砸场子的吧！"), Email(message="请输入正确的邮箱格式")])
    password = PasswordField("密码", validators=[DataRequired("小样，没有钥匙可是进不去的哦！")])
    remember = BooleanField("记住密码")
    submit = SubmitField("点击登陆")


# 发贴
class PostFrom(FlaskForm):
    title = StringField("文章标题", validators=[DataRequired(message="看来你不是标题党")])
    content = TextAreaField("文章内容", validators=[DataRequired(message="空者西天也")])
    submit = SubmitField("点击提交")


# 验证邮箱以便重置密码
class RequesResetForm(FlaskForm):
    email = StringField("邮箱/Email",
                        validators=[DataRequired(message="英雄，邮箱不会也忘了吧！"), Email(message="邮箱的格式是：name@163.com")])
    submit = SubmitField("点击提交")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("臣妾找不到Email啊!")


# 重置密码
class ResetPasswordForm(FlaskForm):
    password = PasswordField("密码", validators=[DataRequired(message="我勒个去，没密码这活没法干了！")])
    # 验证信息字母小写，一定注意
    confirm_password = PasswordField("密码确认", validators=[DataRequired(message="我勒个去，没密码这活没法干了！"),
                                                         EqualTo("password", message="英雄，咱能把密码输入一致不！")])
    # 提交
    submit = SubmitField("点击重置密码")
