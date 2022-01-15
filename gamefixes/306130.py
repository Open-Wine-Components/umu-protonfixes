""" Game fix for The Elder Scrolls Online
"""

#pylint: disable=C0103

from protonfixes import util

def main():
    util.set_environment('PROTON_SET_GAME_DRIVE','1')
