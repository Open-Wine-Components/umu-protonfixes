""" Game fix for Gothic 1
"""
#pylint: disable=C0103

import os
from protonfixes import util

def main():

    # Fix the game getting locked
    util.disable_fsync()
    # To make cinametics work install https://github.com/dosinabox/g1_steam_fix
