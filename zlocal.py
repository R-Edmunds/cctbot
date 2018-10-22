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
    return

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
        # user exists
        entered = session.query(Entrants).join(Twitch)\
                    .filter(Twitch.name==nick).scalar()
        char_exists = session.query(Eve).join(Twitch)\
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
    qry = session.query(Entrants).count()
    if qry > 0:
        session.query(Entrants).delete()
        session.commit()
        print("-- Entrant list reset successfully.")
    else:
        print("-- Entrant list already empty.")
    return

def CCTcount(silent=None):
    count = session.query(Entrants).count()
    if silent == None:
        print("-- There are currently {} CCT entrants.".format(count))
    return count

def CCTremove(nick, silent=None):
    twitch = session.query(Twitch)\
                .filter(Twitch.name==nick).scalar()
    c = session.query(Entrants).filter(Entrants.twitch_id==twitch.id).count()
    if c > 0:
        session.query(Entrants).filter(Entrants.twitch_id==twitch.id).delete()
        session.commit()
        if silent == None:
            print("-- You have now been removed from the CCT list.")
    else:
        if silent == None:
            print("-- You were not on the CCT list.")
    return

def CCTgetchars(nick, silent=None):
    c = session.query(Eve.id).join(Twitch).filter(Twitch.name==nick).count()
    if c > 0:
        qry = session.query(Eve.char).join(Twitch)\
                .filter(Twitch.name==nick).all()
        list = []
        for row in qry:
            list.append(row[0])
        string = ", ".join(list)
        if silent == None:
            print("-- Your associated EVE character(s):  {}".format( string.title() ))
        return string
    else:
        if silent == None:
            print("-- You have no associated EVE character(s).")
        return

def CCTwins(nick, silent=None):
    # temp, add win record
    temp = session.query(Twitch.id).filter(Twitch.name==nick).one()
    # print(temp)
    add = Wins(twitch_id=temp[0])
    session.add(add)
    session.commit()

    # output date, time of last win, win count
    count = session.query(Wins).join(Twitch)\
                .filter(Twitch.name==nick).count()
    if count > 0:
        qry = session.query(Wins).join(Twitch)\
                    .filter(Twitch.name==nick)\
                    .order_by( Wins.date.desc() ).first()

        last_win = qry.date
        last_win = last_win.strftime("%a, %d %b %Y, %H:%M, (EVE-Time)")
        # print(last_win)
        if silent == None:
            print("-- Last CCT win:  {}  |  Total wins:  {}".format( last_win, count ))
    else:
        if silent == None:
            print("-- You have no wins. Keep playing and good luck!")

def CCTdelete(nick):
    scalar = session.query(Twitch).filter(Twitch.name==nick).scalar()
    if scalar:
        session.delete(scalar)
        session.commit()
        print("-- All records associated with your Twitch name have been deleted.")
    else:
        print("-- No records found for your Twitch user.")
    return

def CCTdummy(dummies):
    for row in dummies:
        add = Twitch(name=row[0])
        list = []
        for char in row[1]:
            x = Eve(char=char)
            list.append(x)
        add.eve = list
        add.entrants = Entrants()
        add.wins = [Wins()]
        session.add(add)
    session.commit()
    print("-- {}  dummy entries added".format( len(dummies) ))
    return

def CCTroll():
    c = CCTcount(1)
    if c > 4:
        e = session.query(Twitch.name, Twitch.id)\
                .filter(Entrants.twitch_id==Twitch.id).all()
        session.close()
        winner = random.choice(e)
        CCTremove(winner[0], 1)
        win_record = Wins(twitch_id=winner[1])
        session.add(win_record)
        session.commit()
        print("-- WINNER:  {} - EVE chars:  {}".format( winner[0].title(), CCTgetchars(winner[0], 1).title() ))
    else:
        print("-- There are {} entrants. Get 5 or more before rolling. EVE am ded?!".format(c))


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
    r_cctwins = re.compile("^!cctwins$", re.IGNORECASE)
    r_cctdelete = re.compile("^!cctdelete$", re.IGNORECASE)
    r_ccthelp = re.compile("^!ccthelp$", re.IGNORECASE)
    ADMIN = re.compile("^admin$", re.IGNORECASE)

    while True:
        print("Select irc nick: -\n\n"
            + "  1. admin\n"
            + "  2. fred\n"
            + "  3. geoff\n"
            + "  4. anarchicuk\n\n"
        )
        # slcn = "2"
        slcn = input("Selection:  ")

        if slcn == "1":
            nick = "admin"
            break
        elif slcn == "2":
            nick = "fred"
            break
        elif slcn == "3":
            nick = "geoff"
            break
        elif slcn == "4":
            nick = "anarchicuk"
            break
        os.system('cls')  # on windows
    os.system('cls')  # on windows

    while True:
        msg = input("{}:  ".format(nick)).lower()

        msg_list = msg.split(" ")
        cmd = msg_list[0]
        msg_list.remove(msg_list[0])
        char = " ".join(msg_list)

        connectDB()
        session.execute("PRAGMA foreign_keys=ON")

        if r_cctu.match(msg):
            CCTu(nick, char)
        elif r_cct.match(cmd):
            CCT(nick)
        elif r_cctcount.match(cmd):
            CCTcount()
        elif r_cctremove.match(cmd):
            CCTremove(nick)
        elif r_cctchar.match(cmd) or r_cctchars.match(cmd):
            CCTgetchars(nick)
        elif r_cctdelete.match(cmd):
            CCTdelete(nick)
        elif r_cctwins.match(cmd):
            CCTwins(nick)
        elif r_ccthelp.match(cmd):
            pass # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # admin only cmds
        elif r_cctreset.match(cmd):
            CCTreset()
        elif r_cctroll.match(cmd):
            CCTroll()
        elif r_cctdummy.match(cmd):
            CCTdummy(dummies)
        else:
            print("-- no match")
        session.close()



if __name__ == '__main__':
    main()
