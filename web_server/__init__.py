from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from web_server import test_pass

# Flask初始化
app = Flask(__name__)
# 配置网站密匙
app.config["SECRET_KEY"] = test_pass.secret_key
# 数据库实例生成
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'

db = SQLAlchemy(app)  # 数据库链接初始化
bcrypt = Bcrypt(app)  # 加密初始华
login_manager = LoginManager(app)  # 登陆管理初始化
login_manager.login_message_category = 'info'
login_manager.login_message = u"请先登陆，不然的话，你懂的！"  # 强行登陆的汉化提醒
login_manager.login_view = 'users.login'

app.config['MAIL_SERVER'] = 'smtp.126.com'
# 163:Non SSL:25   SSL:465/994
app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = test_pass.mail_username  # os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = test_pass.mail_password  # os.environ.get('EMAIL_PASS')
mail = Mail(app)

from web_server.users.routes import users
from web_server.posts.routes import posts
from web_server.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)


