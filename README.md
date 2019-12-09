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
# on Ubuntu
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
# or
$ python -m pipenv install
```

Run server
```sh
$ pipenv run flask run
# or
$ python -m pipenv run flask run
```

### References
- http://flask.palletsprojects.com/en/1.1.x/quickstart/
- http://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#sqlite3
- https://codeburst.io/jinja-2-explained-in-5-minutes-88548486834e
- https://datatofish.com/create-database-python-using-sqlite3/
- https://www.sqlite.org/lang_datefunc.html
- https://www.journaldev.com/23365/python-string-to-datetime-strptime
- https://www.programiz.com/python-programming/datetime/strftime
- https://stackoverflow.com/questions/4830535/how-do-i-format-a-date-in-jinja2