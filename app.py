import sqlite3

from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

from datetime import datetime
import pytz

from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    
    def __init__(self, id, title, body, created_at):
        self.id = id
        self.title = title
        self.body = body
        self.created_at = created_at

    def __str__(self):
        return f'id:{self.id} title:{self.title} body:{self.body}'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)
        
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return f'id:{self.id} title:{self.username} body:{self.password}'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        try:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/index')
            else:
                return redirect('/error')
        except AttributeError:
            return redirect('/error')
    else:
        return render_template('login.html')


@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        post = Post(title=title, body=body)

        db.session.add(post)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create.html')


@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):  # put application's code here
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        db.session.commit()
        return redirect('/index')


@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):  # put application's code here
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/index')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
#    app.run(debug=True)
