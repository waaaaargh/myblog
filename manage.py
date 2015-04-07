#!/usr/bin/env python2
from sys import exit

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
    

@manager.command
def importpickle(picklefile, username):
    from myblog import db
    from myblog.model import post, user, comment, category
    import pickle

    # find username
    u = user.query.filter(user.name == username).first()
    if u is None:
        print("[e] user %s is not present in database" % username)
        exit(1)

    with open(picklefile, 'r') as f:
        posts = pickle.load(f)
        
    print("[i] okay, found %i posts" % len(posts))

    for p_old in posts:
        p_new = post()
        p_new.title = p_old.title
        p_new.excerpt = p_old.excerpt
        p_new.content = p_old.content
        p_new.date = p_old.date
        p_new.owner = u

        for c_old in p_old.comments:
            c_new = comment()
            c_new.post = p_new
            c_new.email = c_old.email
            c_new.name = c_old.name
            c_new.text = c_old.text
            c_new.date = c_old.date
            p_new.comments.append(c_new)

        if len(p_old.categories) > 0:
            c_old = p_old.categories[0]
            c_new = category.query.filter(category.name == c_old.name).first()

            if c_new is None:
                c_new = category()
                c_new.name = c_old.name
            
            p_new.category = c_new

        db.session.add(p_new)
        db.session.commit()

if __name__ == "__main__":
    manager.run()
