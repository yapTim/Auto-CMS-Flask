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
        'car_type_types': CAR_TYPE_TYPES,
        'weight_category_types': WEIGHT_CATEGORY_TYPES
    }

    query = 'SELECT DISTINCT car_type FROM cars'
    car_types = fetch_list(get_db(), query)

    query = 'SELECT DISTINCT weight_category from trucks'
    weight_categories = fetch_list(get_db(), query)

    return render_template(
        'vehicles_index.html', car_types=car_types,
        weight_categories=weight_categories, **kwargs)


def fetch_models(table, column, value):
    query = f'''
        SELECT DISTINCT model FROM {table} WHERE {column} = {value}
    '''
    models = fetch_list(get_db(), query)

    return [model['model'] for model in models]


def sort_vehicles_by_model(models, sub_category, table, column, value):
    query = f'''
        SELECT
            id, price, model, {sub_category}
        FROM
            {table}
        WHERE {column} = {value}
    '''
    vehicle_list = fetch_list(get_db(), query)

    vehicles = dict((model, []) for model in models)
    for vehicle in vehicle_list:
        vehicles[vehicle['model']].append(vehicle)

    return vehicles


@app.route('/vehicles/cars/')
def cars_list():
    car_type = request.args.get('car_type')
    print(car_type)
    car_models = fetch_models('cars', 'car_type', car_type)
    cars = sort_vehicles_by_model(
        car_models, 'series', 'cars', 'car_type', car_type)

    return render_template(
        'vehicles.html', vehicle_type='Cars', models=car_models, vehicles=cars)


@app.route('/vehicles/cars/<id>')
def car_detail(id):
    kwargs = {
        'transmission_types': TRANSMISSION_TYPES,
        'fuel_types': FUEL_TYPES
    }

    query = f'''
        SELECT
            car_type, description, fuel, model, price, series, transmission
        FROM
            cars
        WHERE
            id = {id}
    '''
    car = fetch_detail(get_db(), query)
    print(car['car_type'])
    return render_template('vehicle.html', vehicle=car, **kwargs)


@app.route('/vehicles/trucks/')
def trucks_list():
    kwargs = {
        'size_types': SIZE_TYPES,
        'weight_category_types': WEIGHT_CATEGORY_TYPES
    }
    weight_category = request.args.get('weight_category')

    truck_models = fetch_models('trucks', 'weight_category', weight_category)
    trucks = sort_vehicles_by_model(
        truck_models, 'size', 'trucks', 'weight_category', weight_category)

    return render_template(
        'vehicles.html', vehicle_type='Trucks', models=truck_models,
        vehicles=trucks, **kwargs)


@app.route('/vehicles/trucks/<id>')
def truck_detail(id):
    kwargs = {
        'size_types': SIZE_TYPES
    }

    query = f'''
        SELECT
            description, model, price, size, weight_category
        FROM
            trucks
        WHERE
            id = {id}
    '''

    truck = fetch_detail(get_db(), query)
    return render_template('vehicle.html', vehicle=truck, **kwargs)


@app.route('/admin')
def admin_index():
    if not session.get('username', None) or not session.get('user_id', None):
        return redirect(url_for('admin_login'))

    kwargs = {
        'size_types': SIZE_TYPES
    }

    query = 'SELECT id, title FROM posts'
    posts = fetch_list(get_db(), query)

    query = 'SELECT id, model, series FROM cars'
    cars = fetch_list(get_db(), query)

    query = 'SELECT id, model, size FROM trucks'
    trucks = fetch_list(get_db(), query)

    return render_template(
        'admin.html', posts=posts, cars=cars, trucks=trucks, **kwargs)


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


def delete_query(table, id):
    query = f'''
        DELETE FROM {table} WHERE id = {id}
    '''

    commit_data(get_db(), query)


@app.route('/admin/posts/create', methods=['GET', 'POST'])
def admin_add_post():
    kwargs = {
        'post_status_types': POST_STATUS_TYPES
    }

    if request.method == 'GET':
        return render_template('post_form.html', action='Add', **kwargs)

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
        return render_template(
            'post_form.html', action='Add', created=True, **kwargs)


@app.route('/admin/posts/<id>')
def admin_get_post(id):
    kwargs = {
        'post_status_types': POST_STATUS_TYPES
    }

    query = f'''
        SELECT
            id, title, slug, content, status
        FROM
            posts
        WHERE
            id = {id}
    '''

    post = fetch_detail(get_db(), query)
    return render_template(
        'post_form.html', action='Update', post=post, **kwargs)


@app.route('/admin/posts/<id>/update', methods=['POST'])
def admin_update_post(id):
    data = request.form

    title = data.get('title').strip()
    slug = data.get('slug').strip()
    content = data.get('content').strip()
    status = int(data.get('status'))

    query = f'''
        UPDATE
            posts
        SET
            title = '{title}', slug = '{slug}', content = '{content}',
            status={status}
        WHERE
            id = {id}
    '''

    commit_data(get_db(), query)
    return redirect(url_for('admin_get_post', id=id))


@app.route('/admin/posts/<id>/delete', methods=['POST'])
def admin_delete_post(id):
    delete_query('posts', id)
    return redirect(url_for('admin_index'))


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

        return render_template(
            'car_form.html', created=created, action='Add', **kwargs)

    if request.method == 'GET':
        return render_template('car_form.html', action='Add', **kwargs)


@app.route('/admin/cars/<id>')
def admin_get_car(id):
    kwargs = {
        'vehicle_status_types': VEHICLE_STATUS_TYPES,
        'transmission_types': TRANSMISSION_TYPES,
        'fuel_types': FUEL_TYPES,
        'car_type_types': CAR_TYPE_TYPES
    }

    query = f'''
        SELECT id, car_type, model, slug, description, price, status,
               transmission, fuel, series
        FROM
            cars
        WHERE
            id = {id}
    '''

    car = fetch_detail(get_db(), query)
    return render_template(
        'car_form.html', car=car, action='Update', **kwargs)


@app.route('/admin/cars/<id>/update', methods=['POST'])
def admin_update_car(id):
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
        UPDATE
            cars
        SET
            car_type = {car_type}, description = '{description}',
            fuel = {fuel}, model = '{model}',
            price = {price}, series = '{series}', slug = '{slug}',
            status = {status}, transmission = '{transmission}'
        WHERE
            id = {id}

    '''

    commit_data(get_db(), query)
    return redirect(
        url_for('admin_get_car', id=id))


@app.route('/admin/cars/<id>/delete', methods=['POST'])
def admin_delete_car(id):
    delete_query('cars', id)
    return redirect(url_for('admin_index'))


@app.route('/admin/trucks/create', methods=['GET', 'POST'])
def admin_add_truck():
    kwargs = {
        'vehicle_status_types': VEHICLE_STATUS_TYPES,
        'size_types': SIZE_TYPES,
        'weight_category_types': WEIGHT_CATEGORY_TYPES
    }

    if request.method == 'POST':
        data = request.form

        model = data.get('model')
        slug = data.get('slug')
        description = data.get('description')
        price = data.get('price')
        status = data.get('status')
        size = data.get('size')
        weight_category = data.get('weight_category')

        query = f'''
            INSERT INTO
                trucks(
                    description, model, price, size, slug, status,
                    weight_category
                )
            VALUES
                (
                    '{description}', '{model}', {price}, {size}, '{slug}',
                    {status}, {weight_category}
                );

        '''

        created = True
        try:
            commit_data(get_db(), query)
        except Exception as e:
            print(e)
            created = False

        return render_template(
            'truck_form.html', created=created, action='Add', **kwargs)

    if request.method == 'GET':
        return render_template('truck_form.html', action='Add', **kwargs)


@app.route('/admin/trucks/<id>')
def admin_get_truck(id):
    kwargs = {
        'vehicle_status_types': VEHICLE_STATUS_TYPES,
        'size_types': SIZE_TYPES,
        'weight_category_types': WEIGHT_CATEGORY_TYPES
    }

    query = f'''
        SELECT
            id, model, slug, description, price, status, size, weight_category
        FROM
            trucks
        WHERE
            id = {id}
    '''

    truck = fetch_detail(get_db(), query)
    return render_template(
        'truck_form.html', truck=truck, action='Update', **kwargs)


@app.route('/admin/trucks/<id>/update', methods=['POST'])
def admin_update_truck(id):
    data = request.form

    model = data.get('model')
    slug = data.get('slug')
    description = data.get('description')
    price = data.get('price')
    status = data.get('status')
    size = data.get('size')
    weight_category = data.get('weight_category')

    query = f'''
        UPDATE
            trucks
        SET
            description = '{description}', model = '{model}', price = {price},
            size = {size}, slug = '{slug}', status = {status},
            weight_category = {weight_category}
        WHERE
            id = {id}
    '''

    commit_data(get_db(), query)
    return redirect(url_for('admin_get_truck', id=id))


@app.route('/admin/trucks/<id>/delete', methods=['POST'])
def admin_delete_truck(id):
    delete_query('trucks', id)
    return redirect(url_for('admin_index'))


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
