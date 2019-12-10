import sqlite3
from datetime import datetime

from flask import Flask, g, render_template, request

from db import init_db, fetch_detail, fetch_list


DATABASE = 'autocms.sqlite'
app = Flask(__name__)


# This is where most of the procedural code lies
# Add DB connection code
def get_db():
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts')
def posts_list():
    query = '''
        SELECT
            posts.*,
            users.first_name || ' ' || users.last_name AS author
        FROM
            posts INNER JOIN users ON posts.author_id = users.id
        WHERE
            status = 1
    '''
    posts = fetch_list(get_db(), query)
    return render_template('posts.html', posts=posts)


@app.route('/posts/<post_id>')
def post_detail(post_id):
    print(post_id)
    query = f'''
        SELECT
            posts.*,
            users.first_name || ' ' || users.last_name AS author
        FROM
            posts INNER JOIN users ON posts.author_id = users.id
        WHERE
            posts.id = {post_id}
    '''
    post = fetch_detail(get_db(), query)
    return render_template('post.html', post=post)


@app.route('/vehicles')
def list_vehicles():
    return render_template('vehicles.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        query = f'''
            SELECT
                username
            FROM
                users
            WHERE
                username='{username}' AND password='{password}'
        '''

        username = fetch_detail(get_db(), query)

        if not username:
            return render_template(
                'admin_login.html', error='Wrong Credentials!')

        return render_template('index.html')


@app.route('/admin/posts')
def post_admin():
    return render_template('posts_admin.html')


# Create Jinja filters to format datetime from db.
def format_date(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return date.strftime('%b. %d, %Y %I:%M %p')


app.jinja_env.filters['dateformat'] = format_date


# Initialize database
init_db(app)
