from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    excerpt = Column(String)
    content = Column(String)
    date = Column(DateTime)
    comments = relationship("comment", backref="post")

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
    
"""
Creates all the tables in the <engine> database.
"""
def initdb(engine):
    Base.metadata.create_all(bind=engine)
