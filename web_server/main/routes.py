from flask import Blueprint, render_template, request
from web_server.models import Post

main = Blueprint('main', __name__)


# 装饰器，当系统识别到装饰器中的符号，将执行以下代码
@main.route('/')  # 主页
def index():
    page = request.args.get('page', 1, type=int)
    # 倒序显示文章，并设置一页显示多少数据
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5)
    return render_template("main.html", posts=posts)


# 关于页面
@main.route('/about')
def about():
    return render_template("about.html", title="关于")
