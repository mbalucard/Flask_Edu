from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
from web_server import db, bcrypt
from web_server.models import User, Post
from web_server.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequesResetForm, ResetPasswordForm
from web_server.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


# 用户注册模块
@users.route('/register', methods=['GET', 'POST'])
def register():
    # 如果登陆，点注册返回首页
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")  # 用户密码加密
        # 生成用户信息并提交数据库
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # db.create_all()  # 数据库初始化
        db.session.add(user)  # 加入表单
        db.session.commit()  # 提交至数据库
        # 反馈用户注册成功，并跳转
        flash('注册成功，奖励【{}】多多发帖。'.format(form.username.data), 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title="注册界面", form=form)


# 用户登陆模块
@users.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已登陆，点登陆将返回主页
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # 调取用户输入的email信息
        # 验证用户email和密码，如果正确返回至主页，错误则反馈信息
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("登陆成功！", "success")
            next_page = request.args.get("next")  # 未登陆时访问登陆后才能显示的页面，在登陆后返回原页面
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        else:
            flash("登陆失败，请检查Email或密码是否正确", "danger")
    return render_template("login.html", title="登录界面", form=form)


# 登出模块
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.index"))


# 用户资料更新
@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    # 用户信息修改
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # 数据库提交命令
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("更新成功", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    # 用户信息显示
    image_file = url_for("static", filename="user_pics/" + current_user.image_file)
    return render_template("account.html", title="个人主页", image_file=image_file, form=form)


# 实现点击用户名，调用该用所所有文章的功能，且最新发布的在最前面
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


# 邮箱密码重置页面
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequesResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("已对您的邮箱传音，赶紧查看并重置密码", 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='邮箱密码重置', form=form)


# 重新输入新密码页面
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("验证标识不正确，请重试", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")  # 用户密码加密
        # 生成用户信息并提交数据库
        user.password = hashed_password

        db.session.commit()  # 提交至数据库
        # 反馈用户注册成功，并跳转
        flash('您的密码修改成功。', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='新密码输入', form=form)
