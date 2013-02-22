from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    excerpt = Column(String)
    content = Column(String)
    date = Column(Date)

"""
Creates all the tables in the <engine> database.
"""
def initdb(engine):
    Base.metadata.create_all(bind=engine)
