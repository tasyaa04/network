import datetime
import os

from flask import Flask, jsonify, make_response, redirect, render_template
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_restful import Api
from requests import delete, post
from werkzeug.utils import secure_filename

from data import db_session, posts_api
from data.chat import Chat, Message
from data.posts import Comment, CommentForm, Post, PostForm
from data.users import User
from forms.chatform import AccessChatForm, ChatForm, CreateForm
from forms.loginform import LoginForm
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(Post).filter(
            (Post.user == current_user) | (Post.is_private != True))
    else:
        posts = db_sess.query(Post).filter(Post.is_private != True)
    return render_template("index.html", posts=posts)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    return render_template('profile.html', title='Profle', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/enterchat', methods=['GET', 'POST'])
def enter():
    form = AccessChatForm()
    db_sess = db_session.create_session()
    chats = db_sess.query(Chat).all()
    if form.validate_on_submit():
        chat_name = form.chat_name.data
        if db_sess.query(Chat).filter(Chat.title == chat_name).first() is not None:
            current_user.room = chat_name
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect("/chat")
        else:
            return render_template('access.html', title='Chat', form=form, chats=chats,
                                   message='There are no chats like that')
    return render_template('access.html', title='Chat', form=form, chats=chats)


@app.route('/chat', methods=['GET', 'POST'])
def chatting():
    form = ChatForm()
    db_sess = db_session.create_session()
    chat = db_sess.query(Chat).filter(Chat.title == current_user.room).first()
    if form.validate_on_submit():
        msg = Message(
            content=form.text.data,
            user=current_user.name,
            chat=chat
        )
        chat.messages.append(msg)
        db_sess.add(msg)
        db_sess.merge(chat)
        db_sess.commit()
    return render_template('chat.html', title='Chat', chat=chat, form=form)


@app.route('/addchat', methods=['GET', 'POST'])
def add_chat():
    form = CreateForm()
    if form.validate_on_submit():
        if not bool(form.title.data) or not bool(form.user.data):
            return render_template('addchat.html', title='Create', form=form,
                                   message='Enter all fields')
        db_sess = db_session.create_session()
        chat = Chat(
            title=form.title.data,
            users=', '.join([current_user.name, form.user.data])
        )
        db_sess.add(chat)
        db_sess.commit()
        return redirect("/")
    return render_template('addchat.html', title='Create', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/post',  methods=['GET', 'POST'])
@login_required
def add_posts():
    form = PostForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, 'photos', filename))
        image_name = "file:///C:/Users/Hp/PycharmProjects/pythonProject/network/instance/photos/" + filename
        post('http://localhost:5000/api/posts',
             json={'title': form.title.data,
                   'content': form.content.data,
                   'user_id': current_user.id,
                   'is_private': form.is_private.data,
                   'image_name': image_name})
        return redirect('/')
    return render_template('post.html', title='Post',
                           form=form)


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    href = 'http://localhost:5000/api/news/' + str(id)
    delete(href)
    return redirect('/')


@app.route('/get_post/<int:id>', methods=['GET', 'POST'])
@login_required
def get_post(id):
    form = CommentForm()
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post=post
        )
        db_sess.add(comment)
        post.comments.append(comment)
        db_sess.merge(post)
    db_sess.commit()
    return render_template('get_post.html', title='Post',
                           form=form, post=post)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(posts_api.blueprint)
    app.run(debug=True)


if __name__ == '__main__':
    main()
