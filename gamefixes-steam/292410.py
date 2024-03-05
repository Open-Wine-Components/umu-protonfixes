""" Street Racing Syndicate
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    util.protontricks('lavfilters') # fix videos
    util.winedll_override('d3d9', 'n,b') # in case user uses the ThirteenAG widescreen fix
