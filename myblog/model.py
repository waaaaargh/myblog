from myblog import db
from datetime import datetime

class category(db.Model):
    __tablename__ = 'category'
    def __repr__(self):
        return "Category: \"%s\"" % self.name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    posts = db.relationship("post", backref="category")

class post(db.Model):
    __tablename__ = 'post'
    def __repr__(self):
        return "Post \"%s\"" % self.title
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    excerpt = db.Column(db.String)
    content = db.Column(db.String)
    date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    comments = db.relationship("comment", backref="post")
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self):
        db.Model.__init__(self)
        self.date = datetime.now()

class comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    date = db.Column(db.DateTime)
    name = db.Column(db.String)
    email = db.Column(db.String)
    text = db.Column(db.String)

class user(db.Model):
    __tablename__ = "user"
    def __repr__(self):
        return self.name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String, unique=True)
    passwordhash = db.Column(db.String, unique=False)
    posts = db.relationship('post', backref="owner")
    
