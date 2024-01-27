""" Game fix for Stronghold Crusader Extreme HD
Fixes Multiplayer
"""

# pylint: disable=C0103

from protonfixes import util


def main():
    """ Installs directplay
    """

    util.protontricks('directplay')
