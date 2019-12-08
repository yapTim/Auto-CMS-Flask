# Auto-CMS
Made with Python 3.7 and Flask

## How to Run
Prerequisites:
- `Python 3.7`
- Git
- `Pipenv`

Install `Pipenv`
```sh
$ pip install pipenv
# in Ubuntu
$ pip3 install pipenv
```

Clone repository
```sh
$ git clone https://github.com/mikazyap/Auto-CMS-Flask.git
```

Install dependencies
```sh
$ cd auto-cms-flask
$ pipenv install
```

Add `FLASK_APP` environment variable
```sh
$ export FLASK_APP=auto_cms.py
```

Run server
```sh
$ pipenv run flask run
```