from sqlalchemy import Column, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    '''Videos.'''

    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    in_working = Column(Boolean, default=True)
    name = Column(Text)
    file_key = Column(Text)
