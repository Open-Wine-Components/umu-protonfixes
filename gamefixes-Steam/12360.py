""" Game fix for FlatOut: Ultimate Carnage (2008)
This game requires GFWL, so a mocked 'xlive.dll' is required (multiplayer doesn't work, but single player does)

"""

#pylint: disable=C0103

from protonfixes import util


def main():
    util.protontricks('xliveless')
