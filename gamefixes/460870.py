""" Game fix for GOD EATER RESURRECTION
"""
#pylint: disable=C0103

from protonfixes import util

def main():

    # Disables esync prevents crashes.
    util.disable_esync()
