from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


# 发贴
class PostFrom(FlaskForm):
    title = StringField("文章标题", validators=[DataRequired(message="看来你不是标题党")])
    content = TextAreaField("文章内容", validators=[DataRequired(message="空者西天也")])
    submit = SubmitField("点击提交")
