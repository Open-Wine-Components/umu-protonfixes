""" Game fix for GOD EATER 2 Rage Burst
"""
#pylint: disable=C0103

from protonfixes import util

def main():

    # Disables esync prevents crashes.
    util.disable_esync()
