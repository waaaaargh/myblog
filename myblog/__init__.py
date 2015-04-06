from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join
from flask.ext.login import LoginManager

base_path = abspath(join(dirname(__file__), ".."))

app = Flask(__name__, template_folder=join(base_path, "templates"),
            static_folder=join(base_path, "static"))
app.config.from_pyfile(join(base_path, "myblog.cfg"))

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from myblog import login
from myblog import model
from myblog import views
import myblog.admin
