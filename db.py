import sqlite3


# Constants
DRAFT = 0
PUBLISHED = 1


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
