from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///hotsearch.db')
Session = sessionmaker(bind=engine)

class HotSearchRecord(Base):
    __tablename__ = 'hot_searches'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    keyword = Column(String(100))
    rank = Column(Integer)
    hot_value = Column(Integer)


class TopicDetailRecord(Base):
    __tablename__ = 'topic_details'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    keyword = Column(String(100))
    category = Column(String(100), default='未知')
    read_count = Column(Integer)
    discuss_count = Column(Integer)
    interact_count = Column(Integer)
    origin_count = Column(Integer)
    trend_24h = Column(Integer)
    trend_30d = Column(Integer)
    summary = Column(String(500), default='')
    location = Column(String(100), default='')
Base.metadata.create_all(engine)
