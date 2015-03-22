from myblog import db

post_is_in_category = db.Table('association', db.metadata,
                               db.Column('post_id', db.Integer,
                                         db.ForeignKey('posts.id')),
                               db.Column('category_id', db.Integer,
                                         db.ForeignKey('categories.id'))
)


class category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    posts = db.relationship("post", secondary=post_is_in_category)

    def __init__(self, name):
        self.name = name


class post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    excerpt = db.Column(db.String)
    content = db.Column(db.String)
    date = db.Column(db.DateTime)
    categories = db.relationship("category", secondary=post_is_in_category,
                                 backref='categories')
    comments = db.relationship("comment", backref="posts")


class page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    lastmodified = db.Column(db.DateTime)


class comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    date = db.Column(db.DateTime)
    name = db.Column(db.String)
    email = db.Column(db.String)
    text = db.Column(db.String)
