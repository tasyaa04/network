from flask import Flask, render_template, request, redirect, session, make_response
from data import db_session
from data.users import User
from data.posts import Post, PostForm
from forms.user import RegisterForm
from forms.loginform import LoginForm
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(Post).filter(
            (Post.user == current_user) | (Post.is_private != True))
    else:
        posts = db_sess.query(Post).filter(Post.is_private != True)
    return render_template("index.html", posts=posts)


@app.route('/session_test')
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
        db_sess = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.content = form.content.data
        post.image = form.image.data
        post.is_private = form.is_private.data
        current_user.posts.append(post)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('post.html', title='Post',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()