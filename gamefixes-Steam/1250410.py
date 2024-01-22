""" Game fix for Flight Simulator 2020
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """ Needs fastlaunch option
    """

    # Fixes the startup process.
    util.append_argument('-FastLaunch')
