from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, TextField
from wtforms.validators import DataRequired


class AccessChatForm(FlaskForm):
    chat_name = StringField('Chat Name')
    enter = SubmitField('Enter')


class CreateForm(FlaskForm):
    title = StringField('Title')
    user = StringField('User')
    create = SubmitField('Create')


class ChatForm(FlaskForm):
    text = TextField('Enter your message here')
    send = SubmitField('Send')