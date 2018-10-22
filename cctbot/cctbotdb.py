from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class Twitch(Base):
    __tablename__ = 'twitch'
    id = Column(Integer, primary_key=True)
    name = Column(String(35), nullable=False)


class Eve(Base):
    __tablename__ = 'eve'
    id = Column(Integer, primary_key=True)
    twitch_id = Column(Integer, ForeignKey('twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    char = Column(String(70), nullable=False)
    # Use cascade='delete,all' to propagate the deletion of a Twitch row to children
    twitch = relationship(
        Twitch,
        backref=backref('eve',
                         uselist=True,
                         cascade_backrefs=True,
                         lazy='joined',
                         cascade='all,delete-orphan'))


class Entrants(Base):
    __tablename__ = 'entrants'
    id = Column(Integer, primary_key=True)
    twitch_id = Column(Integer, ForeignKey('twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    # Use cascade='delete,all' to propagate the deletion of a Twitch row to children
    twitch = relationship(
        Twitch,
        backref=backref('entrants',
                         uselist=False,
                         cascade_backrefs=True,
                         lazy='joined',
                         cascade='all,delete-orphan'))


class Wins(Base):
    __tablename__ = 'wins'
    id = Column(Integer, primary_key=True)
    twitch_id = Column(Integer, ForeignKey('twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    # Use cascade='delete,all' to propagate the deletion of a Twitch row to children
    date = Column(DateTime, default=func.now(), nullable=False)
    twitch = relationship(
        Twitch,
        backref=backref('wins',
                         uselist=True,
                         cascade_backrefs=True,
                         lazy='joined',
                         cascade='all,delete-orphan'))


engine = create_engine('sqlite:////srv/znc/.znc/cctbot/cctdb.sqlite3')
Base.metadata.create_all(engine)
