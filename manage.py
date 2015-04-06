#!/usr/bin/env python2
from flask.ext.script import Manager

from myblog import app

manager = Manager(app)

@manager.command
def createuser():
    import getpass
    from myblog import db
    from myblog.model import user
    from werkzeug.security import generate_password_hash
    
    username = raw_input("username: ")
    email = raw_input("email: ")
    
    password = None
    password_confirm = None
    while password != password_confirm or password is None:
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Password (confirm): ")
        
        if password != password_confirm:
            print("[e] Passwords do not match")
        else:
            break
            
    print("[i] okay, I will now create a user with the password you provided.")
    u = user()
    u.name = username
    u.email = email
    u.passwordhash = generate_password_hash(password)
    
    db.session.add(u)
    db.session.commit()

    print("[i] user %s created successfully." % u.name)

@manager.command
def initdb():
    from myblog import db
    db.create_all()

if __name__ == "__main__":
    manager.run()
