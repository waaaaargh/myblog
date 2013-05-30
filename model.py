from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

post_is_in_category = Table('association', Base.metadata,
                            Column('post_id', Integer,
                                   ForeignKey('posts.id')),
                            Column('category_id', Integer,
                                   ForeignKey('categories.id'))
                            )


class category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    posts = relationship("post", secondary=post_is_in_category)

    def __init__(self, name):
        self.name = name


class post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    excerpt = Column(String)
    content = Column(String)
    date = Column(DateTime)
    categories = relationship("category", secondary=post_is_in_category,
                              backref='categories')
    comments = relationship("comment", backref="posts")


class page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    lastmodified = Column(DateTime)


class comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    date = Column(DateTime)
    name = Column(String)
    email = Column(String)
    text = Column(String)


def initdb(engine):
    """
    Creates all the tables in the <engine> database.
    """
    Base.metadata.create_all(bind=engine)
