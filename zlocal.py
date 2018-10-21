#!/usr/bin/python3

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

from sqlalchemy.engine import Engine
# from sqlalchemy import event

from dbdev import Base, Twitch, Eve, Entrants, Wins
import random

dummies = [
        ["Lorene Sarvis", ["e-Sarvis", "e-Sarvi2", "e-Sarvis3"]],
        ["Kristel Giancola", ["e-Giancola", "e-Giancol2", "e-Giancola3"]],
        ["Loyd Crick", ["e-Crick", "e-Cric2", "e-Crick3"]],
        ["anarchicuk", ["Sukyakka", "Natalia Blackwater", "Yuzzette Freeman"]],
        ["Temeka Keagle", ["e-Keagle", "e-Keagl2", "e-Keagle3"]],
        ["Helaine Gaona", ["e-Gaona", "e-Gaon2", "e-Gaona3"]],
        ["Peggy Dengler", ["e-Dengler", "e-Dengle2", "e-Dengler3"]],
        ["Irma Seeley", ["e-Seeley", "e-Seele2", "e-Seeley3"]],
        ["Kari Comstock", ["e-Comstock", "e-Comstoc2", "e-Comstock3"]],
        ["Maye Petree", ["e-Petree1", "e-Petree2", "e-Petree13"]],
        ["Jone Mccrady", ["e-Mccrady", "e-Mccrad2", "e-Mccrady3"]],
        ["Corrinne Eastin", ["e-Eastin", "e-Easti2",]],
        ["Roseann Pruneda", ["e-Pruneda", "e-Pruned2",]],
        ["Peg Carithers", ["e-Carithers", "e-Carither2", "e-Carithers3"]],
        ["Yang Castillo", ["e-Castillo", "e-Castill2", "e-Castillo3"]],
        ["Margene Hobgood", ["e-Hobgood", "e-Hobgoo2", "e-Hobgood3"]],
        ["Ruben Folse", ["e-Folse", "e-Fols2", "e-Folse3"]],
        ["Merle Holtsclaw", ["e-Holtsclaw", "e-Holtscla2", "e-Holtsclaw3"]],
        ["Ginger Hans", ["e-Hans", "e-Han2", "e-Hans3"]],
        ["Cyril Haubert", ["e-Haubert", "e-Hauber2",]],
        ["Morris Jelks", ["e-Jelks", "e-Jelk2",]],
        ["Felicita Donlon", ["e-Donlon", "e-Donlo2", "e-Donlon3"]],
        ["Lauryn Darner", ["e-Darner", "e-Darne2",]],
        ["Kortney Rawles", ["e-Rawles", "e-Rawle2", "e-Rawles3"]],
        ["Antoine Metzger", ["e-Metzger",]],
        ["Birgit Fannin", ["e-Fannin", "e-Fanni2", "e-Fannin3"]],
        ["Ezequiel Callison", ["e-Callison", "e-Calliso2", "e-Callison3"]],
        ["Carissa Flaugher", ["e-Flaugher",]],
        ["Nettie Castille", ["e-Castille", "e-Castill2", "e-Castille3"]],
        ["Natisha Deforge", ["e-Deforge", "e-Deforg2", "e-Deforge3"]],
        ["Antonina Defoor", ["e-Defoor", "e-Defoo2", "e-Defoor3"]],
    ]


def connectDB():
    global session
    engine = create_engine('sqlite:///db.sqlite3')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
