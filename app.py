import sqlite3
from datetime import datetime

from flask import (
    Flask, g, render_template, redirect, request, session, url_for)

from db import (
    commit_data, fetch_detail, fetch_list, init_db, CAR_TYPE_TYPES, FUEL_TYPES,
    POST_STATUS_TYPES, SIZE_TYPES, TRANSMISSION_TYPES, VEHICLE_STATUS_TYPES,
    WEIGHT_CATEGORY_TYPES)


DATABASE = 'autocms.sqlite'
app = Flask(__name__)


app.secret_key = 'not_so-$3kret=key'


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
def vehicles_list():
    kwargs = {
        'car_type_types': CAR_TYPE_TYPES
    }

    query = '''
        SELECT DISTINCT car_type FROM cars
    '''
    car_types = fetch_list(get_db(), query)

    return render_template('vehicles.html', car_types=car_types, **kwargs)


@app.route('/vehicles/cars/')
def cars_list():
    car_type = request.args.get('car_type')

    query = f'''
        SELECT DISTINCT model FROM cars WHERE car_type = {car_type}
    '''
    car_models = fetch_list(get_db(), query)
    car_models = [model['model'] for model in car_models]

    query = f'''
        SELECT id, series, price, model FROM cars WHERE car_type = {car_type}
    '''
    cars_list = fetch_list(get_db(), query)

    cars = dict((model, []) for model in car_models)
    for car in cars_list:
        cars[car['model']].append(car)

    return render_template('cars.html', car_models=car_models, cars=cars)


@app.route('/admin')
def admin_index():
    if not session.get('username', None) or not session.get('user_id', None):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        query = f'''
            SELECT
                id,
                username
            FROM
                users
            WHERE
                username='{username}' AND password='{password}'
        '''

        user = fetch_detail(get_db(), query)

        if not user:
            return render_template(
                'admin_login.html', error='Wrong Credentials!')

        session['username'] = user['username']
        session['user_id'] = user['id']

        return redirect(url_for('admin_index'))


@app.route('/admin/posts/create', methods=['GET', 'POST'])
def admin_add_post():
    kwargs = {
        'post_status_types': POST_STATUS_TYPES
    }

    if request.method == 'GET':
        return render_template('post_form.html', **kwargs)

    if request.method == 'POST':
        data = request.form

        title = data.get('title').strip()
        slug = data.get('slug').strip()
        content = data.get('content').strip()
        status = int(data.get('status'))
        author_id = session.get('user_id')

        query = f'''
            INSERT INTO
                posts(content, slug, status, title, author_id)
            VALUES
                ('{content}', '{slug}', {status}, '{title}', {author_id})
        '''

        commit_data(get_db(), query)
        return render_template('post_form.html', created=True, **kwargs)


@app.route('/admin/cars/create', methods=['GET', 'POST'])
def admin_add_car():
    kwargs = {
        'vehicle_status_types': VEHICLE_STATUS_TYPES,
        'transmission_types': TRANSMISSION_TYPES,
        'fuel_types': FUEL_TYPES,
        'car_type_types': CAR_TYPE_TYPES
    }

    if request.method == 'POST':
        data = request.form

        model = data.get('model')
        slug = data.get('slug')
        description = data.get('description')
        price = data.get('price')
        status = data.get('status')
        car_type = data.get('car_type')
        series = data.get('series')
        transmission = data.get('transmission')
        fuel = data.get('fuel')

        query = f'''
            INSERT INTO
                cars(
                    car_type, description, fuel, model, price, series, slug,
                    status, transmission
                )
            VALUES
                (
                    {car_type}, '{description}', {fuel}, '{model}', {price},
                    '{series}', '{slug}', {status}, {transmission}
                );

        '''

        created = True
        try:
            commit_data(get_db(), query)
        except Exception as e:
            print(e)
            created = False

        return render_template('car_form.html', created=created, **kwargs)

    if request.method == 'GET':
        return render_template('car_form.html', **kwargs)


@app.route('/admin/trucks/create', methods=['GET', 'POST'])
def admin_add_truck():
    kwargs = {
        'vehicle_status_types': VEHICLE_STATUS_TYPES,
        'size_types': SIZE_TYPES,
        'weight_category_types': WEIGHT_CATEGORY_TYPES
    }

    if request.method == 'GET':
        return render_template('truck_form.html', **kwargs)


@app.route('/admin/logout')
def admin_logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


# Create Jinja filters to format datetime from db.
def format_date(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    return date.strftime('%b. %d, %Y %I:%M %p')


app.jinja_env.filters['dateformat'] = format_date


# Initialize database
init_db(app)
