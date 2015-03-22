from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

from os.path import abspath, dirname, join
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+join(abspath(join(dirname(__file__), "..")), "myblog.sqlite")

db = SQLAlchemy(app)

from myblog import model
