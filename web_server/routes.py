# import secrets
import random
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from web_server.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostFrom, RequesResetForm, \
    ResetPasswordForm
from web_server import app, db, bcrypt, mail
from web_server.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


# posts = [{'name': "清角", 'title': "无聊", 'content': "沙发", 'date': "2020年11月11日"},
#          {'name': "Alucard", 'title': "发呆", 'content': "板凳", 'date': "2020年11月12日"},
#          {'name': "Dracula", 'title': "大爷", 'content': "楼上的我是你大爷", 'date': "2020年11月12日"}]


# 装饰器，当系统识别到装饰器中的符号，将执行以下代码
@app.route('/')  # 主页
def index():
    page = request.args.get('page', 1, type=int)
    # 倒序显示文章，并设置一页显示多少数据
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5)
    return render_template("main.html", posts=posts)


# 关于页面
@app.route('/about')
def about():
    return render_template("about.html", title="关于")


# 注册模块
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果登陆，点注册返回首页
    if current_user.is_authenticated:
        return redirect(url_for("index"))
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
        return redirect(url_for('login'))
    return render_template("register.html", title="注册界面", form=form)


# 用户登陆模块
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已登陆，点登陆将返回主页
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # 调取用户输入的email信息
        # 验证用户email和密码，如果正确返回至主页，错误则反馈信息
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("登陆成功！", "success")
            next_page = request.args.get("next")  # 未登陆时访问登陆后才能显示的页面，在登陆后返回原页面
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("登陆失败，请检查Email或密码是否正确", "danger")
    return render_template("login.html", title="登录界面", form=form)


# 登出模块
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))


# 图片保存
def save_picture(form_picture):
    # random_hex = secrets.token_hex(8)
    random_hex = str(random.randint(0, 100000))  # 生成随机数
    picture_file_name, file_extension = os.path.splitext(form_picture.filename)  # 获取文件名及后缀
    picture_filename = random_hex + picture_file_name + file_extension  # 交随机数，文件名，后缀组合成新文件名
    picture_path = os.path.join(app.root_path, "static/user_pics", picture_filename)  # 生成文件保存的路径
    # form_picture.save(picture_path)  # 按文件路径保存文件路径
    output_img_size = (100, 100)
    thumbnail_img = Image.open(form_picture)
    thumbnail_img.thumbnail(output_img_size)  # 调整图片大小
    thumbnail_img.save(picture_path)
    return picture_filename


# 用户资料更新
@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    # 用户信息显示
    image_file = url_for("static", filename="user_pics/" + current_user.image_file)
    return render_template("account.html", title="个人主页", image_file=image_file, form=form)


# 发布新贴
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostFrom()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("打完收工", "success")
        return redirect(url_for('index'))
    return render_template("create_post.html", title="发帖", form=form, legend="写新文章")


# 查看单贴
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


# 帖子更新（修改）
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # 仅允许发帖人与登陆id相同的情况下更新
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostFrom()
    # 更新文章功能模块
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("更新成功", "success")
        return redirect(url_for("post", post_id=post.id))
    # 更新文章时，将原文章内容填充
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title="更新文章", form=form, legend="更新文章")


# 删除文章模块
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("文章删除成功", "success")
    return redirect(url_for('index'))


# 实现点击用户名，调用该用所所有文章的功能，且最新发布的在最前面
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("关于重置lucifer论坛登陆方式的邮件", sender='mbalucard<mbalucard@126.com>', recipients=[user.email])
    msg.body = f'''您正在进行【Lucifer论坛】忘记密码操作，请点击下列链接进行重置操作：
    {url_for('reset_token', token=token, _external=True)}'''
    mail.send(msg)


# 邮箱密码重置页面
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequesResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("已对您的邮箱传音，赶紧查看并重置密码", 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='邮箱密码重置', form=form)


# 重新输入新密码页面
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("验证标识不正确，请重试", 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")  # 用户密码加密
        # 生成用户信息并提交数据库
        user.password = hashed_password

        db.session.commit()  # 提交至数据库
        # 反馈用户注册成功，并跳转
        flash('您的密码修改成功。', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='新密码输入', form=form)
