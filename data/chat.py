import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    users = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    messages = orm.relation("Message", back_populates='chat')


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    content = sqlalchemy.Column(sqlalchemy.String)
    user = sqlalchemy.Column(sqlalchemy.String)

    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("chats.id"))

    chat = orm.relation("Chat")

    time = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

