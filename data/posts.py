import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from sqlalchemy_imageattach.entity import Image, image_attachment


class Post(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    image = image_attachment('PostPicture')
    image_name = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relation('User')


class PostPicture(SqlAlchemyBase, Image):
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'), primary_key=True)
    user = relationship('Post')
    __tablename__ = 'post_picture'


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField("Text")
    image = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    is_private = BooleanField("Personal")
    submit = SubmitField('Post')
