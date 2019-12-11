import sqlite3


# Constants

# Posts `status`
DRAFT = 0
PUBLISHED = 1
STATUS_TYPES = (
    (DRAFT, 'Draft'),
    (PUBLISHED, 'Published')
)

# Cars `car_type`
SEDAN = 0
SUV = 1
PICKUP = 2
CAR_TYPES = (
    (SEDAN, 'Sedan'),
    (SUV, 'SUV'),
    (PICKUP, 'Pickup')
)


def init_db(app):
    """ Initialize tables if they do not exist """
    query = '''
        SELECT name FROM sqlite_master WHERE type="table" AND name IN
        ("users", "posts")
    '''
    conn = sqlite3.connect('autocms.sqlite')
    cursor = conn.cursor()
    cursor.execute(query)

    if cursor.fetchone() is None:
        with app.app_context():
            with app.open_resource('schema.sql', mode='r') as f:
                cursor.executescript(f.read())
            conn.commit()


def execute_query(db, query):
    cursor = db.cursor()
    cursor.execute(query)
    return cursor


def fetch_list(db, query):
    cursor = execute_query(db, query)
    data = cursor.fetchall()
    return data


def fetch_detail(db, query):
    cursor = execute_query(db, query)
    data = cursor.fetchone()
    return data


def commit_data(db, query):
    execute_query(db, query)
    db.commit()


# conn = sqlite3.connect('autocms.sqlite')
# conn.row_factory = sqlite3.Row
# cur = conn.cursor()

# cur.execute('''
#     SELECT
#         posts.*,
#         users.first_name || ' ' || users.last_name AS author
#     FROM
#         posts INNER JOIN users ON posts.author_id = users.id
#     WHERE
#         status=1
# ''')
# x = cur.fetchone()
# print(dict(x))
