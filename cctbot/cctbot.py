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

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.engine import Engine

import random
import re
import sys
import znc
sys.path.append('/srv/znc/.znc/cctbot')
from cctbotdb import Base, Twitch, Eve, Entrants, Wins


dummies = [
        ["lorene sarvis", ["e-sarvis", "e-sarvi2", "e-sarvis3"]],
        ["kristel giancola", ["e-giancola", "e-giancol2", "e-giancola3"]],
        ["loyd crick", ["e-crick", "e-cric2", "e-crick3"]],
        ["temeka keagle", ["e-keagle", "e-keagl2", "e-keagle3"]],
        ["helaine gaona", ["e-gaona", "e-gaon2", "e-gaona3"]],
        ["peggy dengler", ["e-dengler", "e-dengle2", "e-dengler3"]],
        ["irma seeley", ["e-seeley", "e-seele2", "e-seeley3"]],
        ["kari comstock", ["e-comstock", "e-comstoc2", "e-comstock3"]],
        ["maye petree", ["e-petree1", "e-petree2", "e-petree13"]],
        ["jone mccrady", ["e-mccrady", "e-mccrad2", "e-mccrady3"]],
        ["corrinne eastin", ["e-eastin", "e-easti2"]],
        ["roseann pruneda", ["e-pruneda", "e-pruned2"]],
        ["peg carithers", ["e-carithers", "e-carither2", "e-carithers3"]],
        ["yang castillo", ["e-castillo", "e-castill2", "e-castillo3"]],
        ["margene hobgood", ["e-hobgood", "e-hobgoo2", "e-hobgood3"]],
        ["ruben folse", ["e-folse", "e-fols2", "e-folse3"]],
        ["merle holtsclaw", ["e-holtsclaw", "e-holtscla2", "e-holtsclaw3"]],
        ["ginger hans", ["e-hans", "e-han2", "e-hans3"]],
        ["cyril haubert", ["e-haubert", "e-hauber2"]],
        ["morris jelks", ["e-jelks", "e-jelk2"]],
        ["felicita donlon", ["e-donlon", "e-donlo2", "e-donlon3"]],
        ["lauryn darner", ["e-darner", "e-darne2"]],
        ["kortney rawles", ["e-rawles", "e-rawle2", "e-rawles3"]],
        ["antoine metzger", ["e-metzger"]],
        ["birgit fannin", ["e-fannin", "e-fanni2", "e-fannin3"]],
        ["ezequiel callison", ["e-callison", "e-calliso2", "e-callison3"]],
        ["carissa flaugher", ["e-flaugher"]],
        ["nettie castille", ["e-castille", "e-castill2", "e-castille3"]],
        ["natisha deforge", ["e-deforge", "e-deforg2", "e-deforge3"]],
        ["antonina defoor", ["e-defoor", "e-defoo2", "e-defoor3"]],
    ]


class cctbot(znc.Module):
    module_types = [znc.CModInfo.UserModule]
    description = "Zarvox Toral's cctbot - by Robin Edmunds 2018"

    def OnChanMsg(self, nick, channel, message):

        # >>>>>>>>>>>> funcs start <<<<<<<<<<<<

        def Accessdenied(nick):
            self.PutIRC("PRIVMSG {} :@{}  ACCESS DENIED:  {}"
                        .format(chan, nick, random.choice(access_denied)))
            return

        def connectDB():
            global session
            engine = create_engine(
                'sqlite:////srv/znc/.znc/cctbot/cctdb.sqlite3'
            )
            Base.metadata.bind = engine

            DBSession = sessionmaker(bind=engine)
            session = DBSession()
            return

        def CCTu(nick, char):
            # !cct EVE CHAR
            twitch = session.query(Twitch).filter(Twitch.name == nick).scalar()
            if twitch is None:
                # user does not exist, add all
                add = Twitch(name=nick)
                add.eve.append(Eve(char=char))
                add.entrants = Entrants()
                session.add(add)
                self.PutIRC("PRIVMSG {} :@{}  Added to CCT list with new EVE \
                character. Good luck!".format(chan, nick))
            else:
                # user exists
                entered = session.query(Entrants).join(Twitch)\
                            .filter(Twitch.name == nick).scalar()
                char_exists = session.query(Eve).join(Twitch)\
                    .filter(Eve.char == char)\
                    .filter(Twitch.name == nick).scalar()
                if entered is None and char_exists is None:
                    # user exists, not entered, char doesnt exist
                    twitch.eve.append(Eve(char=char))
                    twitch.entrants = Entrants()
                    session.add(twitch)
                    self.PutIRC("PRIVMSG {} :@{}  Added to CCT list with new \
                    EVE character. Good luck!".format(chan, nick))
                elif entered is None and char_exists:
                    # all exist but not entered
                    twitch.entrants = Entrants()
                    session.add(twitch)
                    self.PutIRC("PRIVMSG {} :@{}  Added to CCT list. Good \
                    luck!".format(chan, nick))
                elif entered and char_exists is None:
                    # entered but char doesnt exist
                    twitch.eve.append(Eve(char=char))
                    session.add(twitch)
                    self.PutIRC("PRIVMSG {} :@{}  New EVE character added. \
                    Already in CCT list. Good luck!".format(chan, nick))
                elif entered and char_exists:
                    # entered and char exists
                    self.PutIRC("PRIVMSG {} :@{}  Already on CCT list. Good \
                    luck!".format(chan, nick))
                else:
                    self.PutIRC("PRIVMSG {} :@{}  Error:  CCTu() something \
                    went wrong".format(chan, nick))
            session.commit()
            return

        def CCT(nick):
            # !cct - add existing twitch user to entrants table
            twitch = session.query(Twitch).filter(Twitch.name == nick).scalar()
            if twitch is None:
                self.PutIRC("PRIVMSG {} :@{}  You don't have an EVE character \
                associated with your twitch name. Use '!cct EVE CHAR' to \
                enter CCT.".format(chan, nick))
            else:
                if twitch.entrants:
                    self.PutIRC("PRIVMSG {} :@{}  You are already entered. \
                    Good luck!".format(chan, nick))
                else:
                    twitch.entrants = Entrants()
                    session.add(twitch)
                    session.commit()
                    self.PutIRC("PRIVMSG {} :@{}  Added to CCT list. Good \
                    luck!".format(chan, nick))
            return

        def CCTreset():
            # !cctreset (admin only) - empty Entrants table
            qry = session.query(Entrants).count()
            if qry > 0:
                session.query(Entrants).delete()
                session.commit()
                self.PutIRC("PRIVMSG {} :@{}  Entrant list reset \
                successfully.".format(chan, nick))
            else:
                self.PutIRC("PRIVMSG {} :@{}  Entrant list already empty."
                            .format(chan, nick))
            return

        def CCTcount(silent=None):
            # !cctcount - return sum of all entrants
            count = session.query(Entrants).count()
            if silent is None:
                self.PutIRC("PRIVMSG {} :@{}  There are currently * {} * CCT \
                entrants.".format(chan, nick, count))
            return count

        def CCTremove(nick, silent=None):
            # !cctremove - remove user from entrants
            twitch = session.query(Twitch)\
                        .filter(Twitch.name == nick).scalar()
            c = session.query(Entrants)\
                .filter(Entrants.twitch_id == twitch.id).count()
            if c > 0:
                session.query(Entrants)\
                    .filter(Entrants.twitch_id == twitch.id).delete()
                session.commit()
                if silent is None:
                    self.PutIRC("PRIVMSG {} :@{}  You have now been removed \
                    from the CCT list.".format(chan, nick))
            else:
                if silent is None:
                    self.PutIRC("PRIVMSG {} :@{}  You were not on the CCT \
                    list.".format(chan, nick))
            return

        def CCTgetchars(nick, silent=None):
            # !cctchar(s) - return user's eve chars
            c = session.query(Eve.id).join(Twitch)\
                .filter(Twitch.name == nick).count()
            if c > 0:
                qry = session.query(Eve.char).join(Twitch)\
                        .filter(Twitch.name == nick).all()
                list = []
                for row in qry:
                    list.append(row[0])
                string = ", ".join(list)
                if silent is None:
                    self.PutIRC("PRIVMSG {} :@{}  Your associated EVE \
                    character(s):  {}".format(chan, nick,  string.title()))
                return string
            else:
                if silent is None:
                    self.PutIRC("PRIVMSG {} :@{}  You have no associated EVE \
                    character(s).".format(chan, nick))
                return

        def CCTwins(nick, silent=None):
            # # temp, add win record for testing
            # temp = session.query(Twitch.id).filter(Twitch.name==nick).one()
            # # self.PutIRC(temp)
            # add = Wins(twitch_id=temp[0])
            # session.add(add)
            # session.commit()

            # !cctwins - return datetime of last win, win count
            count = session.query(Wins).join(Twitch)\
                        .filter(Twitch.name == nick).count()
            if count > 0:
                # get last win row
                qry = session.query(Wins).join(Twitch)\
                            .filter(Twitch.name == nick)\
                            .order_by(Wins.date.desc()).first()

                last_win = qry.date
                # format date
                last_win = last_win.strftime("%a, %d %b %Y, %H:%M, (EVE-Time)")
                dict = {
                    "count": count,
                    "date": last_win,
                }
                if silent is None:
                    sself.PutIRC("PRIVMSG {} :@{}  Last CCT win:  {}  |  Total\
                     wins:  {}".format(chan, nick,  last_win, count))
                    return
                else:
                    return dict
            else:
                if silent is None:
                    self.PutIRC("PRIVMSG {} :@{}  You have no wins. Keep \
                    playing and good luck!".format(chan, nick))
                return

        def CCTdelete(nick):
            # !cctdelete - remove ALL records for user
            scalar = session.query(Twitch).filter(Twitch.name == nick).scalar()
            if scalar:
                session.delete(scalar)
                session.commit()
                self.PutIRC("PRIVMSG {} :@{}  All records associated with your\
                 Twitch name have been deleted.".format(chan, nick))
            else:
                self.PutIRC("PRIVMSG {} :@{}  No records found for your Twitch\
                 user.".format(chan, nick))
            return

        def CCTdummy(dummies):
            # !cctdummy - add dummy records to db, remove in production
            for row in dummies:
                add = Twitch(name=row[0])
                list = []
                for char in row[1]:
                    x = Eve(char=char)
                    list.append(x)
                add.eve = list
                add.entrants = Entrants()
                # randomise win record entries between 0-4
                r_int = int(random.choice(range(0, 4)))
                if r_int > 0:
                    while r_int > 0:
                        r_int = r_int - 1
                        add.wins.append(Wins())
                session.add(add)
            session.commit()
            self.PutIRC("PRIVMSG {} :@{}  {}  dummy entries added"
                        .format(chan, nick, len(dummies)))
            return

        def CCTroll():
            # !cctroll - select winner, remove from entrants, record win,
            # display win history
            c = CCTcount(1)
            if c > 4:
                e = session.query(Twitch.name, Twitch.id)\
                        .filter(Entrants.twitch_id == Twitch.id).all()
                session.close()
                winner = random.choice(e)
                CCTremove(winner[0], 1)
                win_hist = CCTwins(winner[0], 1)  # get win history
                win_record = Wins(twitch_id=winner[1])
                session.add(win_record)
                session.commit()
                if win_hist:
                    self.PutIRC("PRIVMSG {} :WINNER >>> ** {} **  |  \
                    EVE char(s):  {}  |  Total wins: {}  |  Last win:  {}"
                                .format(
                                    chan,
                                    winner[0].title(),
                                    CCTgetchars(winner[0], 1).title(),
                                    win_hist['count'],
                                    win_hist['date']
                                ))
                else:
                    self.PutIRC("PRIVMSG {} :WINNER >>> ** {} **  |  \
                    EVE char(s):  {}  |  FIRST WIN!"
                                .format(
                                    chan,
                                    winner[0].title(),
                                    CCTgetchars(winner[0], 1).title()
                                ))
            else:
                self.PutIRC("PRIVMSG {} :@{}  There are * {} * entrants. Get 5\
                 or more before rolling. EVE am ded?!"
                            .format(chan, nick, c))

        # >>>>>>>>>>>> funcs end <<<<<<<<<<<<

        # main() in prototype

        # define cmds in regex
        r_cctu = re.compile("^!cct\s...", re.IGNORECASE)
        r_cct = re.compile("^!cct$", re.IGNORECASE)
        r_cctreset = re.compile("^!cctreset$", re.IGNORECASE)
        r_cctroll = re.compile("^!cctroll$", re.IGNORECASE)
        r_cctcount = re.compile("^!cctcount$", re.IGNORECASE)
        r_cctremove = re.compile("^!cctremove$", re.IGNORECASE)
        # r_cctdummy = re.compile("^!cctdummy$", re.IGNORECASE)
        r_cctchar = re.compile("^!cctchar$", re.IGNORECASE)
        r_cctchars = re.compile("^!cctchars$", re.IGNORECASE)
        r_cctwins = re.compile("^!cctwins$", re.IGNORECASE)
        r_cctdelete = re.compile("^!cctdelete$", re.IGNORECASE)
        r_ccthelp = re.compile("^!ccthelp$", re.IGNORECASE)
        # r_ADMIN = re.compile("^anarchicuk$", re.IGNORECASE)
        r_ADMIN = re.compile("^zarvoxtoral$", re.IGNORECASE)

        chan = channel.GetName()
        nick = nick.GetNick()
        nick = nick.lower()
        msg = message.s

        msg = msg.lower()
        msg_list = msg.split(" ")
        cmd = msg_list[0]
        msg_list.remove(msg_list[0])
        char = " ".join(msg_list)

        access_denied = [
            "Facial scan failed to detect features of malnourished goat",
            "Failed to detect elite Q-clicking skills",
            "Green killboard detected",
            "MASB not positioned on edge of rack",
            "Light missile condor detected",
            "Man balls remain to be found",
        ]

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
            self.PutIRC("PRIVMSG {} :The Community Contract Clustertruck! I \
            fly your ships/fits out of Jita 4-4! http://bit.ly/cct4ztm"
                        .format(chan, nick))
        # admin only cmds
        elif r_cctreset.match(cmd):
            if r_ADMIN.match(nick):
                CCTreset()
            else:
                Accessdenied(nick)
        elif r_cctroll.match(cmd):
            if r_ADMIN.match(nick):
                CCTroll()
            else:
                Accessdenied(nick)
        # # testing and dev only cmd
        # elif r_cctdummy.match(cmd):
        #     if r_ADMIN.match(nick):
        #         CCTdummy(dummies)
        #     else:
        #         Accessdenied(nick)
        # else:
        #     self.PutIRC("PRIVMSG {} :@{} no match".format(chan, nick))
        session.close()

        return znc.CONTINUE

# END END END END END END END END END END END END END END
