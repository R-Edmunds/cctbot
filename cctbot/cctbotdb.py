#!/usr/bin/python3
#
# Description: Twitch chatbot built as ZNC user module.
# Copyright (c) 2018 Robin Edmunds
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
    twitch_id = Column(Integer, ForeignKey(
        'twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    char = Column(String(70), nullable=False)
    # brackref cascade don't appear to work despite being pulled directly from
    # sqlalchemy docs. Foreign key CASCADE params are what cause cascade.
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
    twitch_id = Column(Integer, ForeignKey(
        'twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    # brackref cascade don't appear to work despite being pulled directly from
    # sqlalchemy docs. Foreign key CASCADE params are what cause cascade.
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
    twitch_id = Column(Integer, ForeignKey(
        'twitch.id', ondelete='CASCADE', onupdate='CASCADE'))
    # brackref cascade don't appear to work despite being pulled directly from
    # sqlalchemy docs. Foreign key CASCADE params are what cause cascade.
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
