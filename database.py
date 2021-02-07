from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///./data.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Snap(Base):
    __tablename__ = 'snaps'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    total_forks = Column(Integer)
    total_stargazers = Column(Integer)
    total_watchers = Column(Integer)
    total_open_issues = Column(Integer)
    followers = Column(Integer)
    def __repr__(self):
        return f'Snap {self.id}'

class Repo(Base):
    __tablename__ = 'repos'
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer)
    name = Column(String)
    forks_count = Column(Integer)
    stargazers_count = Column(Integer)
    watchers_count = Column(Integer)
    open_issues_count = Column(Integer)
    def __repr__(self):
        return f'Repo {self.id}'

Base.metadata.create_all(engine)
