"""Horizon Zero Dawn Remastered"""

from sys import argv
from os import environ
from protonfixes import util


def main() -> None:
    """Won't connect to internet to login to PSN without using `-showlinkingqr` or `SteamDeck=1` options."""
    if environ.get('SteamDeck', '0') == '0' and '-showlinkingqr' not in argv:
        util.append_argument('-showlinkingqr')
    # this allows the game to detect saves from the original Complete Edition
    util.import_saves_folder(1151640, 'My Documents/Horizon Zero Dawn')
