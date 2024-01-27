""" Call Winetricks GUI
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Requires seccomp
    """

    util.protontricks('gui')
