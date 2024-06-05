""" Game fix for The Quintessential Quintuplets - Five Memories Spent With You
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Install xact
    """

    # Fixes audio not playing and some background music
    util.protontricks('xact')
