import datetime

import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_serializer import SerializerMixin
from wtforms import (BooleanField, FileField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import DataRequired

from .db_session import SqlAlchemyBase


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
    comments = orm.relation("Comment", back_populates='post')

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


class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    user = orm.relation('User')

    post_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("posts.id"))

    post = orm.relation('Post')


class CommentForm(FlaskForm):
    content = StringField('Share your thoughts')
    send = SubmitField('Send')
