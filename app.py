import sqlite3

from flask import Flask, g, render_template

from db import init_db


DATABASE = 'autocms.db'
app = Flask(__name__)


# Add DB connection code
def get_db():
    print('hello')
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/posts')
def post_admin():
    return render_template('posts_admin.html')


# Initialize database
init_db(app)
