
# cctbot - Raffle-Like Twitch Chatbot

## Problem
Elite PVPing EVE Online Twitch streamer Zarvox Toral has a stream event called
"Contract Cluster Truck". In CCT, viewers offer to give Zarvox a ship to fly,
however more ships are offered than can be flown. Zarvox selects a ship by
listing all those people in chat that state their intention to partake in notepad, and then uses random.org to select a winner.

The current solution is inelegant and time-consuming and often leads to
confusion as twitch usernames are rarely the same as EVE character names making it
hard to find the winner's contract within the EVE client.

https://www.twitch.tv/zarvoxtoral

## Solution
A bespoke chatbot written as a __'user module' for the ZNC IRC bouncer.__

The chatbot will accept a short list of __!commands__. Twitch users will enter the CCT event and simultaneously register their EVE
character name(s) against their twitch name.

EVE character names will be stored against corresponding twitch usernames in a
SQLite database.
On a CCT win, these EVE character name(s) will be revealed making it easy for
Zarvox to find the corresponding contract and start flying their ship.

On a win the winning user will be removed from the entrant pool, preventing a second win on the same day.

At the end of the event the admin "Zarvox", will run __!cctreset__ to clear the entrant list ready for the next event.

## Contributing
If you have a suggestion for improvement or would like to contribute, let me know and we can discuss. If you'd like to fork the code for your own project, go ahead.

If you'd like me develop a similar chatbot for you, my services are available for a nominal fee.

## Installation
This chatbot is written as a Python3 user module for the ZNC IRC bouncer. It is the bouncer that manages and maintains the connection to the twitch IRC network.

See ZNC documentation for ZNC setup: https://wiki.znc.in/ZNC

1. Download "cctbot" dir and place in desired location
1. Modify __sys.path.append('/your/cctbot/dir')__ in __cctbot.py__
1. Modify db location __'sqlite://///your/cctbot/dir/db.sqlite3'__ in __cctbot.py AND cctbotdb.py__
1. Symlink __cctbot.py__ to __/your/znc/install/modules__
1. Within ZNC control panel, add the module to your twitch IRC user
1. See HELP.md for end user help

## License
> Description: Twitch chatbot built as ZNC user module.
>
> Copyright &copy; 2018 Robin Edmunds
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <https://www.gnu.org/licenses/>.
