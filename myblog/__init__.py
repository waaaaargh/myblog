from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join

base_path = abspath(join(dirname(__file__), ".."))

app = Flask(__name__, template_folder=join(base_path, "templates"),
            static_folder=join(base_path, "static"))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+join(base_path, "myblog.sqlite")
app.secret_key = "topkek"

db = SQLAlchemy(app)
from myblog import model
from myblog import views
import myblog.admin
