#!/usr/bin/env python2
from flask.ext.script import Manager

from myblog import app

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
