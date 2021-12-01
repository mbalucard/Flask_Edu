from flask import Blueprint, render_template, url_for, flash, abort, redirect, request
from flask_login import current_user, login_required
from web_server import db
from web_server.models import Post
from web_server.posts.forms import PostFrom

posts = Blueprint('posts', __name__)


# 发布新贴
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostFrom()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("打完收工", "success")
        return redirect(url_for('main.index'))
    return render_template("create_post.html", title="发帖", form=form, legend="写新文章")


# 查看单贴
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


# 帖子更新（修改）
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for("posts.post", post_id=post.id))
    # 更新文章时，将原文章内容填充
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title="更新文章", form=form, legend="更新文章")


# 删除文章模块
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("文章删除成功", "success")
    return redirect(url_for('main.index'))
