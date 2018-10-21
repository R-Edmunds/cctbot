#!/usr/bin/python3

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

from sqlalchemy.engine import Engine
# from sqlalchemy import event

from zdb import Base, Twitch, Eve, Entrants, Wins
import random

import os
import re

dummies = [
        ["lorene sarvis", ["e-sarvis", "e-sarvi2", "e-sarvis3"]],
        ["kristel giancola", ["e-giancola", "e-giancol2", "e-giancola3"]],
        ["loyd crick", ["e-crick", "e-cric2", "e-crick3"]],
        ["anarchicuk", ["sukyakka", "natalia blackwater", "yuzzette freeman"]],
        ["temeka keagle", ["e-keagle", "e-keagl2", "e-keagle3"]],
        ["helaine gaona", ["e-gaona", "e-gaon2", "e-gaona3"]],
        ["peggy dengler", ["e-dengler", "e-dengle2", "e-dengler3"]],
        ["irma seeley", ["e-seeley", "e-seele2", "e-seeley3"]],
        ["kari comstock", ["e-comstock", "e-comstoc2", "e-comstock3"]],
        ["maye petree", ["e-petree1", "e-petree2", "e-petree13"]],
        ["jone mccrady", ["e-mccrady", "e-mccrad2", "e-mccrady3"]],
        ["corrinne eastin", ["e-eastin", "e-easti2",]],
        ["roseann pruneda", ["e-pruneda", "e-pruned2",]],
        ["peg carithers", ["e-carithers", "e-carither2", "e-carithers3"]],
        ["yang castillo", ["e-castillo", "e-castill2", "e-castillo3"]],
        ["margene hobgood", ["e-hobgood", "e-hobgoo2", "e-hobgood3"]],
        ["ruben folse", ["e-folse", "e-fols2", "e-folse3"]],
        ["merle holtsclaw", ["e-holtsclaw", "e-holtscla2", "e-holtsclaw3"]],
        ["ginger hans", ["e-hans", "e-han2", "e-hans3"]],
        ["cyril haubert", ["e-haubert", "e-hauber2",]],
        ["morris jelks", ["e-jelks", "e-jelk2",]],
        ["felicita donlon", ["e-donlon", "e-donlo2", "e-donlon3"]],
        ["lauryn darner", ["e-darner", "e-darne2",]],
        ["kortney rawles", ["e-rawles", "e-rawle2", "e-rawles3"]],
        ["antoine metzger", ["e-metzger",]],
        ["birgit fannin", ["e-fannin", "e-fanni2", "e-fannin3"]],
        ["ezequiel callison", ["e-callison", "e-calliso2", "e-callison3"]],
        ["carissa flaugher", ["e-flaugher",]],
        ["nettie castille", ["e-castille", "e-castill2", "e-castille3"]],
        ["natisha deforge", ["e-deforge", "e-deforg2", "e-deforge3"]],
        ["antonina defoor", ["e-defoor", "e-defoo2", "e-defoor3"]],
    ]


def connectDB():
    global session
    engine = create_engine('sqlite:///zdb.sqlite3')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

def CCTu(nick, char):
    twitch = session.query(Twitch).filter(Twitch.name==nick).scalar()
    if twitch == None:
        # user does not exist, add all
        add = Twitch(name=nick)
        add.eve.append(Eve(char=char))
        add.entrants = Entrants()
        session.add(add)
        print("-- You are now on the CCT list, with a new EVE character. Good luck!")
    else:
        entered = session.query(Entrants, Twitch.name)\
                    .filter(Twitch.name==nick).scalar()
        char_exists = session.query(Eve, Twitch.name)\
                    .filter(Eve.char==char)\
                    .filter(Twitch.name==nick).scalar()
        if entered == None and char_exists == None:
            # user exists, not entered, char doesnt exist
            twitch.eve.append(Eve(char=char))
            twitch.entrants = Entrants()
            session.add(twitch)
            print("-- You are now on the CCT list, with a new EVE character. Good luck!")
        elif entered == None and char_exists:
            # all exist but not entered
            twitch.entrants = Entrants()
            session.add(twitch)
            print("-- You are now on the CCT list. Good luck!")
        elif entered and char_exists == None:
            # entered but char doesnt exist
            twitch.eve.append(Eve(char=char))
            session.add(twitch)
            print("-- New EVE character added. Already in CCT list. Good luck!")
        elif entered and char_exists:
            # entered and char exists
            print("-- You are already on the CCT list. Good luck!")
        else:
            print("-- Error:  CCTu() something went wrong")
    session.commit()
    return

def CCT(nick):
    twitch = session.query(Twitch).filter(Twitch.name==nick).scalar()
    if twitch == None:
        print("-- You don't have an EVE character associated with you twitch name. Use '!cct EVE CHAR' to enter.")
    else:
        if twitch.entrants:
            print("-- You are already entered. Good luck!")
        else:
            twitch.entrants = Entrants()
            session.add(twitch)
            session.commit()
            print("-- You are now on the CCT list. Good luck!")
    return

def CCTreset():
    session.query(Entrants).delete()
    session.commit()
    return

def CCTcount():
    count = session.query(Entrants).count()
    print("-- There are currently {} CCT entrants.".format(count))
    return

def CCTremove(nick):
    twitch = session.query(Twitch)\
                .filter(Twitch.name==nick).scalar()
    c = session.query(Entrants).filter(Entrants.twitch_id==twitch.id).count()
    if c > 0:
        session.query(Entrants).filter(Entrants.twitch_id==twitch.id).delete()
        session.commit()
        print("-- You have now been removed from the CCT list.")
    else:
        print("-- You were not on the CCT list.")
    return

def CCTgetchars(nick):
    qry = session.query(Eve.char)\
            .filter(Twitch.name==nick).all()
    list = []
    for row in qry:
        list.append(row[0])
    string = ", ".join(list)
    print("-- Your associated EVE character(s):  {}".format( string.title() ))


def main():
    # define cmds in regex
    r_cctu = re.compile("^!cct\s...", re.IGNORECASE)
    r_cct = re.compile("^!cct$", re.IGNORECASE)
    r_cctreset = re.compile("^!cctreset$", re.IGNORECASE)
    r_cctroll = re.compile("^!cctroll$", re.IGNORECASE)
    r_cctcount = re.compile("^!cctcount$", re.IGNORECASE)
    r_cctremove = re.compile("^!cctremove$", re.IGNORECASE)
    r_cctdummy = re.compile("^!cctdummy$", re.IGNORECASE)
    r_cctchar = re.compile("^!cctchar$", re.IGNORECASE)
    r_cctchars = re.compile("^!cctchars$", re.IGNORECASE)
    r_cctdelete = re.compile("^!cctdelete$", re.IGNORECASE)
    r_ccthelp = re.compile("^!ccthelp$", re.IGNORECASE)
    r_cctabout = re.compile("^!cctabout$", re.IGNORECASE)
    ADMIN = re.compile("^admin$", re.IGNORECASE)

    while True:
        print("Select irc nick: -\n\n"
            + "  1. admin\n"
            + "  2. fred\n"
            + "  3. geoff\n\n"
        )
        slcn = "2"
        # slcn = input("Selection:  ")

        if slcn == "1":
            nick = "admin"
            break
        elif slcn == "2":
            nick = "fred"
            break
        elif slcn == "3":
            nick = "geoff"
            break
        os.system('cls')  # on windows
    os.system('cls')  # on windows

    while True:
        connectDB()
        session.execute("PRAGMA foreign_keys=ON")
        msg = input("{}:  ".format(nick)).lower()

        msg_list = msg.split(" ")
        cmd = msg_list[0]
        msg_list.remove(msg_list[0])
        char = " ".join(msg_list)

        if r_cctu.match(msg):
            print(char.upper())
            CCTu(nick, char)
        elif r_cct.match(cmd):
            CCT(nick)
        elif r_cctreset.match(cmd):
            CCTreset()
        elif r_cctroll.match(cmd):
            pass
        elif r_cctcount.match(cmd):
            CCTcount()
        elif r_cctremove.match(cmd):
            CCTremove(nick)
        elif r_cctdummy.match(cmd):
            pass
        elif r_cctchar.match(cmd):
            CCTgetchars(nick)
        elif r_cctchars.match(cmd):
            CCTgetchars(nick)
        elif r_cctdelete.match(cmd):
            CCTdelete(nick)
        elif r_ccthelp.match(cmd):
            pass
        elif r_cctabout.match(cmd):
            pass
        else:
            print("-- no match")
        session.close()



if __name__ == '__main__':
    main()
