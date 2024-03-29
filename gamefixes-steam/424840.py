""" Game fix for Little Nightmares
"""
# pylint: disable=C0103

from protonfixes import util

def main():
    """ Add launch parameter
    """

    # The game crashes if running with more than one CPU thread,
    # adding "-onethread" will force the game to use only one CPU thread
    util.append_argument('-onethread')
