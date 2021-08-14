""" Game fix for Gothic II: Gold Edition
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():

    # Fix the game getting locked on exit
    util.disable_fsync()
    # To make cinametics work install and FullHD resolution https://github.com/dosinabox/g2_steam_fix
