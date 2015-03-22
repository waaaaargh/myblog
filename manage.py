#!/usr/bin/env python2
from flask.ext.script import Manager

from myblog import app

manager = Manager(app)

@manager.command
def initdb():
    from myblog import db
    db.create_all()

if __name__ == "__main__":
    manager.run()
