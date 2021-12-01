import random
import os
from web_server import app
from flask import url_for
from PIL import Image
from flask_mail import Message
from web_server import app, mail


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("关于重置lucifer论坛登陆方式的邮件", sender='mbalucard<mbalucard@126.com>', recipients=[user.email])
    msg.body = f'''您正在进行【Lucifer论坛】忘记密码操作，请点击下列链接进行重置操作：
    {url_for('users.reset_token', token=token, _external=True)}'''
    mail.send(msg)
