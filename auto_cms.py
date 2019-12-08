from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/posts')
def post_admin():
    return render_template('posts_admin.html')
